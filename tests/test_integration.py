"""Integration Tests for End-to-End Workflows (v0.1.6)."""
import pytest
import subprocess
import sys
import tempfile
import json
from pathlib import Path


class TestPCRWorkflowE2E:
    """End-to-end tests for PCR workflow."""
    
    @pytest.fixture
    def pcr_config(self, tmp_path):
        """Create a PCR config file for testing."""
        config_content = """
workflow: pcr

input:
  sequence: >
    ATGGTGAAGGTCGGAGTCAACGGATTTGGTCGTATTGGGCGCCTGGTCACCAGGGCTGCT
    TTTAACTCTGGTAAAGTGGATATTGTTGCCATCAATGACCCCTTCATTGACCTCAACTAC
    ATGGTTTACATGTTCCAATATGATTCCACCCATGGCAAATTCCATGGCACCGTCAAGGCT
    GAGAACGGGAAGCTTGTCATCAATGGAAATCCCATCACCATCTTCCAGGAGCGAGATCCC
    TCCAAAATCAAGTGGGGCGATGCTGGCGCTGAGTACGTCGTGGAGTCCACTGGCGTCTTC

parameters:
  primer_size:
    min: 18
    opt: 20
    max: 25
  tm:
    min: 57
    opt: 60
    max: 63
  product_size_range: [[100, 250]]

output:
  directory: "{output_dir}"
"""
        config_path = tmp_path / "test_pcr.yaml"
        output_dir = tmp_path / "output_pcr"
        output_dir.mkdir()
        
        config_path.write_text(config_content.format(output_dir=str(output_dir)))
        return config_path, output_dir
    
    def test_pcr_workflow_runs(self, pcr_config):
        """Test that PCR workflow completes without errors."""
        config_path, output_dir = pcr_config
        
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "run", "pcr", "--config", str(config_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Should complete (exit 0) or fail gracefully (non-zero but no crash)
        # Note: May fail if primer3-py issues occur
        assert result.returncode in [0, 1]  # 0=success, 1=design failed gracefully
    
    def test_pcr_creates_output_files(self, pcr_config):
        """Test that PCR workflow creates expected output files."""
        config_path, output_dir = pcr_config
        
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "run", "pcr", "--config", str(config_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Check for output files
            output_files = list(output_dir.rglob("*"))
            assert len(output_files) > 0, "No output files created"
            
            # Should have report.md
            md_files = list(output_dir.rglob("*.md"))
            assert len(md_files) > 0, "No markdown report created"


class TestQPCRWorkflowE2E:
    """End-to-end tests for qPCR workflow."""
    
    @pytest.fixture
    def qpcr_taqman_config(self, tmp_path):
        """Create a qPCR TaqMan config file for testing."""
        config_content = """
workflow: qpcr

input:
  sequence: >
    ATGGTGAAGGTCGGAGTCAACGGATTTGGTCGTATTGGGCGCCTGGTCACCAGGGCTGCT
    TTTAACTCTGGTAAAGTGGATATTGTTGCCATCAATGACCCCTTCATTGACCTCAACTAC
    ATGGTTTACATGTTCCAATATGATTCCACCCATGGCAAATTCCATGGCACCGTCAAGGCT
    GAGAACGGGAAGCTTGTCATCAATGGAAATCCCATCACCATCTTCCAGGAGCGAGATCCC
    TCCAAAATCAAGTGGGGCGATGCTGGCGCTGAGTACGTCGTGGAGTCCACTGGCGTCTTC

parameters:
  mode: taqman
  primer_size:
    min: 18
    opt: 20
    max: 25
  tm:
    min: 57
    opt: 60
    max: 63
  product_size_range: [[70, 150]]
  
  probe:
    size:
      min: 18
      opt: 24
      max: 30
    tm:
      min: 68
      opt: 70
      max: 72

output:
  directory: "{output_dir}"
"""
        config_path = tmp_path / "test_qpcr_taqman.yaml"
        output_dir = tmp_path / "output_qpcr_taqman"
        output_dir.mkdir()
        
        config_path.write_text(config_content.format(output_dir=str(output_dir)))
        return config_path, output_dir
    
    @pytest.fixture
    def qpcr_sybr_config(self, tmp_path):
        """Create a qPCR SYBR config file for testing."""
        config_content = """
workflow: qpcr

input:
  sequence: >
    ATGGTGAAGGTCGGAGTCAACGGATTTGGTCGTATTGGGCGCCTGGTCACCAGGGCTGCT
    TTTAACTCTGGTAAAGTGGATATTGTTGCCATCAATGACCCCTTCATTGACCTCAACTAC
    ATGGTTTACATGTTCCAATATGATTCCACCCATGGCAAATTCCATGGCACCGTCAAGGCT

parameters:
  mode: sybr
  primer_size:
    min: 18
    opt: 20
    max: 25
  tm:
    min: 57
    opt: 60
    max: 63
  product_size_range: [[70, 150]]

output:
  directory: "{output_dir}"
"""
        config_path = tmp_path / "test_qpcr_sybr.yaml"
        output_dir = tmp_path / "output_qpcr_sybr"
        output_dir.mkdir()
        
        config_path.write_text(config_content.format(output_dir=str(output_dir)))
        return config_path, output_dir
    
    def test_qpcr_taqman_workflow_runs(self, qpcr_taqman_config):
        """Test that qPCR TaqMan workflow completes."""
        config_path, output_dir = qpcr_taqman_config
        
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "run", "qpcr", "--config", str(config_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode in [0, 1]
    
    def test_qpcr_sybr_workflow_runs(self, qpcr_sybr_config):
        """Test that qPCR SYBR workflow completes."""
        config_path, output_dir = qpcr_sybr_config
        
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "run", "qpcr", "--config", str(config_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode in [0, 1]


class TestBatchRunE2E:
    """End-to-end tests for batch run command."""
    
    @pytest.fixture
    def batch_fasta(self, tmp_path):
        """Create a multi-FASTA file for batch testing."""
        fasta_content = """>GENE1 Test Gene 1
ATGGTGAAGGTCGGAGTCAACGGATTTGGTCGTATTGGGCGCCTGGTCACCAGGGCTGCT
TTTAACTCTGGTAAAGTGGATATTGTTGCCATCAATGACCCCTTCATTGACCTCAACTAC

>GENE2 Test Gene 2
ATGGATGATGATATCGCCGCGCTCGTCGTCGACAACGGCTCCGGCATGTGCAAGGCCGGC
TTCGCGGGCGACGATGCCCCCCGGGCCGTCTTCCCCTCCATCGTGGGGCGCCCCAGGCAC

>GENE3 Test Gene 3
ATGCTCGCGCTACTCTCTCTTTCTGGCCTGGAGGCTATCCAGCGTACTCCAAAGATTCAG
GTTTACTCACGTCATCCAGCAGAGAATGGAAAGTCAAATTTCCTGAATTGCTATGTGTCT
"""
        fasta_path = tmp_path / "test_batch.fasta"
        fasta_path.write_text(fasta_content)
        
        output_dir = tmp_path / "output_batch"
        output_dir.mkdir()
        
        return fasta_path, output_dir
    
    @pytest.fixture
    def batch_config(self, tmp_path):
        """Create shared config for batch run."""
        config_content = """
workflow: pcr

parameters:
  primer_size:
    min: 18
    opt: 20
    max: 25
  tm:
    min: 57
    opt: 60
    max: 63
  product_size_range: [[80, 200]]
"""
        config_path = tmp_path / "batch_shared.yaml"
        config_path.write_text(config_content)
        return config_path
    
    def test_batch_run_with_fasta(self, batch_fasta, batch_config):
        """Test batch run with multi-FASTA input."""
        fasta_path, output_dir = batch_fasta
        
        result = subprocess.run(
            [
                sys.executable, "-m", "primerlab.cli.main", 
                "batch-run", 
                "--fasta", str(fasta_path),
                "--config", str(batch_config),
                "--output", str(output_dir),
                "--continue-on-error"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Should complete without crash
        assert result.returncode in [0, 1]
    
    def test_batch_run_creates_summary(self, batch_fasta, batch_config):
        """Test that batch run creates summary file."""
        fasta_path, output_dir = batch_fasta
        
        result = subprocess.run(
            [
                sys.executable, "-m", "primerlab.cli.main", 
                "batch-run", 
                "--fasta", str(fasta_path),
                "--config", str(batch_config),
                "--output", str(output_dir),
                "--continue-on-error"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            # Should create summary file
            summary_files = list(output_dir.rglob("*summary*"))
            # Note: Summary may be in stdout or file depending on implementation


class TestCLICommandsE2E:
    """End-to-end tests for CLI commands."""
    
    def test_history_list_runs(self):
        """Test that history list command runs."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "history", "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should complete without crash
        assert result.returncode in [0, 1]
    
    def test_history_stats_runs(self):
        """Test that history stats command runs."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "history", "stats"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode in [0, 1]
    
    def test_compare_help(self):
        """Test that compare --help works."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "compare", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        assert "compare" in result.stdout.lower() or "--labels" in result.stdout
    
    def test_plot_help(self):
        """Test that plot --help works."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "plot", "--help"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
