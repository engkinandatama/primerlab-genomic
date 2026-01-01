"""
Visualization Module.

Provides visualization tools for primer design results.
"""

from primerlab.core.visualization.coverage_map import (
    CoverageMapGenerator,
    PrimerRegion,
    AmpliconRegion,
    CoverageMapResult,
    create_coverage_map,
)

__all__ = [
    "CoverageMapGenerator",
    "PrimerRegion",
    "AmpliconRegion",
    "CoverageMapResult",
    "create_coverage_map",
]
