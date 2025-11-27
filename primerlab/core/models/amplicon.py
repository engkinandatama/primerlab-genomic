from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Amplicon:
    start: int
    end: int
    length: int
    sequence: str
    gc: float
    
    tm_forward: float
    tm_reverse: float

    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "length": self.length,
            "sequence": self.sequence,
            "gc": round(self.gc, 2),
            "tm_forward": round(self.tm_forward, 2),
            "tm_reverse": round(self.tm_reverse, 2),
            "warnings": self.warnings
        }
