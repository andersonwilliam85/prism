"""SetupEngine — plan installation, resolve tools, check readiness.

Consolidates SetupPlanEngine + ToolResolutionEngine + PreflightEngine.
Pure computation — builds plans as data, no I/O.

Volatility: low-medium — installation surface evolves slowly.
"""

from __future__ import annotations

from pathlib import Path


class SetupEngine:
    """Plan installation steps, resolve tool lists, and check requirements.

    All methods return data structures or pass/fail results.
    The manager layer executes plans via accessors.
    """

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------

    def plan_git_config(self, user_info: dict, merged_config: dict) -> list[tuple[str, str]]:
        """Plan git config key-value pairs to set."""
        plan: list[tuple[str, str]] = []

        name = user_info.get("name", user_info.get("full_name", ""))
        email = user_info.get("email", user_info.get("work_email", ""))

        if not name or not email:
            git_cfg = merged_config.get("git", {}).get("user", {})
            name = name or git_cfg.get("name", "")
            email = email or git_cfg.get("email", "")

        if name:
            plan.append(("user.name", name))
        if email:
            plan.append(("user.email", email))

        plan.append(("init.defaultBranch", "main"))
        plan.append(("pull.rebase", "false"))

        extra_config = merged_config.get("git", {}).get("config", {})
        for key, value in extra_config.items():
            plan.append((key, str(value)))

        return plan

    def plan_workspace(self, merged_config: dict) -> list[str]:
        """Plan workspace directories to create."""
        defaults = [
            "projects",
            "experiments",
            "learning",
            "archived",
            "docs",
            "tooling",
        ]

        extra = merged_config.get("workspace", {}).get("directories", [])
        if isinstance(extra, list):
            for d in extra:
                if isinstance(d, str) and d not in defaults:
                    defaults.append(d)

        return defaults

    def plan_repo_clones(self, merged_config: dict, workspace_root: str) -> list[dict]:
        """Plan repository clones from merged config."""
        repositories = merged_config.get("repositories", [])
        if not repositories:
            return []

        ws_root = Path(workspace_root)
        clone_plans: list[dict] = []

        for repo in repositories:
            if isinstance(repo, str):
                url = repo
                name = url.rstrip("/").split("/")[-1].replace(".git", "")
                dest = str(ws_root / "projects" / name)
            elif isinstance(repo, dict):
                url = repo.get("url", "")
                name = repo.get("name", "")
                if not name and url:
                    name = url.rstrip("/").split("/")[-1].replace(".git", "")
                custom_path = repo.get("path")
                if custom_path:
                    dest = str(Path(custom_path).expanduser())
                else:
                    dest = str(ws_root / "projects" / name)
            else:
                continue

            if not url:
                continue

            clone_plans.append({"url": url, "name": name, "dest": dest})

        return clone_plans

    # ------------------------------------------------------------------
    # Tool resolution
    # ------------------------------------------------------------------

    def resolve_tools(
        self,
        merged_config: dict,
        platform_name: str,
        tools_selected: list[str] | None = None,
        tools_excluded: list[str] | None = None,
    ) -> list[dict]:
        """Resolve the final list of tools to install."""
        tools = merged_config.get("tools_required", [])
        if not tools:
            tools = merged_config.get("tools", [])
        if not isinstance(tools, list) or not tools:
            return []

        normalised = [self._normalise_tool(t) for t in tools]
        normalised = [t for t in normalised if t.get("name")]

        # Platform filter
        normalised = [t for t in normalised if self._matches_platform(t, platform_name)]

        # Whitelist
        if tools_selected:
            selected_set = set(tools_selected)
            normalised = [t for t in normalised if t["name"] in selected_set]

        # Blacklist
        if tools_excluded:
            excluded_set = set(tools_excluded)
            normalised = [t for t in normalised if t["name"] not in excluded_set]

        return normalised

    # ------------------------------------------------------------------
    # Preflight checks
    # ------------------------------------------------------------------

    def check_requirements(self, requirements: dict, installed_versions: dict[str, str]) -> tuple[bool, list[str]]:
        """Check whether installed software satisfies requirements."""
        failures: list[str] = []

        for key, requirement in requirements.items():
            if key == "onboarding_version":
                continue

            lookup_key = self._requirement_key_to_tool(key)
            installed = installed_versions.get(lookup_key)

            if isinstance(requirement, bool):
                if requirement and not installed:
                    failures.append(f"{key} is required but not found")
            elif isinstance(requirement, str):
                if not installed:
                    failures.append(f"{key} is required but not found")
                elif not self.version_satisfies(installed, requirement):
                    failures.append(f"{key} {requirement} required, found {installed}")

        return len(failures) == 0, failures

    def version_satisfies(self, installed: str, required: str) -> bool:
        """Check if an installed version satisfies a requirement string."""
        req = required.strip()

        if req.startswith(">="):
            return self._compare_versions(installed, req[2:]) >= 0
        elif req.startswith(">"):
            return self._compare_versions(installed, req[1:]) > 0
        elif req.startswith("<="):
            return self._compare_versions(installed, req[2:]) <= 0
        elif req.startswith("<"):
            return self._compare_versions(installed, req[1:]) < 0
        elif req.startswith("=="):
            return self._compare_versions(installed, req[2:]) == 0

        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_tool(tool: str | dict) -> dict:
        if isinstance(tool, str):
            return {"name": tool}
        if isinstance(tool, dict):
            return dict(tool)
        return {}

    @staticmethod
    def _matches_platform(tool: dict, platform_name: str) -> bool:
        platforms = tool.get("platforms")
        if platforms is None:
            return True
        if isinstance(platforms, list):
            return platform_name in platforms
        return True

    @staticmethod
    def _compare_versions(a: str, b: str) -> int:
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

    @staticmethod
    def _requirement_key_to_tool(key: str) -> str:
        if key == "python_version":
            return "python"
        return key
