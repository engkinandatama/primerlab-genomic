"""
Semi-Nested PCR Engine.

Designs semi-nested PCR primer sets where one primer is shared
between outer and inner reactions.
"""

from typing import Dict, Any, Optional, List, Tuple
from primerlab.core.variants.models import NestedPrimerSet, NestedPCRResult
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper
from primerlab.core.logger import get_logger

logger = get_logger()


class SemiNestedPCREngine:
    """
    Engine for designing semi-nested PCR primers.
    
    Semi-nested PCR uses:
    - One shared primer between outer and inner reactions
    - One unique outer primer
    - One unique inner primer
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize semi-nested PCR engine.
        
        Args:
            config: Optional configuration dict
        """
        self.config = config or {}
        self.p3_wrapper = Primer3Wrapper()
        
        # Default size ranges
        self.outer_size_min = self.config.get("outer_size_min", 400)
        self.outer_size_max = self.config.get("outer_size_max", 600)
        self.inner_size_min = self.config.get("inner_size_min", 150)
        self.inner_size_max = self.config.get("inner_size_max", 300)
        
        # Tm settings
        self.shared_tm_opt = self.config.get("shared_tm_opt", 60.0)
        self.unique_tm_opt = self.config.get("unique_tm_opt", 60.0)
        
        # Shared primer position: "forward" or "reverse"
        self.shared_position = self.config.get("shared_position", "forward")
    
    def design(self, sequence: str) -> NestedPCRResult:
        """
        Design semi-nested PCR primer set.
        
        Args:
            sequence: Template sequence
            
        Returns:
            NestedPCRResult with primer set
        """
        logger.info(f"Designing semi-nested PCR primers for {len(sequence)}bp sequence")
        logger.info(f"Shared primer position: {self.shared_position}")
        
        result = NestedPCRResult(
            sequence_length=len(sequence),
            outer_size_range=(self.outer_size_min, self.outer_size_max),
            inner_size_range=(self.inner_size_min, self.inner_size_max),
        )
        
        # Validate sequence length
        if len(sequence) < self.outer_size_min + 50:
            result.warnings.append(
                f"Sequence too short ({len(sequence)}bp) for semi-nested PCR. "
                f"Minimum recommended: {self.outer_size_min + 50}bp"
            )
            return result
        
        # Step 1: Design outer primers
        logger.info("Step 1: Designing outer primers...")
        outer_primers = self._design_primers(
            sequence, 
            self.outer_size_min, 
            self.outer_size_max
        )
        
        if not outer_primers:
            result.warnings.append("Failed to design outer primers")
            return result
        
        logger.info(f"Found {len(outer_primers)} outer primer candidates")
        
        # Step 2: Design inner primers for each outer pair
        # The shared primer is reused, only design the unique inner primer
        logger.info("Step 2: Designing inner primers with shared primer...")
        seminested_sets: List[NestedPrimerSet] = []
        
        for outer in outer_primers[:5]:  # Top 5 outer candidates
            outer_amplicon = sequence[outer["start"]:outer["end"]]
            
            if len(outer_amplicon) < self.inner_size_min + 20:
                continue
            
            # Design inner pair within outer amplicon
            inner_primers = self._design_primers(
                outer_amplicon,
                self.inner_size_min,
                min(self.inner_size_max, len(outer_amplicon) - 40)
            )
            
            if not inner_primers:
                continue
            
            for inner in inner_primers[:3]:
                # Create semi-nested set
                seminested_set = self._create_seminested_set(
                    sequence, outer, inner, outer_amplicon
                )
                if seminested_set:
                    seminested_sets.append(seminested_set)
        
        if not seminested_sets:
            result.warnings.append("Failed to design semi-nested primer sets")
            result.recommendations.append("Try adjusting size ranges")
            return result
        
        # Step 3: Score and select best
        logger.info(f"Step 3: Scoring {len(seminested_sets)} semi-nested sets...")
        seminested_sets = self._score_seminested_sets(seminested_sets)
        seminested_sets.sort(key=lambda x: x.combined_score, reverse=True)
        
        # Set result
        result.success = True
        result.primer_set = seminested_sets[0]
        result.alternatives = seminested_sets[1:5]
        
        logger.info(f"Semi-nested PCR design complete. Grade: {result.primer_set.grade}")
        return result
    
    def _design_primers(
        self, 
        sequence: str, 
        size_min: int, 
        size_max: int
    ) -> List[Dict[str, Any]]:
        """Design primer pairs for given size range."""
        config = {
            "parameters": {
                "product_size_range": [[size_min, size_max]],
                "tm": {
                    "min": self.shared_tm_opt - 3,
                    "opt": self.shared_tm_opt,
                    "max": self.shared_tm_opt + 3,
                },
                "primer_size": {"min": 18, "opt": 20, "max": 25},
            }
        }
        
        raw_results = self.p3_wrapper.design_primers(sequence, config)
        return self._parse_primer3_results(raw_results)
    
    def _parse_primer3_results(self, raw_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Primer3 results into primer list."""
        primers = []
        num_returned = raw_results.get("PRIMER_LEFT_NUM_RETURNED", 0)
        
        for i in range(num_returned):
            try:
                fwd_pos = raw_results.get(f"PRIMER_LEFT_{i}", (0, 0))
                rev_pos = raw_results.get(f"PRIMER_RIGHT_{i}", (0, 0))
                
                fwd_start, fwd_len = fwd_pos
                rev_start, rev_len = rev_pos
                
                primers.append({
                    "index": i,
                    "fwd_seq": raw_results.get(f"PRIMER_LEFT_{i}_SEQUENCE", ""),
                    "rev_seq": raw_results.get(f"PRIMER_RIGHT_{i}_SEQUENCE", ""),
                    "fwd_tm": raw_results.get(f"PRIMER_LEFT_{i}_TM", 0.0),
                    "rev_tm": raw_results.get(f"PRIMER_RIGHT_{i}_TM", 0.0),
                    "fwd_gc": raw_results.get(f"PRIMER_LEFT_{i}_GC_PERCENT", 0.0),
                    "rev_gc": raw_results.get(f"PRIMER_RIGHT_{i}_GC_PERCENT", 0.0),
                    "start": fwd_start,
                    "end": rev_start,
                    "product_size": raw_results.get(f"PRIMER_PAIR_{i}_PRODUCT_SIZE", 0),
                })
            except (KeyError, TypeError):
                continue
        
        return primers
    
    def _create_seminested_set(
        self,
        sequence: str,
        outer: Dict[str, Any],
        inner: Dict[str, Any],
        outer_amplicon: str
    ) -> Optional[NestedPrimerSet]:
        """Create NestedPrimerSet for semi-nested design."""
        try:
            inner_amplicon = outer_amplicon[inner["start"]:inner["end"]]
            
            # For semi-nested, one primer is shared
            if self.shared_position == "forward":
                # Shared forward: outer_fwd = inner_fwd
                return NestedPrimerSet(
                    # Outer
                    outer_forward=outer["fwd_seq"],
                    outer_reverse=outer["rev_seq"],
                    outer_tm_forward=outer["fwd_tm"],
                    outer_tm_reverse=outer["rev_tm"],
                    outer_gc_forward=outer["fwd_gc"],
                    outer_gc_reverse=outer["rev_gc"],
                    outer_start=outer["start"],
                    outer_end=outer["end"],
                    outer_product_size=outer["product_size"],
                    outer_amplicon_seq=outer_amplicon,
                    # Inner - forward is SHARED (same as outer forward)
                    inner_forward=outer["fwd_seq"],  # SHARED
                    inner_reverse=inner["rev_seq"],  # UNIQUE
                    inner_tm_forward=outer["fwd_tm"],
                    inner_tm_reverse=inner["rev_tm"],
                    inner_gc_forward=outer["fwd_gc"],
                    inner_gc_reverse=inner["rev_gc"],
                    inner_start=0,  # Starts at outer start
                    inner_end=inner["end"],
                    inner_product_size=inner["end"],  # From outer start to inner end
                    inner_amplicon_seq=inner_amplicon,
                )
            else:
                # Shared reverse: outer_rev = inner_rev
                return NestedPrimerSet(
                    # Outer
                    outer_forward=outer["fwd_seq"],
                    outer_reverse=outer["rev_seq"],
                    outer_tm_forward=outer["fwd_tm"],
                    outer_tm_reverse=outer["rev_tm"],
                    outer_gc_forward=outer["fwd_gc"],
                    outer_gc_reverse=outer["rev_gc"],
                    outer_start=outer["start"],
                    outer_end=outer["end"],
                    outer_product_size=outer["product_size"],
                    outer_amplicon_seq=outer_amplicon,
                    # Inner - reverse is SHARED (same as outer reverse)
                    inner_forward=inner["fwd_seq"],  # UNIQUE
                    inner_reverse=outer["rev_seq"],  # SHARED
                    inner_tm_forward=inner["fwd_tm"],
                    inner_tm_reverse=outer["rev_tm"],
                    inner_gc_forward=inner["fwd_gc"],
                    inner_gc_reverse=outer["rev_gc"],
                    inner_start=inner["start"],
                    inner_end=len(outer_amplicon),  # Ends at outer end
                    inner_product_size=len(outer_amplicon) - inner["start"],
                    inner_amplicon_seq=inner_amplicon,
                )
        except (KeyError, TypeError) as e:
            logger.warning(f"Failed to create semi-nested set: {e}")
            return None
    
    def _score_seminested_sets(
        self, 
        sets: List[NestedPrimerSet]
    ) -> List[NestedPrimerSet]:
        """Score semi-nested primer sets."""
        for ns in sets:
            score = 100.0
            
            # Tm uniformity (max -20)
            outer_tm_diff = abs(ns.outer_tm_forward - ns.outer_tm_reverse)
            inner_tm_diff = abs(ns.inner_tm_forward - ns.inner_tm_reverse)
            score -= min(outer_tm_diff * 5, 10)
            score -= min(inner_tm_diff * 5, 10)
            
            # GC content 40-60% (max -10)
            for gc in [ns.outer_gc_forward, ns.outer_gc_reverse, 
                       ns.inner_gc_forward, ns.inner_gc_reverse]:
                if gc < 40 or gc > 60:
                    score -= 2.5
            
            # Size ratio bonus for semi-nested (inner should be ~50-80% of outer)
            size_ratio = ns.inner_product_size / ns.outer_product_size
            if 0.4 < size_ratio < 0.9:
                score += 5  # Bonus for good ratio
            
            ns.combined_score = max(score, 0)
            
            # Grade
            if score >= 90:
                ns.grade = "A"
            elif score >= 80:
                ns.grade = "B"
            elif score >= 70:
                ns.grade = "C"
            elif score >= 60:
                ns.grade = "D"
            else:
                ns.grade = "F"
        
        return sets


def design_seminested_primers(
    sequence: str,
    outer_size_range: Tuple[int, int] = (400, 600),
    inner_size_range: Tuple[int, int] = (150, 300),
    shared_position: str = "forward",
    tm_opt: float = 60.0,
) -> NestedPCRResult:
    """
    Design semi-nested PCR primers.
    
    Args:
        sequence: Template sequence
        outer_size_range: (min, max) for outer amplicon
        inner_size_range: (min, max) for inner amplicon
        shared_position: Which primer is shared ("forward" or "reverse")
        tm_opt: Optimal Tm for all primers
        
    Returns:
        NestedPCRResult with primer set
    """
    config = {
        "outer_size_min": outer_size_range[0],
        "outer_size_max": outer_size_range[1],
        "inner_size_min": inner_size_range[0],
        "inner_size_max": inner_size_range[1],
        "shared_position": shared_position,
        "shared_tm_opt": tm_opt,
        "unique_tm_opt": tm_opt,
    }
    
    engine = SemiNestedPCREngine(config)
    return engine.design(sequence)
