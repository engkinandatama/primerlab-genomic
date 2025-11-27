from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class QCResult:
    hairpin_ok: bool
    homodimer_ok: bool
    heterodimer_ok: bool
    tm_balance_ok: bool

    hairpin_dg: float
    homodimer_dg: float
    heterodimer_dg: Optional[float]

    tm_diff: float

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hairpin_ok": self.hairpin_ok,
            "homodimer_ok": self.homodimer_ok,
            "heterodimer_ok": self.heterodimer_ok,
            "tm_balance_ok": self.tm_balance_ok,
            "hairpin_dg": round(self.hairpin_dg, 2) if self.hairpin_dg is not None else None,
            "homodimer_dg": round(self.homodimer_dg, 2) if self.homodimer_dg is not None else None,
            "heterodimer_dg": round(self.heterodimer_dg, 2) if self.heterodimer_dg is not None else None,
            "tm_diff": round(self.tm_diff, 2),
            "warnings": self.warnings,
            "errors": self.errors
        }
