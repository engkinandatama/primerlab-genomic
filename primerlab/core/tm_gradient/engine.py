"""
Tm Gradient Simulation Engine.

Core thermodynamic calculations for temperature-dependent binding efficiency.
"""

import math
import logging
from typing import List, Optional, Tuple

from .models import TmGradientConfig, TmGradientResult, TmDataPoint

logger = logging.getLogger(__name__)

# Nearest-neighbor thermodynamic parameters (SantaLucia 1998)
# ΔH in kcal/mol, ΔS in cal/(mol·K)
NN_PARAMS = {
    "AA/TT": (-7.9, -22.2),
    "AT/TA": (-7.2, -20.4),
    "TA/AT": (-7.2, -21.3),
    "CA/GT": (-8.5, -22.7),
    "GT/CA": (-8.4, -22.4),
    "CT/GA": (-7.8, -21.0),
    "GA/CT": (-8.2, -22.2),
    "CG/GC": (-10.6, -27.2),
    "GC/CG": (-9.8, -24.4),
    "GG/CC": (-8.0, -19.9),
}

# Initiation parameters
INIT_GC = (0.1, -2.8)  # G or C at end
INIT_AT = (2.3, 4.1)   # A or T at end


def calculate_tm_nearest_neighbor(
    sequence: str,
    na_conc: float = 50.0,
    primer_conc: float = 0.25
) -> Tuple[float, float, float]:
    """
    Calculate Tm using nearest-neighbor method.
    
    Args:
        sequence: Primer sequence (5' to 3')
        na_conc: Na+ concentration in mM
        primer_conc: Primer concentration in µM
        
    Returns:
        Tuple of (Tm, ΔH, ΔS)
    """
    seq = sequence.upper()
    
    # Calculate ΔH and ΔS from nearest-neighbor pairs
    delta_h = 0.0  # kcal/mol
    delta_s = 0.0  # cal/(mol·K)
    
    # Initiation
    if seq[0] in "GC":
        delta_h += INIT_GC[0]
        delta_s += INIT_GC[1]
    else:
        delta_h += INIT_AT[0]
        delta_s += INIT_AT[1]
    
    if seq[-1] in "GC":
        delta_h += INIT_GC[0]
        delta_s += INIT_GC[1]
    else:
        delta_h += INIT_AT[0]
        delta_s += INIT_AT[1]
    
    # Nearest-neighbor pairs
    complement = {"A": "T", "T": "A", "G": "C", "C": "G"}
    
    for i in range(len(seq) - 1):
        pair1 = seq[i:i+2]
        pair2 = complement.get(seq[i+1], "N") + complement.get(seq[i], "N")
        key = f"{pair1}/{pair2}"
        
        if key in NN_PARAMS:
            dh, ds = NN_PARAMS[key]
            delta_h += dh
            delta_s += ds
        else:
            # Default for missing pairs
            delta_h += -8.0
            delta_s += -21.0
    
    # Salt correction
    na_molar = na_conc / 1000.0
    delta_s_corrected = delta_s + 0.368 * len(seq) * math.log(na_molar)
    
    # Calculate Tm
    R = 1.987  # Gas constant cal/(mol·K)
    primer_molar = primer_conc * 1e-6
    
    tm_kelvin = (delta_h * 1000) / (delta_s_corrected + R * math.log(primer_molar / 4))
    tm_celsius = tm_kelvin - 273.15
    
    return tm_celsius, delta_h, delta_s_corrected


def calculate_binding_efficiency(
    temperature: float,
    tm: float,
    delta_h: float,
    delta_s: float
) -> Tuple[float, float, float]:
    """
    Calculate binding efficiency at a given temperature.
    
    Uses thermodynamic model to calculate fraction bound.
    
    Returns:
        Tuple of (efficiency_percent, fraction_bound, delta_g)
    """
    R = 1.987  # cal/(mol·K)
    T_kelvin = temperature + 273.15
    
    # Calculate ΔG at this temperature
    delta_g = delta_h - (T_kelvin * delta_s / 1000.0)
    
    # Calculate equilibrium constant K
    K = math.exp(-delta_g * 1000 / (R * T_kelvin))
    
    # Fraction bound (simplified two-state model)
    # At very high K, fraction approaches 1
    fraction_bound = K / (1 + K)
    
    # Efficiency as percentage
    efficiency = fraction_bound * 100
    
    return efficiency, fraction_bound, delta_g


def simulate_tm_gradient(
    primer_sequence: str,
    primer_name: str = "Primer",
    template_name: Optional[str] = None,
    config: Optional[TmGradientConfig] = None
) -> TmGradientResult:
    """
    Simulate Tm gradient for a primer sequence.
    
    Args:
        primer_sequence: Primer sequence (5' to 3')
        primer_name: Name for identification
        template_name: Optional template name
        config: Gradient configuration
        
    Returns:
        TmGradientResult with data points and analysis
    """
    if config is None:
        config = TmGradientConfig()
    
    # Calculate base Tm and thermodynamic parameters
    tm, delta_h, delta_s = calculate_tm_nearest_neighbor(
        primer_sequence,
        na_conc=config.na_concentration,
        primer_conc=config.primer_concentration
    )
    
    # Simulate efficiency at each temperature
    data_points = []
    temps = config.temperature_range
    
    for temp in temps:
        efficiency, fraction, delta_g = calculate_binding_efficiency(
            temp, tm, delta_h, delta_s
        )
        
        data_points.append(TmDataPoint(
            temperature=temp,
            binding_efficiency=min(100.0, max(0.0, efficiency)),
            fraction_bound=min(1.0, max(0.0, fraction)),
            delta_g=delta_g
        ))
    
    # Find optimal annealing temperature (highest efficiency below Tm)
    optimal_temp = tm - 5.0  # Rule of thumb: 5°C below Tm
    
    # Adjust based on actual efficiency curve
    best_temp = optimal_temp
    best_efficiency = 0.0
    for dp in data_points:
        if dp.temperature < tm and dp.binding_efficiency > best_efficiency:
            best_efficiency = dp.binding_efficiency
            best_temp = dp.temperature
    
    # Calculate recommended range (where efficiency > 80%)
    high_eff_temps = [dp.temperature for dp in data_points if dp.binding_efficiency >= 80]
    if high_eff_temps:
        recommended = (min(high_eff_temps), max(high_eff_temps))
    else:
        recommended = (optimal_temp - 3, optimal_temp + 3)
    
    # Check for warnings
    warnings = []
    if tm < 50:
        warnings.append(f"Very low Tm ({tm:.1f}°C) - primer may have poor specificity")
    if tm > 72:
        warnings.append(f"High Tm ({tm:.1f}°C) - consider redesigning primer")
    
    # Assign grade based on Tm and efficiency curve
    if 55 <= tm <= 68 and best_efficiency >= 95:
        grade = "A"
    elif 50 <= tm <= 72 and best_efficiency >= 85:
        grade = "B"
    elif best_efficiency >= 70:
        grade = "C"
    else:
        grade = "D"
    
    return TmGradientResult(
        primer_name=primer_name,
        primer_sequence=primer_sequence,
        template_name=template_name,
        calculated_tm=tm,
        optimal_annealing_temp=best_temp,
        recommended_range=recommended,
        data_points=data_points,
        grade=grade,
        warnings=warnings
    )
