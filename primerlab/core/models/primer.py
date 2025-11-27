from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class Primer:
    id: str
    sequence: str
    tm: float
    gc: float
    length: int

    hairpin_dg: Optional[float] = None
    homodimer_dg: Optional[float] = None
    heterodimer_dg: Optional[float] = None

    start: Optional[int] = None
    end: Optional[int] = None

    warnings: List[str] = field(default_factory=list)
    
    # Internal use only (Primer3 raw output)
    raw: Optional[Dict[str, Any]] = field(default=None, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary, excluding internal fields."""
        return {
            "id": self.id,
            "sequence": self.sequence,
            "tm": round(self.tm, 2),
            "gc": round(self.gc, 2),
            "length": self.length,
            "hairpin_dg": round(self.hairpin_dg, 2) if self.hairpin_dg is not None else None,
            "homodimer_dg": round(self.homodimer_dg, 2) if self.homodimer_dg is not None else None,
            "heterodimer_dg": round(self.heterodimer_dg, 2) if self.heterodimer_dg is not None else None,
            "start": self.start,
            "end": self.end,
            "warnings": self.warnings
        }
