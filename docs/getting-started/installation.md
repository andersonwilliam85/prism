---
layout: default
title: Installation
---

# Installation

## Requirements

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.9+ | Required |
| Git | Any | Required |
| Flask | Latest | Web UI only |
| Rich | Latest | Better CLI output (optional) |

---

## Install from PyPI

```bash
pip install prism-dx
prism ui            # Launch the web installer
prism install       # Or install directly from CLI
```

---

## Install from Source

```bash
git clone https://github.com/andersonwilliam85/prism.git
cd prism
make install-dev
```

---

## Start the Web UI

```bash
make run
# Opens at http://localhost:5555
```

---

## CLI Usage

```bash
# Show help
prism --help

# Launch web UI
prism ui

# Install a specific prism
prism install --prism prism

# Roll back a previous installation
prism rollback ~/workspace

# View installation history
prism history

# Use a custom npm registry
prism install --prism fortune500 --npm-registry https://npm.mycompany.com
```

---

## Corporate / Air-Gapped Environments

If your environment requires a proxy or custom npm registry, configure them in `prism_config` inside your prism's `package.yaml`:

```yaml
prism_config:
  proxies:
    http: "http://proxy.mycompany.com:8080"
    https: "http://proxy.mycompany.com:8080"
    no_proxy: "localhost,.mycompany.com"

  npm_registry: "https://npm.mycompany.com"
```

Or pass via environment variable / CLI flag:

```bash
export PRISM_NPM_REGISTRY=https://npm.mycompany.com
prism install --prism my-company

# Or inline
prism install --prism my-company --npm-registry https://npm.mycompany.com
```

---

## Platform Notes

### macOS
- Homebrew is installed automatically if missing
- Apple Silicon (M1/M2/M3) fully supported
- Tools without explicit macOS install commands in the tool registry are skipped

### Windows
- Uses winget for package installation
- Run from PowerShell or Git Bash

### Linux / Ubuntu
- Uses `apt-get` for package installation
- WSL2 is fully supported

### No Generic Fallbacks

Tools without explicit platform install commands in the tool registry are skipped. Prism does not guess install commands.

---

## Next Steps

- [Quickstart](quickstart.md)
- [Choose a prism](choosing-a-prism.md)
- [Configuration schema](../reference/configuration-schema.md)
