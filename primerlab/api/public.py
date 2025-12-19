"""
Public API for PrimerLab.
This module provides a high-level programmatic interface for external applications.
"""

from typing import Dict, Any, Optional
from primerlab.core.models import WorkflowResult
from primerlab.workflows.pcr.workflow import run_pcr_workflow
from primerlab.workflows.qpcr.workflow import run_qpcr_workflow
from primerlab.core.config_loader import load_and_merge_config


def validate_primers(
    forward_primer: str,
    reverse_primer: str,
    template: str,
    template_name: str = "template",
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run in-silico PCR validation for a primer pair.
    
    Args:
        forward_primer: Forward primer sequence (5' to 3')
        reverse_primer: Reverse primer sequence (5' to 3')
        template: Template DNA sequence
        template_name: Name for the template (default: "template")
        params: Optional in-silico parameters
        
    Returns:
        Dictionary with validation results including:
        - success: bool
        - products: list of predicted products
        - primary_product: best product if any
        - warnings: list of warnings
        - errors: list of errors
    """
    from primerlab.core.insilico import run_insilico_pcr
    
    result = run_insilico_pcr(
        template=template,
        forward_primer=forward_primer,
        reverse_primer=reverse_primer,
        template_name=template_name,
        params=params
    )
    
    # Convert to dictionary for API response
    primary = None
    if result.products:
        for p in result.products:
            if p.is_primary:
                primary = {
                    "size": p.product_size,
                    "position": f"{p.start_position}-{p.end_position}",
                    "likelihood": p.likelihood_score,
                    "sequence_preview": p.product_sequence[:50] + "..." if len(p.product_sequence) > 50 else p.product_sequence
                }
                break
    
    return {
        "success": result.success,
        "products_count": len(result.products),
        "primary_product": primary,
        "forward_bindings": len(result.all_forward_bindings),
        "reverse_bindings": len(result.all_reverse_bindings),
        "warnings": result.warnings,
        "errors": result.errors
    }


def design_pcr_primers(
    sequence: str, 
    config: Optional[Dict[str, Any]] = None,
    validate: bool = False
) -> WorkflowResult:
    """
    Programmatic entry point for PCR primer design.
    
    Args:
        sequence: DNA sequence string
        config: Optional configuration dictionary override.
                If provided, it merges with/overrides default PCR settings.
        validate: If True, run in-silico PCR validation after design (v0.2.3)
        
    Returns:
        WorkflowResult object containing primers and QC status.
        If validate=True, includes 'insilico_validation' in metadata.
    """
    # Base config structure
    base_config = {
        "workflow": "pcr",
        "input": {"sequence": sequence},
        "parameters": {},
        "output": {"directory": "primerlab_api_out"} # Default output for API calls
    }
    
    # Merge with user config if provided
    final_config = base_config
    if config:
        final_config.update(config)
        final_config["input"]["sequence"] = sequence

    result = run_pcr_workflow(final_config)
    
    # v0.2.3: Optional in-silico validation
    if validate and result.primers:
        fwd = result.primers.get("forward")
        rev = result.primers.get("reverse")
        
        if fwd and rev:
            validation = validate_primers(
                forward_primer=fwd.sequence,
                reverse_primer=rev.sequence,
                template=sequence,
                template_name=result.metadata.workflow if result.metadata else "template"
            )
            # Add validation to metadata
            if result.metadata:
                result.metadata.insilico_validation = validation
            else:
                # Store in result as attribute
                result.insilico_validation = validation
    
    return result


def design_qpcr_assays(
    sequence: str, 
    config: Optional[Dict[str, Any]] = None,
    validate: bool = False
) -> WorkflowResult:
    """
    Programmatic entry point for qPCR assay design (primers + probe).
    
    Args:
        sequence: DNA sequence string
        config: Optional configuration dictionary override.
        validate: If True, run in-silico PCR validation after design (v0.2.3)
        
    Returns:
        WorkflowResult object containing primers, probe, and efficiency metrics.
    """
    base_config = {
        "workflow": "qpcr",
        "input": {"sequence": sequence},
        "parameters": {},
        "output": {"directory": "primerlab_api_out"}
    }
    
    final_config = base_config
    if config:
        final_config.update(config)
        final_config["input"]["sequence"] = sequence

    result = run_qpcr_workflow(final_config)
    
    # v0.2.3: Optional in-silico validation
    if validate and result.primers:
        fwd = result.primers.get("forward")
        rev = result.primers.get("reverse")
        
        if fwd and rev:
            validation = validate_primers(
                forward_primer=fwd.sequence,
                reverse_primer=rev.sequence,
                template=sequence,
                template_name=result.metadata.workflow if result.metadata else "template"
            )
            if result.metadata:
                result.metadata.insilico_validation = validation
            else:
                result.insilico_validation = validation
    
    return result
