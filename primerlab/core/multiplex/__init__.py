"""
Core Multiplex module exports.

This module provides multiplex analysis functionality including
data models, dimer calculation, scoring, and validation.
"""

from primerlab.core.multiplex.models import (
    MultiplexPair,
    DimerResult,
    CompatibilityMatrix,
    MultiplexResult,
    score_to_grade,
    grade_to_emoji,
)
from primerlab.core.multiplex.dimer import DimerEngine

__all__ = [
    "MultiplexPair",
    "DimerResult",
    "CompatibilityMatrix",
    "MultiplexResult",
    "DimerEngine",
    "score_to_grade",
    "grade_to_emoji",
]
