"""
Enhanced Report Generation.

Generates HTML reports with sortable tables and styling.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
from primerlab.core.logger import get_logger

logger = get_logger()


@dataclass
class ReportSection:
    """A section in the report."""
    title: str
    content: str
    section_type: str = "text"  # text, table, code


@dataclass
class ReportData:
    """Data for report generation."""
    title: str
    subtitle: str = ""
    sections: List[ReportSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class HTMLReportGenerator:
    """
    Generates interactive HTML reports with sortable tables.
    """
    
    CSS_STYLES = """
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; 
            color: #333; 
            background: #f5f7fa;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .header h1 { font-size: 2em; margin-bottom: 5px; }
        .header .subtitle { opacity: 0.9; }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .card h2 { 
            color: #667eea;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
        }
        th:hover { background: #e9ecef; }
        th.sorted-asc::after { content: ' ↑'; }
        th.sorted-desc::after { content: ' ↓'; }
        tr:hover { background: #f8f9fa; }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-warning { background: #fff3cd; color: #856404; }
        .badge-danger { background: #f8d7da; color: #721c24; }
        .badge-info { background: #d1ecf1; color: #0c5460; }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .metric-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .metric-value { font-size: 2em; font-weight: bold; color: #667eea; }
        .metric-label { color: #666; font-size: 0.9em; }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Fira Code', monospace;
        }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
        }
        .footer {
            text-align: center;
            color: #666;
            padding: 20px;
            font-size: 0.9em;
        }
    </style>
    """
    
    SORTABLE_JS = """
    <script>
    function sortTable(table, column, asc = true) {
        const dirModifier = asc ? 1 : -1;
        const tbody = table.tBodies[0];
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        const sortedRows = rows.sort((a, b) => {
            const aColText = a.querySelector(`td:nth-child(${column + 1})`).textContent.trim();
            const bColText = b.querySelector(`td:nth-child(${column + 1})`).textContent.trim();
            
            const aNum = parseFloat(aColText);
            const bNum = parseFloat(bColText);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return (aNum - bNum) * dirModifier;
            }
            return aColText.localeCompare(bColText) * dirModifier;
        });
        
        while (tbody.firstChild) {
            tbody.removeChild(tbody.firstChild);
        }
        tbody.append(...sortedRows);
        
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sorted-asc', 'sorted-desc');
        });
        table.querySelector(`th:nth-child(${column + 1})`).classList.add(asc ? 'sorted-asc' : 'sorted-desc');
    }
    
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('th').forEach((th, index) => {
            let asc = true;
            th.addEventListener('click', () => {
                const table = th.closest('table');
                sortTable(table, index, asc);
                asc = !asc;
            });
        });
    });
    </script>
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize generator."""
        self.config = config or {}
    
    def generate(self, data: ReportData) -> str:
        """
        Generate HTML report from data.
        
        Args:
            data: ReportData with sections
            
        Returns:
            HTML string
        """
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'<title>{data.title}</title>',
            self.CSS_STYLES,
            '</head>',
            '<body>',
            '<div class="container">',
            f'<div class="header">',
            f'<h1>{data.title}</h1>',
            f'<div class="subtitle">{data.subtitle}</div>',
            '</div>',
        ]
        
        # Add sections
        for section in data.sections:
            html_parts.append(f'<div class="card">')
            html_parts.append(f'<h2>{section.title}</h2>')
            html_parts.append(section.content)
            html_parts.append('</div>')
        
        html_parts.extend([
            '<div class="footer">',
            'Generated by PrimerLab v0.7.2',
            '</div>',
            '</div>',
            self.SORTABLE_JS,
            '</body>',
            '</html>',
        ])
        
        return '\n'.join(html_parts)
    
    def create_table(
        self,
        headers: List[str],
        rows: List[List[Any]],
    ) -> str:
        """Create sortable table HTML."""
        html = ['<table>']
        html.append('<thead><tr>')
        for h in headers:
            html.append(f'<th>{h}</th>')
        html.append('</tr></thead>')
        
        html.append('<tbody>')
        for row in rows:
            html.append('<tr>')
            for cell in row:
                html.append(f'<td>{cell}</td>')
            html.append('</tr>')
        html.append('</tbody>')
        html.append('</table>')
        
        return '\n'.join(html)
    
    def create_metrics(self, metrics: Dict[str, Any]) -> str:
        """Create metric cards HTML."""
        html = ['<div class="metric-grid">']
        for label, value in metrics.items():
            html.append(f'''
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
            ''')
        html.append('</div>')
        return '\n'.join(html)
    
    def create_badge(self, text: str, badge_type: str = "info") -> str:
        """Create badge HTML."""
        return f'<span class="badge badge-{badge_type}">{text}</span>'


def generate_html_report(
    title: str,
    result_data: Dict[str, Any],
) -> str:
    """
    Generate HTML report from primer design result.
    
    Args:
        title: Report title
        result_data: Result data dict
        
    Returns:
        HTML string
    """
    generator = HTMLReportGenerator()
    
    # Extract data
    primers = result_data.get("primers", {})
    qc = result_data.get("qc", {})
    amplicons = result_data.get("amplicons", [])
    
    sections = []
    
    # Summary metrics
    metrics = {
        "Quality Score": qc.get("quality_score", "N/A"),
        "Grade": qc.get("quality_category", "N/A"),
        "Product Size": f"{amplicons[0].get('length', 'N/A')} bp" if amplicons else "N/A",
        "Primers": len(primers),
    }
    metrics_section = ReportSection(
        title="Summary",
        content=generator.create_metrics(metrics),
    )
    sections.append(metrics_section)
    
    # Primers table
    if primers:
        headers = ["Primer", "Sequence", "Tm (°C)", "GC (%)"]
        rows = []
        for name, p in primers.items():
            rows.append([
                name.capitalize(),
                f"<code>{p.get('sequence', 'N/A')}</code>",
                f"{p.get('tm', 0):.1f}",
                f"{p.get('gc', 0):.1f}",
            ])
        primers_section = ReportSection(
            title="Designed Primers",
            content=generator.create_table(headers, rows),
        )
        sections.append(primers_section)
    
    data = ReportData(
        title=title,
        subtitle="Primer Design Report",
        sections=sections,
    )
    
    return generator.generate(data)
