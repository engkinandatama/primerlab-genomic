"""
Advanced qPCR Features.

Provides HRM optimization, internal control design, quencher recommendations,
and dPCR compatibility checking.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from primerlab.core.logger import get_logger

logger = get_logger()


# Quencher/Reporter compatibility matrix
REPORTER_QUENCHER_MATRIX = {
    "FAM": {
        "compatible": ["TAMRA", "BHQ-1", "DABCYL", "MGB"],
        "optimal": "BHQ-1",
        "wavelength": {"excitation": 495, "emission": 520},
    },
    "VIC": {
        "compatible": ["TAMRA", "BHQ-1", "MGB"],
        "optimal": "MGB",
        "wavelength": {"excitation": 538, "emission": 554},
    },
    "HEX": {
        "compatible": ["BHQ-1", "TAMRA", "DABCYL"],
        "optimal": "BHQ-1",
        "wavelength": {"excitation": 535, "emission": 556},
    },
    "ROX": {
        "compatible": ["BHQ-2", "TAMRA"],
        "optimal": "BHQ-2",
        "wavelength": {"excitation": 586, "emission": 610},
    },
    "CY5": {
        "compatible": ["BHQ-2", "BHQ-3"],
        "optimal": "BHQ-2",
        "wavelength": {"excitation": 649, "emission": 670},
    },
}


@dataclass
class HRMOptimizationResult:
    """Result of HRM optimization analysis."""
    amplicon_length: int
    gc_content: float
    predicted_tm: float
    melt_range: Tuple[float, float]
    resolution_score: float  # 0-100
    snp_discrimination: bool
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amplicon_length": self.amplicon_length,
            "gc_content": self.gc_content,
            "predicted_tm": self.predicted_tm,
            "melt_range": self.melt_range,
            "resolution_score": self.resolution_score,
            "snp_discrimination": self.snp_discrimination,
            "recommendations": self.recommendations,
        }


@dataclass
class InternalControlResult:
    """Result of internal control design."""
    control_type: str  # "endogenous" or "exogenous"
    gene_name: str
    primer_forward: str
    primer_reverse: str
    amplicon_size: int
    tm_forward: float
    tm_reverse: float
    compatible_with_target: bool
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "control_type": self.control_type,
            "gene_name": self.gene_name,
            "forward": self.primer_forward,
            "reverse": self.primer_reverse,
            "amplicon_size": self.amplicon_size,
            "compatible": self.compatible_with_target,
        }


@dataclass
class QuencherRecommendation:
    """Quencher recommendation for a reporter dye."""
    reporter: str
    recommended_quencher: str
    alternative_quenchers: List[str]
    excitation: int
    emission: int
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reporter": self.reporter,
            "quencher": self.recommended_quencher,
            "alternatives": self.alternative_quenchers,
            "wavelengths": {"excitation": self.excitation, "emission": self.emission},
        }


@dataclass
class DPCRCompatibilityResult:
    """Digital PCR compatibility check result."""
    amplicon_length: int
    gc_content: float
    is_compatible: bool
    partition_efficiency: float  # Estimated
    concentration_range: Tuple[float, float]  # copies/μL
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amplicon_length": self.amplicon_length,
            "is_compatible": self.is_compatible,
            "partition_efficiency": self.partition_efficiency,
            "concentration_range": self.concentration_range,
            "warnings": self.warnings,
        }


class AdvancedQPCRTools:
    """
    Advanced qPCR tools for specialized applications.
    """

    # Common endogenous controls
    ENDOGENOUS_CONTROLS = {
        "human": [
            {"gene": "GAPDH", "fwd": "GAGTCAACGGATTTGGTCGT", "rev": "TTGATTTTGGAGGGATCTCG", "size": 238},
            {"gene": "ACTB", "fwd": "CATGTACGTTGCTATCCAGGC", "rev": "CTCCTTAATGTCACGCACGAT", "size": 250},
            {"gene": "18S", "fwd": "GTAACCCGTTGAACCCCATT", "rev": "CCATCCAATCGGTAGTAGCG", "size": 151},
        ],
        "mouse": [
            {"gene": "Gapdh", "fwd": "AGGTCGGTGTGAACGGATTTG", "rev": "TGTAGACCATGTAGTTGAGGTCA", "size": 123},
            {"gene": "Actb", "fwd": "GGCTGTATTCCCCTCCATCG", "rev": "CCAGTTGGTAACAATGCCATGT", "size": 154},
        ],
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize tools."""
        self.config = config or {}

    def optimize_for_hrm(
        self,
        amplicon_seq: str,
        target_snp_position: Optional[int] = None,
    ) -> HRMOptimizationResult:
        """
        Optimize amplicon for High Resolution Melt analysis.
        
        Args:
            amplicon_seq: Amplicon sequence
            target_snp_position: Position of SNP to discriminate (optional)
            
        Returns:
            HRMOptimizationResult
        """
        length = len(amplicon_seq)
        gc_count = sum(1 for c in amplicon_seq.upper() if c in 'GC')
        gc_content = gc_count / length * 100 if length > 0 else 0

        # Predict Tm (simplified)
        predicted_tm = 64.9 + 41 * (gc_count - 16.4) / length if length > 0 else 0

        # Melt range estimation
        melt_low = predicted_tm - 5
        melt_high = predicted_tm + 5

        # Resolution score based on length and GC
        resolution = 100
        recommendations = []

        # Optimal HRM length: 50-300bp
        if length < 50:
            resolution -= 30
            recommendations.append("Amplicon too short for reliable HRM (< 50bp)")
        elif length > 300:
            resolution -= 20
            recommendations.append(f"Consider shorter amplicon for better resolution ({length}bp)")
        elif 80 <= length <= 150:
            resolution += 10  # Optimal range

        # GC content affects resolution
        if gc_content < 30 or gc_content > 70:
            resolution -= 15
            recommendations.append(f"Extreme GC content ({gc_content:.0f}%) may affect melt curve")

        # SNP discrimination
        snp_ok = True
        if target_snp_position:
            if target_snp_position < 10 or target_snp_position > length - 10:
                snp_ok = False
                recommendations.append("SNP too close to amplicon ends")

        return HRMOptimizationResult(
            amplicon_length=length,
            gc_content=gc_content,
            predicted_tm=predicted_tm,
            melt_range=(melt_low, melt_high),
            resolution_score=max(0, min(100, resolution)),
            snp_discrimination=snp_ok,
            recommendations=recommendations,
        )

    def recommend_internal_control(
        self,
        species: str = "human",
        target_tm: float = 60.0,
    ) -> List[InternalControlResult]:
        """
        Recommend internal control primers.
        
        Args:
            species: Target species
            target_tm: Target Tm for compatibility check
            
        Returns:
            List of InternalControlResult
        """
        controls = self.ENDOGENOUS_CONTROLS.get(species.lower(), [])
        results = []

        for ctrl in controls:
            # Simple Tm calculation
            fwd_tm = 2 * (ctrl["fwd"].count('A') + ctrl["fwd"].count('T')) + \
                4 * (ctrl["fwd"].count('G') + ctrl["fwd"].count('C'))
            rev_tm = 2 * (ctrl["rev"].count('A') + ctrl["rev"].count('T')) + \
                     4 * (ctrl["rev"].count('G') + ctrl["rev"].count('C'))

            # Check compatibility (Tm within 3°C)
            compatible = abs(fwd_tm - target_tm) <= 5 and abs(rev_tm - target_tm) <= 5

            notes = []
            if not compatible:
                notes.append(f"Tm mismatch: Fwd={fwd_tm}°C, Rev={rev_tm}°C")

            results.append(InternalControlResult(
                control_type="endogenous",
                gene_name=ctrl["gene"],
                primer_forward=ctrl["fwd"],
                primer_reverse=ctrl["rev"],
                amplicon_size=ctrl["size"],
                tm_forward=fwd_tm,
                tm_reverse=rev_tm,
                compatible_with_target=compatible,
                notes=notes,
            ))

        return results

    def recommend_quencher(self, reporter: str) -> QuencherRecommendation:
        """
        Recommend quencher for a reporter dye.
        
        Args:
            reporter: Reporter dye name (FAM, VIC, HEX, ROX, CY5)
            
        Returns:
            QuencherRecommendation
        """
        reporter = reporter.upper()

        if reporter not in REPORTER_QUENCHER_MATRIX:
            # Default recommendation
            return QuencherRecommendation(
                reporter=reporter,
                recommended_quencher="BHQ-1",
                alternative_quenchers=["TAMRA", "DABCYL"],
                excitation=0,
                emission=0,
                notes=[f"Unknown reporter '{reporter}', using default BHQ-1"],
            )

        info = REPORTER_QUENCHER_MATRIX[reporter]
        alternates = [q for q in info["compatible"] if q != info["optimal"]]

        return QuencherRecommendation(
            reporter=reporter,
            recommended_quencher=info["optimal"],
            alternative_quenchers=alternates,
            excitation=info["wavelength"]["excitation"],
            emission=info["wavelength"]["emission"],
        )

    def check_dpcr_compatibility(
        self,
        amplicon_seq: str,
    ) -> DPCRCompatibilityResult:
        """
        Check amplicon compatibility with digital PCR.
        
        Args:
            amplicon_seq: Amplicon sequence
            
        Returns:
            DPCRCompatibilityResult
        """
        length = len(amplicon_seq)
        gc_count = sum(1 for c in amplicon_seq.upper() if c in 'GC')
        gc_content = gc_count / length * 100 if length > 0 else 0

        warnings = []
        recommendations = []
        is_compatible = True
        efficiency = 95.0

        # Optimal dPCR amplicon: 60-200bp
        if length < 60:
            warnings.append(f"Amplicon too short ({length}bp)")
            is_compatible = False
            efficiency -= 20
        elif length > 250:
            warnings.append(f"Amplicon long for dPCR ({length}bp)")
            efficiency -= 10
            recommendations.append("Consider shorter amplicon for better partitioning")

        # GC extremes
        if gc_content < 35 or gc_content > 65:
            warnings.append(f"GC content ({gc_content:.0f}%) may affect amplification")
            efficiency -= 5

        # Concentration range for dPCR (typical)
        conc_low = 10  # copies/μL
        conc_high = 100000  # copies/μL

        return DPCRCompatibilityResult(
            amplicon_length=length,
            gc_content=gc_content,
            is_compatible=is_compatible,
            partition_efficiency=max(0, efficiency),
            concentration_range=(conc_low, conc_high),
            warnings=warnings,
            recommendations=recommendations,
        )


# Helper functions
def optimize_hrm(amplicon_seq: str) -> HRMOptimizationResult:
    """Optimize amplicon for HRM analysis."""
    tools = AdvancedQPCRTools()
    return tools.optimize_for_hrm(amplicon_seq)


def get_quencher_recommendation(reporter: str) -> QuencherRecommendation:
    """Get quencher recommendation for reporter dye."""
    tools = AdvancedQPCRTools()
    return tools.recommend_quencher(reporter)


def check_dpcr(amplicon_seq: str) -> DPCRCompatibilityResult:
    """Check dPCR compatibility."""
    tools = AdvancedQPCRTools()
    return tools.check_dpcr_compatibility(amplicon_seq)
