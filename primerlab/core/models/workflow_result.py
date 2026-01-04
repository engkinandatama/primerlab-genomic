from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from .primer import Primer
from .amplicon import Amplicon
from .qc import QCResult
from .metadata import RunMetadata

@dataclass
class WorkflowResult:
    workflow: str
    primers: Dict[str, Primer]
    amplicons: List[Amplicon]
    metadata: RunMetadata

    qc: Optional[QCResult] = None

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # v0.1.3: Alternative primer candidates
    alternatives: List[Dict[str, Any]] = field(default_factory=list)

    # Internal diagnostics
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow": self.workflow,
            "primers": {k: v.to_dict() for k, v in self.primers.items()},
            "amplicons": [a.to_dict() for a in self.amplicons],
            "qc": self.qc.to_dict() if self.qc else None,
            "metadata": self.metadata.to_dict(),
            "warnings": self.warnings,
            "errors": self.errors,
            "alternatives": self.alternatives
        }
