from typing import Dict, Any
from datetime import datetime, timezone
from primerlab.core.models import WorkflowResult, Primer, Amplicon, QCResult, RunMetadata
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper
from primerlab.core.logger import get_logger
from primerlab.core.exceptions import WorkflowError

logger = get_logger()

def run_pcr_workflow(config: Dict[str, Any]) -> WorkflowResult:
    """
    Executes the PCR workflow.
    """
    logger.info("Starting PCR Workflow execution...")
    
    # 1. Parse Input
    input_config = config.get("input", {})
    raw_sequence = input_config.get("sequence")
    seq_path = input_config.get("sequence_path")
    
    from primerlab.core.sequence import SequenceLoader
    
    try:
        if seq_path:
            sequence = SequenceLoader.load(seq_path)
        elif raw_sequence:
            sequence = SequenceLoader.load(raw_sequence)
        else:
            raise WorkflowError("No sequence provided in input (sequence or sequence_path).", "ERR_WORKFLOW_001")
    except Exception as e:
        raise WorkflowError(f"Sequence loading failed: {e}", "ERR_WORKFLOW_SEQ")
    
    logger.info(f"Input sequence length: {len(sequence)} bp")

    # 2. Run Primer3
    p3_wrapper = Primer3Wrapper()
    raw_results = p3_wrapper.design_primers(sequence, config)
    
    num_returned = raw_results.get('PRIMER_LEFT_NUM_RETURNED', 0)
    logger.info(f"Primer3 returned {num_returned} pairs.")

    # 3. Multi-Candidate Re-ranking (v0.1.3)
    from primerlab.core.reranking import RerankingEngine
    
    reranker = RerankingEngine(config)
    best_candidate, alternatives = reranker.select_best(raw_results)
    
    # 4. Parse Best Candidate into Data Models
    primers = {}
    amplicons = []
    
    if best_candidate:
        idx = best_candidate["index"]
        
        # v0.1.5: Primer Naming Convention
        # Priority: config > FASTA header > filename > default
        naming_config = config.get("parameters", {}).get("primer_naming", {})
        gene_name = naming_config.get("gene_name")
        
        if not gene_name:
            # Try to get from sequence loader (FASTA header or filename)
            gene_name = SequenceLoader.get_last_sequence_name()
        
        if not gene_name:
            gene_name = "primer"
        
        # Clean gene name for use in primer IDs
        gene_name = gene_name.replace(" ", "_").replace("-", "_")[:20]
        
        # Custom naming pattern or default
        fwd_pattern = naming_config.get("forward_pattern", "{gene}_F{idx}")
        rev_pattern = naming_config.get("reverse_pattern", "{gene}_R{idx}")
        
        fwd_id = fwd_pattern.format(gene=gene_name, idx=idx + 1)
        rev_id = rev_pattern.format(gene=gene_name, idx=idx + 1)
        
        # Forward Primer
        fwd_start, fwd_len = best_candidate["fwd_pos"]
        fwd_primer = Primer(
            id=fwd_id,
            sequence=best_candidate["fwd_seq"],
            tm=best_candidate["fwd_tm"],
            gc=best_candidate["fwd_gc"],
            length=fwd_len,
            start=fwd_start,
            end=fwd_start + fwd_len - 1,
            hairpin_dg=best_candidate["qc_details"].get("hairpin_fwd_dg", 0.0),
            homodimer_dg=best_candidate["qc_details"].get("homodimer_fwd_dg", 0.0),
            raw={"p3_index": idx, "passes_qc": best_candidate["passes_qc"]}
        )
        primers["forward"] = fwd_primer

        # Reverse Primer
        rev_start, rev_len = best_candidate["rev_pos"]
        rev_primer = Primer(
            id=rev_id,
            sequence=best_candidate["rev_seq"],
            tm=best_candidate["rev_tm"],
            gc=best_candidate["rev_gc"],
            length=rev_len,
            start=rev_start - rev_len + 1,
            end=rev_start,
            hairpin_dg=best_candidate["qc_details"].get("hairpin_rev_dg", 0.0),
            homodimer_dg=best_candidate["qc_details"].get("homodimer_rev_dg", 0.0),
            raw={"p3_index": idx, "passes_qc": best_candidate["passes_qc"]}
        )
        primers["reverse"] = rev_primer

        # Amplicon
        # v0.1.5: Extract actual amplicon sequence from template
        amp_start = fwd_start
        amp_end = rev_start
        
        # Extract amplicon sequence (fwd_start to rev_start inclusive)
        if 0 <= amp_start < len(sequence) and amp_start < amp_end <= len(sequence):
            amplicon_seq = sequence[amp_start:amp_end]
            # Calculate GC content
            gc_count = amplicon_seq.upper().count('G') + amplicon_seq.upper().count('C')
            amplicon_gc = (gc_count / len(amplicon_seq)) * 100 if amplicon_seq else 0.0
        else:
            amplicon_seq = "N/A"
            amplicon_gc = 0.0
            logger.warning(f"Could not extract amplicon sequence: positions {amp_start}-{amp_end}")
        
        amplicon = Amplicon(
            start=amp_start,
            end=amp_end,
            length=best_candidate["product_size"],
            sequence=amplicon_seq,
            gc=round(amplicon_gc, 1),
            tm_forward=best_candidate["fwd_tm"],
            tm_reverse=best_candidate["rev_tm"]
        )
        amplicons.append(amplicon)
        
        # Log selection info
        if best_candidate["passes_qc"]:
            logger.info(f"Selected primer pair #{idx} (passes ViennaRNA QC)")
        else:
            reasons = best_candidate["qc_details"].get("rejection_reasons", [])
            logger.warning(f"Best available primer #{idx} has QC warnings: {reasons}")

    # 4. Run QC
    from primerlab.workflows.pcr.qc import PCRQC
    qc_engine = PCRQC(config)
    
    qc_result = None
    if primers:
        qc_result = qc_engine.evaluate_pair(primers["forward"], primers["reverse"])
        
        # v0.1.4: Add quality score from best candidate
        if best_candidate:
            qc_result.quality_score = best_candidate.get("quality_score")
            qc_result.quality_category = best_candidate.get("quality_category")
            qc_result.quality_category_emoji = best_candidate.get("quality_category_emoji")
            qc_result.quality_penalties = best_candidate.get("quality_penalties")
        
        # Add QC warnings to main result warnings
        if qc_result.warnings:
            logger.warning(f"QC Warnings: {qc_result.warnings}")

    # v0.1.4: Get selection rationale
    rationale = None
    rationale_md = ""
    if best_candidate:
        rationale = reranker.get_rationale(best_candidate)
        rationale_md = reranker.get_rationale_markdown(best_candidate)
    
    # 5. Create Metadata
    from primerlab import __version__
    metadata = RunMetadata(
        workflow="pcr",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=__version__,
        parameters=config.get("parameters", {})
    )

    # 6. Create Result
    result = WorkflowResult(
        workflow="pcr",
        primers=primers,
        amplicons=amplicons,
        metadata=metadata,
        qc=qc_result,
        alternatives=alternatives if best_candidate else [],
        raw=raw_results
    )
    
    # v0.1.4: Add rationale to result
    result.rationale = rationale
    result.rationale_md = rationale_md
    
    # v0.1.4: Create audit log
    from primerlab.core.audit import create_audit_log
    from pathlib import Path
    
    output_dir = Path(config.get("output", {}).get("directory", "output"))
    try:
        create_audit_log(
            workflow="pcr",
            config=config,
            sequence=sequence,
            results={
                "success": bool(primers),
                "quality_score": qc_result.quality_score if qc_result else None,
                "quality_category": qc_result.quality_category if qc_result else None,
                "candidates_evaluated": len(reranker.rationale_tracker.passed) + len(reranker.rationale_tracker.rejections),
                "candidates_passed_qc": len(reranker.rationale_tracker.passed),
                "primers_designed": len(primers),
                "alternatives_count": len(alternatives)
            },
            output_dir=output_dir
        )
    except Exception as e:
        logger.warning(f"Failed to create audit log: {e}")
    
    return result

