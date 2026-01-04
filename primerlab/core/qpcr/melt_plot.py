"""
Melt Curve Visualization (v0.6.0).

Generates SVG and PNG plots of melt curves for SYBR Green qPCR.
"""

from typing import List, Dict, Optional, Tuple
from pathlib import Path
import math


def generate_melt_svg(
    melt_curve: List[Dict[str, float]],
    peaks: List[Dict],
    predicted_tm: float,
    output_path: Optional[str] = None,
    width: int = 600,
    height: int = 400,
    title: str = "Melt Curve Analysis",
) -> str:
    """
    Generate SVG melt curve plot.
    
    Args:
        melt_curve: List of {temperature, derivative} points
        peaks: List of peak dictionaries
        predicted_tm: Primary Tm value
        output_path: Optional file path to save SVG
        width: Plot width in pixels
        height: Plot height in pixels
        title: Plot title
        
    Returns:
        SVG string
    """
    if not melt_curve:
        return ""

    # Margins
    margin_left = 60
    margin_right = 30
    margin_top = 50
    margin_bottom = 50

    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    # Data ranges
    temps = [p["temperature"] for p in melt_curve]
    derivs = [p["derivative"] for p in melt_curve]

    temp_min, temp_max = min(temps), max(temps)
    deriv_min, deriv_max = min(derivs), max(derivs)

    # Scaling functions
    def scale_x(temp):
        return margin_left + (temp - temp_min) / (temp_max - temp_min) * plot_width

    def scale_y(deriv):
        if deriv_max == deriv_min:
            return margin_top + plot_height / 2
        return margin_top + plot_height - (deriv - deriv_min) / (deriv_max - deriv_min) * plot_height

    # Build SVG
    svg_parts = []

    # Header
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
    <style>
        .title {{ font: bold 16px sans-serif; fill: #333; }}
        .axis-label {{ font: 12px sans-serif; fill: #666; }}
        .tick-label {{ font: 10px sans-serif; fill: #666; }}
        .curve {{ fill: none; stroke: #2563eb; stroke-width: 2; }}
        .peak-line {{ stroke: #dc2626; stroke-width: 1; stroke-dasharray: 4,2; }}
        .peak-label {{ font: bold 11px sans-serif; fill: #dc2626; }}
        .tm-label {{ font: 12px sans-serif; fill: #059669; }}
        .grid {{ stroke: #e5e7eb; stroke-width: 1; }}
    </style>
    
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="white"/>
    
    <!-- Title -->
    <text x="{width/2}" y="25" class="title" text-anchor="middle">{title}</text>
''')

    # Grid lines
    for i in range(5):
        y = margin_top + i * plot_height / 4
        svg_parts.append(f'    <line x1="{margin_left}" y1="{y}" x2="{width-margin_right}" y2="{y}" class="grid"/>\n')

    # X-axis
    svg_parts.append(f'    <line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{width-margin_right}" y2="{margin_top + plot_height}" stroke="#333" stroke-width="1"/>\n')

    # Y-axis
    svg_parts.append(f'    <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" stroke="#333" stroke-width="1"/>\n')

    # X-axis ticks and labels
    for i in range(6):
        temp = temp_min + i * (temp_max - temp_min) / 5
        x = scale_x(temp)
        svg_parts.append(f'    <line x1="{x}" y1="{margin_top + plot_height}" x2="{x}" y2="{margin_top + plot_height + 5}" stroke="#333"/>\n')
        svg_parts.append(f'    <text x="{x}" y="{margin_top + plot_height + 18}" class="tick-label" text-anchor="middle">{temp:.0f}°C</text>\n')

    # X-axis label
    svg_parts.append(f'    <text x="{width/2}" y="{height - 10}" class="axis-label" text-anchor="middle">Temperature (°C)</text>\n')

    # Y-axis label
    svg_parts.append(f'    <text x="15" y="{height/2}" class="axis-label" text-anchor="middle" transform="rotate(-90 15 {height/2})">-dF/dT</text>\n')

    # Melt curve path
    path_points = []
    for point in melt_curve:
        x = scale_x(point["temperature"])
        y = scale_y(point["derivative"])
        path_points.append(f"{x:.1f},{y:.1f}")

    path_d = "M " + " L ".join(path_points)
    svg_parts.append(f'    <path d="{path_d}" class="curve"/>\n')

    # Peak annotations
    for i, peak in enumerate(peaks):
        temp = peak.get("temperature", predicted_tm)
        x = scale_x(temp)

        # Vertical line at peak
        svg_parts.append(f'    <line x1="{x}" y1="{margin_top}" x2="{x}" y2="{margin_top + plot_height}" class="peak-line"/>\n')

        # Peak label
        label = "Tm" if peak.get("is_primary", i == 0) else f"Peak {i+1}"
        svg_parts.append(f'    <text x="{x + 5}" y="{margin_top + 15}" class="peak-label">{label}: {temp:.1f}°C</text>\n')

    # Primary Tm annotation (if not already shown)
    if not peaks:
        x = scale_x(predicted_tm)
        svg_parts.append(f'    <line x1="{x}" y1="{margin_top}" x2="{x}" y2="{margin_top + plot_height}" class="peak-line"/>\n')
        svg_parts.append(f'    <text x="{x + 5}" y="{margin_top + 15}" class="tm-label">Tm: {predicted_tm:.1f}°C</text>\n')

    svg_parts.append('</svg>')

    svg_content = "\n".join(svg_parts)

    # Save to file if path provided
    if output_path:
        with open(output_path, 'w') as f:
            f.write(svg_content)

    return svg_content


def generate_melt_png(
    melt_curve: List[Dict[str, float]],
    peaks: List[Dict],
    predicted_tm: float,
    output_path: str,
    width: int = 8,
    height: int = 6,
    dpi: int = 100,
    title: str = "Melt Curve Analysis",
) -> bool:
    """
    Generate PNG melt curve plot using matplotlib.
    
    Args:
        melt_curve: List of {temperature, derivative} points
        peaks: List of peak dictionaries
        predicted_tm: Primary Tm value
        output_path: File path to save PNG
        width: Figure width in inches
        height: Figure height in inches
        dpi: Resolution
        title: Plot title
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
    except ImportError:
        return False

    if not melt_curve:
        return False

    temps = [p["temperature"] for p in melt_curve]
    derivs = [p["derivative"] for p in melt_curve]

    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)

    # Plot curve
    ax.plot(temps, derivs, 'b-', linewidth=2, label='Melt curve')

    # Mark peaks
    for i, peak in enumerate(peaks):
        temp = peak.get("temperature", predicted_tm)
        # Find derivative at this temperature
        idx = min(range(len(temps)), key=lambda i: abs(temps[i] - temp))
        deriv = derivs[idx]

        color = 'red' if peak.get("is_primary", i == 0) else 'orange'
        label = f'Tm: {temp:.1f}°C' if peak.get("is_primary", i == 0) else f'Peak {i+1}: {temp:.1f}°C'

        ax.axvline(x=temp, color=color, linestyle='--', alpha=0.7)
        ax.scatter([temp], [deriv], color=color, s=50, zorder=5)
        ax.annotate(label, xy=(temp, deriv), xytext=(5, 10),
                   textcoords='offset points', fontsize=9, color=color)

    # If no peaks, mark primary Tm
    if not peaks:
        idx = min(range(len(temps)), key=lambda i: abs(temps[i] - predicted_tm))
        deriv = derivs[idx]
        ax.axvline(x=predicted_tm, color='green', linestyle='--', alpha=0.7)
        ax.scatter([predicted_tm], [deriv], color='green', s=50, zorder=5)
        ax.annotate(f'Tm: {predicted_tm:.1f}°C', xy=(predicted_tm, deriv),
                   xytext=(5, 10), textcoords='offset points', fontsize=9, color='green')

    ax.set_xlabel('Temperature (°C)', fontsize=11)
    ax.set_ylabel('-dF/dT', fontsize=11)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)

    return True


def annotate_peaks(
    peaks: List[Dict],
    is_single_peak: bool,
) -> List[str]:
    """
    Generate text annotations for peaks.
    
    Args:
        peaks: List of peak dictionaries
        is_single_peak: Whether curve has single peak
        
    Returns:
        List of annotation strings
    """
    annotations = []

    if is_single_peak:
        annotations.append("✓ Single peak detected - specific amplification")
    else:
        annotations.append("⚠ Multiple peaks detected - check for non-specific products")

    for i, peak in enumerate(peaks):
        temp = peak.get("temperature", 0)
        is_primary = peak.get("is_primary", i == 0)

        if is_primary:
            annotations.append(f"Primary Tm: {temp:.1f}°C")
        else:
            annotations.append(f"Secondary peak at {temp:.1f}°C")

    return annotations
