"""
In-silico Integration for Off-target Detection (v0.3.0)

Integrates off-target detection with in-silico PCR results.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from primerlab.core.logger import get_logger
from primerlab.core.insilico.engine import InsilicoPCRResult
from primerlab.core.offtarget.finder import OfftargetFinder, PrimerPairOfftargetResult
from primerlab.core.offtarget.scorer import SpecificityScorer, SpecificityScore

logger = get_logger()


@dataclass
class IntegratedPCRResult:
    """
    Combined in-silico PCR and off-target analysis result.
    
    Attributes:
        insilico_result: In-silico PCR simulation result
        offtarget_result: Off-target analysis result
        specificity_score: Combined specificity score
        is_validated: True if both insilico and specificity pass
        validation_summary: Summary of validation status
    """
    insilico_result: InsilicoPCRResult
    offtarget_result: Optional[PrimerPairOfftargetResult] = None
    specificity_score: Optional[SpecificityScore] = None
    is_validated: bool = False
    validation_summary: str = ""

    def __post_init__(self):
        """Generate validation summary."""
        summaries = []

        # Check in-silico result
        if self.insilico_result.success:
            if self.insilico_result.has_unique_product:
                summaries.append("✓ Unique product predicted")
            else:
                product_count = len(self.insilico_result.products)
                if product_count == 0:
                    summaries.append("✗ No products predicted")
                else:
                    summaries.append(f"⚠ {product_count} products predicted")
        else:
            summaries.append("✗ In-silico simulation failed")

        # Check specificity
        if self.specificity_score:
            grade = self.specificity_score.grade
            score = self.specificity_score.overall_score
            if self.specificity_score.is_acceptable:
                summaries.append(f"✓ Specificity: {score:.1f} ({grade})")
            else:
                summaries.append(f"✗ Specificity: {score:.1f} ({grade})")

        self.validation_summary = " | ".join(summaries)

        # Determine if validated
        insilico_pass = (
            self.insilico_result.success  and
            self.insilico_result.has_unique_product
        )
        specificity_pass = (
            self.specificity_score is None  or
            self.specificity_score.is_acceptable
        )
        self.is_validated = insilico_pass and specificity_pass


def integrate_offtarget_check(
    insilico_result: InsilicoPCRResult,
    database: str,
    target_id: Optional[str] = None,
    mode: str = "auto"
) -> IntegratedPCRResult:
    """
    Run off-target check on in-silico PCR result.
    
    Args:
        insilico_result: Result from in-silico PCR
        database: Path to database for off-target search
        target_id: Expected target sequence ID
        mode: Alignment mode
        
    Returns:
        IntegratedPCRResult with combined analysis
    """
    # Get primers from result
    fwd_primer = insilico_result.forward_primer
    rev_primer = insilico_result.reverse_primer

    # Run off-target finder
    finder = OfftargetFinder(database=database, target_id=target_id, mode=mode)
    offtarget_result = finder.find_primer_pair_offtargets(
        forward_primer=fwd_primer,
        reverse_primer=rev_primer,
        target_id=target_id
    )

    # Score specificity
    scorer = SpecificityScorer()
    _, _, combined_score = scorer.score_primer_pair(offtarget_result)

    return IntegratedPCRResult(
        insilico_result=insilico_result,
        offtarget_result=offtarget_result,
        specificity_score=combined_score
    )
