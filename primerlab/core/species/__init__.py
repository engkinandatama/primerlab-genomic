"""
Species-Specific Primer Analysis Module.

Provides tools for analyzing primer specificity across multiple species.
"""

from .models import (
    SpeciesTemplate,
    BindingSite,
    SpeciesBinding,
    SpecificityMatrix,
    SpeciesCheckResult,
    score_to_grade,
)
from .loader import (
    load_species_template,
    load_species_templates,
    load_multi_fasta,
    parse_fasta,
)
from .alignment import (
    find_binding_sites,
    calculate_match_percent,
    reverse_complement,
    local_align,
)
from .binding import (
    analyze_primer_binding,
    compare_binding_across_species,
    check_species_specificity,
)
from .scoring import (
    CrossReactivityScore,
    calculate_cross_reactivity_score,
    generate_specificity_matrix_table,
    detect_offtarget_species,
)

__all__ = [
    # Models
    "SpeciesTemplate",
    "BindingSite",
    "SpeciesBinding",
    "SpecificityMatrix",
    "SpeciesCheckResult",
    "score_to_grade",
    # Loader
    "load_species_template",
    "load_species_templates",
    "load_multi_fasta",
    "parse_fasta",
    # Alignment
    "find_binding_sites",
    "calculate_match_percent",
    "reverse_complement",
    "local_align",
    # Binding analysis
    "analyze_primer_binding",
    "compare_binding_across_species",
    "check_species_specificity",
    # Scoring (v0.4.2)
    "CrossReactivityScore",
    "calculate_cross_reactivity_score",
    "generate_specificity_matrix_table",
    "detect_offtarget_species",
]
