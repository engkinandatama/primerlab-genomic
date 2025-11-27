"""
qPCR workflow progress tracking.
Defines the steps for qPCR workflow execution.
"""

# qPCR Workflow Progress Steps
QPCR_STEPS = [
    "Initializing",
    "Loading sequence",
    "Designing primers and probe (Primer3)",
    "Running QC checks",
    "Calculating efficiency",
    "Validating amplicon size",
    "Generating report",
    "Complete"
]

def get_step_name(step_index: int) -> str:
    """
    Returns the name of the step at the given index.
    
    Args:
        step_index: Index of the step (0-based)
        
    Returns:
        Step name string
    """
    if 0 <= step_index < len(QPCR_STEPS):
        return QPCR_STEPS[step_index]
    return "Unknown step"

def get_total_steps() -> int:
    """
    Returns the total number of steps in the qPCR workflow.
    """
    return len(QPCR_STEPS)
