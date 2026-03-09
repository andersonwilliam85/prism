"""ScaffoldEngine — generate package scaffolding for new prisms.

Extracted from scripts/package_manager.py. Pure computation —
returns file path → content mapping, caller writes to disk.

Volatility: low — scaffold structure is stable.
"""

from __future__ import annotations

from datetime import datetime


class ScaffoldEngine:
    """Generate file scaffolding for new prism packages."""

    def generate(self, name: str, template: str = "basic") -> dict[str, str]:
        """Generate a scaffold for a new prism package.

        Args:
            name: Package name.
            template: "basic" (full) or "minimal" (bare-bones).

        Returns:
            Dict mapping relative file paths to content strings.
        """
        safe_name = name.replace("-config", "").replace(" ", "-").lower()
        display_name = safe_name.replace("-", " ").title()
        today = datetime.now().strftime("%Y-%m-%d")

        if template == "minimal":
            return self._minimal_scaffold(safe_name, display_name, today)
        return self._basic_scaffold(safe_name, display_name, today)

    def _basic_scaffold(self, safe_name: str, display_name: str, today: str) -> dict[str, str]:
        files: dict[str, str] = {}

        files["package.yaml"] = (
            f"package:\n"
            f'  name: "{safe_name}-prism"\n'
            f'  version: "1.0.0"\n'
            f'  description: "{display_name} development environment"\n'
            f'  type: "company"\n'
            f'  author: "{display_name} IT Team"\n'
            f'  homepage: "https://dev.example.com"\n'
            f"\n"
            f"prism_config:\n"
            f'  theme: "midnight"\n'
            f"  branding:\n"
            f'    name: "{display_name} Prism"\n'
            f'    tagline: "Empowering {display_name} Development"\n'
            f'    primary_color: "#1e3a8a"\n'
            f"\n"
            f"bundled_prisms:\n"
            f"  base:\n"
            f'    - id: "base"\n'
            f'      name: "{display_name} Base"\n'
            f'      description: "Company-wide settings: proxy, git, required tools"\n'
            f"      required: true\n"
            f'      config: "base/{safe_name}.yaml"\n'
            f"\n"
            f"  teams:\n"
            f'    - id: "platform"\n'
            f'      name: "Platform Team"\n'
            f'      config: "teams/platform.yaml"\n'
            f'    - id: "backend"\n'
            f'      name: "Backend Team"\n'
            f'      config: "teams/backend.yaml"\n'
            f"\n"
            f"setup:\n"
            f"  post_install:\n"
            f'    message: "{display_name} prism installed!"\n'
            f"\n"
            f"user_info_fields:\n"
            f'  - id: "name"\n'
            f'    label: "Full Name"\n'
            f'    type: "text"\n'
            f"    required: true\n"
            f'  - id: "email"\n'
            f'    label: "Company Email"\n'
            f'    type: "email"\n'
            f"    required: true\n"
            f"\n"
            f"distribution:\n"
            f"  local:\n"
            f'    path: "prisms/{safe_name}/"\n'
            f"    discoverable: true\n"
            f"\n"
            f"metadata:\n"
            f'  tags: ["company", "template"]\n'
            f'  company_size: "medium"\n'
            f'  last_updated: "{today}"\n'
        )

        files[f"base/{safe_name}.yaml"] = (
            f"company:\n"
            f'  name: "{display_name}"\n'
            f'  domain: "example.com"\n'
            f"\n"
            f"environment:\n"
            f"  proxy:\n"
            f'    http: "http://proxy.example.com:8080"\n'
            f'    https: "http://proxy.example.com:8080"\n'
            f"\n"
            f"git:\n"
            f"  user:\n"
            f'    name: "${{USER}}"\n'
            f'    email: "${{USER}}@example.com"\n'
            f"\n"
            f"tools_required:\n"
            f"  - git\n"
            f"  - docker\n"
        )

        files["teams/platform.yaml"] = "# Platform Team sub-prism\n\ntools_required: []\n"
        files["teams/backend.yaml"] = "# Backend Team sub-prism\n\ntools_required: []\n"

        files["welcome.yaml"] = (
            f"company:\n"
            f'  name: "{display_name}"\n'
            f"\n"
            f"welcome:\n"
            f'  title: "Welcome to {display_name}"\n'
            f'  subtitle: "Your development environment is ready!"\n'
        )

        files["resources.yaml"] = (
            f"company:\n"
            f'  name: "{display_name}"\n'
            f"\n"
            f"resources:\n"
            f"  developer_tools:\n"
            f'    - name: "GitHub"\n'
            f'      url: "https://github.com"\n'
            f'      description: "Source code"\n'
        )

        return files

    def _minimal_scaffold(self, safe_name: str, display_name: str, today: str) -> dict[str, str]:
        files: dict[str, str] = {}

        files["package.yaml"] = (
            f"package:\n"
            f'  name: "{safe_name}-prism"\n'
            f'  version: "1.0.0"\n'
            f'  description: "{display_name} development environment"\n'
            f'  type: "company"\n'
            f"\n"
            f"metadata:\n"
            f'  tags: ["template"]\n'
            f'  last_updated: "{today}"\n'
        )

        return files
