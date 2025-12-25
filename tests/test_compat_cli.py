"""
Integration tests for CLI check-compat command.
"""
import json
import pytest
import subprocess
import sys
from unittest.mock import patch
from primerlab.cli.main import main

@pytest.fixture
def primers_json(tmp_path):
    path = tmp_path / "primers.json"
    data = [
        {"name": "P1", "fwd": "AGCTAGCTAGCTAGCT", "rev": "TCGATCGATCGATCGA", "tm": 60.0},
        {"name": "P2", "fwd": "CGATCGATCGATCGAT", "rev": "ATCGATCGATCGATCG", "tm": 62.0}
    ]
    with open(path, "w") as f:
        json.dump(data, f)
    return path

def test_cli_check_compat_run(primers_json, tmp_path):
    """Test 'primerlab check-compat' command runs successfully."""
    output_dir = tmp_path / "cli_output"
    
    # Construct args
    args = [
        "primerlab", "check-compat",
        "--primers", str(primers_json),
        "--output", str(output_dir)
    ]
    
    with patch.object(sys, 'argv', args):
        with pytest.raises(SystemExit) as e:
            main()
        
        # Exit code 0 = compatible, 1 = incompatible (both are valid outcomes)
        # The key is that CLI ran successfully and produced output
        assert e.value.code in [0, 1]
    
    # Check output files were created
    assert output_dir.exists()
    assert (output_dir / "compat_report.md").exists()
    assert (output_dir / "compat_analysis.json").exists()

def test_cli_check_compat_missing_file():
    """Test handling of missing input file."""
    args = ["primerlab", "check-compat", "--primers", "nonexistent.json"]
    with patch.object(sys, 'argv', args):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1
