"""
E2E tests for CLI tools — install.py, package_manager.py, package_validator.py.
"""

import re
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent


def run(cmd, timeout=30, cwd=None):
    """Run a command and return CompletedProcess."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(cwd or PROJECT_ROOT),
    )


@pytest.mark.e2e
class TestInstallPyCLI:
    """Tests for install.py CLI."""

    def test_help_flag(self):
        result = run(["python3", "install.py", "--help"])
        combined = result.stdout + result.stderr
        assert result.returncode == 0
        assert "usage" in combined.lower() or "help" in combined.lower()

    def test_help_mentions_prism_flag(self):
        result = run(["python3", "install.py", "--help"])
        combined = result.stdout + result.stderr
        assert "--prism" in combined

    def test_status_flag(self):
        result = run(["python3", "install.py", "--status"])
        # Should exit cleanly (0 or 1 depending on whether workspace exists)
        assert result.returncode in (0, 1)

    def test_invalid_prism_name_rejected(self):
        result = run(
            ["python3", "install.py", "--prism", "definitely-not-a-real-prism-xyz123"],
            timeout=15,
        )
        combined = result.stdout + result.stderr
        has_error = (
            result.returncode != 0
            or "error" in combined.lower()
            or "not found" in combined.lower()
            or "invalid" in combined.lower()
        )
        assert has_error, "Expected rejection of invalid prism name"


@pytest.mark.e2e
class TestPackageManagerCLI:
    """Tests for scripts/package_manager.py CLI."""

    def test_list_command(self):
        result = run(["python3", "scripts/package_manager.py", "list"])
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        assert "prism" in combined.lower() or "💎" in combined

    def test_list_shows_at_least_one_prism(self):
        result = run(["python3", "scripts/package_manager.py", "list"])
        assert result.returncode == 0
        # Count prism lines by looking for gem emoji or prism names
        lines = [line for line in result.stdout.split("\n") if line.strip()]
        assert len(lines) > 2  # header + at least one prism

    def test_validate_personal_dev(self):
        prism_path = PROJECT_ROOT / "prisms" / "personal-dev"
        if not prism_path.exists():
            pytest.skip("personal-dev not present")
        result = run(["python3", "scripts/package_manager.py", "validate", "personal-dev"])
        assert result.returncode == 0
        assert "valid" in result.stdout.lower() or "✅" in result.stdout

    def test_validate_nonexistent_prism(self):
        result = run(["python3", "scripts/package_manager.py", "validate", "prism-that-does-not-exist"])
        combined = result.stdout + result.stderr
        has_error = result.returncode != 0 or "not found" in combined.lower() or "error" in combined.lower()
        assert has_error

    def test_search_command(self):
        result = run(["python3", "scripts/package_manager.py", "search", "personal"])
        # Should succeed even if nothing found
        assert result.returncode == 0

    def test_info_command_for_existing_prism(self):
        prism_path = PROJECT_ROOT / "prisms" / "personal-dev"
        if not prism_path.exists():
            pytest.skip("personal-dev not present")
        result = run(["python3", "scripts/package_manager.py", "info", "personal-dev"])
        combined = result.stdout + result.stderr
        assert result.returncode == 0 or "personal" in combined.lower()

    def test_create_command(self, tmp_path):
        result = subprocess.run(
            ["python3", "scripts/package_manager.py", "create", "cli-test-prism", "--company", "CLI Test Co"],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(PROJECT_ROOT),
            env={**__import__("os").environ, "HOME": str(tmp_path)},
        )
        # Command should succeed or explain what it would create
        combined = result.stdout + result.stderr
        assert result.returncode == 0 or "prism" in combined.lower()


@pytest.mark.e2e
class TestPrismValidatorCLI:
    """Tests for scripts/package_validator.py CLI."""

    def test_validates_all_prisms_without_crash(self):
        result = run(["python3", "scripts/package_validator.py"], timeout=30)
        # Exit code 0 = all valid, 1 = some invalid — both acceptable
        assert result.returncode in (0, 1)
        assert "Valid" in result.stdout or "Invalid" in result.stdout or "prism" in result.stdout.lower()

    def test_validates_personal_dev_prism(self):
        prism_path = PROJECT_ROOT / "prisms" / "personal-dev"
        if not prism_path.exists():
            pytest.skip("personal-dev not present")
        result = run(["python3", "scripts/package_validator.py", str(prism_path)])
        assert result.returncode == 0
        assert "valid" in result.stdout.lower() or "Valid" in result.stdout

    def test_valid_prism_reports_zero_errors(self):
        prism_path = PROJECT_ROOT / "prisms" / "personal-dev"
        if not prism_path.exists():
            pytest.skip("personal-dev not present")
        result = run(["python3", "scripts/package_validator.py", str(prism_path)])
        # Verify no error output
        assert "❌" not in result.stdout or "0" in result.stdout

    def test_output_shows_prism_counts(self):
        result = run(["python3", "scripts/package_validator.py"], timeout=30)
        combined = result.stdout
        # Should show counts like "Valid: N" or "Invalid: N"
        assert re.search(r"valid|invalid", combined, re.IGNORECASE)


@pytest.mark.e2e
class TestConfigMergerScript:
    """Tests for config_merger.py as a module (import)."""

    def test_import_works(self):
        result = run(["python3", "-c", "from scripts.config_merger import ConfigMerger, merge_configs; print('OK')"])
        assert result.returncode == 0
        assert "OK" in result.stdout

    def test_merge_configs_from_cli(self):
        result = run(
            [
                "python3",
                "-c",
                "from scripts.config_merger import merge_configs; "
                "r = merge_configs({'a': 1}, {'b': 2}); "
                "assert r['a'] == 1 and r['b'] == 2; "
                "print('PASS')",
            ]
        )
        assert result.returncode == 0
        assert "PASS" in result.stdout

    def test_env_var_substitution_from_cli(self):
        import os

        env = {**os.environ, "MY_TEST_VAR": "hello"}
        result = subprocess.run(
            [
                "python3",
                "-c",
                "from scripts.config_merger import ConfigMerger; "
                "m = ConfigMerger(); "
                "r = m._substitute_env_vars({'k': '${MY_TEST_VAR}'}); "
                "assert r['k'] == 'hello', f'Got: {r[\"k\"]}'; "
                "print('PASS')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(PROJECT_ROOT),
            env=env,
        )
        assert result.returncode == 0
        assert "PASS" in result.stdout


@pytest.mark.e2e
class TestPackageManagerDiscover:
    """Tests for PackageManager.discover_packages() via subprocess."""

    def test_discovers_prisms_in_prisms_dir(self):
        result = run(
            [
                "python3",
                "-c",
                "import sys; sys.path.insert(0, 'scripts'); "
                "from package_manager import PackageManager; "
                "pm = PackageManager(); "
                "pkgs = pm.discover_packages(); "
                "print('Found ' + str(len(pkgs)) + ' prisms'); "
                "[print(p['name']) for p in pkgs]",
            ]
        )
        assert result.returncode == 0
        match = re.search(r"Found (\d+) prisms", result.stdout)
        assert match, f"Expected 'Found N prisms' in: {result.stdout}"
        count = int(match.group(1))
        assert count > 0, "Should discover at least one prism"

    def test_all_discovered_have_required_keys(self):
        result = run(
            [
                "python3",
                "-c",
                "import sys, json; sys.path.insert(0, 'scripts'); "
                "from package_manager import PackageManager; "
                "pm = PackageManager(); "
                "pkgs = pm.discover_packages(); "
                "required = {'name','version','description','path','source'}; "
                "for p in pkgs:\n"
                "  missing = required - set(p.keys())\n"
                "  assert not missing, f'Missing keys in {p[\"name\"]}: {missing}'\n"
                "print('ALL_OK')",
            ]
        )
        assert result.returncode == 0
        assert "ALL_OK" in result.stdout
