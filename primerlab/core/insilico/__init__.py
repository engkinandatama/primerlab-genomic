"""
In-silico PCR Simulation Module (v0.3.4)

Virtual PCR simulation for amplicon prediction and primer validation.
"""

from primerlab.core.insilico.engine import InsilicoPCR, run_insilico_pcr
from primerlab.core.insilico.binding import (
    BindingSite,
    analyze_binding,
    calculate_corrected_tm,      # v0.3.4
    check_three_prime_stability, # v0.3.4
    calculate_three_prime_dg,
)
from primerlab.core.insilico.report import (
    generate_markdown_report,
    generate_amplicon_fasta,
    format_console_alignment
)

__all__ = [
    "InsilicoPCR",
    "run_insilico_pcr",
    "BindingSite",
    "analyze_binding",
    "calculate_corrected_tm",       # v0.3.4
    "check_three_prime_stability",  # v0.3.4
    "calculate_three_prime_dg",
    "generate_markdown_report",
    "generate_amplicon_fasta",
    "format_console_alignment",
]
