"""
Primer Quality Scoring Engine (v0.1.4)

Calculates combined quality score from:
- Primer3 penalty
- ViennaRNA QC (hairpin, dimer)
- Sequence QC (GC clamp, Poly-X)

Scores are mode-specific (strict/standard/relaxed).

Scientific References:
1. Benchling (2024). "PCR Primer Design Guidelines"
2. IDT (2024). "Primer & Probe Design Guidelines"
3. DeGenPrime (2023). Nucleic Acids Research
4. SantaLucia J. (1998). PNAS 95:1460-1465
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
from primerlab.core.logger import get_logger

logger = get_logger()


@dataclass
class ScoringResult:
    """Result of quality scoring."""
    score: int  # 0-100
    category: str  # Excellent, Good, Fair, Poor
    category_emoji: str  # ✅ or ⚠️ or ❌
    penalties: Dict[str, int]  # Individual penalties applied

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "category": self.category,
            "category_emoji": self.category_emoji,
            "penalties": self.penalties
        }


# Penalty configurations by QC mode
PENALTY_CONFIG = {
    "strict": {
        "hairpin_3end_threshold": -2.0,
        "hairpin_3end_penalty": -20,
        "hairpin_internal_threshold": -3.0,
        "hairpin_internal_penalty": -15,
        "self_dimer_threshold": -5.0,
        "self_dimer_penalty": -20,
        "heterodimer_threshold": -5.0,
        "heterodimer_penalty": -15,
        "gc_clamp_weak_penalty": -20,
        "gc_clamp_strong_penalty": -10,
        "poly_x_penalty": -15,
    },
    "standard": {
        "hairpin_3end_threshold": -3.0,
        "hairpin_3end_penalty": -15,
        "hairpin_internal_threshold": -6.0,
        "hairpin_internal_penalty": -10,
        "self_dimer_threshold": -6.0,
        "self_dimer_penalty": -15,
        "heterodimer_threshold": -6.0,
        "heterodimer_penalty": -10,
        "gc_clamp_weak_penalty": -15,
        "gc_clamp_strong_penalty": -5,
        "poly_x_penalty": -10,
    },
    "relaxed": {
        "hairpin_3end_threshold": -6.0,
        "hairpin_3end_penalty": -10,
        "hairpin_internal_threshold": -9.0,
        "hairpin_internal_penalty": -5,
        "self_dimer_threshold": -9.0,
        "self_dimer_penalty": -10,
        "heterodimer_threshold": -9.0,
        "heterodimer_penalty": -5,
        "gc_clamp_weak_penalty": -10,
        "gc_clamp_strong_penalty": 0,
        "poly_x_penalty": -5,
    }
}

# Score category thresholds
SCORE_CATEGORIES = [
    (85, 100, "Excellent", "✅"),
    (70, 84, "Good", "✅"),
    (50, 69, "Fair", "⚠️"),
    (0, 49, "Poor", "❌"),
]


def get_category(score: int) -> Tuple[str, str]:
    """Get category name and emoji for a score."""
    for min_score, max_score, category, emoji in SCORE_CATEGORIES:
        if min_score <= score <= max_score:
            return category, emoji
    return "Poor", "❌"


def calculate_quality_score(
    primer3_penalty: float,
    hairpin_dg_fwd: Optional[float] = None,
    hairpin_dg_rev: Optional[float] = None,
    homodimer_dg_fwd: Optional[float] = None,
    homodimer_dg_rev: Optional[float] = None,
    heterodimer_dg: Optional[float] = None,
    gc_clamp_fwd: Optional[str] = None,  # "ok", "weak", "strong"
    gc_clamp_rev: Optional[str] = None,
    poly_x_fwd: bool = False,
    poly_x_rev: bool = False,
    qc_mode: str = "standard"
) -> ScoringResult:
    """
    Calculate combined quality score.
    
    Args:
        primer3_penalty: Primer3 pair penalty (lower = better)
        hairpin_dg_*: Hairpin ΔG values from ViennaRNA
        homodimer_dg_*: Homodimer ΔG values
        heterodimer_dg: Heterodimer ΔG value
        gc_clamp_*: GC clamp status ("ok", "weak", "strong")
        poly_x_*: Poly-X detected flag
        qc_mode: QC mode (strict/standard/relaxed)
    
    Returns:
        ScoringResult with score, category, and penalty breakdown
    """
    config = PENALTY_CONFIG.get(qc_mode, PENALTY_CONFIG["standard"])
    penalties = {}

    # Base score from Primer3 penalty
    # Primer3 penalty typically 0-10, we scale by 10
    primer3_deduction = min(50, int(primer3_penalty * 10))
    penalties["primer3"] = -primer3_deduction

    # Hairpin penalties (forward)
    if hairpin_dg_fwd is not None:
        if hairpin_dg_fwd < config["hairpin_3end_threshold"]:
            penalties["hairpin_fwd"] = config["hairpin_3end_penalty"]

    # Hairpin penalties (reverse)
    if hairpin_dg_rev is not None:
        if hairpin_dg_rev < config["hairpin_3end_threshold"]:
            penalties["hairpin_rev"] = config["hairpin_3end_penalty"]

    # Homodimer penalties
    if homodimer_dg_fwd is not None:
        if homodimer_dg_fwd < config["self_dimer_threshold"]:
            penalties["homodimer_fwd"] = config["self_dimer_penalty"]

    if homodimer_dg_rev is not None:
        if homodimer_dg_rev < config["self_dimer_threshold"]:
            penalties["homodimer_rev"] = config["self_dimer_penalty"]

    # Heterodimer penalty
    if heterodimer_dg is not None:
        if heterodimer_dg < config["heterodimer_threshold"]:
            penalties["heterodimer"] = config["heterodimer_penalty"]

    # GC clamp penalties
    if gc_clamp_fwd == "weak":
        penalties["gc_clamp_fwd"] = config["gc_clamp_weak_penalty"]
    elif gc_clamp_fwd == "strong":
        penalties["gc_clamp_fwd"] = config["gc_clamp_strong_penalty"]

    if gc_clamp_rev == "weak":
        penalties["gc_clamp_rev"] = config["gc_clamp_weak_penalty"]
    elif gc_clamp_rev == "strong":
        penalties["gc_clamp_rev"] = config["gc_clamp_strong_penalty"]

    # Poly-X penalties
    if poly_x_fwd:
        penalties["poly_x_fwd"] = config["poly_x_penalty"]
    if poly_x_rev:
        penalties["poly_x_rev"] = config["poly_x_penalty"]

    # Calculate final score
    total_penalty = sum(penalties.values())
    score = max(0, min(100, 100 + total_penalty))

    category, emoji = get_category(score)

    logger.debug(f"Quality score: {score} ({category}) - penalties: {penalties}")

    return ScoringResult(
        score=score,
        category=category,
        category_emoji=emoji,
        penalties=penalties
    )


def score_from_qc_result(
    primer3_penalty: float,
    qc_result: Any,  # QCResult dataclass
    qc_mode: str = "standard"
) -> ScoringResult:
    """
    Calculate score from QCResult object.
    
    Args:
        primer3_penalty: Primer3 pair penalty
        qc_result: QCResult dataclass instance
        qc_mode: QC mode (strict/standard/relaxed)
    
    Returns:
        ScoringResult
    """
    return calculate_quality_score(
        primer3_penalty=primer3_penalty,
        hairpin_dg_fwd=getattr(qc_result, 'hairpin_dg', None),
        hairpin_dg_rev=getattr(qc_result, 'hairpin_dg', None),
        homodimer_dg_fwd=getattr(qc_result, 'homodimer_dg', None),
        homodimer_dg_rev=getattr(qc_result, 'homodimer_dg', None),
        heterodimer_dg=getattr(qc_result, 'heterodimer_dg', None),
        qc_mode=qc_mode
    )
