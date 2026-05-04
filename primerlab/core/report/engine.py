import os
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

class ReportEngine:
    """
    Engine for rendering reports using Jinja2 templates.
    """

    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the report engine.
        
        Args:
            template_dir: Path to the directory containing templates.
                         Defaults to primerlab/core/report/templates/
        """
        if template_dir is None:
            template_dir = os.path.join(
                os.path.dirname(__file__), "templates"
            )
        
        self.template_dir = template_dir
        # Ensure template directory exists
        os.makedirs(self.template_dir, exist_ok=True)
        
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml', 'j2']),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template file (e.g., 'report.html.j2')
            context: Dictionary of data to pass to the template
            
        Returns:
            Rendered string
        """
        template = self.env.get_template(template_name)
        return template.render(**context)

    def generate_pdf(self, html_content: str, output_path: str):
        """
        Convert HTML content to PDF using xhtml2pdf.
        
        Args:
            html_content: HTML string to convert
            output_path: Path to save the PDF file
        """
        try:
            from xhtml2pdf import pisa
            
            with open(output_path, "wb") as result_file:
                pisa_status = pisa.CreatePDF(
                    html_content,
                    dest=result_file
                )
                
            if pisa_status.err:
                raise RuntimeError(f"PDF generation failed with error code {pisa_status.err}")
                
        except ImportError:
            raise ImportError(
                "xhtml2pdf is required for PDF generation. "
                "Install it with 'pip install xhtml2pdf'."
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate PDF: {e}")
