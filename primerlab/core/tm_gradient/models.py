"""
Tm Gradient Data Models.

Dataclasses for temperature gradient simulation configuration and results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class TmGradientConfig:
    """Configuration for Tm gradient simulation."""
    min_temp: float = 50.0          # Minimum temperature (°C)
    max_temp: float = 72.0          # Maximum temperature (°C)
    step_size: float = 0.5          # Temperature step (°C)
    na_concentration: float = 50.0   # Na+ concentration (mM)
    mg_concentration: float = 1.5    # Mg2+ concentration (mM)
    primer_concentration: float = 0.25  # Primer concentration (µM)

    @property
    def temperature_range(self) -> List[float]:
        """Generate list of temperatures to simulate."""
        temps = []
        temp = self.min_temp
        while temp <= self.max_temp:
            temps.append(round(temp, 2))
            temp += self.step_size
        return temps


@dataclass
class TmDataPoint:
    """Single data point in Tm gradient curve."""
    temperature: float              # Temperature (°C)
    binding_efficiency: float       # 0-100% binding efficiency
    fraction_bound: float           # 0-1 fraction of primer bound
    delta_g: float                  # ΔG at this temperature (kcal/mol)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature": self.temperature,
            "binding_efficiency": self.binding_efficiency,
            "fraction_bound": self.fraction_bound,
            "delta_g": self.delta_g
        }


@dataclass
class TemperatureSensitivity:
    """Temperature sensitivity analysis for a primer."""
    primer_name: str
    optimal_temp: float             # Optimal annealing temperature
    sensitivity_score: float        # 0-100, higher = less sensitive
    tolerance_range: float          # ±°C range with >80% efficiency
    narrow_window: bool             # True if tolerance < 2°C

    # Detailed data
    efficiency_at_optimal: float    # Efficiency at optimal temp
    efficiency_at_minus_5: float    # Efficiency at optimal-5°C
    efficiency_at_plus_5: float     # Efficiency at optimal+5°C

    grade: str = "A"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primer_name": self.primer_name,
            "optimal_temp": self.optimal_temp,
            "sensitivity_score": self.sensitivity_score,
            "tolerance_range": self.tolerance_range,
            "narrow_window": self.narrow_window,
            "efficiency_at_optimal": self.efficiency_at_optimal,
            "grade": self.grade
        }


@dataclass
class TmGradientResult:
    """Complete result of Tm gradient simulation."""
    primer_name: str
    primer_sequence: str
    template_name: Optional[str] = None

    # Calculated Tm
    calculated_tm: float = 0.0

    # Optimal annealing
    optimal_annealing_temp: float = 0.0
    recommended_range: tuple = (55.0, 65.0)

    # Data points
    data_points: List[TmDataPoint] = field(default_factory=list)

    # Sensitivity
    sensitivity: Optional[TemperatureSensitivity] = None

    # Summary
    grade: str = "A"
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primer_name": self.primer_name,
            "primer_sequence": self.primer_sequence,
            "template_name": self.template_name,
            "calculated_tm": self.calculated_tm,
            "optimal_annealing_temp": self.optimal_annealing_temp,
            "recommended_range": list(self.recommended_range),
            "data_points": [dp.to_dict() for dp in self.data_points],
            "sensitivity": self.sensitivity.to_dict() if self.sensitivity else None,
            "grade": self.grade,
            "warnings": self.warnings
        }

    @property
    def max_efficiency(self) -> float:
        """Get maximum efficiency across all temperatures."""
        if not self.data_points:
            return 0.0
        return max(dp.binding_efficiency for dp in self.data_points)

    @property
    def efficiency_curve(self) -> List[tuple]:
        """Get (temp, efficiency) pairs for plotting."""
        return [(dp.temperature, dp.binding_efficiency) for dp in self.data_points]


def score_to_grade(score: float) -> str:
    """Convert sensitivity score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    return "F"
