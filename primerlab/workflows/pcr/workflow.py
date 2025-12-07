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
        
        # Forward Primer
        fwd_start, fwd_len = best_candidate["fwd_pos"]
        fwd_primer = Primer(
            id=f"forward_{idx}",
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
            id=f"reverse_{idx}",
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
        amplicon = Amplicon(
            start=fwd_start,
            end=rev_start,
            length=best_candidate["product_size"],
            sequence="N/A",
            gc=0.0,
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
        
        # Add QC warnings to main result warnings
        if qc_result.warnings:
            logger.warning(f"QC Warnings: {qc_result.warnings}")

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
    
    return result
