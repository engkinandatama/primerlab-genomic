"""
Off-target Detection Module (v0.3.0)

Provides primer off-target detection and specificity analysis.
"""

from primerlab.core.offtarget.finder import OfftargetFinder, find_offtargets
from primerlab.core.offtarget.scorer import SpecificityScorer, calculate_specificity

__all__ = [
    "OfftargetFinder",
    "find_offtargets",
    "SpecificityScorer",
    "calculate_specificity"
]
