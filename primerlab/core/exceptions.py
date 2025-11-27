class PrimerLabException(Exception):
    """Base exception for all PrimerLab errors."""
    def __init__(self, message, error_code=None, details=None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

class ConfigError(PrimerLabException):
    """Raised when configuration is invalid or missing."""
    pass

class SequenceError(PrimerLabException):
    """Raised when input sequence is invalid."""
    pass

class ToolExecutionError(PrimerLabException):
    """Raised when an external tool (Primer3, BLAST) fails."""
    pass

class WorkflowError(PrimerLabException):
    """Raised when a workflow logic fails."""
    pass
