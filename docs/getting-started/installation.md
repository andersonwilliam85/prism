# Installation

## Requirements

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.9+ | Required |
| Git | Any | Required |
| Flask | Latest | Web UI only |
| Rich | Latest | Better CLI output (optional) |

---

## Install Dependencies

```bash
# Minimal (CLI only)
pip3 install pyyaml

# Full (Web UI + better CLI)
pip3 install pyyaml flask rich

# Or using requirements file
pip3 install -r requirements.txt
```

---

## Clone the Repository

```bash
git clone https://github.com/andersonwilliam85/prism.git
cd prism
```

---

## Start the Web UI

```bash
python3 install-ui.py
# Opens at http://localhost:5555
```

Or via Makefile:

```bash
make install-dev  # installs dependencies
make run          # starts web UI
```

---

## CLI Usage

```bash
# Show help
python3 install.py --help

# Install with a specific prism
python3 install.py --prism personal-dev

# Use a custom npm registry
python3 install.py --prism fortune500 --npm-registry https://npm.mycompany.com

# Check installation status
python3 install.py --status
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
python3 install.py --prism my-company

# Or inline
python3 install.py --prism my-company --npm-registry https://npm.mycompany.com
```

---

## Platform Notes

### macOS
- Homebrew is installed automatically if missing
- Apple Silicon (M1/M2/M3) fully supported

### Windows
- Chocolatey is installed automatically if missing
- Run from PowerShell or Git Bash

### Linux / Ubuntu
- Uses `apt-get` for package installation
- WSL2 is fully supported

---

## Next Steps

- [Quickstart](quickstart.md)
- [Choose a prism](../user-guide/choosing-a-prism.md)
- [Configuration schema](../reference/configuration-schema.md)
