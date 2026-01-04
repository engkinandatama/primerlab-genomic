"""
PrimerLab Auto Parameter Suggestion Engine

v0.1.5: Analyzes Primer3 failure reasons and suggests parameter relaxations.

This module follows the architecture rules:
- Core layer module (workflow-agnostic)
- No imports from workflows or CLI
"""

from typing import Dict, Any, List, Optional
from primerlab.core.logger import get_logger

logger = get_logger()


# Suggestion rules based on common failure patterns
RELAXATION_RULES = {
    "tm": {
        "description": "Widen melting temperature range",
        "adjustment": {"min": -2.0, "max": +2.0},
        "triggers": ["too few", "tm constraint", "melting temperature"]
    },
    "gc": {
        "description": "Relax GC content constraints",
        "adjustment": {"min": -10.0, "max": +10.0},
        "triggers": ["gc content", "gc%", "gc constraint"]
    },
    "product_size": {
        "description": "Widen product size range",
        "adjustment": {"min": -50, "max": +50},
        "triggers": ["product size", "too short", "too long", "size constraint"]
    },
    "primer_size": {
        "description": "Widen primer length range",
        "adjustment": {"min": -2, "max": +2},
        "triggers": ["primer length", "oligo size", "too few"]
    },
    "probe_tm": {
        "description": "Relax probe Tm constraints (qPCR)",
        "adjustment": {"min": -3.0, "max": +2.0},
        "triggers": ["internal oligo", "probe", "hyb probe"]
    }
}


def analyze_failure(error_details: Dict[str, Any]) -> List[str]:
    """
    Analyze Primer3 failure reasons and identify which constraints caused issues.
    
    Args:
        error_details: Dict containing left_explain, right_explain, pair_explain
        
    Returns:
        List of constraint categories that likely caused the failure
    """
    problem_areas = []

    # Combine all explain texts
    explains = [
        str(error_details.get("left_explain", "")).lower(),
        str(error_details.get("right_explain", "")).lower(),
        str(error_details.get("pair_explain", "")).lower()
    ]
    combined_text = " ".join(explains)

    # Check each rule's triggers
    for category, rule in RELAXATION_RULES.items():
        for trigger in rule["triggers"]:
            if trigger in combined_text:
                if category not in problem_areas:
                    problem_areas.append(category)
                break

    # If no specific issues found, suggest general relaxations
    if not problem_areas:
        problem_areas = ["tm", "gc", "product_size"]

    return problem_areas


def suggest_relaxed_parameters(
    config: Dict[str, Any],
    error_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate parameter relaxation suggestions based on failure analysis.
    
    Args:
        config: Current workflow configuration
        error_details: Optional dict with Primer3 explain strings
        
    Returns:
        Dict containing:
        - suggestions: List of specific parameter changes
        - relaxed_config: Ready-to-use relaxed config
        - explanation: Human-readable explanation
    """
    params = config.get("parameters", {})
    workflow = config.get("workflow", "pcr")

    # Analyze what caused the failure
    if error_details:
        problem_areas = analyze_failure(error_details)
    else:
        # Default: suggest all common relaxations
        problem_areas = ["tm", "gc", "product_size"]

    suggestions = []
    relaxed_params = _deep_copy(params)

    # Generate suggestions for each problem area
    for area in problem_areas:
        if area == "tm":
            suggestion = _suggest_tm_relaxation(params, relaxed_params)
            if suggestion:
                suggestions.append(suggestion)

        elif area == "gc":
            suggestion = _suggest_gc_relaxation(params, relaxed_params)
            if suggestion:
                suggestions.append(suggestion)

        elif area == "product_size":
            suggestion = _suggest_product_size_relaxation(params, relaxed_params)
            if suggestion:
                suggestions.append(suggestion)

        elif area == "primer_size":
            suggestion = _suggest_primer_size_relaxation(params, relaxed_params)
            if suggestion:
                suggestions.append(suggestion)

        elif area == "probe_tm" and workflow == "qpcr":
            suggestion = _suggest_probe_tm_relaxation(params, relaxed_params)
            if suggestion:
                suggestions.append(suggestion)

    # Build relaxed config
    relaxed_config = _deep_copy(config)
    relaxed_config["parameters"] = relaxed_params

    # Generate explanation
    explanation = _generate_explanation(suggestions)

    return {
        "suggestions": suggestions,
        "relaxed_config": relaxed_config,
        "explanation": explanation,
        "problem_areas": problem_areas
    }


def _suggest_tm_relaxation(params: Dict, relaxed: Dict) -> Optional[Dict]:
    """Suggest Tm range relaxation."""
    tm = params.get("tm", {})
    current_min = tm.get("min", 57.0)
    current_max = tm.get("max", 63.0)

    adj = RELAXATION_RULES["tm"]["adjustment"]
    new_min = current_min + adj["min"]
    new_max = current_max + adj["max"]

    # Apply to relaxed params
    if "tm" not in relaxed:
        relaxed["tm"] = {}
    relaxed["tm"]["min"] = new_min
    relaxed["tm"]["max"] = new_max

    return {
        "parameter": "tm",
        "current": f"{current_min}°C - {current_max}°C",
        "suggested": f"{new_min}°C - {new_max}°C",
        "description": RELAXATION_RULES["tm"]["description"]
    }


def _suggest_gc_relaxation(params: Dict, relaxed: Dict) -> Optional[Dict]:
    """Suggest GC content relaxation."""
    gc = params.get("gc", {})
    current_min = gc.get("min", 40.0)
    current_max = gc.get("max", 60.0)

    adj = RELAXATION_RULES["gc"]["adjustment"]
    new_min = max(20.0, current_min + adj["min"])  # Don't go below 20%
    new_max = min(80.0, current_max + adj["max"])  # Don't go above 80%

    if "gc" not in relaxed:
        relaxed["gc"] = {}
    relaxed["gc"]["min"] = new_min
    relaxed["gc"]["max"] = new_max

    return {
        "parameter": "gc",
        "current": f"{current_min}% - {current_max}%",
        "suggested": f"{new_min}% - {new_max}%",
        "description": RELAXATION_RULES["gc"]["description"]
    }


def _suggest_product_size_relaxation(params: Dict, relaxed: Dict) -> Optional[Dict]:
    """Suggest product size range relaxation."""
    size_range = params.get("product_size_range", [[75, 300]])

    if size_range and len(size_range) > 0:
        current_min = size_range[0][0]
        current_max = size_range[0][1]

        adj = RELAXATION_RULES["product_size"]["adjustment"]
        new_min = max(50, current_min + adj["min"])  # Don't go below 50bp
        new_max = current_max + adj["max"]

        relaxed["product_size_range"] = [[new_min, new_max]]

        return {
            "parameter": "product_size_range",
            "current": f"{current_min}bp - {current_max}bp",
            "suggested": f"{new_min}bp - {new_max}bp",
            "description": RELAXATION_RULES["product_size"]["description"]
        }
    return None


def _suggest_primer_size_relaxation(params: Dict, relaxed: Dict) -> Optional[Dict]:
    """Suggest primer size relaxation."""
    size = params.get("primer_size", {})
    current_min = size.get("min", 18)
    current_max = size.get("max", 27)

    adj = RELAXATION_RULES["primer_size"]["adjustment"]
    new_min = max(15, current_min + adj["min"])
    new_max = min(35, current_max + adj["max"])

    if "primer_size" not in relaxed:
        relaxed["primer_size"] = {}
    relaxed["primer_size"]["min"] = new_min
    relaxed["primer_size"]["max"] = new_max

    return {
        "parameter": "primer_size",
        "current": f"{current_min}nt - {current_max}nt",
        "suggested": f"{new_min}nt - {new_max}nt",
        "description": RELAXATION_RULES["primer_size"]["description"]
    }


def _suggest_probe_tm_relaxation(params: Dict, relaxed: Dict) -> Optional[Dict]:
    """Suggest probe Tm relaxation for qPCR."""
    probe = params.get("probe", {})
    if not probe:
        return None

    probe_tm = probe.get("tm", {})
    current_min = probe_tm.get("min", 68.0)
    current_max = probe_tm.get("max", 72.0)

    adj = RELAXATION_RULES["probe_tm"]["adjustment"]
    new_min = current_min + adj["min"]
    new_max = current_max + adj["max"]

    if "probe" not in relaxed:
        relaxed["probe"] = {}
    if "tm" not in relaxed["probe"]:
        relaxed["probe"]["tm"] = {}
    relaxed["probe"]["tm"]["min"] = new_min
    relaxed["probe"]["tm"]["max"] = new_max

    return {
        "parameter": "probe.tm",
        "current": f"{current_min}°C - {current_max}°C",
        "suggested": f"{new_min}°C - {new_max}°C",
        "description": RELAXATION_RULES["probe_tm"]["description"]
    }


def _generate_explanation(suggestions: List[Dict]) -> str:
    """Generate human-readable explanation of suggestions."""
    if not suggestions:
        return "No specific suggestions available. Try using a different sequence region."

    lines = [
        "💡 **Suggested Parameter Relaxations:**",
        ""
    ]

    for i, s in enumerate(suggestions, 1):
        lines.append(f"{i}. **{s['description']}**")
        lines.append(f"   Current: {s['current']} → Suggested: {s['suggested']}")
        lines.append("")

    lines.append("To apply these suggestions, you can:")
    lines.append("  1. Update your config file with the suggested values")
    lines.append("  2. Use `--auto-retry` flag to automatically retry with relaxed parameters")

    return "\n".join(lines)


def _deep_copy(d: Dict) -> Dict:
    """Simple deep copy for nested dicts (avoids external dependency)."""
    import copy
    return copy.deepcopy(d)


def format_suggestions_for_cli(result: Dict[str, Any]) -> str:
    """
    Format suggestion result for CLI output.
    
    Args:
        result: Output from suggest_relaxed_parameters()
        
    Returns:
        Formatted string for terminal display
    """
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("🔧 AUTO PARAMETER SUGGESTION")
    lines.append("=" * 60)
    lines.append("")
    lines.append(result["explanation"])
    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)
