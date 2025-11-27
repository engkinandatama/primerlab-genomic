from typing import Dict, Any, List
from primerlab.core.models import Primer, QCResult
from primerlab.core.logger import get_logger
from primerlab.core.tools.vienna_wrapper import ViennaWrapper

logger = get_logger()

class PCRQC:
    """
    Handles Quality Control checks for PCR primers.
    """
    def __init__(self, config: Dict[str, Any]):
        self.qc_config = config.get("qc", {})
        self.tm_diff_max = self.qc_config.get("tm_diff_max", 5.0)
        self.hairpin_dg_min = self.qc_config.get("hairpin_dg_min", -3.0) 
        self.dimer_dg_min = self.qc_config.get("dimer_dg_min", -6.0)
        
        # Initialize ViennaRNA
        self.vienna = ViennaWrapper()

    def evaluate_pair(self, fwd: Primer, rev: Primer) -> QCResult:
        """
        Evaluates a primer pair against QC thresholds using ViennaRNA.
        """
        warnings = []
        errors = []

        # 1. Tm Balance Check
        tm_diff = abs(fwd.tm - rev.tm)
        tm_balance_ok = tm_diff <= self.tm_diff_max
        
        if not tm_balance_ok:
            msg = f"Tm difference ({tm_diff:.2f}°C) exceeds limit ({self.tm_diff_max}°C)"
            warnings.append(msg)

        # 2. Hairpin Check (ViennaRNA)
        # Calculate real MFE using RNAfold
        fwd_fold = self.vienna.fold(fwd.sequence)
        rev_fold = self.vienna.fold(rev.sequence)
        
        fwd_dg = fwd_fold["mfe"]
        rev_dg = rev_fold["mfe"]
        
        # Update Primer objects with real ΔG
        fwd.hairpin_dg = fwd_dg
        rev.hairpin_dg = rev_dg
        
        fwd_hairpin_ok = fwd_dg >= self.hairpin_dg_min
        rev_hairpin_ok = rev_dg >= self.hairpin_dg_min
        
        hairpin_ok = fwd_hairpin_ok and rev_hairpin_ok
        
        if not fwd_hairpin_ok:
            warnings.append(f"Forward primer hairpin ΔG ({fwd_dg}) too stable")
        if not rev_hairpin_ok:
            warnings.append(f"Reverse primer hairpin ΔG ({rev_dg}) too stable")

        # 3. Homodimer Check (ViennaRNA cofold)
        fwd_homo = self.vienna.cofold(fwd.sequence, fwd.sequence)
        rev_homo = self.vienna.cofold(rev.sequence, rev.sequence)
        
        fwd_homo_dg = fwd_homo["mfe"]
        rev_homo_dg = rev_homo["mfe"]
        
        # Update Primer objects
        fwd.homodimer_dg = fwd_homo_dg
        rev.homodimer_dg = rev_homo_dg
        
        fwd_homo_ok = fwd_homo_dg >= self.dimer_dg_min
        rev_homo_ok = rev_homo_dg >= self.dimer_dg_min
        
        homodimer_ok = fwd_homo_ok and rev_homo_ok
        
        if not fwd_homo_ok:
            warnings.append(f"Forward primer homodimer ΔG ({fwd_homo_dg}) too stable")
        if not rev_homo_ok:
            warnings.append(f"Reverse primer homodimer ΔG ({rev_homo_dg}) too stable")

        # 4. Heterodimer Check (Cross-Dimer)
        hetero = self.vienna.cofold(fwd.sequence, rev.sequence)
        hetero_dg = hetero["mfe"]
        
        # Update Primer objects (optional, usually stored in pair result)
        fwd.heterodimer_dg = hetero_dg
        rev.heterodimer_dg = hetero_dg
        
        heterodimer_ok = hetero_dg >= self.dimer_dg_min
        
        if not heterodimer_ok:
            warnings.append(f"Heterodimer (Fwd+Rev) ΔG ({hetero_dg}) too stable")

        # Construct Result
        result = QCResult(
            hairpin_ok=hairpin_ok,
            homodimer_ok=homodimer_ok,
            heterodimer_ok=heterodimer_ok,
            tm_balance_ok=tm_balance_ok,
            hairpin_dg=min(fwd_dg, rev_dg), # Worst case
            homodimer_dg=min(fwd_homo_dg, rev_homo_dg), # Worst case
            heterodimer_dg=hetero_dg,
            tm_diff=tm_diff,
            warnings=warnings,
            errors=errors
        )

        return result
