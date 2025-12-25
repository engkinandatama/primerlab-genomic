"""
In-silico Compatibility Simulation.

Predicts amplicons for each primer pair and checks for overlapping products.
Used to validate that multiple primer pairs can work together in a single reaction.
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AmpliconOverlap:
    """Represents an overlap between two amplicons."""
    pair1_name: str
    pair2_name: str
    pair1_start: int
    pair1_end: int
    pair2_start: int
    pair2_end: int
    overlap_start: int
    overlap_end: int
    overlap_length: int
    is_problematic: bool  # True if overlap may cause issues
    warning: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "pair1_name": self.pair1_name,
            "pair2_name": self.pair2_name,
            "pair1_range": [self.pair1_start, self.pair1_end],
            "pair2_range": [self.pair2_start, self.pair2_end],
            "overlap_range": [self.overlap_start, self.overlap_end],
            "overlap_length": self.overlap_length,
            "is_problematic": self.is_problematic,
            "warning": self.warning
        }


@dataclass
class PredictedAmplicon:
    """Simplified amplicon prediction result."""
    pair_name: str
    start: int
    end: int
    length: int
    sequence: str
    forward_primer: str
    reverse_primer: str
    success: bool
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "pair_name": self.pair_name,
            "start": self.start,
            "end": self.end,
            "length": self.length,
            "success": self.success,
            "error": self.error
        }


@dataclass
class OverlapAnalysisResult:
    """Complete result of overlap analysis."""
    template_name: str
    template_length: int
    amplicons: List[PredictedAmplicon]
    overlaps: List[AmpliconOverlap]
    has_problems: bool
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "template_name": self.template_name,
            "template_length": self.template_length,
            "amplicons": [a.to_dict() for a in self.amplicons],
            "overlaps": [o.to_dict() for o in self.overlaps],
            "has_problems": self.has_problems,
            "warnings": self.warnings
        }


def check_overlap(
    start1: int, end1: int,
    start2: int, end2: int
) -> Tuple[bool, int, int, int]:
    """
    Check if two ranges overlap.
    
    Returns:
        Tuple of (has_overlap, overlap_start, overlap_end, overlap_length)
    """
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)
    
    if overlap_start < overlap_end:
        return True, overlap_start, overlap_end, overlap_end - overlap_start
    return False, 0, 0, 0


def predict_amplicons_for_pairs(
    template: str,
    primer_pairs: List[Dict],
    template_name: str = "template"
) -> List[PredictedAmplicon]:
    """
    Predict amplicons for each primer pair on the template.
    
    Args:
        template: DNA template sequence
        primer_pairs: List of dicts with 'name', 'forward', 'reverse' keys
        template_name: Name of the template
        
    Returns:
        List of PredictedAmplicon results
    """
    try:
        from primerlab.core.insilico.engine import InsilicoPCR
    except ImportError:
        logger.warning("InsilicoPCR engine not available")
        return []
    
    amplicons = []
    engine = InsilicoPCR()
    
    for pair in primer_pairs:
        name = pair.get("name", f"Pair_{len(amplicons)+1}")
        forward = pair.get("forward", "")
        reverse = pair.get("reverse", "")
        
        if not forward or not reverse:
            amplicons.append(PredictedAmplicon(
                pair_name=name,
                start=0, end=0, length=0,
                sequence="",
                forward_primer=forward,
                reverse_primer=reverse,
                success=False,
                error="Missing primer sequence"
            ))
            continue
        
        try:
            result = engine.run(template, forward, reverse, template_name)
            
            if result.products:
                # Take primary/first product
                product = result.products[0]
                amplicons.append(PredictedAmplicon(
                    pair_name=name,
                    start=product.start_position,
                    end=product.end_position,
                    length=product.product_size,
                    sequence=product.product_sequence[:100] + "..." if len(product.product_sequence) > 100 else product.product_sequence,
                    forward_primer=forward,
                    reverse_primer=reverse,
                    success=True
                ))
            else:
                amplicons.append(PredictedAmplicon(
                    pair_name=name,
                    start=0, end=0, length=0,
                    sequence="",
                    forward_primer=forward,
                    reverse_primer=reverse,
                    success=False,
                    error="No amplicon predicted"
                ))
                
        except Exception as e:
            amplicons.append(PredictedAmplicon(
                pair_name=name,
                start=0, end=0, length=0,
                sequence="",
                forward_primer=forward,
                reverse_primer=reverse,
                success=False,
                error=str(e)
            ))
    
    return amplicons


def analyze_overlaps(
    amplicons: List[PredictedAmplicon],
    min_overlap_warning: int = 50
) -> List[AmpliconOverlap]:
    """
    Analyze overlaps between predicted amplicons.
    
    Args:
        amplicons: List of predicted amplicons
        min_overlap_warning: Minimum overlap (bp) to generate warning
        
    Returns:
        List of AmpliconOverlap results
    """
    overlaps = []
    successful = [a for a in amplicons if a.success]
    
    for i in range(len(successful)):
        for j in range(i + 1, len(successful)):
            a1 = successful[i]
            a2 = successful[j]
            
            has_overlap, o_start, o_end, o_len = check_overlap(
                a1.start, a1.end,
                a2.start, a2.end
            )
            
            if has_overlap:
                is_problematic = o_len >= min_overlap_warning
                warning = None
                
                if is_problematic:
                    warning = f"Significant overlap ({o_len}bp) may cause competition"
                
                overlaps.append(AmpliconOverlap(
                    pair1_name=a1.pair_name,
                    pair2_name=a2.pair_name,
                    pair1_start=a1.start,
                    pair1_end=a1.end,
                    pair2_start=a2.start,
                    pair2_end=a2.end,
                    overlap_start=o_start,
                    overlap_end=o_end,
                    overlap_length=o_len,
                    is_problematic=is_problematic,
                    warning=warning
                ))
    
    return overlaps


def run_insilico_compat_simulation(
    template: str,
    primer_pairs: List[Dict],
    template_name: str = "template",
    min_overlap_warning: int = 50
) -> OverlapAnalysisResult:
    """
    Run complete in-silico compatibility simulation.
    
    Args:
        template: DNA template sequence
        primer_pairs: List of primer pair dicts with 'name', 'forward', 'reverse'
        template_name: Name of the template
        min_overlap_warning: Minimum overlap to flag as problematic
        
    Returns:
        OverlapAnalysisResult with all predictions and overlap analysis
    """
    logger.info(f"Running in-silico compat simulation for {len(primer_pairs)} pairs")
    
    # Predict amplicons
    amplicons = predict_amplicons_for_pairs(template, primer_pairs, template_name)
    
    # Analyze overlaps
    overlaps = analyze_overlaps(amplicons, min_overlap_warning)
    
    # Compile warnings
    warnings = []
    failed_pairs = [a.pair_name for a in amplicons if not a.success]
    if failed_pairs:
        warnings.append(f"Failed to predict amplicons for: {', '.join(failed_pairs)}")
    
    problematic_overlaps = [o for o in overlaps if o.is_problematic]
    if problematic_overlaps:
        warnings.append(f"{len(problematic_overlaps)} overlapping amplicon pair(s) detected")
    
    has_problems = len(problematic_overlaps) > 0
    
    return OverlapAnalysisResult(
        template_name=template_name,
        template_length=len(template),
        amplicons=amplicons,
        overlaps=overlaps,
        has_problems=has_problems,
        warnings=warnings
    )
