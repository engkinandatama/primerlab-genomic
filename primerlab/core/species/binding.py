"""
Primer Binding Site Comparison Across Species.

Compare primer binding across multiple species templates.
"""

import logging
from typing import List, Dict, Optional

from .models import (
    SpeciesTemplate, BindingSite, SpeciesBinding, 
    SpecificityMatrix, SpeciesCheckResult, score_to_grade
)
from .alignment import find_binding_sites

logger = logging.getLogger(__name__)


def analyze_primer_binding(
    primer_name: str,
    primer_seq: str,
    template: SpeciesTemplate,
    min_match_percent: float = 70.0,
    max_mismatches: int = 5
) -> SpeciesBinding:
    """
    Analyze binding of a primer to a species template.
    
    Args:
        primer_name: Name of the primer
        primer_seq: Primer sequence
        template: Species template to check
        min_match_percent: Minimum match % to consider binding
        max_mismatches: Maximum mismatches to consider binding
        
    Returns:
        SpeciesBinding result
    """
    sites = find_binding_sites(
        primer_seq,
        template.sequence,
        min_match_percent=min_match_percent,
        max_mismatches=max_mismatches
    )
    
    binding_sites = []
    best_match = 0.0
    
    for pos, strand, match_pct, mismatches, mm_pos in sites:
        site = BindingSite(
            position=pos,
            strand=strand,
            match_percent=match_pct,
            mismatches=mismatches,
            mismatch_positions=mm_pos
        )
        binding_sites.append(site)
        best_match = max(best_match, match_pct)
    
    return SpeciesBinding(
        species_name=template.species_name,
        primer_name=primer_name,
        primer_sequence=primer_seq,
        binding_sites=binding_sites,
        best_match_percent=best_match
    )


def compare_binding_across_species(
    primers: List[Dict[str, str]],
    target_template: SpeciesTemplate,
    offtarget_templates: Dict[str, SpeciesTemplate],
    min_match_percent: float = 70.0,
    max_mismatches: int = 5
) -> SpecificityMatrix:
    """
    Compare primer binding across target and off-target species.
    
    Args:
        primers: List of dicts with 'name', 'forward', 'reverse' keys
        target_template: Template of target species
        offtarget_templates: Dict of off-target species templates
        min_match_percent: Minimum match % to consider binding
        max_mismatches: Maximum mismatches to consider binding
        
    Returns:
        SpecificityMatrix with all binding results
    """
    all_templates = {target_template.species_name: target_template}
    all_templates.update(offtarget_templates)
    
    primer_names = []
    bindings = {}
    
    for primer in primers:
        name = primer.get("name", "unknown")
        fwd = primer.get("forward", "")
        rev = primer.get("reverse", "")
        
        # Check both forward and reverse primers
        for direction, seq in [("_fwd", fwd), ("_rev", rev)]:
            if not seq:
                continue
            
            full_name = f"{name}{direction}"
            primer_names.append(full_name)
            bindings[full_name] = {}
            
            for species_name, template in all_templates.items():
                binding = analyze_primer_binding(
                    full_name,
                    seq,
                    template,
                    min_match_percent=min_match_percent,
                    max_mismatches=max_mismatches
                )
                bindings[full_name][species_name] = binding
    
    return SpecificityMatrix(
        primer_names=primer_names,
        species_names=list(all_templates.keys()),
        target_species=target_template.species_name,
        bindings=bindings
    )


def check_species_specificity(
    primers: List[Dict[str, str]],
    target_template: SpeciesTemplate,
    offtarget_templates: Dict[str, SpeciesTemplate],
    config: Optional[Dict] = None
) -> SpeciesCheckResult:
    """
    Comprehensive species specificity check.
    
    Args:
        primers: List of primer pair dicts
        target_template: Target species template
        offtarget_templates: Off-target species templates
        config: Optional configuration dict
        
    Returns:
        SpeciesCheckResult with specificity scores
    """
    config = config or {}
    min_match = config.get("min_match_percent", 70.0)
    max_mm = config.get("max_mismatches", 5)
    offtarget_threshold = config.get("offtarget_threshold", 80.0)
    
    # Build specificity matrix
    matrix = compare_binding_across_species(
        primers, target_template, offtarget_templates,
        min_match_percent=min_match, max_mismatches=max_mm
    )
    
    # Calculate scores and warnings
    warnings = []
    recommendations = []
    scores = []
    all_specific = True
    
    for primer_name in matrix.primer_names:
        spec_score = matrix.get_specificity_score(primer_name)
        scores.append(spec_score)
        
        # Check for off-target binding
        for species_name in matrix.species_names:
            if species_name == matrix.target_species:
                continue
            
            binding = matrix.get_binding(primer_name, species_name)
            if binding and binding.best_match_percent >= offtarget_threshold:
                warnings.append(
                    f"{primer_name} shows strong binding ({binding.best_match_percent:.1f}%) "
                    f"to off-target species: {species_name}"
                )
                all_specific = False
    
    # Calculate overall score
    overall_score = sum(scores) / len(scores) if scores else 0.0
    grade = score_to_grade(overall_score)
    
    if not all_specific:
        recommendations.append(
            "Consider redesigning primers with off-target binding to improve specificity"
        )
    
    if overall_score < 70:
        recommendations.append(
            "Overall specificity is low - review primer design for target species"
        )
    
    return SpeciesCheckResult(
        target_species=target_template.species_name,
        primers_checked=len(primers),
        species_checked=len(matrix.species_names),
        specificity_matrix=matrix,
        overall_score=overall_score,
        grade=grade,
        is_specific=all_specific,
        warnings=warnings,
        recommendations=recommendations
    )
