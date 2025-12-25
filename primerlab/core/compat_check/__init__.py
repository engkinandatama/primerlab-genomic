"""
Primer Compatibility Check module exports.

This module provides compatibility analysis functionality including
data models, dimer calculation, scoring, validation, and overlap detection.
"""

from primerlab.core.compat_check.models import (
    MultiplexPair,
    DimerResult,
    CompatibilityMatrix,
    MultiplexResult,
    score_to_grade,
    grade_to_emoji,
)
from primerlab.core.compat_check.dimer import DimerEngine
from primerlab.core.compat_check.scoring import MultiplexScorer, MULTIPLEX_CONFIG
from primerlab.core.compat_check.validator import MultiplexValidator
from primerlab.core.compat_check.report import (
    generate_json_report,
    generate_markdown_report,
    generate_excel_report,
    generate_idt_plate,
)
from primerlab.core.compat_check.overlap_detection import (
    run_insilico_compat_simulation,
    predict_amplicons_for_pairs,
    analyze_overlaps,
    OverlapAnalysisResult,
    PredictedAmplicon,
    AmpliconOverlap,
)

__all__ = [
    # Models
    "MultiplexPair",
    "DimerResult",
    "CompatibilityMatrix",
    "MultiplexResult",
    # Engine
    "DimerEngine",
    # Scoring
    "MultiplexScorer",
    "MULTIPLEX_CONFIG",
    # Validation
    "MultiplexValidator",
    # Utilities
    "score_to_grade",
    "grade_to_emoji",
    # Reports
    "generate_json_report",
    "generate_markdown_report",
    "generate_excel_report",
    "generate_idt_plate",
    # Overlap Detection (v0.4.1)
    "run_insilico_compat_simulation",
    "predict_amplicons_for_pairs",
    "analyze_overlaps",
    "OverlapAnalysisResult",
    "PredictedAmplicon",
    "AmpliconOverlap",
]
