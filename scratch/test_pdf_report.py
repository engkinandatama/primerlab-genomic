import os
import sys
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from primerlab.core.report.generator import ReportGenerator
from primerlab.core.report.models import ReportFormat, PrimerInfo

def test_pdf():
    print("Testing PDF Generation...")
    
    # 1. Create a dummy report
    gen = ReportGenerator()
    gen.add_design(
        forward_seq="ATGGTGAGCAAGGGCGAGGAG",
        reverse_seq="TTACTTGTACAGCTCGTCCATGCC",
        forward_tm=60.5,
        reverse_tm=59.8,
        forward_gc=55.2,
        reverse_gc=52.4,
        product_size=720,
        quality_score=92.5
    )
    
    gen.add_validation(
        amplicons=1,
        product_size=720,
        success_probability=0.98
    )
    
    gen.add_offtarget(
        database="RefSeq Genome",
        forward_hits=0,
        reverse_hits=0,
        grade="A",
        score=100.0
    )
    
    gen.report.warnings = ["Product size is slightly larger than optimal for RAA."]
    gen.report.recommendations = ["Consider optimizing Mg2+ concentration for better yield."]
    
    # 2. Save as PDF
    output_pdf = "test_report.pdf"
    try:
        print(f"Generating PDF to {output_pdf}...")
        gen.save(output_pdf, format=ReportFormat.PDF)
        print(f"Success! Report saved to {output_pdf}")
    except Exception as e:
        print(f"Failed: {e}")
        print("\nNote: You might need to install dependencies:")
        print("pip install jinja2 weasyprint")

if __name__ == "__main__":
    test_pdf()
