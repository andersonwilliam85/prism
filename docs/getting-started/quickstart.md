---
layout: default
title: Quickstart
---

# Quickstart

Get your development environment configured in minutes with Prism.

---

## Prerequisites

- Python 3.9+
- Git

```bash
make install-dev
```

---

## Option A: Web UI (Recommended)

```bash
make run
# Opens at http://localhost:5555
```

The web UI walks you through:
1. **Choose a prism** — prism, startup, acme-corp, fortune500, etc.
2. **Select sub-prisms** — pick your role, division, team, etc.
3. **Select tools** — tool selection page with categories (Core, Editor, Containers, Runtime, Cloud, Kubernetes, CLI), hover tooltips, and platform-aware filtering
4. **Fill in your info** — name, email, platform-specific fields (inline validation, no alerts)
5. **Install** — watch the live progress log; cancel/retry if needed

---

## Option B: CLI

```bash
# Install from PyPI
pip install prism-dx
prism install

# Install a specific prism
prism install --prism prism

# Install with a custom npm registry (corporate environments)
prism install --prism fortune500 --npm-registry https://npm.mycompany.com
```

---

## What Gets Installed

After installation you'll have:

```
~/workspace/
+-- projects/          <- your code lives here
+-- experiments/
+-- learning/
+-- archived/
+-- docs/
|   +-- config/        <- your prism configuration files
|       +-- merged-config.yaml   <- the merged result of all sub-prisms
|       +-- user-info.yaml
+-- tooling/
```

Plus:
- Git configured with your name and email
- SSH key generated (`~/.ssh/id_ed25519`)
- Only the tools you checked in the UI get installed (from the centralized tool registry)
- Repositories cloned (if declared in your prism)
- A `.prism_rollback.json` manifest for undoing the installation

---

## Rollback

If something goes wrong, reverse the installation:

```bash
prism rollback ~/workspace
```

The rollback engine reads `.prism_rollback.json` and undoes all recorded actions in LIFO order (uninstalls tools, deletes files and directories, restores config changes).

---

## Installation History

View previous installations on your machine:

```bash
prism history
```

Also available via the `/api/history` endpoint.

---

## Your First Custom Prism

```bash
# Create a scaffold for your company
prism packages create my-company --company "My Company"

# Customize the base configuration
vim prisms/my-company.prism/base/my-company.yaml

# Add tools to the tool registry
vim prisms/my-company.prism/base/tool-registry.yaml

# Validate it
prism packages validate my-company

# Install it
prism install --prism my-company
```

---

## Next Steps

- [Choose the right prism](choosing-a-prism.md)
- [Understand sub-prism inheritance](../user-guide/config-inheritance.md)
- [Create your own prism](../user-guide/creating-configurations.md)
- [Configuration schema reference](../reference/configuration-schema.md)
