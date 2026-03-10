---
layout: default
title: Rollback System
---

# Rollback System

Prism tracks every action during installation so it can undo them if something fails. Rollback is owned by the **InstallationEngine**, which receives a **RollbackAccessor** via constructor injection for I/O (state persistence, file deletion, command execution).

---

## Action Types

Every install step records what it did as a `RollbackAction`:

| Action Type | Target | Rollback Behavior |
|---|---|---|
| `file_created` | File path | Auto-rollback: delete the file |
| `dir_created` | Directory path | Auto-rollback: delete the directory tree |
| `command_executed` | Command string | Requires explicit `rollback_command` |
| `package_installed` | Package name | Requires explicit `rollback_command` |
| `config_changed` | Config key/path | Restores `original_value` if recorded |

### Auto-Rollback vs Explicit Rollback

- **Auto-rollback types** (`file_created`, `dir_created`): The accessor knows how to undo these without any additional information — it deletes the file or directory.
- **Explicit rollback types** (`command_executed`, `package_installed`): These require a `rollback_command` string specified at recording time. If no rollback command is provided, the action is skipped during rollback and a warning is logged.
- **Config changes**: Rolled back only if `original_value` was captured when the change was recorded.

---

## LIFO Undo Sequence

Actions are undone in reverse chronological order (Last-In-First-Out). If an installation creates a directory, writes files into it, then installs a package, the rollback sequence is:

```
1. Uninstall the package (rollback_command)
2. Delete the files (auto)
3. Delete the directory (auto)
```

This ensures dependent artifacts are removed before their containers.

---

## InstallationEngine — Rollback Logic

The InstallationEngine handles rollback computation and delegates I/O to the RollbackAccessor:

```python
engine = InstallationEngine(rollback_accessor=accessor, ...)

# Create state for an installation
state = engine.create_rollback_state("my-company-prism")

# Record actions as installation progresses
engine.record_rollback_action(state, "dir_created", "/home/user/workspace")
engine.record_rollback_action(state, "file_created", "/home/user/workspace/config.yaml")
engine.record_rollback_action(state, "command_executed", "npm install eslint",
                              rollback_command="npm uninstall eslint")

# Compute the undo plan (LIFO, filtered)
plan = engine.compute_rollback_plan(state)

# Validate completeness — warns about actions with no rollback path
all_covered, warnings = engine.validate_rollback_completeness(state)
```

---

## RollbackAccessor (I/O)

The accessor handles persistence and execution:

### State Persistence

Rollback state is serialized to JSON temp files (`/tmp/prism_rollback_*.json`). This survives crashes — if the process dies mid-install, the state file remains on disk for recovery.

```python
accessor = RollbackAccessor()

# Save state to temp file
path = accessor.save_state(state)
# Returns something like: /tmp/prism_rollback_a1b2c3.json

# Load state from temp file (e.g., after crash)
recovered_state = accessor.load_state(path)
```

### Rollback Execution

The accessor executes each action in the rollback plan:

```python
# Delete a file
accessor.delete_file("/home/user/workspace/config.yaml")

# Delete a directory tree
accessor.delete_directory("/home/user/workspace")

# Run a rollback command (60-second timeout)
success, output = accessor.run_command("npm uninstall eslint")
```

---

## State File Format

```json
{
  "package_name": "my-company-prism",
  "started_at": "2026-03-10T12:00:00",
  "rolled_back": false,
  "actions": [
    {
      "action_type": "dir_created",
      "target": "/home/user/workspace",
      "rollback_command": "",
      "original_value": "",
      "timestamp": "2026-03-10T12:00:01"
    },
    {
      "action_type": "file_created",
      "target": "/home/user/workspace/config.yaml",
      "rollback_command": "",
      "original_value": "",
      "timestamp": "2026-03-10T12:00:02"
    }
  ]
}
```

---

## Crash Recovery

If Prism crashes during installation:

1. The rollback state file remains in `/tmp/prism_rollback_*.json`
2. On next run, Prism can detect incomplete installations by scanning for state files
3. The state is loaded via the RollbackAccessor's `load_state()` method
4. The rollback plan is computed and executed to clean up partial state

If the state file itself is corrupted (invalid JSON, missing keys), `load_state()` returns `None` and the recovery is skipped.

---

## Completeness Validation

Before starting an install, the InstallationEngine can check if all planned actions have rollback coverage:

```python
all_covered, warnings = engine.validate_rollback_completeness(state)
if not all_covered:
    for w in warnings:
        print(f"Warning: {w}")
    # e.g., "No rollback for command_executed: custom-setup.sh"
```

Actions without rollback paths are silently skipped during rollback execution. The validation step lets you surface these gaps proactively.

---

## See Also

- [Architecture](architecture.md) — Where InstallationEngine and RollbackAccessor fit in the system
- [Privilege Separation](privilege-separation.md) — How rollback interacts with sudo operations
- [Installation](../getting-started/installation.md) — The install flow that generates rollback actions
