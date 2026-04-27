"""
Wrapper for Primer3's ThermoAnalysis engine.
Provides a unified interface for calculating thermodynamics of primers and probes.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import primer3

from primerlab.core.logger import get_logger

logger = get_logger()

@dataclass
class ThermoResult:
    """Result of a thermodynamic calculation."""
    tm: float
    dg: float
    dh: float
    ds: float
    structure_found: bool
    ascii_structure: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tm": self.tm,
            "dg": self.dg,
            "dh": self.dh,
            "ds": self.ds,
            "structure_found": self.structure_found,
            "ascii_structure": self.ascii_structure
        }


class ThermocalcWrapper:
    """
    Wrapper for primer3.thermoanalysis.ThermoAnalysis.
    Handles thermodynamic calculations for oligonucleotides.
    """
    
    def __init__(
        self,
        mv_conc: float = 50.0,
        dv_conc: float = 1.5,
        dntp_conc: float = 0.6,
        dna_conc: float = 50.0,
        tm_method: str = 'santalucia',
        salt_corrections: str = 'santalucia'
    ):
        """
        Initialize the ThermoAnalysis wrapper with specific buffer conditions.
        
        Args:
            mv_conc: Monovalent cation concentration (mM)
            dv_conc: Divalent cation concentration (mM)
            dntp_conc: dNTP concentration (mM)
            dna_conc: DNA/oligo concentration (nM)
            tm_method: Method for Tm calculation ('santalucia' or 'breslauer')
            salt_corrections: Method for salt correction ('santalucia', 'owczarzy', 'schildkraut')
        """
        self.mv_conc = mv_conc
        self.dv_conc = dv_conc
        self.dntp_conc = dntp_conc
        self.dna_conc = dna_conc
        self.tm_method = tm_method
        self.salt_corrections = salt_corrections
        
        # Determine internal method IDs based on string names
        # Default primer3-py uses 1 for santalucia, 0 for breslauer/schildkraut
        tm_method_id = 1 if tm_method.lower() == 'santalucia' else 0
        
        salt_corr_id = 1 # santalucia
        if salt_corrections.lower() == 'owczarzy':
            salt_corr_id = 2
        elif salt_corrections.lower() == 'schildkraut':
            salt_corr_id = 0
            
        try:
            self.ta = primer3.thermoanalysis.ThermoAnalysis()
            self.ta.mv_conc = self.mv_conc
            self.ta.dv_conc = self.dv_conc
            self.ta.dntp_conc = self.dntp_conc
            self.ta.dna_conc = self.dna_conc
            self.ta.tm_method = tm_method_id
            self.ta.salt_correction_method = salt_corr_id
        except Exception as e:
            logger.error(f"Failed to initialize ThermoAnalysis: {e}")
            raise
            
    def calc_tm(self, seq: str) -> float:
        """Calculate melting temperature (Tm) of a sequence."""
        try:
            # Check if calc_tm or calcTm is the method name in this primer3 version
            if hasattr(self.ta, 'calc_tm'):
                return self.ta.calc_tm(seq)
            else:
                return self.ta.calcTm(seq)
        except Exception as e:
            logger.error(f"Error calculating Tm for {seq}: {e}")
            return 0.0
            
    def calc_hairpin(self, seq: str) -> ThermoResult:
        """Calculate hairpin formation thermodynamics."""
        try:
            if hasattr(self.ta, 'calc_hairpin'):
                res = self.ta.calc_hairpin(seq)
            else:
                res = self.ta.calcHairpin(seq)
                
            return ThermoResult(
                tm=res.tm,
                dg=res.dg,
                dh=res.dh,
                ds=res.ds,
                structure_found=res.structure_found,
                ascii_structure=res.ascii_structure if hasattr(res, 'ascii_structure') else getattr(res, 'structure', None)
            )
        except Exception as e:
            logger.debug(f"No hairpin found or error for {seq}: {e}")
            return ThermoResult(tm=-273.15, dg=0.0, dh=0.0, ds=0.0, structure_found=False)
            
    def calc_homodimer(self, seq: str) -> ThermoResult:
        """Calculate homodimer formation thermodynamics."""
        try:
            if hasattr(self.ta, 'calc_homodimer'):
                res = self.ta.calc_homodimer(seq)
            else:
                res = self.ta.calcHomodimer(seq)
                
            return ThermoResult(
                tm=res.tm,
                dg=res.dg,
                dh=res.dh,
                ds=res.ds,
                structure_found=res.structure_found,
                ascii_structure=res.ascii_structure if hasattr(res, 'ascii_structure') else getattr(res, 'structure', None)
            )
        except Exception as e:
            logger.debug(f"No homodimer found or error for {seq}: {e}")
            return ThermoResult(tm=-273.15, dg=0.0, dh=0.0, ds=0.0, structure_found=False)
            
    def calc_heterodimer(self, seq1: str, seq2: str) -> ThermoResult:
        """Calculate heterodimer formation thermodynamics between two sequences."""
        try:
            if hasattr(self.ta, 'calc_heterodimer'):
                res = self.ta.calc_heterodimer(seq1, seq2)
            else:
                res = self.ta.calcHeterodimer(seq1, seq2)
                
            return ThermoResult(
                tm=res.tm,
                dg=res.dg,
                dh=res.dh,
                ds=res.ds,
                structure_found=res.structure_found,
                ascii_structure=res.ascii_structure if hasattr(res, 'ascii_structure') else getattr(res, 'structure', None)
            )
        except Exception as e:
            logger.debug(f"No heterodimer found or error for {seq1} and {seq2}: {e}")
            return ThermoResult(tm=-273.15, dg=0.0, dh=0.0, ds=0.0, structure_found=False)
            
    def calc_end_stability(self, seq: str) -> ThermoResult:
        """Calculate 3' end stability (ΔG) of a sequence.
        By default, it calculates the stability of the last 5 bases.
        """
        try:
            # Extract last 5 bases
            if len(seq) > 5:
                end_seq = seq[-5:]
            else:
                end_seq = seq
                
            # Create perfect complement
            complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'N': 'N'}
            comp_seq = "".join(complement.get(base, 'N') for base in reversed(end_seq))
            
            if hasattr(self.ta, 'calc_end_stability'):
                res = self.ta.calc_end_stability(end_seq, comp_seq)
            else:
                res = self.ta.calcEndStability(end_seq, comp_seq)
                
            return ThermoResult(
                tm=res.tm,
                dg=res.dg,
                dh=res.dh,
                ds=res.ds,
                structure_found=res.structure_found,
                ascii_structure=None
            )
        except Exception as e:
            logger.debug(f"End stability calculation error for {seq}: {e}")
            return ThermoResult(tm=-273.15, dg=0.0, dh=0.0, ds=0.0, structure_found=False)
