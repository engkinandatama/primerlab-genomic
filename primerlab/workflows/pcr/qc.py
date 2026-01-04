"""
PCR-specific Quality Control module.

Extends BaseQC with PCR-specific validation. This module follows
the architecture principle that workflows import from core/, not
from other workflows.

Version: v0.3.6
"""

from typing import Dict, Any
from primerlab.core.models import Primer, QCResult
from primerlab.core.logger import get_logger
from primerlab.core.qc import BaseQC

logger = get_logger()


class PCRQC(BaseQC):
    """
    Quality Control for PCR primers.
    
    Extends BaseQC with any PCR-specific validation logic.
    Currently uses all base functionality without modifications,
    but can be extended for PCR-specific checks in the future.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize PCRQC with configuration.
        
        Args:
            config: Full workflow configuration dict containing 'qc' section
        """
        super().__init__(config)
        # PCR-specific thresholds can be added here

    def evaluate_pair(self, fwd: Primer, rev: Primer) -> QCResult:
        """
        Evaluate a PCR primer pair against QC thresholds.
        
        Uses base evaluation plus any PCR-specific checks.
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            QCResult with all evaluation results
        """
        # Use base evaluation
        result = super().evaluate_pair(fwd, rev)

        # PCR-specific checks can be added here in the future
        # For example: product size validation, GC content checks, etc.

        return result
