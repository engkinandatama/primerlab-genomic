"""
qPCR Report Generator using standardized template.
v0.9.3+ - Report Standardization
"""

from typing import Dict, Any
from primerlab.core.models import WorkflowResult
from primerlab.core.report.base_report import BaseReportTemplate
from primerlab.core.logger import get_logger

logger = get_logger()


class qPCRReportGenerator:
    """
    Generates qPCR-specific reports using standardized template.
    """

    def generate_report(self, result: WorkflowResult) -> str:
        """
        Generates a Markdown report for qPCR workflow results.
        
        Uses BaseReportTemplate for standardized formatting,
        with qPCR-specific additions.
        """
        # Use base template
        template = qPCRReportTemplate(result)
        return template.build("qPCR Primer Design Report")


class qPCRReportTemplate(BaseReportTemplate):
    """
    qPCR-specific report template extending base template.
    """
    
    def build(self, title: str) -> str:
        """Build qPCR report with additional qPCR-specific sections."""
        self.lines = []
        
        # Standard sections
        self.generate_header(title)
        self.generate_executive_summary()
        self.generate_input_parameters()
        self.generate_primer_table()
        self.generate_amplicon_visualization()
        
        # qPCR-specific: Efficiency metrics
        self.generate_qpcr_metrics()
        
        # Standard sections continued
        self.generate_qc_section()
        self.generate_alternatives()
        self.generate_footer()
        
        return "\n".join(self.lines)
    
    def generate_qpcr_metrics(self) -> None:
        """Generate qPCR-specific metrics section."""
        self.lines.append("---")
        self.lines.append("")
        self.lines.append("## qPCR-Specific Metrics")
        self.lines.append("")
        
        # Efficiency
        efficiency = None
        if hasattr(self.result, 'efficiency') and self.result.efficiency:
            efficiency = self.result.efficiency
        
        self.lines.append("| Metric | Value | Status |")
        self.lines.append("|:-------|------:|:------:|")
        
        if efficiency:
            if 90 <= efficiency <= 110:
                status = "✅ Optimal"
            elif 80 <= efficiency < 90 or 110 < efficiency <= 120:
                status = "⚠️ Acceptable"
            else:
                status = "❌ Outside range"
            self.lines.append(f"| **PCR Efficiency** | {efficiency}% | {status} |")
        else:
            self.lines.append("| **PCR Efficiency** | N/A | - |")
        
        # Amplicon info for qPCR
        if self.result.amplicons:
            amp = self.result.amplicons[0]
            
            # qPCR prefers short amplicons
            if amp.length and amp.length <= 150:
                size_status = "✅ Optimal for qPCR"
            elif amp.length and amp.length <= 200:
                size_status = "⚠️ Acceptable"
            else:
                size_status = "⚠️ Consider shorter"
            
            self.lines.append(f"| **Amplicon Length** | {amp.length} bp | {size_status} |")
        
        # Probe info
        probe = self.result.primers.get("probe") if self.result.primers else None
        if probe:
            self.lines.append(f"| **Probe Tm** | {probe.tm:.1f}°C | ✅ Included |")
        else:
            self.lines.append("| **Probe** | N/A | Not designed |")
        
        self.lines.append("")
