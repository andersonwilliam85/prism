---
layout: default
title: Rollback System
---

# Rollback System

Prism tracks every action during installation and persists a `.prism_rollback.json` manifest to disk. This manifest powers both the `prism rollback` CLI command and the UI rollback button.

The rollback engine lives at `prism/engines/rollback_engine.py` and is shared by the CLI (`prism rollback`) and the API (`/api/rollback`).

---

## `.prism_rollback.json` Manifest

Every installation writes a `.prism_rollback.json` file to the workspace directory. This file records every action taken during the install so it can be reversed later.

```json
{
  "package_name": "my-company-prism",
  "started_at": "2026-03-10T12:00:00",
  "actions": [
    {
      "type": "dir_created",
      "target": "/home/user/workspace",
      "rollback_command": "",
      "original_value": "",
      "timestamp": "2026-03-10T12:00:01"
    },
    {
      "type": "file_created",
      "target": "/home/user/workspace/config.yaml",
      "rollback_command": "",
      "original_value": "",
      "timestamp": "2026-03-10T12:00:02"
    },
    {
      "type": "tool_installed",
      "target": "docker",
      "rollback_command": "brew uninstall --cask docker",
      "original_value": "",
      "timestamp": "2026-03-10T12:00:03"
    }
  ]
}
```

---

## Action Types

Every install step records what it did as an action in the manifest:

| Action Type | Target | Rollback Behavior |
|---|---|---|
| `tool_installed` | Tool name | Runs the `rollback_command` (uninstall command from tool registry) |
| `file_created` | File path | Deletes the file |
| `dir_created` | Directory path | Removes the directory (skips if not empty) |
| `config_changed` | Config key/path | Restores `original_value` if recorded |

### Tool Uninstall Commands

Because tools are defined in the centralized `tool-registry.yaml` with explicit `uninstall` commands per platform, the rollback engine knows exactly how to reverse each tool installation. Tools without uninstall commands are skipped during rollback.

---

## LIFO Undo Sequence

Actions are undone in reverse chronological order (Last-In-First-Out). If an installation creates a directory, writes files into it, then installs a tool, the rollback sequence is:

```
1. Uninstall the tool (rollback_command from registry)
2. Delete the files
3. Delete the directory
```

This ensures dependent artifacts are removed before their containers.

---

## CLI: `prism rollback`

```bash
# Roll back using workspace path
prism rollback ~/workspace

# Without arguments, searches common locations for .prism_rollback.json
prism rollback
```

The CLI searches for `.prism_rollback.json` in these locations (in order):
1. The provided workspace path
2. `~/.prism_rollback.json`
3. Current working directory

After rollback completes, the manifest file is deleted.

---

## UI Rollback

The web UI includes a rollback button. When clicked, it calls the `/api/rollback` endpoint, which uses the same `rollback_engine.py` as the CLI.

---

## Rollback Engine

The rollback engine at `prism/engines/rollback_engine.py` provides three functions:

```python
from prism.engines.rollback_engine import find_manifest, load_manifest, execute_rollback

# Find the manifest file
manifest_path = find_manifest("/home/user/workspace")

# Load and parse it
manifest = load_manifest(manifest_path)

# Execute rollback with optional progress callback
results = execute_rollback(manifest, log_fn=lambda msg, level: print(msg))
```

Each result in the returned list contains:
- `action` — the target (tool name, file path, etc.)
- `type` — the action type
- `success` — whether the rollback succeeded
- `detail` — human-readable outcome ("uninstalled", "removed", "already gone", "not empty")

---

## Crash Recovery

If Prism crashes during installation:

1. The `.prism_rollback.json` manifest remains on disk
2. On next run, `prism rollback` can find and load the manifest
3. The rollback plan is computed and executed to clean up partial state

---

## Installation History

The `prism history` command scans common directories for `.prism_installed` and `.prism_rollback.json` markers to list previous installations:

```bash
prism history
prism history ~/dev ~/projects
```

Also available via the `/api/history` endpoint.

---

## See Also

- [Architecture](architecture.md) — Where the rollback engine fits in the system
- [Privilege Separation](privilege-separation.md) — How rollback interacts with sudo operations
- [Installation](../getting-started/installation.md) — The install flow that generates rollback actions
