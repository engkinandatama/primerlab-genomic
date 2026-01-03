"""
Visualization Module.

Provides visualization tools for primer design results.

Submodules:
    - gc_profile: GC content profile visualization (v0.1.6)
    - coverage_map: Primer coverage map visualization (v0.7.2)
"""

# v0.7.2 Coverage Map
from primerlab.core.visualization.coverage_map import (
    CoverageMapGenerator,
    PrimerRegion,
    AmpliconRegion,
    CoverageMapResult,
    create_coverage_map,
)

# v0.1.6 GC Profile (moved from ../visualization.py to gc_profile.py)
from primerlab.core.visualization.gc_profile import (
    calculate_gc_profile,
    plot_gc_profile,
    generate_gc_profile_from_result,
    THEMES,
)

__all__ = [
    # v0.7.2 Coverage Map
    "CoverageMapGenerator",
    "PrimerRegion",
    "AmpliconRegion",
    "CoverageMapResult",
    "create_coverage_map",
    # v0.1.6 GC Profile
    "calculate_gc_profile",
    "plot_gc_profile",
    "generate_gc_profile_from_result",
    "THEMES",
]
