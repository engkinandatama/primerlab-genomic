"""
qPCR Efficiency Tools.

Provides standard curve calculation, efficiency prediction,
and qPCR performance analysis.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import math
from primerlab.core.logger import get_logger

logger = get_logger()


@dataclass
class StandardCurveResult:
    """Result of standard curve analysis."""
    concentrations: List[float]
    ct_values: List[float]
    slope: float
    intercept: float
    r_squared: float
    efficiency: float  # PCR efficiency (%)
    dynamic_range: float  # log10 range
    lod: Optional[float] = None  # Limit of detection
    loq: Optional[float] = None  # Limit of quantification

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slope": self.slope,
            "intercept": self.intercept,
            "r_squared": self.r_squared,
            "efficiency": self.efficiency,
            "dynamic_range": self.dynamic_range,
            "lod": self.lod,
            "loq": self.loq,
            "data_points": len(self.concentrations),
        }

    @property
    def is_acceptable(self) -> bool:
        """Check if efficiency is in acceptable range (90-110%)."""
        return 90.0 <= self.efficiency <= 110.0

    @property
    def grade(self) -> str:
        """Grade the standard curve quality."""
        if self.r_squared >= 0.99 and 95 <= self.efficiency <= 105:
            return "A"
        elif self.r_squared >= 0.98 and 90 <= self.efficiency <= 110:
            return "B"
        elif self.r_squared >= 0.95 and 85 <= self.efficiency <= 115:
            return "C"
        else:
            return "D"


@dataclass
class EfficiencyPrediction:
    """Predicted primer efficiency based on thermodynamic properties."""
    primer_forward: str
    primer_reverse: str
    predicted_efficiency: float
    confidence: float
    factors: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "predicted_efficiency": self.predicted_efficiency,
            "confidence": self.confidence,
            "factors": self.factors,
            "recommendations": self.recommendations,
        }


class EfficiencyCalculator:
    """
    Calculates PCR efficiency from standard curve data.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize calculator."""
        self.config = config or {}

    def calculate_from_curve(
        self,
        concentrations: List[float],
        ct_values: List[float],
    ) -> StandardCurveResult:
        """
        Calculate efficiency from standard curve data.
        
        Args:
            concentrations: Template concentrations (copies or dilution factors)
            ct_values: Corresponding Ct/Cq values
            
        Returns:
            StandardCurveResult with efficiency and statistics
        """
        if len(concentrations) != len(ct_values):
            raise ValueError("Concentrations and Ct values must have same length")

        if len(concentrations) < 3:
            raise ValueError("At least 3 data points required for standard curve")

        # Convert to log10 scale
        log_conc = [math.log10(c) for c in concentrations if c > 0]
        ct_filtered = [ct for c, ct in zip(concentrations, ct_values) if c > 0]

        # Linear regression
        n = len(log_conc)
        sum_x = sum(log_conc)
        sum_y = sum(ct_filtered)
        sum_xy = sum(x * y for x, y in zip(log_conc, ct_filtered))
        sum_x2 = sum(x * x for x in log_conc)
        sum_y2 = sum(y * y for y in ct_filtered)

        # Slope and intercept
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            raise ValueError("Cannot calculate slope - degenerate data")

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n

        # R-squared
        ss_tot = sum_y2 - (sum_y * sum_y) / n
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(log_conc, ct_filtered))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Efficiency: E = 10^(-1/slope) - 1
        efficiency = (10 ** (-1 / slope) - 1) * 100 if slope != 0 else 0

        # Dynamic range
        dynamic_range = max(log_conc) - min(log_conc) if log_conc else 0

        result = StandardCurveResult(
            concentrations=concentrations,
            ct_values=ct_values,
            slope=slope,
            intercept=intercept,
            r_squared=r_squared,
            efficiency=efficiency,
            dynamic_range=dynamic_range,
        )

        logger.info(f"Standard curve: E={efficiency:.1f}%, R²={r_squared:.4f}")
        return result

    def predict_efficiency(
        self,
        forward_seq: str,
        reverse_seq: str,
        tm_forward: float,
        tm_reverse: float,
        gc_forward: float,
        gc_reverse: float,
        amplicon_length: int,
    ) -> EfficiencyPrediction:
        """
        Predict primer efficiency based on thermodynamic properties.
        
        Args:
            forward_seq: Forward primer sequence
            reverse_seq: Reverse primer sequence
            tm_forward: Forward primer Tm
            tm_reverse: Reverse primer Tm
            gc_forward: Forward primer GC%
            gc_reverse: Reverse primer GC%
            amplicon_length: Amplicon length in bp
            
        Returns:
            EfficiencyPrediction with predicted efficiency
        """
        factors = {}
        base_efficiency = 100.0

        # Tm difference penalty
        tm_diff = abs(tm_forward - tm_reverse)
        if tm_diff > 2:
            penalty = min(tm_diff * 2, 10)
            base_efficiency -= penalty
            factors["tm_difference"] = -penalty
        else:
            factors["tm_difference"] = 0

        # GC content balance
        gc_avg = (gc_forward + gc_reverse) / 2
        if 45 <= gc_avg <= 55:
            factors["gc_content"] = 2
            base_efficiency += 2
        elif gc_avg < 40 or gc_avg > 60:
            factors["gc_content"] = -5
            base_efficiency -= 5
        else:
            factors["gc_content"] = 0

        # Amplicon length factor
        if 80 <= amplicon_length <= 150:
            factors["amplicon_length"] = 5
            base_efficiency += 5
        elif amplicon_length > 300:
            penalty = min((amplicon_length - 300) / 50, 10)
            factors["amplicon_length"] = -penalty
            base_efficiency -= penalty
        else:
            factors["amplicon_length"] = 0

        # Primer length factor
        fwd_len = len(forward_seq)
        rev_len = len(reverse_seq)
        if 18 <= fwd_len <= 22 and 18 <= rev_len <= 22:
            factors["primer_length"] = 2
            base_efficiency += 2
        else:
            factors["primer_length"] = 0

        # Confidence based on factors
        confidence = 0.7 + (sum(1 for v in factors.values() if v >= 0) / len(factors)) * 0.3

        # Recommendations
        recommendations = []
        if tm_diff > 2:
            recommendations.append(f"Consider adjusting primers to reduce Tm difference ({tm_diff:.1f}°C)")
        if gc_avg < 40:
            recommendations.append("GC content is low - may reduce binding stability")
        if gc_avg > 60:
            recommendations.append("GC content is high - may cause secondary structures")
        if amplicon_length > 300:
            recommendations.append(f"Amplicon is long ({amplicon_length}bp) - consider shorter product for qPCR")

        return EfficiencyPrediction(
            primer_forward=forward_seq,
            primer_reverse=reverse_seq,
            predicted_efficiency=max(min(base_efficiency, 120), 60),
            confidence=confidence,
            factors=factors,
            recommendations=recommendations,
        )


def calculate_efficiency(
    concentrations: List[float],
    ct_values: List[float],
) -> StandardCurveResult:
    """
    Calculate PCR efficiency from standard curve.
    
    Args:
        concentrations: Template concentrations
        ct_values: Corresponding Ct values
        
    Returns:
        StandardCurveResult
    """
    calculator = EfficiencyCalculator()
    return calculator.calculate_from_curve(concentrations, ct_values)


def predict_primer_efficiency(
    forward_seq: str,
    reverse_seq: str,
    tm_forward: float = 60.0,
    tm_reverse: float = 60.0,
    gc_forward: float = 50.0,
    gc_reverse: float = 50.0,
    amplicon_length: int = 100,
) -> EfficiencyPrediction:
    """
    Predict primer efficiency from thermodynamic properties.
    
    Args:
        forward_seq: Forward primer sequence
        reverse_seq: Reverse primer sequence
        tm_forward: Forward Tm
        tm_reverse: Reverse Tm
        gc_forward: Forward GC%
        gc_reverse: Reverse GC%
        amplicon_length: Amplicon length
        
    Returns:
        EfficiencyPrediction
    """
    calculator = EfficiencyCalculator()
    return calculator.predict_efficiency(
        forward_seq, reverse_seq,
        tm_forward, tm_reverse,
        gc_forward, gc_reverse,
        amplicon_length,
    )
