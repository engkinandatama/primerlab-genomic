"""
Core QC module exports.

This module provides the base QC functionality used by workflow-specific
QC modules. All shared thermodynamic and structural QC logic lives here.
"""

from primerlab.core.qc.base_qc import BaseQC

__all__ = ["BaseQC"]
