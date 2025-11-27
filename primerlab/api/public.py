"""
Public API for PrimerLab.
This module provides a high-level programmatic interface for external applications.
"""

from typing import Dict, Any, Optional
from primerlab.core.models import WorkflowResult

def design_pcr_primers(sequence: str, config: Optional[Dict[str, Any]] = None) -> WorkflowResult:
    """
    Programmatic entry point for PCR primer design.
    
    Args:
        sequence: DNA sequence string
        config: Optional configuration dictionary override
        
    Returns:
        WorkflowResult object
    """
    # TODO: Implement API wrapper logic
    raise NotImplementedError("API not yet implemented in v0.4")

def design_qpcr_assays(sequence: str, config: Optional[Dict[str, Any]] = None) -> WorkflowResult:
    """
    Programmatic entry point for qPCR assay design (primers + probe).
    
    Args:
        sequence: DNA sequence string
        config: Optional configuration dictionary override
        
    Returns:
        WorkflowResult object
    """
    # TODO: Implement API wrapper logic
    raise NotImplementedError("API not yet implemented in v0.4")
