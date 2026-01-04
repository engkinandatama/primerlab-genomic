"""
qPCR design logic module.
Contains qPCR-specific design rules and primer selection logic.
"""

from typing import Dict, Any, List
from primerlab.core.models import Primer
from primerlab.core.logger import get_logger

logger = get_logger()

def parse_primer3_output(raw_results: Dict[str, Any]) -> Dict[str, Primer]:
    """
    Parses Primer3 output and creates Primer objects.
    
    Args:
        raw_results: Raw dictionary from Primer3
        
    Returns:
        Dictionary with 'forward', 'reverse', and optionally 'probe'
    """
    primers = {}

    num_returned = raw_results.get('PRIMER_LEFT_NUM_RETURNED', 0)

    if num_returned > 0:
        # Forward Primer
        fwd_seq = raw_results.get('PRIMER_LEFT_0_SEQUENCE')
        fwd_tm = raw_results.get('PRIMER_LEFT_0_TM')
        fwd_gc = raw_results.get('PRIMER_LEFT_0_GC_PERCENT')
        fwd_start, fwd_len = raw_results.get('PRIMER_LEFT_0')

        fwd_primer = Primer(
            id="forward_0",
            sequence=fwd_seq,
            tm=fwd_tm,
            gc=fwd_gc,
            length=fwd_len,
            start=fwd_start,
            end=fwd_start + fwd_len - 1,
            hairpin_dg=raw_results.get('PRIMER_LEFT_0_HAIRPIN_TH', 0.0),
            homodimer_dg=raw_results.get('PRIMER_LEFT_0_HOMODIMER_TH', 0.0)
        )
        primers["forward"] = fwd_primer

        # Reverse Primer
        rev_seq = raw_results.get('PRIMER_RIGHT_0_SEQUENCE')
        rev_tm = raw_results.get('PRIMER_RIGHT_0_TM')
        rev_gc = raw_results.get('PRIMER_RIGHT_0_GC_PERCENT')
        rev_start, rev_len = raw_results.get('PRIMER_RIGHT_0')

        rev_primer = Primer(
            id="reverse_0",
            sequence=rev_seq,
            tm=rev_tm,
            gc=rev_gc,
            length=rev_len,
            start=rev_start - rev_len + 1, # 5' end on template
            end=rev_start, # 3' end on template (Primer3 returns this as index)
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

            probe = Primer(
                id="probe_0",
                sequence=probe_seq,
                tm=probe_tm,
                gc=probe_gc,
                length=probe_len,
                start=probe_start,
                end=probe_start + probe_len - 1,
                hairpin_dg=raw_results.get('PRIMER_INTERNAL_0_HAIRPIN_TH', 0.0),
                homodimer_dg=raw_results.get('PRIMER_INTERNAL_0_HOMODIMER_TH', 0.0)
            )
            primers["probe"] = probe
        else:
            logger.warning("No internal probe designed by Primer3")

    return primers
