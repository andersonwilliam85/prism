---
layout: default
title: Prism System
---

# Prism System

**Modular, distributable, version-controlled development environment configurations.**

---

## Overview

The Prism system lets organizations create, distribute, and install complete development environment configurations as self-contained **prisms**. Like a prism refracts white light into a spectrum, Prism refracts organizational complexity into clear, composable configuration layers.

### Key Benefits

- **Hierarchical** — base -> division -> role -> team, each layer inheriting the last
- **Modular** — install only the sub-prisms you need
- **Centralized tool registry** — tools defined once in `tool-registry.yaml`, referenced by name
- **Distributable** — share via git, registry, or local files
- **Version-controlled** — track changes over time
- **Discoverable** — auto-finds prisms in `prisms/`
- **Validatable** — config engine validates tool registry, tool references, and email patterns
- **Rollback** — `.prism_rollback.json` manifest enables `prism rollback`

---

## Tool Registry

Each prism's base directory contains a `tool-registry.yaml` file — the single source of truth for every installable tool. Child configs reference tools by string name only (e.g., `- git`).

### Tool Definition Format

```yaml
git:
  label: Git
  summary: Version control
  description: Track changes, branch, merge, and collaborate on code
  category: core
  platforms:
    mac: brew install git
    ubuntu: sudo apt-get install -y git
    linux: sudo apt-get install -y git
    windows: winget install Git.Git
  uninstall:
    mac: brew uninstall git
    ubuntu: sudo apt-get remove -y git
    linux: sudo apt-get remove -y git
    windows: winget uninstall Git.Git
```

### Fields

| Field | Description |
|---|---|
| `label` | Display name shown in the UI |
| `summary` | Short tagline, always visible next to the label |
| `description` | Full explanation, shown on hover in the UI |
| `category` | Grouping key for the UI |
| `platforms` | Per-OS install commands (mac, ubuntu, linux, windows) |
| `uninstall` | Per-OS uninstall commands (used by rollback) |

### Tool Categories

| Category | Examples |
|---|---|
| `core` | git, curl |
| `editor` | VS Code, Cursor, Zed, Neovim, Sublime Text |
| `containers` | Docker, Rancher Desktop, Podman |
| `runtime` | nvm, pyenv, SDKMAN, .NET, Rust, Go, Perl, rbenv |
| `cloud` | AWS CLI, Azure CLI, Google Cloud CLI, Terraform, Pulumi |
| `kubernetes` | kubectl, Helm, K9s, kubectx, Stern, Kustomize, Skaffold, Argo CD |
| `cli` | GitHub CLI, HTTPie, jq, tmux, ripgrep, fd, fzf, lazygit |

### No Generic Fallbacks

Tools without explicit platform install commands for the current OS are skipped. Prism does not guess install commands.

### Validation

The config engine validates the tool registry:
- Every tool must have `platforms` (install commands)
- Every tool should have `uninstall` commands (for rollback)
- Every platform with an install command should have a matching uninstall command
- Tool references in sub-prism configs (e.g., `tools_required: [git]`) must exist in the registry

---

## Starter Packages

Prism ships with 8 starter packages in the `prisms/` directory:

| Package | Directory | Use Case |
|---|---|---|
| `prism` | `prisms/prism.prism/` | Default — solo developers |
| `startup` | `prisms/startup.prism/` | Startups (10--50) |
| `acme-corp` | `prisms/acme-corp.prism/` | Template for companies (100--1K) |
| `consulting-firm` | `prisms/consulting-firm.prism/` | Multi-client work |
| `fortune500` | `prisms/fortune500.prism/` | Enterprise (50K+) |
| `university` | `prisms/university.prism/` | Academic institutions |
| `opensource` | `prisms/opensource.prism/` | Community projects |
| `cli-test-prism` | `prisms/cli-test-prism.prism/` | CLI testing fixture |

---

## Quick Start

### List Available Prisms

```bash
prism packages list
```

### Get Prism Info

```bash
prism packages info acme-corp
```

### Install a Prism

```bash
# Via CLI
prism install --prism acme-corp

# Via Web UI
make run
```

### Roll Back an Installation

```bash
prism rollback ~/workspace
```

### View Installation History

```bash
prism history
```

### Validate a Prism

```bash
prism packages validate my-company
```

---

## Prism Structure

### Minimal Prism

```
my-company.prism/
+-- package.yaml          # REQUIRED — identity, prism_config, bundled_prisms
+-- README.md             # Recommended
+-- base/
    +-- my-company.yaml   # Referenced by bundled_prisms.base
    +-- tool-registry.yaml # Centralized tool definitions
```

### Full Hierarchical Prism

```
my-company.prism/
+-- package.yaml
+-- README.md
+-- welcome.yaml
+-- resources.yaml
+-- base/
|   +-- my-company.yaml         # Company-wide settings
|   +-- tool-registry.yaml      # Centralized tool definitions
+-- divisions/
|   +-- technology.yaml
|   +-- digital.yaml
|   +-- data-analytics.yaml
+-- roles/
|   +-- software-engineer.yaml
|   +-- devops-engineer.yaml
|   +-- data-engineer.yaml
+-- teams/
    +-- platform-team.yaml
    +-- mobile-team.yaml
```

---

## `package.yaml` Schema (Summary)

```yaml
package:          # Identity: name, version, description, type
prism_config:     # Prism tool settings: theme, proxy, registry, branding
bundled_prisms:   # Hierarchical sub-prisms: base + optional tiers
setup:            # File installation steps
user_info_fields: # Info collected from the user
distribution:     # Where this prism is sourced from
metadata:         # Tags, keywords, company_size
```

See [Configuration Schema](configuration-schema.md) for the complete reference.

---

## Installation Flow

1. User selects a prism and sub-prisms
2. UI presents tool selection page with categories — user checks the tools they want
3. UI sends `toolsSelected` from checkboxes to the API
4. Only checked tools get installed; `tools_selected=[]` means nothing is installed
5. Installation engine executes install commands from the tool registry
6. Subprocesses have timeouts and `GIT_TERMINAL_PROMPT=0`
7. A `.prism_rollback.json` manifest is persisted for later rollback
8. User can cancel/retry from the UI

---

## Creating Your Own Prism

### Option 1: Scaffold Generator

```bash
prism packages create my-company --company "My Company"
```

### Option 2: Copy a Template

```bash
# Small/medium company starting point
cp -r prisms/acme-corp.prism prisms/my-company.prism

# Enterprise starting point
cp -r prisms/fortune500.prism prisms/my-company.prism
```

### Option 3: From Scratch

See [Creating Prisms](../user-guide/creating-configurations.md).

---

## CLI Reference

### `prism install`

```bash
prism install --prism <prism-name>
```

### `prism rollback`

```bash
prism rollback <workspace>
```

Reads `.prism_rollback.json` and reverses all recorded actions in LIFO order.

### `prism history`

```bash
prism history [search_paths...]
```

Scans for `.prism_installed` and `.prism_rollback.json` markers. Default search paths: `~`, `~/dev`, `~/projects`, `~/workspace`, `~/Development`. Also available via the `/api/history` endpoint.

### `prism packages list`

Lists all discoverable prisms in `prisms/`.

### `prism packages info`

```bash
prism packages info <prism-name>
```

Shows full prism details — version, type, sub-prism tiers, metadata.

### `prism packages validate`

```bash
prism packages validate <prism-name>
```

Checks:
- `package.yaml` exists and is valid YAML
- Required fields present
- `bundled_prisms` config files exist on disk
- `user_info_fields` have valid types
- `prism_config.theme` is a valid theme name
- Tool registry has install + uninstall commands
- Tool references exist in the registry

### `prism ui`

```bash
prism ui
```

Launches the web UI at `http://localhost:5555`.

---

## Best Practices

### 1. Versioning

Use [Semantic Versioning](https://semver.org/):
- `1.0.0` — initial release
- `1.0.1` — bug fixes (broken links, typos)
- `1.1.0` — new sub-prisms or tiers
- `2.0.0` — breaking changes (restructure, rename tiers)

### 2. One base sub-prism per prism

The `base` tier should have exactly one entry marked `required: true`. It holds settings that apply to **everyone** in your organization.

### 3. Security

Never include in prisms:
- API keys or secrets
- Personal SSH keys
- Private internal URLs (in public repos)

Use environment variable placeholders:
```yaml
git:
  user:
    email: "${USER}@mycompany.com"
```

### 4. Testing

```bash
# Validate structure
prism packages validate my-company

# Full install in clean environment
prism install --prism my-company
```

### 5. Documentation

Always include:
- `README.md` — what's included, how to customize
- Comments in YAML sub-prism files

---

## Support

1. Check prism README: `prisms/<name>.prism/README.md`
2. Validate: `prism packages validate <name>`
3. [Open an issue](https://github.com/andersonwilliam85/prism/issues)

---

**Prism — Refract complexity into clarity**
