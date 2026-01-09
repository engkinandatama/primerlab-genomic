"""
Config Validation (v0.3.2)

Validate PrimerLab configuration files with helpful error messages.
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationError:
    """A single validation error."""
    path: str
    message: str
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "message": self.message,
            "suggestion": self.suggestion
        }


@dataclass
class ValidationResult:
    """Result of config validation."""
    valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary for JSON serialization."""
        return {
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings]
        }


class ConfigValidator:
    """
    Validate PrimerLab configuration files.
    
    Provides helpful error messages and suggestions.
    """

    # Required fields for each section
    REQUIRED_FIELDS = {
        "sequence": ["sequence", "source"],
        "primers": ["product_size"],
    }

    # Valid values for enum fields
    VALID_VALUES = {
        "primers.gc_clamp": [0, 1, 2, 3],
        "output.format": ["markdown", "json", "csv", "xlsx"],
        "offtarget.mode": ["auto", "blast", "biopython"],
    }

    # Type validators
    TYPE_VALIDATORS = {
        "primers.tm_opt": (float, int),
        "primers.gc_percent_min": (float, int),
        "offtarget.evalue": (float, int),
        "offtarget.identity": (float, int),
        "offtarget.max_hits": int,
    }

    def __init__(self):
        """Initialize validator."""
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate a configuration dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            ValidationResult with errors and warnings
        """
        self.errors = []
        self.warnings = []

        # Validate required sections
        self._validate_required_sections(config)

        # Validate offtarget section if present
        if "offtarget" in config:
            self._validate_offtarget(config["offtarget"])

        # Validate primers section
        if "primers" in config:
            self._validate_primers(config["primers"])

        return ValidationResult(
            valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings
        )

    def _validate_required_sections(self, config: Dict[str, Any]):
        """Validate required sections exist."""
        if "sequence" not in config and "input" not in config:
            self.errors.append(ValidationError(
                path="sequence",
                message="Missing 'sequence' or 'input' section",
                suggestion="Add 'sequence:' section with 'source: file' or inline sequence"
            ))

    def _validate_offtarget(self, offtarget: Dict[str, Any]):
        """Validate offtarget configuration."""
        if offtarget.get("enabled", False):
            # Database is required if enabled
            if not offtarget.get("database"):
                self.errors.append(ValidationError(
                    path="offtarget.database",
                    message="Off-target enabled but no database specified",
                    suggestion="Set 'database: /path/to/genome.fasta'"
                ))
            else:
                db_path = Path(offtarget["database"])
                if not db_path.exists():
                    self.warnings.append(ValidationError(
                        path="offtarget.database",
                        message=f"Database file not found: {db_path}",
                        suggestion="Check the path or use --blast-db to override"
                    ))

        # Validate mode
        if "mode" in offtarget:
            if offtarget["mode"] not in ["auto", "blast", "biopython"]:
                self.errors.append(ValidationError(
                    path="offtarget.mode",
                    message=f"Invalid mode: {offtarget['mode']}",
                    suggestion="Use 'auto', 'blast', or 'biopython'"
                ))

        # Validate numeric fields
        if "evalue" in offtarget:
            if not isinstance(offtarget["evalue"], (int, float)):
                self.errors.append(ValidationError(
                    path="offtarget.evalue",
                    message="E-value must be a number",
                    suggestion="Example: evalue: 10.0"
                ))

        if "identity" in offtarget:
            val = offtarget["identity"]
            if not isinstance(val, (int, float)) or val < 0 or val > 100:
                self.errors.append(ValidationError(
                    path="offtarget.identity",
                    message="Identity must be 0-100",
                    suggestion="Example: identity: 80.0"
                ))

    def _validate_primers(self, primers: Dict[str, Any]):
        """Validate primers configuration."""
        # Validate product_size
        if "product_size" in primers:
            ps = primers["product_size"]
            if isinstance(ps, dict):
                required = ["min", "max"]
                for key in required:
                    if key not in ps:
                        self.warnings.append(ValidationError(
                            path=f"primers.product_size.{key}",
                            message=f"Missing product_size.{key}",
                            suggestion="Add min, opt, max values"
                        ))

        # Validate Tm range
        if "tm_min" in primers and "tm_max" in primers:
            if primers["tm_min"] > primers["tm_max"]:
                self.errors.append(ValidationError(
                    path="primers.tm_min/tm_max",
                    message="tm_min is greater than tm_max",
                    suggestion="Swap the values"
                ))


def validate_config(config: Dict[str, Any]) -> ValidationResult:
    """
    Convenience function to validate config.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        ValidationResult
    """
    validator = ConfigValidator()
    return validator.validate(config)


def format_validation_errors(result: ValidationResult) -> str:
    """
    Format validation errors for display.
    
    Args:
        result: ValidationResult
        
    Returns:
        Formatted error string
    """
    lines = []

    if result.errors:
        lines.append("❌ Configuration Errors:")
        for err in result.errors:
            lines.append(f"   • {err.path}: {err.message}")
            if err.suggestion:
                lines.append(f"     💡 {err.suggestion}")

    if result.warnings:
        lines.append("\n⚠️  Warnings:")
        for warn in result.warnings:
            lines.append(f"   • {warn.path}: {warn.message}")
            if warn.suggestion:
                lines.append(f"     💡 {warn.suggestion}")

    return "\n".join(lines)
