"""
PCR Variants Module.

Provides engines for specialized PCR techniques:
- Nested PCR
- Semi-Nested PCR
"""

from primerlab.core.variants.models import (
    NestedPrimerSet,
    NestedPCRResult,
)
from primerlab.core.variants.nested import (
    NestedPCREngine,
    design_nested_primers,
)
from primerlab.core.variants.seminested import (
    SemiNestedPCREngine,
    design_seminested_primers,
)

__all__ = [
    "NestedPrimerSet",
    "NestedPCRResult",
    "NestedPCREngine",
    "design_nested_primers",
    "SemiNestedPCREngine",
    "design_seminested_primers",
]
