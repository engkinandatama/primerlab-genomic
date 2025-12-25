"""
Unit tests for compat check report generation.
"""

import json
import pytest
from pathlib import Path
from primerlab.core.compat_check.models import MultiplexResult, MultiplexPair
from primerlab.core.compat_check.report import generate_json_report, generate_markdown_report

@pytest.fixture
def mock_compat_result():
    return MultiplexResult(
        pairs=[
            MultiplexPair("P1", "ATGC", "GCTA", tm_forward=60.0, tm_reverse=60.0, gc_forward=50.0, gc_reverse=50.0)
        ],
        score=85.0,
        grade="B",
        is_valid=True,
        warnings=["Minor Tm difference"],
        errors=[],
        recommendations=["Adjust P1 forward"],
        component_scores={"dimer_score": 35.0, "tm_uniformity": 20.0, "gc_uniformity": 15.0}
    )

def test_generate_json_report(tmp_path, mock_compat_result):
    """Test JSON report generation."""
    output_path = generate_json_report(mock_compat_result, tmp_path)
    
    assert output_path.exists()
    assert output_path.name == "compat_analysis.json"
    
    with open(output_path) as f:
        data = json.load(f)
        assert data["score"] == 85.0
        assert data["grade"] == "B"
        assert len(data["warnings"]) == 1

def test_generate_markdown_report(tmp_path, mock_compat_result):
    """Test Markdown report generation."""
    output_path = generate_markdown_report(mock_compat_result, tmp_path)
    
    assert output_path.exists()
    assert output_path.name == "compat_report.md"
    
    with open(output_path, encoding='utf-8') as f:
        content = f.read()
        assert "Compatibility Report" in content
        assert "COMPATIBLE" in content
        assert "**85.0/100**" in content
        assert "**B**" in content
        assert "Minor Tm difference" in content
        assert "Adjust P1 forward" in content
