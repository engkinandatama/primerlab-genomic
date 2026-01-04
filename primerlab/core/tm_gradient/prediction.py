"""
Tm Gradient Prediction and Sensitivity Analysis.

Provides optimal annealing temperature prediction and sensitivity scoring.
"""

import logging
from typing import List, Optional, Dict

from .models import (
    TmGradientConfig,
    TmGradientResult,
    TemperatureSensitivity,
    score_to_grade
)
from .engine import simulate_tm_gradient

logger = logging.getLogger(__name__)


def predict_optimal_annealing(
    primers: List[Dict[str, str]],
    config: Optional[TmGradientConfig] = None
) -> Dict[str, float]:
    """
    Predict optimal annealing temperature for a set of primers.
    
    Finds temperature where all primers have good efficiency.
    
    Args:
        primers: List of dicts with 'name' and 'sequence' keys
        config: Gradient configuration
        
    Returns:
        Dict with 'optimal', 'range_min', 'range_max', per-primer results
    """
    if config is None:
        config = TmGradientConfig()

    results = {}
    optimal_temps = []
    all_ranges = []

    for primer in primers:
        name = primer.get("name", "Primer")
        seq = primer.get("sequence", primer.get("forward", primer.get("fwd", "")))

        if not seq:
            continue

        result = simulate_tm_gradient(seq, name, config=config)
        results[name] = {
            "optimal": result.optimal_annealing_temp,
            "tm": result.calculated_tm,
            "grade": result.grade
        }

        optimal_temps.append(result.optimal_annealing_temp)
        all_ranges.append(result.recommended_range)

    if not optimal_temps:
        return {"optimal": 60.0, "range_min": 55.0, "range_max": 65.0}

    # Calculate consensus optimal - average of all optimals
    consensus_optimal = sum(optimal_temps) / len(optimal_temps)

    # Find overlapping range
    range_min = max(r[0] for r in all_ranges) if all_ranges else 55.0
    range_max = min(r[1] for r in all_ranges) if all_ranges else 65.0

    # If ranges don't overlap, use consensus with warning
    if range_min > range_max:
        range_min = consensus_optimal - 3
        range_max = consensus_optimal + 3

    return {
        "optimal": round(consensus_optimal, 1),
        "range_min": round(range_min, 1),
        "range_max": round(range_max, 1),
        "primers": results
    }


def analyze_temperature_sensitivity(
    primer_sequence: str,
    primer_name: str = "Primer",
    config: Optional[TmGradientConfig] = None
) -> TemperatureSensitivity:
    """
    Analyze how sensitive a primer is to temperature changes.
    
    Lower sensitivity = primer works well across temperature range.
    Higher sensitivity = primer requires precise temperature control.
    
    Args:
        primer_sequence: Primer sequence
        primer_name: Primer identifier
        config: Gradient configuration
        
    Returns:
        TemperatureSensitivity analysis
    """
    if config is None:
        config = TmGradientConfig()

    # Run gradient simulation
    result = simulate_tm_gradient(primer_sequence, primer_name, config=config)

    optimal_temp = result.optimal_annealing_temp

    # Find efficiency at optimal and ±5°C
    eff_at_optimal = 0.0
    eff_at_minus_5 = 0.0
    eff_at_plus_5 = 0.0

    for dp in result.data_points:
        if abs(dp.temperature - optimal_temp) < 0.3:
            eff_at_optimal = dp.binding_efficiency
        if abs(dp.temperature - (optimal_temp - 5)) < 0.3:
            eff_at_minus_5 = dp.binding_efficiency
        if abs(dp.temperature - (optimal_temp + 5)) < 0.3:
            eff_at_plus_5 = dp.binding_efficiency

    # Calculate tolerance range (temps with >80% efficiency)
    high_eff_temps = [dp.temperature for dp in result.data_points 
                      if dp.binding_efficiency >= 80]

    if high_eff_temps:
        tolerance_range = max(high_eff_temps) - min(high_eff_temps)
    else:
        tolerance_range = 0.0

    # Narrow window if < 4°C range
    narrow_window = tolerance_range < 4.0

    # Sensitivity score (higher = less sensitive = better)
    # Based on tolerance range and efficiency retention at ±5°C
    avg_retention = (eff_at_minus_5 + eff_at_plus_5) / 2
    sensitivity_score = min(100, tolerance_range * 10 + avg_retention * 0.3)

    grade = score_to_grade(sensitivity_score)

    return TemperatureSensitivity(
        primer_name=primer_name,
        optimal_temp=optimal_temp,
        sensitivity_score=round(sensitivity_score, 1),
        tolerance_range=round(tolerance_range, 1),
        narrow_window=narrow_window,
        efficiency_at_optimal=round(eff_at_optimal, 1),
        efficiency_at_minus_5=round(eff_at_minus_5, 1),
        efficiency_at_plus_5=round(eff_at_plus_5, 1),
        grade=grade
    )


def compare_primer_sensitivity(
    primers: List[Dict[str, str]],
    config: Optional[TmGradientConfig] = None
) -> List[TemperatureSensitivity]:
    """
    Compare temperature sensitivity across multiple primers.
    
    Args:
        primers: List of dicts with 'name' and 'sequence' keys
        config: Gradient configuration
        
    Returns:
        List of TemperatureSensitivity, sorted by score (best first)
    """
    if config is None:
        config = TmGradientConfig()

    sensitivities = []

    for primer in primers:
        name = primer.get("name", "Primer")
        seq = primer.get("sequence", primer.get("forward", primer.get("fwd", "")))

        if not seq:
            continue

        sens = analyze_temperature_sensitivity(seq, name, config)
        sensitivities.append(sens)

    # Sort by score descending (best first)
    sensitivities.sort(key=lambda x: x.sensitivity_score, reverse=True)

    return sensitivities
