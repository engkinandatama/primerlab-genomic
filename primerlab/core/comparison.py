"""
PrimerLab Primer Comparison Tool

v0.1.5: Compare two primer pairs side-by-side with pros/cons analysis.

This module follows the architecture rules:
- Core layer module (workflow-agnostic)
- No imports from workflows or CLI
"""

from typing import Dict, Any, List, Optional, Tuple
from primerlab.core.logger import get_logger

logger = get_logger()


# Optimal ranges for comparison metrics
OPTIMAL_RANGES = {
    "tm": {"min": 57.0, "max": 63.0, "optimal": 60.0},
    "gc": {"min": 40.0, "max": 60.0, "optimal": 50.0},
    "hairpin_dg": {"max": -3.0, "good": -6.0},  # Less negative is better
    "homodimer_dg": {"max": -6.0, "good": -9.0},  # Less negative is better
    "quality_score": {"min": 70, "excellent": 85}
}


def compare_primers(
    primer_a: Dict[str, Any],
    primer_b: Dict[str, Any],
    labels: Tuple[str, str] = ("A", "B")
) -> Dict[str, Any]:
    """
    Compare two primer pairs and return comprehensive analysis.
    
    Args:
        primer_a: First primer result dict (from result.json)
        primer_b: Second primer result dict (from result.json)
        labels: Labels for the two primers (default: ("A", "B"))
        
    Returns:
        Dict containing:
        - winner: "A" | "B" | "tie"
        - scores: {a: float, b: float}
        - comparison_table: List of metric comparisons
        - pros_cons: {a: {pros: [], cons: []}, b: {pros: [], cons: []}}
    """
    label_a, label_b = labels

    # Extract key metrics from each result
    metrics_a = _extract_metrics(primer_a)
    metrics_b = _extract_metrics(primer_b)

    # Build comparison table
    comparison_table = _build_comparison_table(metrics_a, metrics_b, labels)

    # Determine pros/cons for each
    pros_cons_a = _analyze_pros_cons(metrics_a)
    pros_cons_b = _analyze_pros_cons(metrics_b)

    # Calculate overall scores
    score_a = _calculate_comparison_score(metrics_a)
    score_b = _calculate_comparison_score(metrics_b)

    # Determine winner
    if abs(score_a - score_b) < 5:  # Within 5 points = tie
        winner = "tie"
    elif score_a > score_b:
        winner = label_a
    else:
        winner = label_b

    return {
        "winner": winner,
        "scores": {label_a: score_a, label_b: score_b},
        "comparison_table": comparison_table,
        "pros_cons": {
            label_a: pros_cons_a,
            label_b: pros_cons_b
        },
        "metrics": {
            label_a: metrics_a,
            label_b: metrics_b
        }
    }


def _extract_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key metrics from a workflow result."""
    metrics = {
        "quality_score": None,
        "fwd_tm": None,
        "rev_tm": None,
        "tm_balance": None,
        "fwd_gc": None,
        "rev_gc": None,
        "fwd_hairpin_dg": None,
        "rev_hairpin_dg": None,
        "fwd_homodimer_dg": None,
        "rev_homodimer_dg": None,
        "product_size": None,
        "fwd_sequence": None,
        "rev_sequence": None
    }

    # Handle different input structures
    primers = result.get("primers", {})
    qc = result.get("qc", {})
    amplicons = result.get("amplicons", [])

    # QC data
    if qc:
        metrics["quality_score"] = qc.get("quality_score")

    # Forward primer
    fwd = primers.get("forward", {})
    if fwd:
        metrics["fwd_tm"] = fwd.get("tm")
        metrics["fwd_gc"] = fwd.get("gc")
        metrics["fwd_hairpin_dg"] = fwd.get("hairpin_dg", 0.0)
        metrics["fwd_homodimer_dg"] = fwd.get("homodimer_dg", 0.0)
        metrics["fwd_sequence"] = fwd.get("sequence")

    # Reverse primer
    rev = primers.get("reverse", {})
    if rev:
        metrics["rev_tm"] = rev.get("tm")
        metrics["rev_gc"] = rev.get("gc")
        metrics["rev_hairpin_dg"] = rev.get("hairpin_dg", 0.0)
        metrics["rev_homodimer_dg"] = rev.get("homodimer_dg", 0.0)
        metrics["rev_sequence"] = rev.get("sequence")

    # Tm balance
    if metrics["fwd_tm"] and metrics["rev_tm"]:
        metrics["tm_balance"] = abs(metrics["fwd_tm"] - metrics["rev_tm"])

    # Amplicon
    if amplicons:
        metrics["product_size"] = amplicons[0].get("length")

    return metrics


def _build_comparison_table(
    metrics_a: Dict, 
    metrics_b: Dict,
    labels: Tuple[str, str]
) -> List[Dict]:
    """Build a comparison table of all metrics."""
    label_a, label_b = labels
    table = []

    comparison_items = [
        ("Quality Score", "quality_score", "higher", None),
        ("Forward Tm", "fwd_tm", "closer_to_60", "°C"),
        ("Reverse Tm", "rev_tm", "closer_to_60", "°C"),
        ("Tm Balance (Δ)", "tm_balance", "lower", "°C"),
        ("Forward GC", "fwd_gc", "closer_to_50", "%"),
        ("Reverse GC", "rev_gc", "closer_to_50", "%"),
        ("Fwd Hairpin ΔG", "fwd_hairpin_dg", "higher", "kcal/mol"),
        ("Rev Hairpin ΔG", "rev_hairpin_dg", "higher", "kcal/mol"),
        ("Product Size", "product_size", "info", "bp"),
    ]

    for name, key, comparison_type, unit in comparison_items:
        val_a = metrics_a.get(key)
        val_b = metrics_b.get(key)

        # Determine which is better
        better = _determine_better(val_a, val_b, comparison_type)

        # Format values
        fmt_a = _format_value(val_a, unit)
        fmt_b = _format_value(val_b, unit)

        table.append({
            "metric": name,
            label_a: fmt_a,
            label_b: fmt_b,
            "better": better,
            "unit": unit
        })

    return table


def _determine_better(val_a, val_b, comparison_type: str) -> str:
    """Determine which value is better based on comparison type."""
    if val_a is None and val_b is None:
        return "tie"
    if val_a is None:
        return "B"
    if val_b is None:
        return "A"

    if comparison_type == "higher":
        if val_a > val_b:
            return "A"
        elif val_b > val_a:
            return "B"
        return "tie"

    elif comparison_type == "lower":
        if val_a < val_b:
            return "A"
        elif val_b < val_a:
            return "B"
        return "tie"

    elif comparison_type == "closer_to_60":
        diff_a = abs(val_a - 60.0)
        diff_b = abs(val_b - 60.0)
        if diff_a < diff_b:
            return "A"
        elif diff_b < diff_a:
            return "B"
        return "tie"

    elif comparison_type == "closer_to_50":
        diff_a = abs(val_a - 50.0)
        diff_b = abs(val_b - 50.0)
        if diff_a < diff_b:
            return "A"
        elif diff_b < diff_a:
            return "B"
        return "tie"

    return "tie"


def _format_value(value, unit: Optional[str]) -> str:
    """Format a value with unit for display."""
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)


def _analyze_pros_cons(metrics: Dict) -> Dict[str, List[str]]:
    """Analyze pros and cons based on metrics."""
    pros = []
    cons = []

    # Quality Score
    qs = metrics.get("quality_score")
    if qs is not None:
        if qs >= 85:
            pros.append(f"Excellent quality score ({qs})")
        elif qs >= 70:
            pros.append(f"Good quality score ({qs})")
        elif qs < 50:
            cons.append(f"Poor quality score ({qs})")

    # Tm Balance
    tm_bal = metrics.get("tm_balance")
    if tm_bal is not None:
        if tm_bal <= 1.0:
            pros.append(f"Excellent Tm balance (Δ{tm_bal:.1f}°C)")
        elif tm_bal > 3.0:
            cons.append(f"Poor Tm balance (Δ{tm_bal:.1f}°C)")

    # GC Content
    for which, key in [("Forward", "fwd_gc"), ("Reverse", "rev_gc")]:
        gc = metrics.get(key)
        if gc is not None:
            if 45 <= gc <= 55:
                pros.append(f"{which} primer has optimal GC ({gc:.0f}%)")
            elif gc < 35 or gc > 65:
                cons.append(f"{which} primer has suboptimal GC ({gc:.0f}%)")

    # Hairpin
    for which, key in [("Forward", "fwd_hairpin_dg"), ("Reverse", "rev_hairpin_dg")]:
        dg = metrics.get(key)
        if dg is not None and dg < -6.0:
            cons.append(f"{which} has strong hairpin (ΔG={dg:.1f})")

    # Homodimer
    for which, key in [("Forward", "fwd_homodimer_dg"), ("Reverse", "rev_homodimer_dg")]:
        dg = metrics.get(key)
        if dg is not None and dg < -9.0:
            cons.append(f"{which} has strong homodimer (ΔG={dg:.1f})")

    return {"pros": pros, "cons": cons}


def _calculate_comparison_score(metrics: Dict) -> float:
    """Calculate overall comparison score (0-100)."""
    score = 50.0  # Start at neutral

    # Quality score component (0-40 points)
    qs = metrics.get("quality_score")
    if qs is not None:
        score += (qs - 50) * 0.4  # Scale quality score contribution

    # Tm balance component (0-15 points)
    tm_bal = metrics.get("tm_balance")
    if tm_bal is not None:
        if tm_bal <= 1.0:
            score += 15
        elif tm_bal <= 2.0:
            score += 10
        elif tm_bal <= 3.0:
            score += 5

    # GC optimality (0-10 points)
    for key in ["fwd_gc", "rev_gc"]:
        gc = metrics.get(key)
        if gc is not None:
            deviation = abs(gc - 50)
            if deviation <= 5:
                score += 5
            elif deviation <= 10:
                score += 2

    # Hairpin penalty (-10 points each)
    for key in ["fwd_hairpin_dg", "rev_hairpin_dg"]:
        dg = metrics.get(key)
        if dg is not None and dg < -6.0:
            score -= 10

    return max(0, min(100, score))


def format_comparison_for_cli(result: Dict[str, Any], labels: Tuple[str, str] = ("A", "B")) -> str:
    """
    Format comparison result for CLI output.
    
    Args:
        result: Output from compare_primers()
        labels: Labels used for comparison
        
    Returns:
        Formatted string for terminal display
    """
    label_a, label_b = labels
    lines = []

    lines.append("")
    lines.append("=" * 70)
    lines.append("🔬 PRIMER COMPARISON")
    lines.append("=" * 70)
    lines.append("")

    # Scores and winner
    scores = result["scores"]
    winner = result["winner"]

    lines.append(f"📊 Overall Scores: {label_a}={scores[label_a]:.0f}  vs  {label_b}={scores[label_b]:.0f}")

    if winner == "tie":
        lines.append("🏆 Result: TIE (scores within 5 points)")
    else:
        lines.append(f"🏆 Winner: {winner}")

    lines.append("")
    lines.append("-" * 70)
    lines.append("")

    # Comparison table
    lines.append(f"{'Metric':<25} {label_a:>15} {label_b:>15}  {'Better':>8}")
    lines.append("-" * 70)

    for row in result["comparison_table"]:
        metric = row["metric"]
        val_a = row[label_a]
        val_b = row[label_b]
        better = row["better"]

        # Add indicator for better value
        better_str = "←" if better == "A" else ("→" if better == "B" else "=")

        lines.append(f"{metric:<25} {val_a:>15} {val_b:>15}  {better_str:>8}")

    lines.append("")
    lines.append("-" * 70)
    lines.append("")

    # Pros and Cons
    pros_cons = result["pros_cons"]

    for label in [label_a, label_b]:
        pc = pros_cons[label]
        lines.append(f"📋 {label} Analysis:")

        if pc["pros"]:
            for pro in pc["pros"]:
                lines.append(f"   ✅ {pro}")

        if pc["cons"]:
            for con in pc["cons"]:
                lines.append(f"   ⚠️ {con}")

        if not pc["pros"] and not pc["cons"]:
            lines.append("   No significant notes")

        lines.append("")

    lines.append("=" * 70)

    return "\n".join(lines)


def load_result_json(filepath: str) -> Dict[str, Any]:
    """Load a result.json file for comparison."""
    import json
    from pathlib import Path

    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Result file not found: {filepath}")

    with open(path, 'r') as f:
        return json.load(f)
