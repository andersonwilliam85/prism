# 🚀 Quickstart

Get your development environment configured in minutes with Prism.

---

## Prerequisites

- Python 3.9+
- Git

```bash
# Install Python dependencies
pip3 install pyyaml flask rich
```

---

## Option A: Web UI (Recommended)

```bash
cd prism
python3 install-ui.py
# Opens at http://localhost:5555
```

The web UI walks you through:
1. **Choose a prism** — personal-dev, startup, acme-corp, fortune500, etc.
2. **Select sub-prisms** — pick your role, division, team, etc.
3. **Fill in your info** — name, email, platform-specific fields
4. **Install** — watch the live progress log

---

## Option B: CLI

```bash
# Basic install — prompts for name and email
python3 install.py

# Install a specific prism
python3 install.py --prism personal-dev

# Install with a custom npm registry (corporate environments)
python3 install.py --prism fortune500 --npm-registry https://npm.mycompany.com
```

---

## What Gets Installed

After installation you'll have:

```
~/workspace/
├── projects/          ← your code lives here
├── experiments/
├── learning/
├── archived/
├── docs/
│   └── config/        ← your prism configuration files
│       ├── merged-config.yaml   ← the merged result of all sub-prisms
│       └── user-info.yaml
└── tooling/
```

Plus:
- Git configured with your name and email
- SSH key generated (`~/.ssh/id_ed25519`)
- Tools from your prism installed (git, docker, kubectl, etc.)
- Repositories cloned (if declared in your prism)

---

## Your First Custom Prism

```bash
# Create a scaffold for your company
python3 scripts/package_manager.py create my-company --company "My Company"

# Customize the base configuration
vim prisms/my-company/base/my-company.yaml

# Validate it
python3 scripts/package_manager.py validate my-company

# Install it
python3 install.py --prism my-company
```

---

## Next Steps

- [Choose the right prism](../user-guide/choosing-a-prism.md)
- [Understand sub-prism inheritance](../user-guide/config-inheritance.md)
- [Create your own prism](../user-guide/creating-configurations.md)
- [Configuration schema reference](../reference/configuration-schema.md)
