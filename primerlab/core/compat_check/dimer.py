"""
Cross-Dimer Calculation Engine.

This module provides the DimerEngine class for calculating cross-dimer
interactions between primers in a multiplex set using ViennaRNA.

Version: v0.4.0
"""

from typing import Dict, Any, List, Tuple, Optional
from primerlab.core.logger import get_logger
from primerlab.core.tools.vienna_wrapper import ViennaWrapper
from primerlab.core.compat_check.models import (
    MultiplexPair,
    DimerResult,
    CompatibilityMatrix,
)

logger = get_logger()


class DimerEngine:
    """
    Engine for calculating cross-dimer interactions in multiplex primer sets.
    
    Uses ViennaRNA (RNAcofold) to calculate ΔG of hetero/homodimer formation.
    Includes caching to avoid redundant calculations.
    
    Attributes:
        threshold: ΔG threshold below which a dimer is problematic (kcal/mol)
        vienna: ViennaRNA wrapper instance
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize DimerEngine with configuration.
        
        Args:
            config: Configuration dict with multiplex.dimer_dg_threshold
        """
        config = config or {}
        compat_config = config.get("multiplex", {})

        # Configurable threshold (more negative = more stable = worse)
        self.threshold = compat_config.get("dimer_dg_threshold", -6.0)

        # Initialize ViennaRNA wrapper
        self.vienna = ViennaWrapper()

        # Cache for dimer results: (seq1, seq2) -> DimerResult
        self._cache: Dict[Tuple[str, str], DimerResult] = {}

        # Track ViennaRNA availability
        self._vienna_available: Optional[bool] = None

    def _check_vienna(self) -> bool:
        """Check if ViennaRNA is available (cached)."""
        if self._vienna_available is None:
            # Try a simple fold to check availability
            result = self.vienna.fold("ATGC")
            self._vienna_available = "error" not in result
            if not self._vienna_available:
                logger.warning(
                    "ViennaRNA not available. Dimer calculations will return ΔG=0."
                )
        return self._vienna_available

    def _get_cache_key(self, seq1: str, seq2: str) -> Tuple[str, str]:
        """Get normalized cache key (order-independent for same pair)."""
        # Sort to ensure (A,B) and (B,A) use same key
        if seq1 <= seq2:
            return (seq1, seq2)
        return (seq2, seq1)

    def check_dimer(
        self,
        seq1: str,
        seq2: str,
        name1: str = "primer1",
        name2: str = "primer2"
    ) -> DimerResult:
        """
        Calculate dimer ΔG between two primer sequences.
        
        Uses ViennaRNA RNAcofold for accurate thermodynamic prediction.
        Falls back to ΔG=0 if ViennaRNA is unavailable.
        
        Args:
            seq1: First primer sequence
            seq2: Second primer sequence
            name1: Name/identifier for first primer
            name2: Name/identifier for second primer
            
        Returns:
            DimerResult with ΔG and structure
        """
        seq1 = seq1.upper()
        seq2 = seq2.upper()

        # Check cache first
        cache_key = self._get_cache_key(seq1, seq2)
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            # Return copy with updated names
            return DimerResult(
                primer1_name=name1,
                primer2_name=name2,
                primer1_seq=seq1,
                primer2_seq=seq2,
                delta_g=cached.delta_g,
                structure=cached.structure,
                is_problematic=cached.is_problematic,
            )

        # Check ViennaRNA availability
        if not self._check_vienna():
            # Fallback: return neutral result
            result = DimerResult(
                primer1_name=name1,
                primer2_name=name2,
                primer1_seq=seq1,
                primer2_seq=seq2,
                delta_g=0.0,
                structure="(ViennaRNA unavailable)",
                is_problematic=False,
            )
            self._cache[cache_key] = result
            return result

        # Calculate dimer using ViennaRNA
        cofold_result = self.vienna.cofold(seq1, seq2)

        delta_g = cofold_result.get("mfe", 0.0)
        structure = cofold_result.get("structure", "")

        # Check if problematic (ΔG below threshold)
        is_problematic = delta_g < self.threshold

        result = DimerResult(
            primer1_name=name1,
            primer2_name=name2,
            primer1_seq=seq1,
            primer2_seq=seq2,
            delta_g=delta_g,
            structure=structure,
            is_problematic=is_problematic,
        )

        # Cache the result
        self._cache[cache_key] = result

        return result

    def build_matrix(self, pairs: List[MultiplexPair]) -> CompatibilityMatrix:
        """
        Build NxN compatibility matrix for all primers in the multiplex set.
        
        Checks all combinations:
        - Forward homodimers (F with F)
        - Reverse homodimers (R with R)
        - Forward-reverse heterodimers (F with R, same pair)
        - Cross-pair dimers (all combinations between different pairs)
        
        Args:
            pairs: List of MultiplexPair objects
            
        Returns:
            CompatibilityMatrix with all dimer results
        """
        # Collect all primers with their identifiers
        primers: List[Tuple[str, str]] = []  # (name, sequence)

        for pair in pairs:
            primers.append((f"{pair.name}_F", pair.forward))
            primers.append((f"{pair.name}_R", pair.reverse))

        # Build matrix
        matrix: Dict[Tuple[str, str], DimerResult] = {}
        worst_dimer: Optional[DimerResult] = None
        worst_dg = float('inf')
        problematic_count = 0

        n = len(primers)
        total_checks = 0

        # Check all unique pairs (including homodimers)
        for i in range(n):
            for j in range(i, n):
                name1, seq1 = primers[i]
                name2, seq2 = primers[j]

                result = self.check_dimer(seq1, seq2, name1, name2)
                matrix[(name1, name2)] = result
                total_checks += 1

                if result.is_problematic:
                    problematic_count += 1

                # Track worst dimer
                if result.delta_g < worst_dg:
                    worst_dg = result.delta_g
                    worst_dimer = result

        return CompatibilityMatrix(
            primer_names=[name for name, _ in primers],
            matrix=matrix,
            worst_dimer=worst_dimer,
            total_dimers=total_checks,
            problematic_count=problematic_count,
        )

    def get_problematic_pairs(
        self,
        matrix: CompatibilityMatrix
    ) -> List[DimerResult]:
        """
        Get all problematic dimer pairs from a matrix.
        
        Args:
            matrix: Compatibility matrix to analyze
            
        Returns:
            List of problematic DimerResult objects, sorted by ΔG (worst first)
        """
        problematic = matrix.get_problematic_dimers()
        return sorted(problematic, key=lambda d: d.delta_g)

    def clear_cache(self):
        """Clear the dimer calculation cache."""
        self._cache.clear()
        logger.debug("Dimer cache cleared")
