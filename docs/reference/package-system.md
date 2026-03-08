# Prism System

**Modular, distributable, version-controlled development environment configurations.**

---

## Overview

The Prism system lets organizations create, distribute, and install complete development environment configurations as self-contained **prisms**. Like a prism refracts white light into a spectrum, Prism refracts organizational complexity into clear, composable configuration layers.

### Key Benefits

✅ **Hierarchical** — base → division → role → team, each layer inheriting the last
✅ **Modular** — install only the sub-prisms you need
✅ **Distributable** — share via git, registry, or local files
✅ **Version-controlled** — track changes over time
✅ **Discoverable** — auto-finds prisms in `prisms/`
✅ **Validatable** — check structure before installing

---

## Quick Start

### List Available Prisms

```bash
python3 scripts/package_manager.py list
```

```
💎 Available Prisms

  💎 acme-corp-prism (v1.0.0) 🌈
     ACME Corp prism — example template for small-to-medium companies
     Type: company | Size: medium | Theme: midnight
     Sub-prism tiers: base (1), orgs (1), teams (1)

  💎 fortune500-prism (v1.0.0) 🌈
     Fortune 500 enterprise prism — secure, compliant, multi-tier
     Type: enterprise | Size: enterprise | Theme: midnight
     Sub-prism tiers: base (1), divisions (3), roles (5), business_units (3)

  🌈 = has hierarchical sub-prisms
```

### Get Prism Info

```bash
python3 scripts/package_manager.py info acme-corp
```

### Install a Prism

```bash
# Via CLI
python3 install.py --prism acme-corp

# Via Web UI
make run
```

### Validate a Prism

```bash
python3 scripts/package_manager.py validate my-company
```

---

## Prism Structure

### Minimal Prism

```
my-company/
├── package.yaml          # REQUIRED — identity, prism_config, bundled_prisms
├── README.md             # Recommended
├── welcome.yaml          # Optional — welcome page content
├── resources.yaml        # Optional — links and resources
└── base/
    └── my-company.yaml   # Referenced by bundled_prisms.base
```

### Full Hierarchical Prism

```
my-company/
├── package.yaml
├── README.md
├── welcome.yaml
├── resources.yaml
├── base/
│   └── my-company.yaml         # Company-wide settings
├── divisions/
│   ├── technology.yaml
│   ├── digital.yaml
│   └── data-analytics.yaml
├── roles/
│   ├── software-engineer.yaml
│   ├── devops-engineer.yaml
│   └── data-engineer.yaml
└── teams/
    ├── platform-team.yaml
    └── mobile-team.yaml
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

## Creating Your Own Prism

### Option 1: Scaffold Generator

```bash
python3 scripts/package_manager.py create my-company --company "My Company"
```

Creates:
```
prisms/my-company/
├── package.yaml
├── README.md
├── welcome.yaml
├── resources.yaml
├── base/
│   └── my-company.yaml
└── teams/
    └── (empty — add your teams)
```

### Option 2: Copy a Template

```bash
# Small/medium company starting point
cp -r prisms/acme-corp prisms/my-company

# Enterprise starting point
cp -r prisms/fortune500.prism prisms/my-company.prism
```

### Option 3: From Scratch

See [Creating Prisms](../user-guide/creating-configurations.md).

---

## CLI Reference

### `list`
```bash
python3 scripts/package_manager.py list
```
Lists all discoverable prisms in `prisms/`.

### `info`
```bash
python3 scripts/package_manager.py info <prism-name>
```
Shows full prism details — version, type, sub-prism tiers, metadata.

### `install`
```bash
python3 scripts/package_manager.py install <prism-name>

# Dry run — show what would be installed without doing it
python3 scripts/package_manager.py install <prism-name> --dry-run

# From a custom path
python3 scripts/package_manager.py install <prism-name> --source /path/to/prism
```

### `validate`
```bash
python3 scripts/package_manager.py validate <prism-name>
```
Checks:
- ✅ `package.yaml` exists and is valid YAML
- ✅ Required fields present
- ✅ `bundled_prisms` config files exist on disk
- ✅ `user_info_fields` have valid types
- ✅ `prism_config.theme` is a valid theme name

### `search`
```bash
python3 scripts/package_manager.py search enterprise
```

### `create`
```bash
python3 scripts/package_manager.py create my-company --company "My Company Inc"
```

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

⚠️ **Never include in prisms:**
- API keys or secrets
- Personal SSH keys
- Private internal URLs (in public repos)

✅ **Use environment variable placeholders:**
```yaml
git:
  user:
    email: "${USER}@mycompany.com"
```

### 4. Testing

```bash
# Validate structure
python3 scripts/package_manager.py validate my-company

# Dry-run install
python3 scripts/package_manager.py install my-company --dry-run

# Full install in clean environment
rm -rf config/
python3 install.py --prism my-company
```

### 5. Documentation

Always include:
- ✅ `README.md` — what's included, how to customize
- ✅ Comments in YAML sub-prism files

---

## Use Cases

### Company-wide rollout

```bash
# Create once
python3 scripts/package_manager.py create acmecorp --company "ACME Corp"
# ... customize ...

# Every new hire runs:
python3 install.py --prism acmecorp
# or opens the web UI: make run
```

### Multiple engineering teams

```
my-company/
├── base/my-company.yaml     # Company-wide
└── teams/
    ├── mobile.yaml          # Swift, Kotlin
    ├── web.yaml             # React, TypeScript
    ├── ml.yaml              # Python, TensorFlow
    └── platform.yaml        # Go, Kubernetes
```

New hire selects their team in the installer.

### Multi-region enterprise

```
my-company/
├── base/my-company.yaml
└── divisions/
    ├── us.yaml              # US cloud accounts
    ├── eu.yaml              # EU accounts, GDPR tooling
    └── apac.yaml            # APAC accounts
```

---

## Support

1. Check prism README: `prisms/<name>/README.md`
2. Validate: `python3 scripts/package_manager.py validate <name>`
3. [Open an issue](https://github.com/andersonwilliam85/prism/issues)

---

**💎 Prism — Refract complexity into clarity**
