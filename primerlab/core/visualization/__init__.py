"""
Visualization Module.

Provides visualization tools for primer design results.
"""

# v0.7.2 Coverage Map (new)
from primerlab.core.visualization.coverage_map import (
    CoverageMapGenerator,
    PrimerRegion,
    AmpliconRegion,
    CoverageMapResult,
    create_coverage_map,
)

# v0.1.6 GC Profile (legacy - re-export from visualization.py file)
# Note: The functions live in ../visualization.py (file), we import and re-export here
import sys
import os

# Import from the parent visualization.py file
_parent_dir = os.path.dirname(os.path.dirname(__file__))
_viz_module_path = os.path.join(_parent_dir, "visualization.py")

# Import the functions using importlib
import importlib.util
_spec = importlib.util.spec_from_file_location("visualization_legacy", _viz_module_path)
_viz_legacy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_viz_legacy)

# Re-export legacy functions
calculate_gc_profile = _viz_legacy.calculate_gc_profile
plot_gc_profile = _viz_legacy.plot_gc_profile
generate_gc_profile_from_result = _viz_legacy.generate_gc_profile_from_result
THEMES = _viz_legacy.THEMES

__all__ = [
    # v0.7.2 Coverage Map
    "CoverageMapGenerator",
    "PrimerRegion",
    "AmpliconRegion",
    "CoverageMapResult",
    "create_coverage_map",
    # v0.1.6 GC Profile (legacy)
    "calculate_gc_profile",
    "plot_gc_profile",
    "generate_gc_profile_from_result",
    "THEMES",
]
