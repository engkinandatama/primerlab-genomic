"""
Species-Specific Data Models.

Dataclasses for species-specific primer analysis.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class SpeciesTemplate:
    """Represents a species template sequence."""
    species_name: str
    sequence: str
    description: str = ""
    accession: str = ""

    @property
    def length(self) -> int:
        return len(self.sequence)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "species_name": self.species_name,
            "sequence_length": self.length,
            "description": self.description,
            "accession": self.accession
        }


@dataclass
class BindingSite:
    """Represents a primer binding site on a template."""
    position: int
    strand: str  # '+' or '-'
    match_percent: float
    mismatches: int
    mismatch_positions: List[int] = field(default_factory=list)
    binding_sequence: str = ""

    @property
    def is_strong_binding(self) -> bool:
        """Strong binding = >80% match."""
        return self.match_percent >= 80.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "strand": self.strand,
            "match_percent": self.match_percent,
            "mismatches": self.mismatches,
            "mismatch_positions": self.mismatch_positions,
            "is_strong_binding": self.is_strong_binding
        }


@dataclass
class SpeciesBinding:
    """Binding result for a primer on a specific species."""
    species_name: str
    primer_name: str
    primer_sequence: str
    binding_sites: List[BindingSite] = field(default_factory=list)
    best_match_percent: float = 0.0
    is_specific: bool = True  # True if only binds to target species

    @property
    def has_binding(self) -> bool:
        return len(self.binding_sites) > 0

    @property
    def binding_count(self) -> int:
        return len(self.binding_sites)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "species_name": self.species_name,
            "primer_name": self.primer_name,
            "binding_count": self.binding_count,
            "best_match_percent": self.best_match_percent,
            "is_specific": self.is_specific,
            "binding_sites": [b.to_dict() for b in self.binding_sites]
        }


@dataclass
class SpecificityMatrix:
    """Matrix of primer binding across multiple species."""
    primer_names: List[str]
    species_names: List[str]
    target_species: str
    bindings: Dict[str, Dict[str, SpeciesBinding]] = field(default_factory=dict)
    # bindings[primer_name][species_name] = SpeciesBinding

    def get_binding(self, primer: str, species: str) -> Optional[SpeciesBinding]:
        return self.bindings.get(primer, {}).get(species)

    def get_specificity_score(self, primer: str) -> float:
        """
        Calculate specificity score for a primer.
        100 = binds only to target, 0 = binds equally to all.
        """
        if primer not in self.bindings:
            return 0.0

        target_binding = self.bindings[primer].get(self.target_species)
        if not target_binding or not target_binding.has_binding:
            return 0.0

        target_strength = target_binding.best_match_percent

        # Calculate off-target binding
        offtarget_max = 0.0
        for species, binding in self.bindings[primer].items():
            if species != self.target_species and binding.has_binding:
                offtarget_max = max(offtarget_max, binding.best_match_percent)

        # Score = target strength - off-target strength
        specificity = target_strength - offtarget_max
        return max(0.0, min(100.0, specificity))

    def to_dict(self) -> Dict[str, Any]:
        matrix_data = {}
        for primer, species_dict in self.bindings.items():
            matrix_data[primer] = {
                species: binding.to_dict() 
                for species, binding in species_dict.items()
            }

        return {
            "primer_names": self.primer_names,
            "species_names": self.species_names,
            "target_species": self.target_species,
            "matrix": matrix_data
        }


@dataclass
class SpeciesCheckResult:
    """Complete result of species specificity check."""
    target_species: str
    primers_checked: int
    species_checked: int
    specificity_matrix: SpecificityMatrix
    overall_score: float  # 0-100 average specificity
    grade: str  # A-F
    is_specific: bool  # True if all primers specific to target
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_species": self.target_species,
            "primers_checked": self.primers_checked,
            "species_checked": self.species_checked,
            "overall_score": self.overall_score,
            "grade": self.grade,
            "is_specific": self.is_specific,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "specificity_matrix": self.specificity_matrix.to_dict()
        }


def score_to_grade(score: float) -> str:
    """Convert specificity score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
