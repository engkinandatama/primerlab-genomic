"""
Amplicon Coverage Map Visualization.

Visualizes primer positions on a sequence with coverage overlays.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from primerlab.core.logger import get_logger

logger = get_logger()


@dataclass
class PrimerRegion:
    """A primer region on the sequence."""
    name: str
    start: int
    end: int
    direction: str  # "forward" or "reverse"
    color: str = "#4CAF50"  # Green

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass  
class AmpliconRegion:
    """An amplicon region between primers."""
    name: str
    start: int
    end: int
    forward_primer: str
    reverse_primer: str
    color: str = "#2196F3"  # Blue

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass
class CoverageMapResult:
    """Result of coverage map generation."""
    sequence_length: int
    primers: List[PrimerRegion] = field(default_factory=list)
    amplicons: List[AmpliconRegion] = field(default_factory=list)
    coverage_depth: List[int] = field(default_factory=list)
    total_coverage: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sequence_length": self.sequence_length,
            "primer_count": len(self.primers),
            "amplicon_count": len(self.amplicons),
            "total_coverage": self.total_coverage,
            "primers": [{"name": p.name, "start": p.start, "end": p.end} for p in self.primers],
            "amplicons": [{"name": a.name, "start": a.start, "end": a.end, "length": a.length} for a in self.amplicons],
        }


class CoverageMapGenerator:
    """
    Generates amplicon coverage map visualizations.
    """

    # Color palette for multiple primer pairs
    PRIMER_COLORS = [
        "#4CAF50",  # Green
        "#2196F3",  # Blue
        "#FF9800",  # Orange
        "#9C27B0",  # Purple
        "#F44336",  # Red
        "#009688",  # Teal
    ]

    AMPLICON_COLORS = [
        "#81C784",  # Light green
        "#64B5F6",  # Light blue
        "#FFB74D",  # Light orange
        "#BA68C8",  # Light purple
        "#E57373",  # Light red
        "#4DB6AC",  # Light teal
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize generator."""
        self.config = config or {}

    def create_map(
        self,
        sequence_length: int,
        primer_pairs: List[Dict[str, Any]],
    ) -> CoverageMapResult:
        """
        Create coverage map from primer pairs.
        
        Args:
            sequence_length: Length of template sequence
            primer_pairs: List of {forward: {start, end}, reverse: {start, end}, name}
            
        Returns:
            CoverageMapResult with coverage data
        """
        logger.info(f"Creating coverage map for {sequence_length}bp with {len(primer_pairs)} primer pairs")

        primers = []
        amplicons = []
        coverage_depth = [0] * sequence_length

        for i, pair in enumerate(primer_pairs):
            color_idx = i % len(self.PRIMER_COLORS)
            name = pair.get("name", f"Pair_{i+1}")

            # Forward primer
            fwd = pair.get("forward", {})
            if fwd:
                fwd_region = PrimerRegion(
                    name=f"{name}_F",
                    start=fwd.get("start", 0),
                    end=fwd.get("end", 0),
                    direction="forward",
                    color=self.PRIMER_COLORS[color_idx],
                )
                primers.append(fwd_region)

            # Reverse primer
            rev = pair.get("reverse", {})
            if rev:
                rev_region = PrimerRegion(
                    name=f"{name}_R",
                    start=rev.get("start", 0),
                    end=rev.get("end", 0),
                    direction="reverse",
                    color=self.PRIMER_COLORS[color_idx],
                )
                primers.append(rev_region)

            # Amplicon region
            if fwd and rev:
                amp_start = fwd.get("start", 0)
                amp_end = rev.get("end", 0)

                amplicon = AmpliconRegion(
                    name=name,
                    start=amp_start,
                    end=amp_end,
                    forward_primer=f"{name}_F",
                    reverse_primer=f"{name}_R",
                    color=self.AMPLICON_COLORS[color_idx],
                )
                amplicons.append(amplicon)

                # Update coverage depth
                for pos in range(amp_start, min(amp_end, sequence_length)):
                    coverage_depth[pos] += 1

        # Calculate total coverage
        covered_positions = sum(1 for d in coverage_depth if d > 0)
        total_coverage = (covered_positions / sequence_length) * 100 if sequence_length > 0 else 0

        result = CoverageMapResult(
            sequence_length=sequence_length,
            primers=primers,
            amplicons=amplicons,
            coverage_depth=coverage_depth,
            total_coverage=total_coverage,
        )

        logger.info(f"Coverage map created: {total_coverage:.1f}% coverage")
        return result

    def generate_svg(
        self,
        result: CoverageMapResult,
        width: int = 800,
        height: int = 200,
        show_labels: bool = True,
    ) -> str:
        """
        Generate SVG visualization of coverage map.
        
        Args:
            result: CoverageMapResult from create_map()
            width: SVG width
            height: SVG height
            show_labels: Whether to show primer labels
            
        Returns:
            SVG string
        """
        margin_left = 60
        margin_right = 20
        margin_top = 40
        margin_bottom = 60

        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom

        seq_len = result.sequence_length
        scale = plot_width / seq_len if seq_len > 0 else 1

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
            '<style>',
            '  .title { font-family: sans-serif; font-size: 14px; font-weight: bold; }',
            '  .label { font-family: sans-serif; font-size: 10px; }',
            '  .axis-label { font-family: sans-serif; font-size: 11px; }',
            '  .primer-label { font-family: monospace; font-size: 8px; }',
            '</style>',
            f'<text x="{width // 2}" y="20" class="title" text-anchor="middle">Amplicon Coverage Map</text>',
        ]

        # Draw sequence backbone
        backbone_y = margin_top + plot_height // 2
        svg_parts.append(
            f'<line x1="{margin_left}" y1="{backbone_y}" x2="{margin_left + plot_width}" y2="{backbone_y}" '
            f'stroke="#333" stroke-width="2"/>'
        )

        # Draw amplicon regions (behind primers)
        for amp in result.amplicons:
            x = margin_left + amp.start * scale
            w = (amp.end - amp.start) * scale
            svg_parts.append(
                f'<rect x="{x}" y="{backbone_y - 15}" width="{w}" height="30" '
                f'fill="{amp.color}" fill-opacity="0.3" stroke="{amp.color}" stroke-width="1"/>'
            )

        # Draw primers
        primer_height = 12
        for primer in result.primers:
            x = margin_left + primer.start * scale
            w = (primer.end - primer.start) * scale
            y = backbone_y - primer_height if primer.direction == "forward" else backbone_y

            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{w}" height="{primer_height}" '
                f'fill="{primer.color}" stroke="#333" stroke-width="0.5"/>'
            )

            # Arrow direction
            if primer.direction == "forward":
                arrow_x = x + w - 3
                svg_parts.append(
                    f'<polygon points="{arrow_x},{y+2} {arrow_x+6},{y+primer_height//2} {arrow_x},{y+primer_height-2}" '
                    f'fill="white"/>'
                )
            else:
                arrow_x = x + 3
                svg_parts.append(
                    f'<polygon points="{arrow_x},{y+2} {arrow_x-6},{y+primer_height//2} {arrow_x},{y+primer_height-2}" '
                    f'fill="white"/>'
                )

            # Labels
            if show_labels:
                label_y = y - 3 if primer.direction == "forward" else y + primer_height + 10
                svg_parts.append(
                    f'<text x="{x + w/2}" y="{label_y}" class="primer-label" text-anchor="middle">'
                    f'{primer.name}</text>'
                )

        # Draw axis
        svg_parts.append(
            f'<line x1="{margin_left}" y1="{height - margin_bottom + 10}" '
            f'x2="{margin_left + plot_width}" y2="{height - margin_bottom + 10}" stroke="#333"/>'
        )

        # Axis ticks
        tick_interval = seq_len // 5 if seq_len > 5 else 1
        for i in range(0, seq_len + 1, tick_interval):
            x = margin_left + i * scale
            svg_parts.append(
                f'<line x1="{x}" y1="{height - margin_bottom + 10}" x2="{x}" y2="{height - margin_bottom + 15}" stroke="#333"/>'
            )
            svg_parts.append(
                f'<text x="{x}" y="{height - margin_bottom + 28}" class="axis-label" text-anchor="middle">{i}</text>'
            )

        # Legend
        svg_parts.append(
            f'<text x="{margin_left}" y="{height - 10}" class="label">'
            f'Coverage: {result.total_coverage:.1f}% | Amplicons: {len(result.amplicons)}</text>'
        )

        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)


def create_coverage_map(
    sequence_length: int,
    primer_pairs: List[Dict[str, Any]],
) -> CoverageMapResult:
    """
    Create amplicon coverage map.
    
    Args:
        sequence_length: Length of template sequence
        primer_pairs: List of primer pair dicts
        
    Returns:
        CoverageMapResult
    """
    generator = CoverageMapGenerator()
    return generator.create_map(sequence_length, primer_pairs)
