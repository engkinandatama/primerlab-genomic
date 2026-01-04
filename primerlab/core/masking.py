"""
PrimerLab Region Masking Module

v0.1.5 Priority 6: Exclude repetitive or problematic regions from primer design.

Features:
- Detect lowercase masked regions (RepeatMasker convention)
- Parse BED files for custom excluded regions
- Integrate with Primer3 SEQUENCE_EXCLUDED_REGION
- Support N-masking detection
"""

from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from primerlab.core.logger import get_logger

logger = get_logger()


class RegionMask:
    """
    Represents a masked/excluded region in a sequence.
    
    Attributes:
        start: 0-based start position
        end: 0-based end position (exclusive)
        reason: Why this region is masked (e.g., "repeat", "low_complexity", "user")
    """

    def __init__(self, start: int, end: int, reason: str = "masked"):
        self.start = start
        self.end = end
        self.reason = reason

    @property
    def length(self) -> int:
        return self.end - self.start

    def __repr__(self) -> str:
        return f"RegionMask({self.start}-{self.end}, {self.reason})"

    def to_primer3_format(self) -> Tuple[int, int]:
        """Convert to Primer3 SEQUENCE_EXCLUDED_REGION format (start, length)."""
        return (self.start, self.length)


class RegionMasker:
    """
    Detects and manages masked regions in sequences.
    
    Supports:
    - Lowercase masking (RepeatMasker softmasked output)
    - N-masking (hardmasked regions)
    - BED file regions
    - Manual coordinate input
    """

    def __init__(self):
        self.masks: List[RegionMask] = []

    def detect_lowercase_masks(self, sequence: str, min_length: int = 5) -> List[RegionMask]:
        """
        Detect lowercase regions (softmasked repeats).
        
        Args:
            sequence: DNA sequence (mixed case)
            min_length: Minimum length to consider as masked region
            
        Returns:
            List of RegionMask objects
        """
        masks = []
        in_mask = False
        mask_start = 0

        for i, char in enumerate(sequence):
            is_lower = char.islower()

            if is_lower and not in_mask:
                # Start of masked region
                in_mask = True
                mask_start = i
            elif not is_lower and in_mask:
                # End of masked region
                in_mask = False
                length = i - mask_start
                if length >= min_length:
                    masks.append(RegionMask(mask_start, i, "repeat"))

        # Handle case where sequence ends with masked region
        if in_mask:
            length = len(sequence) - mask_start
            if length >= min_length:
                masks.append(RegionMask(mask_start, len(sequence), "repeat"))

        logger.debug(f"Detected {len(masks)} lowercase masked regions")
        return masks

    def detect_n_masks(self, sequence: str, min_length: int = 3) -> List[RegionMask]:
        """
        Detect N-masked regions (hardmasked).
        
        Args:
            sequence: DNA sequence
            min_length: Minimum run of Ns to consider
            
        Returns:
            List of RegionMask objects
        """
        masks = []
        in_mask = False
        mask_start = 0
        seq_upper = sequence.upper()

        for i, char in enumerate(seq_upper):
            is_n = (char == 'N')

            if is_n and not in_mask:
                in_mask = True
                mask_start = i
            elif not is_n and in_mask:
                in_mask = False
                length = i - mask_start
                if length >= min_length:
                    masks.append(RegionMask(mask_start, i, "n_masked"))

        if in_mask:
            length = len(sequence) - mask_start
            if length >= min_length:
                masks.append(RegionMask(mask_start, len(sequence), "n_masked"))

        logger.debug(f"Detected {len(masks)} N-masked regions")
        return masks

    def parse_bed_file(self, bed_path: str, seq_name: Optional[str] = None) -> List[RegionMask]:
        """
        Parse BED file for excluded regions.
        
        Args:
            bed_path: Path to BED file
            seq_name: Filter by sequence name (optional)
            
        Returns:
            List of RegionMask objects
        """
        masks = []
        path = Path(bed_path)

        if not path.exists():
            logger.warning(f"BED file not found: {bed_path}")
            return masks

        try:
            with open(path) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("track"):
                        continue

                    parts = line.split("\t")
                    if len(parts) < 3:
                        logger.warning(f"Invalid BED line {line_num}: {line}")
                        continue

                    chrom = parts[0]
                    start = int(parts[1])
                    end = int(parts[2])
                    reason = parts[3] if len(parts) > 3 else "bed_region"

                    # Filter by sequence name if provided
                    if seq_name and chrom != seq_name:
                        continue

                    masks.append(RegionMask(start, end, reason))

            logger.info(f"Loaded {len(masks)} regions from BED file: {bed_path}")
        except Exception as e:
            logger.error(f"Failed to parse BED file: {e}")

        return masks

    def add_manual_region(self, start: int, end: int, reason: str = "user") -> None:
        """Add a manually specified excluded region."""
        self.masks.append(RegionMask(start, end, reason))

    def analyze_sequence(
        self, 
        sequence: str, 
        detect_lowercase: bool = True,
        detect_n: bool = True,
        min_length: int = 5
    ) -> List[RegionMask]:
        """
        Analyze sequence for all types of masked regions.
        
        Args:
            sequence: DNA sequence
            detect_lowercase: Enable softmask detection
            detect_n: Enable N-mask detection
            min_length: Minimum region length
            
        Returns:
            Combined list of all detected masks
        """
        all_masks = list(self.masks)  # Start with manual masks

        if detect_lowercase:
            all_masks.extend(self.detect_lowercase_masks(sequence, min_length))

        if detect_n:
            all_masks.extend(self.detect_n_masks(sequence, min_length))

        # Merge overlapping regions
        merged = self._merge_overlapping(all_masks)

        logger.info(f"Total masked regions: {len(merged)} ({self._total_masked_bp(merged)} bp)")
        return merged

    def _merge_overlapping(self, masks: List[RegionMask]) -> List[RegionMask]:
        """Merge overlapping or adjacent masked regions."""
        if not masks:
            return []

        # Sort by start position
        sorted_masks = sorted(masks, key=lambda m: m.start)
        merged = [sorted_masks[0]]

        for mask in sorted_masks[1:]:
            last = merged[-1]
            if mask.start <= last.end:
                # Overlapping or adjacent - extend the last region
                merged[-1] = RegionMask(
                    last.start, 
                    max(last.end, mask.end),
                    "merged"
                )
            else:
                merged.append(mask)

        return merged

    def _total_masked_bp(self, masks: List[RegionMask]) -> int:
        """Calculate total masked base pairs."""
        return sum(m.length for m in masks)

    def to_primer3_excluded(self, masks: List[RegionMask]) -> List[Tuple[int, int]]:
        """
        Convert masks to Primer3 SEQUENCE_EXCLUDED_REGION format.
        
        Returns:
            List of (start, length) tuples
        """
        return [m.to_primer3_format() for m in masks]

    def get_mask_summary(self, masks: List[RegionMask], sequence_length: int) -> Dict[str, Any]:
        """
        Generate summary statistics for masked regions.
        
        Returns:
            Dict with mask statistics
        """
        total_masked = self._total_masked_bp(masks)
        percent_masked = (total_masked / sequence_length * 100) if sequence_length > 0 else 0

        by_reason = {}
        for mask in masks:
            by_reason[mask.reason] = by_reason.get(mask.reason, 0) + 1

        return {
            "total_regions": len(masks),
            "total_masked_bp": total_masked,
            "percent_masked": round(percent_masked, 1),
            "by_reason": by_reason,
            "sequence_length": sequence_length
        }


def apply_masks_to_config(config: Dict[str, Any], masks: List[RegionMask]) -> Dict[str, Any]:
    """
    Apply masked regions to Primer3 configuration.
    
    Args:
        config: PrimerLab config dict
        masks: List of RegionMask objects
        
    Returns:
        Updated config with SEQUENCE_EXCLUDED_REGION
    """
    if not masks:
        return config

    # Ensure parameters section exists
    if "parameters" not in config:
        config["parameters"] = {}

    # Convert masks to Primer3 format
    excluded = [(m.start, m.length) for m in masks]

    # Add to config
    config["parameters"]["excluded_regions"] = excluded

    logger.info(f"Applied {len(masks)} excluded regions to config")
    return config


def format_mask_report(masks: List[RegionMask], sequence_length: int) -> str:
    """Format masked regions as CLI-friendly report."""
    if not masks:
        return "No masked regions detected."

    masker = RegionMasker()
    summary = masker.get_mask_summary(masks, sequence_length)

    lines = []
    lines.append("")
    lines.append("=" * 50)
    lines.append("🔒 Region Masking Summary")
    lines.append("=" * 50)
    lines.append(f"  Sequence Length: {summary['sequence_length']} bp")
    lines.append(f"  Masked Regions: {summary['total_regions']}")
    lines.append(f"  Total Masked: {summary['total_masked_bp']} bp ({summary['percent_masked']}%)")
    lines.append("")
    lines.append("  By Reason:")
    for reason, count in summary['by_reason'].items():
        lines.append(f"    {reason}: {count} regions")
    lines.append("")

    if len(masks) <= 10:
        lines.append("  Regions:")
        for mask in masks:
            lines.append(f"    {mask.start:>6} - {mask.end:<6} ({mask.length:>4} bp) [{mask.reason}]")
    else:
        lines.append(f"  First 5 regions:")
        for mask in masks[:5]:
            lines.append(f"    {mask.start:>6} - {mask.end:<6} ({mask.length:>4} bp) [{mask.reason}]")
        lines.append(f"  ... and {len(masks) - 5} more")

    lines.append("=" * 50)
    lines.append("")

    return "\n".join(lines)
