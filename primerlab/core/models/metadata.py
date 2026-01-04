from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class RunMetadata:
    workflow: str
    timestamp: str
    version: str

    input_hash: str = ""
    config_hash: str = ""

    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow": self.workflow,
            "timestamp": self.timestamp,
            "version": self.version,
            "input_hash": self.input_hash,
            "config_hash": self.config_hash,
            "parameters": self.parameters
        }
