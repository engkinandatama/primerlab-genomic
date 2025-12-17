"""
PrimerLab GC Profile Visualization Module

v0.1.5 Priority 6: Advanced visualization for amplicon GC content.

Features:
- Sliding window GC content analysis  
- Primer position highlighting
- Light/Dark mode themes
- Publication-quality output (PNG/SVG)
"""

from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
from primerlab.core.logger import get_logger

logger = get_logger()

# Professional color schemes
THEMES = {
    "light": {
        "background": "#FFFFFF",
        "text": "#1F2937",
        "grid": "#E5E7EB",
        "gc_line": "#3B82F6",  # Blue
        "gc_fill": "#93C5FD",  # Light blue
        "primer_fwd": "#10B981",  # Green
        "primer_rev": "#EF4444",  # Red
        "probe": "#8B5CF6",  # Purple
        "threshold_high": "#FCD34D",  # Yellow
        "threshold_low": "#FCD34D",
        "title": "#111827",
        "spine": "#D1D5DB",
    },
    "dark": {
        "background": "#0F172A",  # Slate 900
        "text": "#E2E8F0",  # Slate 200
        "grid": "#334155",  # Slate 700
        "gc_line": "#60A5FA",  # Blue 400
        "gc_fill": "#1E3A5F",  # Blue dark
        "primer_fwd": "#34D399",  # Green 400
        "primer_rev": "#F87171",  # Red 400
        "probe": "#A78BFA",  # Purple 400
        "threshold_high": "#FBBF24",  # Yellow 400
        "threshold_low": "#FBBF24",
        "title": "#F8FAFC",  # Slate 50
        "spine": "#475569",  # Slate 600
    }
}


def calculate_gc_profile(sequence: str, window_size: int = 20, step: int = 1) -> Tuple[List[int], List[float]]:
    """
    Calculate GC content across sequence using sliding window.
    
    Args:
        sequence: DNA sequence string
        window_size: Size of sliding window (default: 20bp)
        step: Step size for sliding (default: 1)
        
    Returns:
        Tuple of (positions, gc_percentages)
    """
    positions = []
    gc_values = []
    
    seq_upper = sequence.upper()
    
    for i in range(0, len(seq_upper) - window_size + 1, step):
        window = seq_upper[i:i + window_size]
        gc_count = window.count('G') + window.count('C')
        gc_percent = (gc_count / window_size) * 100
        
        # Position is center of window
        positions.append(i + window_size // 2)
        gc_values.append(gc_percent)
    
    return positions, gc_values


def plot_gc_profile(
    sequence: str,
    primer_fwd: Optional[Dict[str, Any]] = None,
    primer_rev: Optional[Dict[str, Any]] = None,
    probe: Optional[Dict[str, Any]] = None,
    amplicon_start: int = 0,
    amplicon_end: Optional[int] = None,
    window_size: int = 20,
    theme: str = "light",
    output_path: Optional[str] = None,
    title: str = "GC Content Profile",
    show_thresholds: bool = True,
    figsize: Tuple[int, int] = (12, 6),
    dpi: int = 150
) -> Optional[str]:
    """
    Generate professional GC content profile plot.
    
    Args:
        sequence: DNA sequence to analyze
        primer_fwd: Forward primer dict with 'start', 'end', 'sequence'
        primer_rev: Reverse primer dict with 'start', 'end', 'sequence'
        probe: Probe dict (for qPCR)
        amplicon_start: Start position of amplicon in sequence
        amplicon_end: End position of amplicon
        window_size: Sliding window size
        theme: 'light' or 'dark'
        output_path: Path to save plot (PNG/SVG)
        title: Plot title
        show_thresholds: Show ideal GC range (40-60%)
        figsize: Figure size (width, height)
        dpi: Resolution for PNG output
        
    Returns:
        Path to saved plot, or None if display only
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib.ticker import MultipleLocator
    except ImportError:
        logger.warning("matplotlib not installed. Run: pip install matplotlib")
        return None
    
    # Get theme colors
    colors = THEMES.get(theme, THEMES["light"])
    
    # Calculate GC profile
    if amplicon_end is None:
        amplicon_end = len(sequence)
    
    amplicon_seq = sequence[amplicon_start:amplicon_end]
    positions, gc_values = calculate_gc_profile(amplicon_seq, window_size)
    
    # Adjust positions to absolute coordinates
    positions = [p + amplicon_start for p in positions]
    
    # Create figure with custom style
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=figsize, facecolor=colors["background"])
    ax.set_facecolor(colors["background"])
    
    # Plot GC content line with fill
    ax.fill_between(positions, 0, gc_values, 
                    color=colors["gc_fill"], alpha=0.4, label='_nolegend_')
    ax.plot(positions, gc_values, 
            color=colors["gc_line"], linewidth=2.5, label='GC Content')
    
    # Ideal GC range thresholds
    if show_thresholds:
        ax.axhline(y=60, color=colors["threshold_high"], 
                   linestyle='--', linewidth=1.5, alpha=0.7, label='Ideal Range (40-60%)')
        ax.axhline(y=40, color=colors["threshold_low"], 
                   linestyle='--', linewidth=1.5, alpha=0.7, label='_nolegend_')
        
        # Shade ideal zone
        ax.axhspan(40, 60, color=colors["gc_fill"], alpha=0.1)
    
    # Plot primer positions
    legend_handles = []
    
    if primer_fwd:
        fwd_start = primer_fwd.get('start', 0)
        fwd_end = primer_fwd.get('end', fwd_start + 20)
        ax.axvspan(fwd_start, fwd_end, color=colors["primer_fwd"], 
                   alpha=0.3, label='_nolegend_')
        ax.axvline(x=fwd_start, color=colors["primer_fwd"], 
                   linewidth=2, linestyle='-', label='Forward Primer')
        ax.axvline(x=fwd_end, color=colors["primer_fwd"], 
                   linewidth=2, linestyle='-', label='_nolegend_')
        legend_handles.append(mpatches.Patch(
            color=colors["primer_fwd"], alpha=0.5, label='Forward Primer'))
    
    if primer_rev:
        rev_start = primer_rev.get('start', len(sequence) - 20)
        rev_end = primer_rev.get('end', len(sequence))
        ax.axvspan(rev_start, rev_end, color=colors["primer_rev"], 
                   alpha=0.3, label='_nolegend_')
        ax.axvline(x=rev_start, color=colors["primer_rev"], 
                   linewidth=2, linestyle='-', label='_nolegend_')
        ax.axvline(x=rev_end, color=colors["primer_rev"], 
                   linewidth=2, linestyle='-', label='_nolegend_')
        legend_handles.append(mpatches.Patch(
            color=colors["primer_rev"], alpha=0.5, label='Reverse Primer'))
    
    if probe:
        probe_start = probe.get('start', 0)
        probe_end = probe.get('end', probe_start + 20)
        ax.axvspan(probe_start, probe_end, color=colors["probe"], 
                   alpha=0.3, label='_nolegend_')
        legend_handles.append(mpatches.Patch(
            color=colors["probe"], alpha=0.5, label='Probe'))
    
    # Styling
    ax.set_xlabel('Position (bp)', fontsize=12, fontweight='medium', color=colors["text"])
    ax.set_ylabel('GC Content (%)', fontsize=12, fontweight='medium', color=colors["text"])
    ax.set_title(title, fontsize=14, fontweight='bold', color=colors["title"], pad=15)
    
    # Set axis limits
    ax.set_ylim(0, 100)
    ax.set_xlim(min(positions) - 10, max(positions) + 10)
    
    # Grid styling
    ax.grid(True, linestyle='-', alpha=0.3, color=colors["grid"])
    ax.yaxis.set_major_locator(MultipleLocator(20))
    
    # Spine styling
    for spine in ax.spines.values():
        spine.set_color(colors["spine"])
        spine.set_linewidth(1)
    
    # Tick styling
    ax.tick_params(colors=colors["text"], labelsize=10)
    
    # Legend
    gc_line = plt.Line2D([0], [0], color=colors["gc_line"], linewidth=2.5, label='GC Content')
    threshold_line = plt.Line2D([0], [0], color=colors["threshold_high"], 
                                linewidth=1.5, linestyle='--', label='Ideal Range')
    
    all_handles = [gc_line, threshold_line] + legend_handles
    ax.legend(handles=all_handles, loc='upper right', 
              framealpha=0.9, facecolor=colors["background"],
              edgecolor=colors["spine"], labelcolor=colors["text"])
    
    # Tight layout
    plt.tight_layout()
    
    # Save or show
    if output_path:
        path = Path(output_path)
        plt.savefig(path, dpi=dpi, facecolor=colors["background"], 
                    edgecolor='none', bbox_inches='tight')
        plt.close()
        logger.info(f"GC profile plot saved to: {path}")
        return str(path)
    else:
        plt.show()
        return None


def generate_gc_profile_from_result(
    result: Dict[str, Any],
    sequence: str,
    output_dir: str,
    theme: str = "light"
) -> Optional[str]:
    """
    Generate GC profile plot from workflow result.
    
    Args:
        result: WorkflowResult as dict
        sequence: Original DNA sequence
        output_dir: Directory to save plot
        theme: 'light' or 'dark'
        
    Returns:
        Path to saved plot
    """
    primers = result.get("primers", {})
    amplicons = result.get("amplicons", [])
    
    if not amplicons:
        logger.warning("No amplicons found, cannot generate GC profile")
        return None
    
    amplicon = amplicons[0]
    
    primer_fwd = None
    primer_rev = None
    probe = None
    
    if "forward" in primers:
        fwd = primers["forward"]
        primer_fwd = {
            "start": fwd.get("start", 0),
            "end": fwd.get("end", 0),
            "sequence": fwd.get("sequence", "")
        }
    
    if "reverse" in primers:
        rev = primers["reverse"]
        primer_rev = {
            "start": rev.get("start", 0),
            "end": rev.get("end", 0),
            "sequence": rev.get("sequence", "")
        }
    
    if "probe" in primers:
        prb = primers["probe"]
        probe = {
            "start": prb.get("start", 0),
            "end": prb.get("end", 0),
            "sequence": prb.get("sequence", "")
        }
    
    output_path = Path(output_dir) / f"gc_profile_{theme}.png"
    
    return plot_gc_profile(
        sequence=sequence,
        primer_fwd=primer_fwd,
        primer_rev=primer_rev,
        probe=probe,
        amplicon_start=amplicon.get("start", 0),
        amplicon_end=amplicon.get("end", len(sequence)),
        theme=theme,
        output_path=str(output_path),
        title=f"GC Content Profile - {result.get('workflow', 'PCR').upper()}"
    )
