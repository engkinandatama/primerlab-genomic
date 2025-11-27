from typing import Dict, Any
from datetime import datetime
from primerlab.core.models import WorkflowResult, Primer, Amplicon, QCResult, RunMetadata
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper
from primerlab.core.sequence import SequenceLoader
from primerlab.core.logger import get_logger
from primerlab.core.exceptions import WorkflowError
from primerlab.workflows.pcr.qc import PCRQC

logger = get_logger()

def run_qpcr_workflow(config: Dict[str, Any]) -> WorkflowResult:
    """
    Executes the qPCR workflow (Primers + Probe).
    """
    logger.info("Starting qPCR Workflow execution...")
    
    # 1. Parse Input
    input_config = config.get("input", {})
    raw_sequence = input_config.get("sequence")
    seq_path = input_config.get("sequence_path")
    
    try:
        if seq_path:
            sequence = SequenceLoader.load(seq_path)
        elif raw_sequence:
            sequence = SequenceLoader.load(raw_sequence)
        else:
            raise WorkflowError("No sequence provided.", "ERR_WORKFLOW_001")
    except Exception as e:
        raise WorkflowError(f"Sequence loading failed: {e}", "ERR_WORKFLOW_SEQ")

    logger.info(f"Input sequence length: {len(sequence)} bp")

    # 2. Run Primer3 (with Probe settings)
    p3_wrapper = Primer3Wrapper()
    raw_results = p3_wrapper.design_primers(sequence, config)
    
    num_returned = raw_results.get('PRIMER_LEFT_NUM_RETURNED', 0)
    logger.info(f"Primer3 returned {num_returned} sets.")

    # 3. Parse Results
    primers = {}
    amplicons = []
    
    if num_returned > 0:
        # Forward
        fwd_seq = raw_results.get('PRIMER_LEFT_0_SEQUENCE')
        fwd_tm = raw_results.get('PRIMER_LEFT_0_TM')
        fwd_gc = raw_results.get('PRIMER_LEFT_0_GC_PERCENT')
        fwd_start, fwd_len = raw_results.get('PRIMER_LEFT_0')
        
        fwd_primer = Primer(
            id="forward_0", sequence=fwd_seq, tm=fwd_tm, gc=fwd_gc, length=fwd_len,
            start=fwd_start, end=fwd_start + fwd_len - 1,
            hairpin_dg=raw_results.get('PRIMER_LEFT_0_HAIRPIN_TH', 0.0),
            homodimer_dg=raw_results.get('PRIMER_LEFT_0_HOMODIMER_TH', 0.0)
        )
        primers["forward"] = fwd_primer

        # Reverse
        rev_seq = raw_results.get('PRIMER_RIGHT_0_SEQUENCE')
        rev_tm = raw_results.get('PRIMER_RIGHT_0_TM')
        rev_gc = raw_results.get('PRIMER_RIGHT_0_GC_PERCENT')
        rev_start, rev_len = raw_results.get('PRIMER_RIGHT_0')
        
        rev_primer = Primer(
            id="reverse_0", sequence=rev_seq, tm=rev_tm, gc=rev_gc, length=rev_len,
            start=rev_start, end=rev_start - rev_len + 1,
            hairpin_dg=raw_results.get('PRIMER_RIGHT_0_HAIRPIN_TH', 0.0),
            homodimer_dg=raw_results.get('PRIMER_RIGHT_0_HOMODIMER_TH', 0.0)
        )
        primers["reverse"] = rev_primer

        # Probe (Internal Oligo)
        probe_seq = raw_results.get('PRIMER_INTERNAL_0_SEQUENCE')
        if probe_seq:
            probe_tm = raw_results.get('PRIMER_INTERNAL_0_TM')
            probe_gc = raw_results.get('PRIMER_INTERNAL_0_GC_PERCENT')
            probe_start, probe_len = raw_results.get('PRIMER_INTERNAL_0')
            
            probe_obj = Primer(
                id="probe_0", sequence=probe_seq, tm=probe_tm, gc=probe_gc, length=probe_len,
                start=probe_start, end=probe_start + probe_len - 1,
                hairpin_dg=raw_results.get('PRIMER_INTERNAL_0_HAIRPIN_TH', 0.0),
                homodimer_dg=raw_results.get('PRIMER_INTERNAL_0_HOMODIMER_TH', 0.0)
            )
            primers["probe"] = probe_obj
        else:
            logger.warning("No internal probe designed by Primer3!")

        # Amplicon
        product_size = raw_results.get('PRIMER_PAIR_0_PRODUCT_SIZE')
        amplicon = Amplicon(
            start=fwd_start, end=rev_start, length=product_size,
            sequence="N/A", gc=0.0, tm_forward=fwd_tm, tm_reverse=rev_tm
        )
        amplicons.append(amplicon)

    # 4. Run QC (Reuse PCRQC + Probe Logic)
    # TODO: Implement specific qPCR QC (Probe Tm check)
    qc_engine = PCRQC(config)
    qc_result = None
    if primers:
        qc_result = qc_engine.evaluate_pair(primers["forward"], primers["reverse"])
        
        # Additional Probe QC
        if "probe" in primers:
            probe = primers["probe"]
            avg_primer_tm = (primers["forward"].tm + primers["reverse"].tm) / 2
            tm_diff_probe = probe.tm - avg_primer_tm
            
            # Probe Tm must be higher
            min_diff = config.get("qc", {}).get("probe_tm_min_diff", 5.0)
            if tm_diff_probe < min_diff:
                msg = f"Probe Tm ({probe.tm:.2f}) is not significantly higher than primers ({avg_primer_tm:.2f}). Diff: {tm_diff_probe:.2f} < {min_diff}"
                qc_result.warnings.append(msg)
                qc_result.tm_balance_ok = False # Flag as issue

        if qc_result.warnings:
            logger.warning(f"QC Warnings: {qc_result.warnings}")

    # 5. Metadata & Result
    metadata = RunMetadata(
        workflow="qpcr",
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0",
        parameters=config.get("parameters", {})
    )

    result = WorkflowResult(
        workflow="qpcr",
        primers=primers,
        amplicons=amplicons,
        metadata=metadata,
        qc=qc_result,
        raw=raw_results
    )
    
    return result
