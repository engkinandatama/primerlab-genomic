"""
Multiplex Analysis Data Models.

This module contains the data structures for multiplex primer analysis,
including primer pairs, dimer results, and compatibility matrices.

Version: v0.4.0
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class MultiplexPair:
    """
    Represents a single primer pair in a multiplex context.
    
    Attributes:
        name: Identifier for this primer pair (e.g., gene name)
        forward: Forward primer sequence (5' -> 3')
        reverse: Reverse primer sequence (5' -> 3')
        tm_forward: Melting temperature of forward primer (°C)
        tm_reverse: Melting temperature of reverse primer (°C)
        gc_forward: GC content of forward primer (%)
        gc_reverse: GC content of reverse primer (%)
        target_region: Optional description of target region
    """
    name: str
    forward: str
    reverse: str
    tm_forward: float = 0.0
    tm_reverse: float = 0.0
    gc_forward: float = 0.0
    gc_reverse: float = 0.0
    target_region: Optional[str] = None
    
    def __post_init__(self):
        """Normalize sequences to uppercase."""
        self.forward = self.forward.upper()
        self.reverse = self.reverse.upper()
    
    @property
    def avg_tm(self) -> float:
        """Average Tm of the primer pair."""
        return (self.tm_forward + self.tm_reverse) / 2
    
    @property
    def avg_gc(self) -> float:
        """Average GC content of the primer pair."""
        return (self.gc_forward + self.gc_reverse) / 2
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "forward": self.forward,
            "reverse": self.reverse,
            "tm_forward": self.tm_forward,
            "tm_reverse": self.tm_reverse,
            "gc_forward": self.gc_forward,
            "gc_reverse": self.gc_reverse,
            "target_region": self.target_region,
            "avg_tm": self.avg_tm,
            "avg_gc": self.avg_gc,
        }


@dataclass
class DimerResult:
    """
    Result of cross-dimer analysis between two primers.
    
    Attributes:
        primer1_name: Name/identifier of first primer
        primer2_name: Name/identifier of second primer
        primer1_seq: Sequence of first primer
        primer2_seq: Sequence of second primer
        delta_g: Gibbs free energy of dimerization (kcal/mol)
                 More negative = more stable = worse
        structure: Visual representation of dimer alignment
        is_problematic: True if ΔG exceeds threshold (too stable)
    """
    primer1_name: str
    primer2_name: str
    primer1_seq: str
    primer2_seq: str
    delta_g: float
    structure: str = ""
    is_problematic: bool = False
    
    @property
    def is_homodimer(self) -> bool:
        """True if this is a homodimer (same primer with itself)."""
        return self.primer1_seq == self.primer2_seq
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary for JSON serialization."""
        return {
            "primer1_name": self.primer1_name,
            "primer2_name": self.primer2_name,
            "primer1_seq": self.primer1_seq,
            "primer2_seq": self.primer2_seq,
            "delta_g": self.delta_g,
            "structure": self.structure,
            "is_problematic": self.is_problematic,
            "is_homodimer": self.is_homodimer,
        }


@dataclass
class CompatibilityMatrix:
    """
    NxN compatibility matrix for all primers in a multiplex set.
    
    Attributes:
        primer_names: List of primer names/identifiers
        matrix: Dictionary mapping (primer1, primer2) -> DimerResult
        worst_dimer: The most problematic dimer interaction
        total_dimers: Total number of dimer checks performed
        problematic_count: Number of problematic dimers found
    """
    primer_names: List[str] = field(default_factory=list)
    matrix: Dict[Tuple[str, str], DimerResult] = field(default_factory=dict)
    worst_dimer: Optional[DimerResult] = None
    total_dimers: int = 0
    problematic_count: int = 0
    
    def get_dimer(self, name1: str, name2: str) -> Optional[DimerResult]:
        """Get dimer result for a specific pair."""
        # Check both orderings
        if (name1, name2) in self.matrix:
            return self.matrix[(name1, name2)]
        if (name2, name1) in self.matrix:
            return self.matrix[(name2, name1)]
        return None
    
    def get_problematic_dimers(self) -> List[DimerResult]:
        """Get all problematic dimer interactions."""
        return [d for d in self.matrix.values() if d.is_problematic]
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary for JSON serialization."""
        # Convert matrix to list format for JSON
        matrix_list = [d.to_dict() for d in self.matrix.values()]
        
        return {
            "primer_names": self.primer_names,
            "matrix": matrix_list,
            "worst_dimer": self.worst_dimer.to_dict() if self.worst_dimer else None,
            "total_dimers": self.total_dimers,
            "problematic_count": self.problematic_count,
        }


@dataclass
class MultiplexResult:
    """
    Complete result of multiplex compatibility analysis.
    
    Attributes:
        pairs: List of primer pairs analyzed
        matrix: Compatibility matrix with all dimer results
        score: Overall compatibility score (0-100)
        grade: Letter grade (A/B/C/D/F)
        warnings: List of warning messages
        recommendations: List of recommendations for improvement
        config_used: Configuration parameters used (for reproducibility)
        # Phase 3 additions (with defaults for backward compatibility):
        is_valid: Explicit validation status
        errors: List of error messages
        component_scores: Breakdown of scoring components
    """
    # Original fields (Phase 1-2) - with defaults
    pairs: List[MultiplexPair] = field(default_factory=list)
    matrix: Optional[CompatibilityMatrix] = None
    score: float = 0.0
    grade: str = "F"
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    config_used: Dict[str, Any] = field(default_factory=dict)
    # Phase 3 additions - with defaults for backward compatibility
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    component_scores: Dict[str, float] = field(default_factory=dict)
    
    @property
    def is_compatible(self) -> bool:
        """True if the multiplex set is compatible (grade A, B, or C)."""
        return self.grade in ("A", "B", "C")
    
    @property
    def pair_count(self) -> int:
        """Number of primer pairs in the set."""
        return len(self.pairs)
    
    @property
    def avg_tm(self) -> float:
        """Average Tm of all primers in the set."""
        if not self.pairs:
            return 0.0
        return sum(p.avg_tm for p in self.pairs) / len(self.pairs)
    
    @property
    def avg_gc(self) -> float:
        """Average GC content of all primers in the set."""
        if not self.pairs:
            return 0.0
        return sum(p.avg_gc for p in self.pairs) / len(self.pairs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary for JSON serialization."""
        return {
            "pairs": [p.to_dict() for p in self.pairs],
            "matrix": self.matrix.to_dict() if self.matrix else None,
            "score": self.score,
            "grade": self.grade,
            "is_compatible": self.is_compatible,
            "is_valid": self.is_valid,
            "pair_count": self.pair_count,
            "avg_tm": self.avg_tm,
            "avg_gc": self.avg_gc,
            "warnings": self.warnings,
            "errors": self.errors,
            "recommendations": self.recommendations,
            "component_scores": self.component_scores,
            "config_used": self.config_used,
        }


# Utility functions for grade calculation
def score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 85:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 55:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"


def grade_to_emoji(grade: str) -> str:
    """Convert letter grade to display emoji."""
    return {
        "A": "✅",
        "B": "✅",
        "C": "⚠️",
        "D": "⚠️",
        "F": "❌",
    }.get(grade, "❓")
