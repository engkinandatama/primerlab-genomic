"""
Cross-Reactivity Scoring and Analysis.

Enhanced scoring and visualization for species specificity.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .models import SpeciesCheckResult, SpecificityMatrix, SpeciesBinding

logger = logging.getLogger(__name__)


@dataclass
class CrossReactivityScore:
    """Detailed cross-reactivity score for a primer."""
    primer_name: str
    target_binding: float  # % binding to target
    max_offtarget_binding: float  # % binding to worst off-target
    specificity_score: float  # 0-100, 100 = perfectly specific
    offtarget_species: List[str] = field(default_factory=list)
    is_specific: bool = True
    grade: str = "A"
    
    def to_dict(self) -> Dict:
        return {
            "primer_name": self.primer_name,
            "target_binding": self.target_binding,
            "max_offtarget_binding": self.max_offtarget_binding,
            "specificity_score": self.specificity_score,
            "offtarget_species": self.offtarget_species,
            "is_specific": self.is_specific,
            "grade": self.grade
        }


def calculate_cross_reactivity_score(
    matrix: SpecificityMatrix,
    primer_name: str,
    offtarget_threshold: float = 70.0
) -> CrossReactivityScore:
    """
    Calculate detailed cross-reactivity score for a primer.
    
    Score formula:
    - 100 = only binds to target, no off-target binding
    - Penalized by off-target binding strength
    - Bonus for strong target binding
    
    Args:
        matrix: Specificity matrix with all bindings
        primer_name: Primer to score
        offtarget_threshold: Min binding % to consider off-target
        
    Returns:
        CrossReactivityScore with detailed breakdown
    """
    if primer_name not in matrix.bindings:
        return CrossReactivityScore(
            primer_name=primer_name,
            target_binding=0,
            max_offtarget_binding=0,
            specificity_score=0,
            is_specific=False,
            grade="F"
        )
    
    bindings = matrix.bindings[primer_name]
    target_species = matrix.target_species
    
    # Get target binding
    target_binding = bindings.get(target_species)
    target_pct = target_binding.best_match_percent if target_binding else 0
    
    # Get max off-target binding
    max_offtarget = 0.0
    offtarget_list = []
    
    for species, binding in bindings.items():
        if species == target_species:
            continue
        if binding.has_binding and binding.best_match_percent >= offtarget_threshold:
            offtarget_list.append(species)
            max_offtarget = max(max_offtarget, binding.best_match_percent)
    
    # Calculate score
    # Base: target binding percentage
    # Penalty: subtract off-target binding
    specificity_score = max(0, target_pct - max_offtarget)
    
    # Bonus for strong target with no off-target
    if target_pct >= 90 and max_offtarget < 50:
        specificity_score = min(100, specificity_score + 10)
    
    # Is specific?
    is_specific = len(offtarget_list) == 0
    
    # Grade
    if specificity_score >= 90:
        grade = "A"
    elif specificity_score >= 80:
        grade = "B"
    elif specificity_score >= 70:
        grade = "C"
    elif specificity_score >= 60:
        grade = "D"
    else:
        grade = "F"
    
    return CrossReactivityScore(
        primer_name=primer_name,
        target_binding=target_pct,
        max_offtarget_binding=max_offtarget,
        specificity_score=specificity_score,
        offtarget_species=offtarget_list,
        is_specific=is_specific,
        grade=grade
    )


def generate_specificity_matrix_table(matrix: SpecificityMatrix) -> str:
    """
    Generate ASCII table representation of specificity matrix.
    
    Returns:
        Formatted string table
    """
    if not matrix.primer_names or not matrix.species_names:
        return "Empty matrix"
    
    # Calculate column widths
    primer_width = max(len(p) for p in matrix.primer_names)
    species_width = max(len(s) for s in matrix.species_names)
    col_width = max(6, species_width)
    
    lines = []
    
    # Header row
    header = f"{'Primer':<{primer_width}} |"
    for species in matrix.species_names:
        marker = "*" if species == matrix.target_species else ""
        header += f" {species[:col_width]}{marker:^{col_width-len(species[:col_width])}} |"
    lines.append(header)
    lines.append("-" * len(header))
    
    # Data rows
    for primer in matrix.primer_names:
        row = f"{primer:<{primer_width}} |"
        for species in matrix.species_names:
            binding = matrix.get_binding(primer, species)
            if binding and binding.has_binding:
                pct = f"{binding.best_match_percent:.0f}%"
            else:
                pct = "-"
            row += f" {pct:^{col_width}} |"
        lines.append(row)
    
    lines.append("")
    lines.append("* = target species")
    
    return "\n".join(lines)


def detect_offtarget_species(
    result: SpeciesCheckResult,
    threshold: float = 70.0
) -> List[Dict]:
    """
    Detect off-target species with significant binding.
    
    Args:
        result: Species check result
        threshold: Minimum binding % to flag
        
    Returns:
        List of off-target detections with details
    """
    detections = []
    matrix = result.specificity_matrix
    
    for primer in matrix.primer_names:
        for species in matrix.species_names:
            if species == matrix.target_species:
                continue
            
            binding = matrix.get_binding(primer, species)
            if binding and binding.best_match_percent >= threshold:
                detections.append({
                    "primer": primer,
                    "species": species,
                    "binding_percent": binding.best_match_percent,
                    "binding_count": binding.binding_count,
                    "severity": "HIGH" if binding.best_match_percent >= 90 else 
                               "MEDIUM" if binding.best_match_percent >= 80 else "LOW"
                })
    
    # Sort by severity
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    detections.sort(key=lambda x: (severity_order[x["severity"]], -x["binding_percent"]))
    
    return detections
