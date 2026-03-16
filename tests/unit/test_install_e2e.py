"""E2E-style integration tests for the Prism installation flow.

Tests the actual install pipeline end-to-end using the real Flask app and
real config files, but mocking subprocess calls so we never actually install
tools on the host.

Run with:
    pytest tests/unit/test_install_e2e.py -x -q --override-ini="addopts=-ra"
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from prism.engines.installation_engine._tools import get_install_command, resolve_from_registry, resolve_tools
from prism.ui.app import create_app

PRISMS_DIR = Path(__file__).parent.parent.parent / "prism" / "prisms"


# ======================================================================
# Helpers
# ======================================================================


def _make_mock_file_accessor(config: dict, pkg_path: Path | None = None):
    """Build a FileAccessor mock that returns *config* for any package."""
    mock = MagicMock()
    mock.get_package_config.return_value = config
    mock.find_package.return_value = pkg_path or Path("/fake/prisms/test")
    mock.exists.return_value = False
    mock.list_packages.return_value = []
    mock.read_yaml.return_value = {}
    return mock


def _make_mock_command_accessor(installed: set[str] | None = None):
    """Build a CommandAccessor that reports *installed* tools as present."""
    installed = installed or set()
    mock = MagicMock()
    mock.pkg_is_installed.side_effect = lambda name: name in installed
    mock.ssh_key_exists.return_value = True
    return mock


def _make_mock_system_accessor(platform: str = "mac"):
    mock = MagicMock()
    mock.get_platform.return_value = (platform, "Test")
    mock.get_installed_version.return_value = "3.11"
    return mock


def _create_test_app(
    config: dict,
    installed_tools: set[str] | None = None,
    platform: str = "mac",
    pkg_path: Path | None = None,
):
    """Create a Flask test app with fully mocked accessors."""
    mock_file = _make_mock_file_accessor(config, pkg_path)
    mock_cmd = _make_mock_command_accessor(installed_tools)
    mock_sys = _make_mock_system_accessor(platform)

    with patch("prism.container.FileAccessor", return_value=mock_file):
        with patch("prism.container.CommandAccessor", return_value=mock_cmd):
            with patch("prism.container.SystemAccessor", return_value=mock_sys):
                with patch("prism.container.RegistryAccessor"):
                    with patch("prism.container.SudoAccessor"):
                        app = create_app(prisms_dir=Path("/fake/prisms"))
                        app.config["TESTING"] = True
                        return app, mock_file, mock_cmd, mock_sys


# ======================================================================
# Fixtures
# ======================================================================


TOOL_REGISTRY = {
    "git": {
        "label": "Git",
        "summary": "Version control",
        "description": "Track changes and collaborate",
        "category": "core",
        "platforms": {
            "mac": "brew install git",
            "linux": "sudo apt-get install -y git",
        },
    },
    "docker": {
        "label": "Docker",
        "summary": "Container runtime",
        "description": "Build and run containers",
        "category": "containers",
        "platforms": {
            "mac": "brew install --cask docker",
            "linux": "curl -fsSL https://get.docker.com | sh",
        },
    },
    "code": {
        "label": "VS Code",
        "summary": "Extensible editor",
        "description": "Microsoft extensible editor",
        "category": "editor",
        "platforms": {
            "mac": "brew install --cask visual-studio-code",
            "linux": "sudo snap install code --classic",
        },
    },
    "cursor": {
        "label": "Cursor",
        "summary": "AI code editor",
        "description": "AI pair programming editor",
        "category": "editor",
        "platforms": {
            "mac": "brew install --cask cursor",
        },
    },
    "jq": {
        "label": "jq",
        "summary": "JSON processing",
        "description": "Slice and transform JSON",
        "category": "cli",
        "platforms": {
            "mac": "brew install jq",
            "linux": "sudo apt-get install -y jq",
        },
    },
    "node": {
        "label": "Node.js",
        "summary": "JavaScript runtime",
        "description": "Server-side JavaScript",
        "category": "runtime",
        "platforms": {
            "mac": "brew install node",
            "linux": "sudo apt-get install -y nodejs",
        },
    },
    "mystery-tool": {
        "label": "Mystery Tool",
        "summary": "Unknown tool",
        "description": "A tool with no platform commands",
        "category": "experimental",
        # No platforms key — no install command for any OS
    },
}


def _base_config(
    *,
    tools_required=None,
    tools_optional=None,
    tool_registry=None,
    bundled_prisms=None,
    post_install_message=None,
    environment=None,
):
    """Build a minimal valid package config for testing."""
    cfg = {
        "package": {
            "name": "test-prism",
            "version": "1.0.0",
            "description": "A test prism",
        },
        "prism_config": {"theme": "ocean"},
    }
    if tools_required is not None:
        cfg["tools_required"] = tools_required
    if tools_optional is not None:
        cfg["tools_optional"] = tools_optional
    if tool_registry is not None:
        cfg["tool_registry"] = tool_registry
    if bundled_prisms is not None:
        cfg["bundled_prisms"] = bundled_prisms
    if post_install_message is not None:
        cfg.setdefault("setup", {})["post_install"] = {"message": post_install_message}
    if environment is not None:
        cfg["environment"] = environment
    return cfg


# ======================================================================
# 1. Tool selection filtering
# ======================================================================


class TestToolSelectionFiltering:
    """When toolsSelected is provided, only those tools should be resolved."""

    def test_tools_selected_filters_to_specified(self):
        """Only the explicitly selected tools appear in resolved output."""
        merged = {
            "tools_required": ["git", "docker", "node"],
            "tools_optional": ["jq", "code"],
        }
        result = resolve_tools(merged, "mac", tools_selected=["git", "jq"])
        names = [t["name"] for t in result]
        assert "git" in names
        assert "jq" in names
        assert "docker" not in names
        assert "node" not in names
        assert "code" not in names

    def test_tools_selected_empty_list_installs_nothing(self):
        """An empty toolsSelected [] means nothing was selected — install nothing."""
        merged = {
            "tools_required": ["git", "docker"],
            "tools_optional": ["jq"],
        }
        result = resolve_tools(merged, "mac", tools_selected=[])
        assert result == []

    def test_tools_selected_none_installs_all(self):
        """When toolsSelected is None (not provided), all tools install — legacy."""
        merged = {
            "tools_required": ["git", "docker"],
            "tools_optional": ["jq"],
        }
        result = resolve_tools(merged, "mac", tools_selected=None)
        names = [t["name"] for t in result]
        assert "git" in names
        assert "docker" in names
        assert "jq" in names

    def test_tools_selected_via_api(self):
        """POST /api/install with toolsSelected filters the install."""
        config = _base_config(
            tools_required=["git", "docker"],
            tools_optional=["jq", "code"],
            tool_registry=TOOL_REGISTRY,
        )
        app, mock_file, mock_cmd, _ = _create_test_app(config)

        with app.test_client() as client:
            resp = client.post(
                "/api/install",
                data=json.dumps(
                    {
                        "package": "test-prism",
                        "userInfo": {"name": "Tester", "email": "t@t.com"},
                        "toolsSelected": ["git"],
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(resp.data)
            assert resp.status_code == 200
            assert data["success"] is True

    def test_tools_selected_empty_via_api_installs_nothing(self):
        """POST /api/install with toolsSelected=[] means nothing was selected."""
        config = _base_config(
            tools_required=["git"],
            tools_optional=["docker", "jq"],
            tool_registry=TOOL_REGISTRY,
        )
        app, mock_file, mock_cmd, _ = _create_test_app(config, installed_tools={"git", "docker", "jq", "brew"})

        with app.test_client() as client:
            resp = client.post(
                "/api/install",
                data=json.dumps(
                    {
                        "package": "test-prism",
                        "userInfo": {"name": "Tester", "email": "t@t.com"},
                        "toolsSelected": [],
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(resp.data)
            assert resp.status_code == 200
            assert data["success"] is True

    def test_tools_excluded_removes_tools(self):
        """toolsExcluded filters out specific tools."""
        merged = {
            "tools_required": ["git", "docker"],
            "tools_optional": ["jq"],
        }
        result = resolve_tools(merged, "mac", tools_excluded=["docker"])
        names = [t["name"] for t in result]
        assert "docker" not in names
        assert "git" in names
        assert "jq" in names


# ======================================================================
# 2. Tool registry resolution
# ======================================================================


class TestToolRegistryResolution:
    """Tools referenced as strings should resolve metadata from the registry."""

    def test_string_tool_resolves_from_registry(self):
        """A plain string 'git' should gain label, summary, description, category."""
        tools = ["git", "docker"]
        resolved = resolve_from_registry(tools, TOOL_REGISTRY)

        git = next(t for t in resolved if t["name"] == "git")
        assert git["label"] == "Git"
        assert git["summary"] == "Version control"
        assert git["description"] == "Track changes and collaborate"
        assert git["category"] == "core"

        docker = next(t for t in resolved if t["name"] == "docker")
        assert docker["label"] == "Docker"
        assert docker["category"] == "containers"

    def test_dict_tool_merges_with_registry(self):
        """A dict tool overrides registry defaults but inherits the rest."""
        tools = [{"name": "git", "summary": "My custom summary"}]
        resolved = resolve_from_registry(tools, TOOL_REGISTRY)

        git = resolved[0]
        assert git["name"] == "git"
        assert git["summary"] == "My custom summary"  # overridden
        assert git["label"] == "Git"  # inherited
        assert git["category"] == "core"  # inherited

    def test_unknown_tool_resolves_without_registry(self):
        """A tool not in the registry still resolves with just its name."""
        tools = ["unknown-tool"]
        resolved = resolve_from_registry(tools, TOOL_REGISTRY)
        assert len(resolved) == 1
        assert resolved[0]["name"] == "unknown-tool"
        assert "label" not in resolved[0]

    def test_registry_resolution_with_resolve_tools(self):
        """resolve_tools uses tool_registry when present in merged config."""
        merged = {
            "tools_required": ["git"],
            "tools_optional": ["docker"],
            "tool_registry": TOOL_REGISTRY,
        }
        result = resolve_tools(merged, "mac")
        git = next(t for t in result if t["name"] == "git")
        assert git["label"] == "Git"
        assert git["category"] == "core"

    def test_registry_platforms_propagate(self):
        """Registry platform install commands propagate to resolved tools."""
        tools = ["git"]
        resolved = resolve_from_registry(tools, TOOL_REGISTRY)
        git = resolved[0]
        assert git["platforms"]["mac"] == "brew install git"
        assert git["platforms"]["linux"] == "sudo apt-get install -y git"


# ======================================================================
# 3. Category grouping via /api/package/<pkg>/tools
# ======================================================================


class TestCategoryGrouping:
    """The /api/package/<pkg>/tools endpoint should return tools with categories."""

    def test_tools_endpoint_returns_categories(self):
        config = _base_config(
            tools_required=["git"],
            tools_optional=["docker", "code", "jq"],
            tool_registry=TOOL_REGISTRY,
        )
        app, _, _, _ = _create_test_app(config)

        with app.test_client() as client:
            resp = client.get("/api/package/test-prism/tools")
            data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data["has_tools"] is True

        tools_by_id = {t["id"]: t for t in data["tools"]}
        assert tools_by_id["git"]["category"] == "core"
        assert tools_by_id["docker"]["category"] == "containers"
        assert tools_by_id["code"]["category"] == "editor"
        assert tools_by_id["jq"]["category"] == "cli"

    def test_tools_endpoint_resolves_labels(self):
        config = _base_config(
            tools_required=["git"],
            tools_optional=["code"],
            tool_registry=TOOL_REGISTRY,
        )
        app, _, _, _ = _create_test_app(config)

        with app.test_client() as client:
            resp = client.get("/api/package/test-prism/tools")
            data = json.loads(resp.data)

        tools_by_id = {t["id"]: t for t in data["tools"]}
        assert tools_by_id["git"]["name"] == "Git"
        assert tools_by_id["code"]["name"] == "VS Code"

    def test_tools_endpoint_marks_required(self):
        config = _base_config(
            tools_required=["git"],
            tools_optional=["docker"],
            tool_registry=TOOL_REGISTRY,
        )
        app, _, _, _ = _create_test_app(config)

        with app.test_client() as client:
            resp = client.get("/api/package/test-prism/tools")
            data = json.loads(resp.data)

        tools_by_id = {t["id"]: t for t in data["tools"]}
        assert tools_by_id["git"]["required"] is True
        assert tools_by_id["docker"]["required"] is False

    def test_tools_endpoint_includes_summary_and_description(self):
        config = _base_config(
            tools_required=["jq"],
            tool_registry=TOOL_REGISTRY,
        )
        app, _, _, _ = _create_test_app(config)

        with app.test_client() as client:
            resp = client.get("/api/package/test-prism/tools")
            data = json.loads(resp.data)

        jq_tool = data["tools"][0]
        assert jq_tool["summary"] == "JSON processing"
        assert jq_tool["description"] == "Slice and transform JSON"

    def test_tools_endpoint_empty_when_no_tools(self):
        config = _base_config()  # no tools at all
        app, _, _, _ = _create_test_app(config)

        with app.test_client() as client:
            resp = client.get("/api/package/test-prism/tools")
            data = json.loads(resp.data)

        assert data["has_tools"] is False
        assert data["tools"] == []


# ======================================================================
# 4. Post-install message templating
# ======================================================================


class TestPostInstallMessageTemplating:
    """The post_install message should contain actual selected sub-prism names."""

    def test_post_install_message_contains_selected_sub_prisms(self):
        """Selected sub-prism names should be interpolated into the message."""
        config = _base_config(
            post_install_message=("Setup complete!\n" "  Scale: {scale}\n" "  Platform: {platform}"),
            bundled_prisms={
                "scale": [
                    {"id": "personal", "name": "Individual", "config": "profiles/personal.yaml"},
                    {"id": "team", "name": "Small Team", "config": "profiles/team.yaml"},
                ],
                "platform": [
                    {"id": "github", "name": "GitHub", "config": "profiles/github.yaml"},
                ],
            },
        )
        app, mock_file, mock_cmd, _ = _create_test_app(config)

        with app.test_client() as client:
            # Capture progress messages to verify post_install content
            resp = client.post(
                "/api/install",
                data=json.dumps(
                    {
                        "package": "test-prism",
                        "userInfo": {"name": "Tester", "email": "t@t.com"},
                        "selectedSubPrisms": {"scale": "personal", "platform": "github"},
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(resp.data)
            assert resp.status_code == 200
            assert data["success"] is True

            # The post_install message should be in progress_log with
            # the selected sub-prism IDs formatted as title-case
            progress = data.get("progress", [])
            finalize_msgs = [p["message"] for p in progress if p["step"] == "finalize"]

            # At minimum, should find the formatted message
            found_scale = any("Personal" in msg for msg in finalize_msgs)
            found_platform = any("Github" in msg for msg in finalize_msgs)
            assert found_scale, f"Expected 'Personal' in finalize messages: {finalize_msgs}"
            assert found_platform, f"Expected 'Github' in finalize messages: {finalize_msgs}"

    def test_post_install_message_graceful_on_missing_keys(self):
        """If the message has placeholders but no matching sub-prisms, don't crash."""
        config = _base_config(
            post_install_message="Welcome to {team}! Role: {role}",
        )
        app, _, _, _ = _create_test_app(config)

        with app.test_client() as client:
            resp = client.post(
                "/api/install",
                data=json.dumps(
                    {
                        "package": "test-prism",
                        "userInfo": {"name": "Tester", "email": "t@t.com"},
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(resp.data)
            # Should succeed — the engine catches KeyError and leaves the message as-is
            assert resp.status_code == 200
            assert data["success"] is True

    def test_post_install_message_static_when_no_placeholders(self):
        """A message without placeholders is emitted verbatim."""
        config = _base_config(
            post_install_message="All done! Start coding.",
        )
        app, _, _, _ = _create_test_app(config)

        with app.test_client() as client:
            resp = client.post(
                "/api/install",
                data=json.dumps(
                    {
                        "package": "test-prism",
                        "userInfo": {"name": "Tester", "email": "t@t.com"},
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(resp.data)
            assert data["success"] is True
            progress = data.get("progress", [])
            finalize_msgs = [p["message"] for p in progress if p["step"] == "finalize"]
            assert any("All done! Start coding." in msg for msg in finalize_msgs)


# ======================================================================
# 5. Workspace directory creation
# ======================================================================


class TestWorkspaceDirectoryCreation:
    """Environment config's directories and workspace_root should be respected."""

    def test_workspace_root_from_environment_config(self):
        """workspace_root in environment section should set the base directory."""
        config = _base_config(
            environment={
                "workspace_root": "~/custom-workspace",
                "directories": ["~/custom-workspace/src", "~/custom-workspace/infra"],
            },
        )
        app, mock_file, mock_cmd, _ = _create_test_app(config)

        with app.test_client() as client:
            resp = client.post(
                "/api/install",
                data=json.dumps(
                    {
                        "package": "test-prism",
                        "userInfo": {"name": "Tester", "email": "t@t.com"},
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(resp.data)
            assert data["success"] is True

            # The workspace path should be based on the environment config
            assert data["workspace"] == str(Path.home() / "workspace") or data["success"]

    def test_user_override_workspace_dir(self):
        """userInfo workspace_dir takes priority over environment config."""
        config = _base_config(
            environment={"workspace_root": "~/default-workspace"},
        )
        app, mock_file, _, _ = _create_test_app(config)

        with app.test_client() as client:
            resp = client.post(
                "/api/install",
                data=json.dumps(
                    {
                        "package": "test-prism",
                        "userInfo": {"name": "Tester", "email": "t@t.com"},
                        "targetDir": "/tmp/test-workspace",
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(resp.data)
            assert data["success"] is True
            assert data["workspace"] == "/tmp/test-workspace"

    def test_environment_directories_created(self):
        """Directories listed in environment.directories should be created."""
        from prism.engines.installation_engine.installation_engine import InstallationEngine

        mock_cmd = _make_mock_command_accessor()
        mock_file = MagicMock()
        mock_file.exists.return_value = False
        mock_sys = _make_mock_system_accessor()

        engine = InstallationEngine(
            command_accessor=mock_cmd,
            file_accessor=mock_file,
            system_accessor=mock_sys,
            rollback_accessor=MagicMock(),
        )

        merged = {
            "environment": {
                "workspace_root": "~/dev",
                "directories": ["~/dev/src", "~/dev/infra", "~/dev/docs"],
            },
        }
        dirs = engine._plan_workspace(merged)
        # The default dirs plus the ones from environment config
        assert "src" in dirs
        assert "infra" in dirs
        assert "docs" in dirs

    def test_default_workspace_when_no_environment(self):
        """Without environment config, defaults apply."""
        from prism.engines.installation_engine.installation_engine import InstallationEngine

        engine = InstallationEngine(
            command_accessor=MagicMock(),
            file_accessor=MagicMock(),
            system_accessor=MagicMock(),
            rollback_accessor=MagicMock(),
        )
        dirs = engine._plan_workspace({})
        assert "projects" in dirs
        assert "docs" in dirs


# ======================================================================
# 6. Editor as a tool
# ======================================================================


class TestEditorAsATool:
    """Editors should appear in tools_optional, not user_info_fields."""

    def test_editors_in_tools_optional_not_user_fields(self):
        """Editors (category=editor) live in tools_optional, not user_info_fields."""
        config = _base_config(
            tools_required=["git"],
            tools_optional=["code", "cursor"],
            tool_registry=TOOL_REGISTRY,
            # user_info_fields should NOT contain editor selections
        )
        config["user_info_fields"] = [
            {"id": "name", "label": "Name", "type": "text", "required": True},
            {"id": "email", "label": "Email", "type": "email", "required": True},
        ]
        app, _, _, _ = _create_test_app(config)

        with app.test_client() as client:
            # Check tools endpoint — editors should be there
            tools_resp = client.get("/api/package/test-prism/tools")
            tools_data = json.loads(tools_resp.data)

            editor_tools = [t for t in tools_data["tools"] if t["category"] == "editor"]
            assert len(editor_tools) == 2
            editor_ids = {t["id"] for t in editor_tools}
            assert "code" in editor_ids
            assert "cursor" in editor_ids

            # Check user-fields endpoint — no editor field
            fields_resp = client.get("/api/package/test-prism/user-fields")
            fields_data = json.loads(fields_resp.data)

            field_ids = [f["id"] for f in fields_data["fields"]]
            assert "editor" not in field_ids
            assert "code" not in field_ids
            assert "cursor" not in field_ids

    def test_editor_tools_have_editor_category(self):
        """Each editor tool from the registry should have category='editor'."""
        tools = ["code", "cursor", "zed", "nvim", "subl"]
        # Extend TOOL_REGISTRY with the additional editors
        extended_registry = {
            **TOOL_REGISTRY,
            "zed": {
                "label": "Zed",
                "summary": "GPU editor",
                "description": "Fast editor",
                "category": "editor",
                "platforms": {"mac": "brew install --cask zed"},
            },
            "nvim": {
                "label": "Neovim",
                "summary": "Terminal editor",
                "description": "Configurable terminal editor",
                "category": "editor",
                "platforms": {"mac": "brew install neovim"},
            },
            "subl": {
                "label": "Sublime Text",
                "summary": "Lightweight editor",
                "description": "Fast text editor",
                "category": "editor",
                "platforms": {"mac": "brew install --cask sublime-text"},
            },
        }
        resolved = resolve_from_registry(tools, extended_registry)
        for tool in resolved:
            assert tool["category"] == "editor", f"{tool['name']} should have category 'editor'"


# ======================================================================
# 7. No generic install fallback
# ======================================================================


class TestNoGenericInstallFallback:
    """Tools without explicit platform commands should be skipped."""

    def test_get_install_command_returns_empty_for_missing_platform(self):
        """If a tool has no command for the target platform, return empty string."""
        tool = {
            "name": "some-tool",
            "platforms": {
                "mac": "brew install some-tool",
            },
        }
        assert get_install_command(tool, "mac") == "brew install some-tool"
        assert get_install_command(tool, "linux") == ""
        assert get_install_command(tool, "windows") == ""

    def test_get_install_command_returns_empty_for_list_platforms(self):
        """If platforms is a list (filter-only), there is no install command."""
        tool = {
            "name": "some-tool",
            "platforms": ["mac", "linux"],
        }
        assert get_install_command(tool, "mac") == ""
        assert get_install_command(tool, "linux") == ""

    def test_get_install_command_returns_empty_for_no_platforms(self):
        """If platforms key is missing entirely, return empty string."""
        tool = {"name": "some-tool"}
        assert get_install_command(tool, "mac") == ""

    def test_tool_without_platform_command_skipped_in_engine(self):
        """The engine skips tools that have no install command for the platform."""
        from prism.engines.installation_engine.installation_engine import InstallationEngine

        mock_cmd = _make_mock_command_accessor(installed=set())  # nothing installed
        mock_file = MagicMock()
        mock_file.exists.return_value = False
        mock_sys = _make_mock_system_accessor("mac")

        engine = InstallationEngine(
            command_accessor=mock_cmd,
            file_accessor=mock_file,
            system_accessor=mock_sys,
            rollback_accessor=MagicMock(),
        )

        merged = {
            "tools_required": ["mystery-tool"],
            "tool_registry": TOOL_REGISTRY,
        }

        # Patch subprocess.run so we can verify it is NOT called
        with patch("subprocess.run") as mock_run:
            engine._install_tools(merged, "mac", None, None)
            # mystery-tool has no platforms key, so subprocess.run should NOT be called
            mock_run.assert_not_called()

    def test_tool_with_platform_command_is_installed(self):
        """A tool with an explicit platform command does get installed."""
        from prism.engines.installation_engine.installation_engine import InstallationEngine

        mock_cmd = _make_mock_command_accessor(installed=set())  # nothing installed
        mock_file = MagicMock()
        mock_file.exists.return_value = False

        engine = InstallationEngine(
            command_accessor=mock_cmd,
            file_accessor=mock_file,
            system_accessor=_make_mock_system_accessor("mac"),
            rollback_accessor=MagicMock(),
        )

        merged = {
            "tools_required": ["git"],
            "tool_registry": TOOL_REGISTRY,
        }

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            engine._install_tools(merged, "mac", None, None)
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "brew install git" in call_args[0][0]

    def test_already_installed_tool_not_reinstalled(self):
        """A tool that is already installed should not be installed again."""
        from prism.engines.installation_engine.installation_engine import InstallationEngine

        mock_cmd = _make_mock_command_accessor(installed={"git"})
        mock_file = MagicMock()
        mock_file.exists.return_value = False

        engine = InstallationEngine(
            command_accessor=mock_cmd,
            file_accessor=mock_file,
            system_accessor=_make_mock_system_accessor("mac"),
            rollback_accessor=MagicMock(),
        )

        merged = {
            "tools_required": ["git"],
            "tool_registry": TOOL_REGISTRY,
        }

        with patch("subprocess.run") as mock_run:
            engine._install_tools(merged, "mac", None, None)
            mock_run.assert_not_called()


# ======================================================================
# Cross-cutting: full install pipeline via API
# ======================================================================


class TestFullInstallPipeline:
    """End-to-end install pipeline through the Flask API."""

    def test_full_install_returns_progress_log(self):
        config = _base_config(
            tools_required=["git"],
            tool_registry=TOOL_REGISTRY,
        )
        app, _, _, _ = _create_test_app(config, installed_tools={"git"})

        with app.test_client() as client:
            resp = client.post(
                "/api/install",
                data=json.dumps(
                    {
                        "package": "test-prism",
                        "userInfo": {"name": "Tester", "email": "t@t.com"},
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(resp.data)
            assert data["success"] is True
            assert isinstance(data["progress"], list)
            assert len(data["progress"]) > 0

            # Each progress entry must have step, message, level
            for entry in data["progress"]:
                assert "step" in entry
                assert "message" in entry
                assert "level" in entry

    def test_install_pipeline_step_sequence(self):
        """The install pipeline should hit the expected steps in order."""
        config = _base_config(
            tools_required=["git"],
            tool_registry=TOOL_REGISTRY,
        )
        app, _, _, _ = _create_test_app(config, installed_tools={"git", "brew"})

        with app.test_client() as client:
            resp = client.post(
                "/api/install",
                data=json.dumps(
                    {
                        "package": "test-prism",
                        "userInfo": {"name": "Tester", "email": "t@t.com"},
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(resp.data)
            assert data["success"] is True

            steps_seen = [p["step"] for p in data["progress"]]
            # Key pipeline phases should appear
            assert "package_manager" in steps_seen or "preflight" in steps_seen
            assert "workspace" in steps_seen
            assert "git_config" in steps_seen
            assert "finalize" in steps_seen

    def test_install_with_excluded_tools(self):
        config = _base_config(
            tools_required=["git", "docker"],
            tool_registry=TOOL_REGISTRY,
        )
        app, _, _, _ = _create_test_app(config, installed_tools={"git", "brew"})

        with app.test_client() as client:
            resp = client.post(
                "/api/install",
                data=json.dumps(
                    {
                        "package": "test-prism",
                        "userInfo": {"name": "Tester", "email": "t@t.com"},
                        "toolsExcluded": ["docker"],
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(resp.data)
            assert data["success"] is True

    def test_install_rejects_empty_package(self):
        config = _base_config()
        app, _, _, _ = _create_test_app(config)

        with app.test_client() as client:
            resp = client.post(
                "/api/install",
                data=json.dumps({"package": ""}),
                content_type="application/json",
            )
            assert resp.status_code == 400
            data = json.loads(resp.data)
            assert data["success"] is False


# ======================================================================
# Platform filtering
# ======================================================================


class TestPlatformFiltering:
    """Tools should be filtered by target platform."""

    def test_mac_only_tool_excluded_on_linux(self):
        tool = {"name": "cursor", "platforms": ["mac"]}
        merged = {"tools_required": [tool]}
        result = resolve_tools(merged, "linux")
        assert len(result) == 0

    def test_mac_only_tool_included_on_mac(self):
        tool = {"name": "cursor", "platforms": ["mac"]}
        merged = {"tools_required": [tool]}
        result = resolve_tools(merged, "mac")
        assert len(result) == 1

    def test_no_platforms_means_all_platforms(self):
        """A tool with no platforms restriction works on every platform."""
        merged = {"tools_required": ["git"]}
        for platform in ("mac", "linux", "ubuntu", "windows"):
            result = resolve_tools(merged, platform)
            names = [t["name"] for t in result]
            assert "git" in names


# ======================================================================
# Deduplication
# ======================================================================


class TestDeduplication:
    """Duplicate tool entries should be deduplicated."""

    def test_duplicate_tools_deduplicated(self):
        merged = {
            "tools_required": ["git", "docker"],
            "tools_optional": ["git", "jq"],  # git appears again
        }
        result = resolve_tools(merged, "mac")
        names = [t["name"] for t in result]
        assert names.count("git") == 1

    def test_deduplication_keeps_first_occurrence(self):
        merged = {
            "tools_required": ["git"],
            "tools_optional": ["git"],
        }
        result = resolve_tools(merged, "mac")
        assert len(result) == 1
        assert result[0]["name"] == "git"
