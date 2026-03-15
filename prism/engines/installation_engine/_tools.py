"""Tool resolution, filtering, and install commands — private submodule.

Pure functions for normalising tool specs, filtering by platform/selection,
and generating platform-specific install commands.
"""

from __future__ import annotations

from prism.models.installation import PrivilegedStep


def resolve_tools(
    merged_config: dict,
    platform_name: str,
    tools_selected: list[str] | None = None,
    tools_excluded: list[str] | None = None,
) -> list[dict]:
    """Resolve and filter the tool list from merged config."""
    tools_req = merged_config.get("tools_required", [])
    tools_opt = merged_config.get("tools_optional", [])
    tools = list(tools_req) + list(tools_opt)
    if not tools:
        tools = merged_config.get("tools", [])
    if not isinstance(tools, list) or not tools:
        return []

    normalised = [normalise_tool(t) for t in tools]
    normalised = [t for t in normalised if t.get("name")]
    normalised = [t for t in normalised if matches_platform(t, platform_name)]

    if tools_selected:
        selected_set = set(tools_selected)
        normalised = [t for t in normalised if t["name"] in selected_set]
    if tools_excluded:
        excluded_set = set(tools_excluded)
        normalised = [t for t in normalised if t["name"] not in excluded_set]

    return normalised


def build_effective_tool_config(merged_config: dict, config: dict) -> dict:
    """Build effective config with tool keys from both merged and base."""
    effective = dict(merged_config)
    if "tools_required" not in effective and "tools_required" in config:
        effective["tools_required"] = config["tools_required"]
    if "tools" not in effective and "tools" in config:
        effective["tools"] = config["tools"]
    return effective


def plan_privileged_installs(
    merged_config: dict,
    platform_name: str,
    tools_selected: list[str] | None,
    tools_excluded: list[str] | None,
    is_installed_fn,
) -> list[PrivilegedStep]:
    """Plan privileged install steps for tools that aren't yet installed."""
    tools = resolve_tools(merged_config, platform_name, tools_selected, tools_excluded)
    if not tools:
        return []

    needs_sudo = platform_name not in ("mac",)
    steps: list[PrivilegedStep] = []
    for tool in tools:
        name = tool["name"]
        if not is_installed_fn(name):
            cmd = get_install_command(name, platform_name)
            steps.append(PrivilegedStep(name=name, command=cmd, needs_sudo=needs_sudo, platform=platform_name))

    return steps


def normalise_tool(tool: str | dict) -> dict:
    """Normalise a tool entry to a dict with at least a 'name' key."""
    if isinstance(tool, str):
        return {"name": tool}
    if isinstance(tool, dict):
        return dict(tool)
    return {}


def matches_platform(tool: dict, platform_name: str) -> bool:
    """Check if a tool is compatible with the given platform."""
    platforms = tool.get("platforms")
    if platforms is None:
        return True
    if isinstance(platforms, list):
        return platform_name in platforms
    return True


def get_install_command(tool_name: str, platform_name: str) -> str:
    """Return the platform-specific install command for a tool."""
    if platform_name == "mac":
        return f"brew install {tool_name}"
    elif platform_name in ("ubuntu", "linux"):
        return f"sudo apt-get install -y {tool_name}"
    elif platform_name == "windows":
        return f"choco install {tool_name} -y"
    return f"install {tool_name}"
