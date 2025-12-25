"""
Core Multiplex module exports.

This module provides multiplex analysis functionality including
data models, dimer calculation, scoring, and validation.
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
    # Reports (Phase 3 + 4)
    "generate_json_report",
    "generate_markdown_report",
    "generate_excel_report",
    "generate_idt_plate",
]

