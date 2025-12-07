import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from primerlab.core.models import WorkflowResult
from primerlab.core.logger import get_logger
from primerlab.core.exceptions import PrimerLabException

logger = get_logger()

class OutputManager:
    """
    Handles creation of run directories and saving of results.
    """
    def __init__(self, base_dir: str, workflow_name: str):
        self.base_dir = Path(base_dir)
        self.workflow_name = workflow_name
        self.run_dir = self._create_run_dir()
        
    def _create_run_dir(self) -> Path:
        """Creates a timestamped run directory."""
        # Format: YYYYMMDD_HHMMSS_WORKFLOW (e.g., 20251127_115143_PCR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"{timestamp}_{self.workflow_name.upper()}"
        full_path = self.base_dir / run_name
        
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Output directory created: {full_path}")
            return full_path
        except Exception as e:
            raise PrimerLabException(f"Failed to create output directory: {e}")

    def save_json(self, result: WorkflowResult, filename: str = "result.json"):
        """Saves WorkflowResult to a JSON file."""
        file_path = self.run_dir / filename
        try:
            data = result.to_dict()
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Result saved to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")

    def save_csv(self, result: WorkflowResult, filename: str = "primers.csv"):
        """Saves primers to a CSV file for easy spreadsheet viewing."""
        file_path = self.run_dir / filename
        try:
            primers = result.primers
            if not primers:
                logger.warning("No primers to export to CSV.")
                return
            
            # Define CSV columns
            fieldnames = [
                "Name", "Sequence", "Length", "Tm", "GC%", 
                "Hairpin_dG", "Homodimer_dG", "Heterodimer_dG",
                "Start", "End", "Warnings"
            ]
            
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for name, primer in primers.items():
                    writer.writerow({
                        "Name": primer.id,
                        "Sequence": primer.sequence,
                        "Length": primer.length,
                        "Tm": round(primer.tm, 2),
                        "GC%": round(primer.gc, 2),
                        "Hairpin_dG": round(primer.hairpin_dg, 2) if primer.hairpin_dg else "",
                        "Homodimer_dG": round(primer.homodimer_dg, 2) if primer.homodimer_dg else "",
                        "Heterodimer_dG": round(primer.heterodimer_dg, 2) if primer.heterodimer_dg else "",
                        "Start": primer.start if primer.start else "",
                        "End": primer.end if primer.end else "",
                        "Warnings": "; ".join(primer.warnings) if primer.warnings else ""
                    })
            
            logger.info(f"CSV export saved to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save CSV: {e}")

    def save_ordering_format(self, result: WorkflowResult, vendor: str = "idt"):
        """
        Saves primers in vendor-specific ordering format.
        Supported vendors: idt, sigma, thermo
        """
        primers = result.primers
        if not primers:
            logger.warning("No primers to export for ordering.")
            return
        
        vendor = vendor.lower()
        filename = f"order_{vendor}.csv"
        file_path = self.run_dir / filename
        
        try:
            with open(file_path, 'w', newline='') as f:
                if vendor == "idt":
                    # IDT format: Name, Sequence, Scale, Purification
                    writer = csv.writer(f)
                    writer.writerow(["Name", "Sequence", "Scale", "Purification"])
                    for name, primer in primers.items():
                        writer.writerow([primer.id, primer.sequence, "25nm", "STD"])
                
                elif vendor == "sigma":
                    # Sigma format: Oligo Name, Sequence (5' to 3')
                    writer = csv.writer(f)
                    writer.writerow(["Oligo Name", "Sequence (5' to 3')"])
                    for name, primer in primers.items():
                        writer.writerow([primer.id, primer.sequence])
                
                elif vendor == "thermo":
                    # Thermo Fisher format: Name, Sequence, Scale
                    writer = csv.writer(f)
                    writer.writerow(["Name", "Sequence", "Scale"])
                    for name, primer in primers.items():
                        writer.writerow([primer.id, primer.sequence, "25 nmole"])
                
                else:
                    logger.warning(f"Unknown vendor '{vendor}'. Using generic format.")
                    writer = csv.writer(f)
                    writer.writerow(["Name", "Sequence"])
                    for name, primer in primers.items():
                        writer.writerow([primer.id, primer.sequence])
            
            logger.info(f"Ordering format ({vendor.upper()}) saved to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save ordering format: {e}")

    def save_debug_data(self, data: Dict[str, Any], filename: str = "debug_raw.json"):
        """Saves raw debug data."""
        debug_dir = self.run_dir / "debug"
        debug_dir.mkdir(exist_ok=True)
        
        file_path = debug_dir / filename
        try:
            with open(file_path, 'w') as f:
                # Handle non-serializable objects if necessary, but for now assume dict is clean
                json.dump(data, f, indent=2, default=str)
            logger.debug(f"Debug data saved to: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to save debug data: {e}")
