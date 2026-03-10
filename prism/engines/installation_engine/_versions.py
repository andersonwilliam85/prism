"""Version comparison and requirements checking — private submodule.

Pure functions with zero external dependencies.
"""

from __future__ import annotations


def version_satisfies(installed: str, required: str) -> bool:
    """Check if an installed version satisfies a version requirement string."""
    req = required.strip()
    if req.startswith(">="):
        return compare_versions(installed, req[2:]) >= 0
    elif req.startswith(">"):
        return compare_versions(installed, req[1:]) > 0
    elif req.startswith("<="):
        return compare_versions(installed, req[2:]) <= 0
    elif req.startswith("<"):
        return compare_versions(installed, req[1:]) < 0
    elif req.startswith("=="):
        return compare_versions(installed, req[2:]) == 0
    return True


def compare_versions(a: str, b: str) -> int:
    """Compare two version strings. Returns -1, 0, or 1."""
    a_parts = [int(x) for x in a.strip().split(".") if x.isdigit()]
    b_parts = [int(x) for x in b.strip().split(".") if x.isdigit()]
    for i in range(max(len(a_parts), len(b_parts))):
        av = a_parts[i] if i < len(a_parts) else 0
        bv = b_parts[i] if i < len(b_parts) else 0
        if av < bv:
            return -1
        if av > bv:
            return 1
    return 0


def check_version_requirements(
    requirements: dict,
    installed_versions: dict[str, str],
) -> tuple[bool, list[str]]:
    """Check whether installed versions satisfy all requirements."""
    failures: list[str] = []
    for key, requirement in requirements.items():
        if key == "onboarding_version":
            continue
        lookup_key = "python" if key == "python_version" else key
        installed = installed_versions.get(lookup_key)

        if isinstance(requirement, bool):
            if requirement and not installed:
                failures.append(f"{key} is required but not found")
        elif isinstance(requirement, str):
            if not installed:
                failures.append(f"{key} is required but not found")
            elif not version_satisfies(installed, requirement):
                failures.append(f"{key} {requirement} required, found {installed}")

    return len(failures) == 0, failures
