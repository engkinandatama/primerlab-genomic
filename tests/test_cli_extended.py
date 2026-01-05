"""Extended CLI Tests for v0.8.1 Coverage Expansion."""
import pytest
import subprocess
import sys


def run_cli(*args):
    """Helper to run CLI commands."""
    result = subprocess.run(
        [sys.executable, "-m", "primerlab.cli.main"] + list(args),
        capture_output=True,
        text=True,
        timeout=30
    )
    return result


class TestCLICommands:
    """Tests for all major CLI commands help."""
    
    @pytest.mark.parametrize("cmd", [
        "version",
        "run",
        "batch-generate",
        "init",
        "health",
        "insilico",
        "blast",
        "compare",
        "plot",
        "history",
        "tm-gradient",
        "check-compat",
        "species-check",
        "batch-run",
        "qpcr-efficiency",
    ])
    def test_command_help(self, cmd):
        """All commands should have working --help."""
        result = run_cli(cmd, "--help")
        assert result.returncode == 0, f"{cmd} --help failed: {result.stderr}"
    
    def test_version_output(self):
        """Version command should show version number."""
        result = run_cli("--version")
        assert result.returncode == 0
        assert "0.8" in result.stdout

    def test_run_pcr_help(self):
        """run pcr --help should work."""
        result = run_cli("run", "pcr", "--help")
        output = result.stdout + result.stderr
        assert "--sequence" in output or "--config" in output

    def test_run_qpcr_help(self):
        """run qpcr --help should work."""
        result = run_cli("run", "qpcr", "--help")
        output = result.stdout + result.stderr
        assert "--sequence" in output or "--config" in output


class TestCLIErrorHandling:
    """Tests for CLI error handling."""
    
    def test_unknown_command(self):
        """Unknown command should exit non-zero."""
        result = run_cli("unknown_xyz_cmd")
        assert result.returncode != 0
    
    def test_run_without_args(self):
        """run without workflow should show usage."""
        result = run_cli("run")
        output = result.stdout + result.stderr
        # Should show usage or error
        assert "usage" in output.lower() or "error" in output.lower() or result.returncode != 0


class TestCLIHistory:
    """Tests for history subcommands."""
    
    def test_history_list(self):
        """history list should work."""
        result = run_cli("history", "list")
        # May show "no designs" but shouldn't crash
        assert result.returncode == 0
    
    def test_history_stats(self):
        """history stats should work."""
        result = run_cli("history", "stats")
        # May show empty stats but shouldn't crash
        assert result.returncode == 0


class TestCLIOutputFormats:
    """Tests for output format flags in run help."""
    
    def test_run_has_export_flag(self):
        """run --help should show --export."""
        result = run_cli("run", "--help")
        assert "--export" in result.stdout
    
    def test_run_has_json_flag(self):
        """run --help should show --json."""
        result = run_cli("run", "--help")
        output = result.stdout + result.stderr
        assert "--json" in output or "json" in output.lower()
    
    def test_run_has_quiet_flag(self):
        """run --help should show --quiet."""
        result = run_cli("run", "--help")
        assert "--quiet" in result.stdout
    
    def test_run_has_dry_run_flag(self):
        """run --help should show --dry-run."""
        result = run_cli("run", "--help")
        assert "--dry-run" in result.stdout


class TestCLIHealth:
    """Tests for health command details."""
    
    def test_health_shows_python(self):
        """health should show Python info."""
        result = run_cli("health")
        output = result.stdout + result.stderr
        assert "Python" in output or "python" in output
    
    def test_health_shows_version(self):
        """health should show PrimerLab version."""
        result = run_cli("health")
        output = result.stdout + result.stderr
        assert "PrimerLab" in output or "0.8" in output


class TestCLIInit:
    """Tests for init command."""
    
    def test_init_shows_workflows(self):
        """init --help should show workflow options."""
        result = run_cli("init", "--help")
        output = result.stdout + result.stderr
        assert "--workflow" in output or "pcr" in output.lower() or "qpcr" in output.lower()
