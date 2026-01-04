"""
qPCR-specific Quality Control module.

Extends BaseQC with qPCR-specific validation including probe checks,
amplicon size validation, and efficiency estimation.

This module follows the architecture principle that workflows import
from core/, not from other workflows.

Version: v0.3.6
"""

from typing import Dict, Any
from primerlab.core.models import Primer, QCResult
from primerlab.core.logger import get_logger
from primerlab.core.qc import BaseQC

logger = get_logger()


class qPCRQC(BaseQC):
    """
    Quality Control for qPCR primers and probes.
    
    Extends BaseQC with qPCR-specific validation:
    - Probe Tm validation (must be higher than primers)
    - Probe secondary structure check
    - Amplicon size validation (70-150bp optimal for qPCR)
    - PCR efficiency estimation
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize qPCRQC with configuration.
        
        Args:
            config: Full workflow configuration dict containing 'qc' section
        """
        super().__init__(config)

        # qPCR-specific thresholds
        self.amplicon_size_min = self.qc_config.get("amplicon_size_min", 70)
        self.amplicon_size_max = self.qc_config.get("amplicon_size_max", 150)
        self.probe_tm_min_diff = self.qc_config.get("probe_tm_min_diff", 8.0)

    def evaluate_probe(self, probe: Primer, fwd: Primer, rev: Primer) -> Dict[str, Any]:
        """
        Evaluates probe-specific QC metrics.
        
        Args:
            probe: Probe primer
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            Dict with probe QC results
        """
        warnings = []

        # 1. Probe Tm Check
        avg_primer_tm = (fwd.tm + rev.tm) / 2
        tm_diff = probe.tm - avg_primer_tm

        probe_tm_ok = tm_diff >= self.probe_tm_min_diff

        if not probe_tm_ok:
            msg = f"Probe Tm ({probe.tm:.2f}°C) is not significantly higher than primers ({avg_primer_tm:.2f}°C). Diff: {tm_diff:.2f}°C < {self.probe_tm_min_diff}°C"
            warnings.append(msg)

        # 2. Probe Secondary Structure (using ViennaRNA)
        probe_fold = self.vienna.fold(probe.sequence)
        probe_dg = probe_fold.get("mfe", 0.0)

        if "error" in probe_fold:
            warnings.append("Probe secondary structure QC skipped: ViennaRNA (RNAfold) not available or failed.")
            probe_hairpin_ok = True
        else:
            probe_hairpin_ok = probe_dg >= self.hairpin_dg_min

        if not probe_hairpin_ok:
            warnings.append(f"Probe hairpin ΔG ({probe_dg:.2f}) too stable (threshold: {self.hairpin_dg_min})")

        return {
            "probe_tm_ok": probe_tm_ok,
            "probe_hairpin_ok": probe_hairpin_ok,
            "tm_diff": tm_diff,
            "probe_dg": probe_dg,
            "warnings": warnings
        }

    def validate_amplicon_size(self, amplicon_size: int) -> Dict[str, Any]:
        """
        Validates amplicon size against qPCR-optimal range (70-150bp).
        
        Args:
            amplicon_size: Size of the amplicon in base pairs
            
        Returns:
            Dict with size validation results
        """
        size_ok = self.amplicon_size_min <= amplicon_size <= self.amplicon_size_max

        warnings = []
        if not size_ok:
            if amplicon_size < self.amplicon_size_min:
                warnings.append(f"Amplicon size ({amplicon_size}bp) is too short for reliable qPCR (min: {self.amplicon_size_min}bp)")
            else:
                warnings.append(f"Amplicon size ({amplicon_size}bp) is too long for optimal qPCR efficiency (max: {self.amplicon_size_max}bp)")

        return {
            "size_ok": size_ok,
            "size": amplicon_size,
            "warnings": warnings
        }

    def estimate_efficiency(self, fwd: Primer, rev: Primer, probe: Primer = None) -> float:
        """
        Estimates PCR efficiency based on thermodynamic properties.
        
        Simple model:
        - Base efficiency: 95%
        - Penalty for unstable hairpins
        - Penalty for dimers
        - Bonus for good Tm balance
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            probe: Optional probe (not currently used in calculation)
            
        Returns:
            Estimated efficiency percentage (80-110%)
        """
        base_efficiency = 95.0

        # Hairpin penalty
        hairpin_penalty = 0.0
        if fwd.hairpin_dg < self.hairpin_dg_min:
            hairpin_penalty += abs(fwd.hairpin_dg - self.hairpin_dg_min) * 0.5
        if rev.hairpin_dg < self.hairpin_dg_min:
            hairpin_penalty += abs(rev.hairpin_dg - self.hairpin_dg_min) * 0.5

        # Dimer penalty
        dimer_penalty = 0.0
        if fwd.homodimer_dg < self.dimer_dg_min:
            dimer_penalty += abs(fwd.homodimer_dg - self.dimer_dg_min) * 0.3
        if rev.homodimer_dg < self.dimer_dg_min:
            dimer_penalty += abs(rev.homodimer_dg - self.dimer_dg_min) * 0.3

        # Tm balance bonus
        tm_diff = abs(fwd.tm - rev.tm)
        tm_bonus = 0.0
        if tm_diff <= 1.0:
            tm_bonus = 3.0
        elif tm_diff <= 2.0:
            tm_bonus = 1.0

        # Calculate final efficiency
        efficiency = base_efficiency - hairpin_penalty - dimer_penalty + tm_bonus

        # Clamp to realistic range (80-110%)
        efficiency = max(80.0, min(110.0, efficiency))

        return round(efficiency, 1)
