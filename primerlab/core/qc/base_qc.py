"""
Base Quality Control module for PrimerLab.

This module contains the shared QC functionality used by all workflow-specific
QC modules (PCR, qPCR, etc.). It follows the architecture rule that core modules
must be workflow-agnostic and reusable.

Version: v0.3.6
"""

from typing import Dict, Any, List, Optional
from primerlab.core.models import Primer, QCResult
from primerlab.core.logger import get_logger
from primerlab.core.tools.vienna_wrapper import ViennaWrapper

logger = get_logger()


class BaseQC:
    """
    Base Quality Control class for primer pair evaluation.
    
    Provides shared functionality for:
    - ViennaRNA thermodynamic analysis (hairpin, homodimer, heterodimer)
    - Tm balance checking
    - Configurable thresholds
    
    Workflow-specific QC modules should extend this class and add
    their specific validation logic.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize BaseQC with configuration.
        
        Args:
            config: Full workflow configuration dict containing 'qc' section
        """
        self.config = config
        self.qc_config = config.get("qc", {})

        # Common QC thresholds
        self.tm_diff_max = self.qc_config.get("tm_diff_max", 5.0)
        self.hairpin_dg_min = self.qc_config.get("hairpin_dg_min", -3.0)
        self.dimer_dg_min = self.qc_config.get("dimer_dg_min", -6.0)

        # Initialize ViennaRNA wrapper
        self.vienna = ViennaWrapper()

    def check_tm_balance(self, fwd: Primer, rev: Primer) -> Dict[str, Any]:
        """
        Check melting temperature balance between primers.
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            Dict with tm_balance_ok, tm_diff, and warnings
        """
        tm_diff = abs(fwd.tm - rev.tm)
        tm_balance_ok = tm_diff <= self.tm_diff_max

        warnings = []
        if not tm_balance_ok:
            msg = f"Tm difference ({tm_diff:.2f}°C) exceeds limit ({self.tm_diff_max}°C)"
            warnings.append(msg)

        return {
            "tm_balance_ok": tm_balance_ok,
            "tm_diff": tm_diff,
            "warnings": warnings
        }

    def check_hairpin(self, fwd: Primer, rev: Primer) -> Dict[str, Any]:
        """
        Check hairpin formation using ViennaRNA RNAfold.
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            Dict with hairpin_ok, fwd_dg, rev_dg, and warnings
        """
        warnings = []

        # Calculate MFE using RNAfold
        fwd_fold = self.vienna.fold(fwd.sequence)
        rev_fold = self.vienna.fold(rev.sequence)

        fwd_dg = fwd_fold.get("mfe", 0.0)
        rev_dg = rev_fold.get("mfe", 0.0)

        # Check if ViennaRNA failed or is missing
        if "error" in fwd_fold or "error" in rev_fold:
            warnings.append("Secondary structure QC skipped: ViennaRNA (RNAfold) not available or failed.")
            fwd_hairpin_ok = True
            rev_hairpin_ok = True
        else:
            fwd_hairpin_ok = fwd_dg >= self.hairpin_dg_min
            rev_hairpin_ok = rev_dg >= self.hairpin_dg_min

        hairpin_ok = fwd_hairpin_ok and rev_hairpin_ok

        if not fwd_hairpin_ok:
            warnings.append(f"Forward primer hairpin ΔG ({fwd_dg}) too stable")
        if not rev_hairpin_ok:
            warnings.append(f"Reverse primer hairpin ΔG ({rev_dg}) too stable")

        return {
            "hairpin_ok": hairpin_ok,
            "fwd_dg": fwd_dg,
            "rev_dg": rev_dg,
            "warnings": warnings
        }

    def check_homodimer(self, fwd: Primer, rev: Primer) -> Dict[str, Any]:
        """
        Check homodimer formation using ViennaRNA RNAcofold.
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            Dict with homodimer_ok, fwd_homo_dg, rev_homo_dg, and warnings
        """
        warnings = []

        # Calculate homodimer MFE
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

        return {
            "homodimer_ok": homodimer_ok,
            "fwd_homo_dg": fwd_homo_dg,
            "rev_homo_dg": rev_homo_dg,
            "warnings": warnings
        }

    def check_heterodimer(self, fwd: Primer, rev: Primer) -> Dict[str, Any]:
        """
        Check heterodimer formation between primers using ViennaRNA RNAcofold.
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            Dict with heterodimer_ok, hetero_dg, and warnings
        """
        warnings = []

        # Calculate heterodimer MFE
        hetero = self.vienna.cofold(fwd.sequence, rev.sequence)
        hetero_dg = hetero["mfe"]

        # Update Primer objects
        fwd.heterodimer_dg = hetero_dg
        rev.heterodimer_dg = hetero_dg

        heterodimer_ok = hetero_dg >= self.dimer_dg_min

        if not heterodimer_ok:
            warnings.append(f"Heterodimer (Fwd+Rev) ΔG ({hetero_dg}) too stable")

        return {
            "heterodimer_ok": heterodimer_ok,
            "hetero_dg": hetero_dg,
            "warnings": warnings
        }

    def evaluate_pair(self, fwd: Primer, rev: Primer) -> QCResult:
        """
        Evaluate a primer pair against all QC thresholds.
        
        This is the main entry point for checking a primer pair.
        
        Args:
            fwd: Forward primer
            rev: Reverse primer
            
        Returns:
            QCResult with all evaluation results
        """
        all_warnings = []
        errors = []

        # 1. Tm Balance
        tm_result = self.check_tm_balance(fwd, rev)
        all_warnings.extend(tm_result["warnings"])

        # 2. Hairpin
        hairpin_result = self.check_hairpin(fwd, rev)
        all_warnings.extend(hairpin_result["warnings"])

        # 3. Homodimer
        homodimer_result = self.check_homodimer(fwd, rev)
        all_warnings.extend(homodimer_result["warnings"])

        # 4. Heterodimer
        heterodimer_result = self.check_heterodimer(fwd, rev)
        all_warnings.extend(heterodimer_result["warnings"])

        # Construct Result
        result = QCResult(
            hairpin_ok=hairpin_result["hairpin_ok"],
            homodimer_ok=homodimer_result["homodimer_ok"],
            heterodimer_ok=heterodimer_result["heterodimer_ok"],
            tm_balance_ok=tm_result["tm_balance_ok"],
            hairpin_dg=min(hairpin_result["fwd_dg"], hairpin_result["rev_dg"]),
            homodimer_dg=min(homodimer_result["fwd_homo_dg"], homodimer_result["rev_homo_dg"]),
            heterodimer_dg=heterodimer_result["hetero_dg"],
            tm_diff=tm_result["tm_diff"],
            warnings=all_warnings,
            errors=errors
        )

        return result
