"""
Tm Gradient Simulation Module.

Provides temperature gradient simulation for optimal annealing temperature prediction.
"""

from .models import (
    TmGradientConfig,
    TmGradientResult,
    TemperatureSensitivity,
    TmDataPoint,
)
from .engine import (
    simulate_tm_gradient,
    calculate_binding_efficiency,
)
from .prediction import (
    predict_optimal_annealing,
    analyze_temperature_sensitivity,
)

__all__ = [
    # Models
    "TmGradientConfig",
    "TmGradientResult",
    "TemperatureSensitivity",
    "TmDataPoint",
    # Engine
    "simulate_tm_gradient",
    "calculate_binding_efficiency",
    # Prediction
    "predict_optimal_annealing",
    "analyze_temperature_sensitivity",
]
