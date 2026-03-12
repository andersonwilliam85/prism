"""Tests for the prism CLI entry point and subcommand routing."""

from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def run_cli(*args: str, timeout: int = 10) -> subprocess.CompletedProcess:
    """Run the prism CLI via the module entry point."""
    return subprocess.run(
        ["python3", "-c", f"from prism.cli import main; import sys; sys.argv = ['prism'] + {list(args)!r}; main()"],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(PROJECT_ROOT),
    )


class TestRootCommand:
    def test_no_args_prints_help(self):
        result = run_cli()
        assert result.returncode == 0
        assert "install" in result.stdout
        assert "ui" in result.stdout
        assert "packages" in result.stdout

    def test_help_flag(self):
        result = run_cli("--help")
        assert result.returncode == 0
        assert "Prism" in result.stdout

    def test_version_flag(self):
        result = run_cli("--version")
        assert result.returncode == 0
        assert "prism" in result.stdout


class TestInstallSubcommand:
    def test_help(self):
        result = run_cli("install", "--help")
        assert result.returncode == 0
        assert "--prism" in result.stdout
        assert "--resume" in result.stdout
        assert "--status" in result.stdout
        assert "--config" in result.stdout
        assert "--npm-registry" in result.stdout
        assert "--skip-privileged" in result.stdout

    def test_status_flag(self):
        result = run_cli("install", "--status")
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        # Should list available packages or say none found
        assert "prism" in combined.lower() or "package" in combined.lower()


class TestUISubcommand:
    def test_help(self):
        result = run_cli("ui", "--help")
        assert result.returncode == 0
        assert "--port" in result.stdout
        assert "--host" in result.stdout
        assert "--no-browser" in result.stdout


class TestPackagesSubcommand:
    def test_help(self):
        result = run_cli("packages", "--help")
        assert result.returncode == 0
        assert "list" in result.stdout
        assert "validate" in result.stdout
        assert "info" in result.stdout

    def test_list(self):
        result = run_cli("packages", "list")
        assert result.returncode == 0
        assert "prism" in result.stdout

    def test_list_shows_version_and_description(self):
        result = run_cli("packages", "list")
        assert result.returncode == 0
        assert "2.0.0" in result.stdout
        assert "Default Prism" in result.stdout

    def test_validate_all(self):
        result = run_cli("packages", "validate")
        assert result.returncode == 0
        assert "Valid" in result.stdout

    def test_validate_single_package(self):
        result = run_cli("packages", "validate", "prism")
        assert result.returncode == 0
        assert "Valid" in result.stdout

    def test_validate_nonexistent_package(self):
        result = run_cli("packages", "validate", "nonexistent-xyz-123")
        assert result.returncode == 1

    def test_info_existing_package(self):
        result = run_cli("packages", "info", "prism")
        assert result.returncode == 0
        assert "Name:" in result.stdout
        assert "Version:" in result.stdout
        assert "prism" in result.stdout

    def test_info_shows_tiers(self):
        result = run_cli("packages", "info", "prism")
        assert result.returncode == 0
        assert "Tier:" in result.stdout

    def test_info_nonexistent_package(self):
        result = run_cli("packages", "info", "nonexistent-xyz-123")
        assert result.returncode == 1
        assert "not found" in result.stdout.lower()
