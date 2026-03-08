# Prism Configuration Schema

Complete YAML schema reference for `package.yaml` — the manifest for every prism.

---

## Overview

Every prism lives in its own directory inside `prisms/` and must have a `package.yaml` file. The schema has five top-level sections:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eef2ff', 'primaryTextColor': '#1e293b', 'primaryBorderColor': '#6366f1', 'lineColor': '#6366f1', 'secondaryColor': '#f0fdf4', 'tertiaryColor': '#faf5ff', 'background': '#ffffff', 'mainBkg': '#eef2ff', 'nodeBorder': '#6366f1', 'clusterBkg': '#f8faff', 'edgeLabelBackground': '#ffffff'}}}%%

flowchart LR
    PY["package.yaml"]

    PY --> PKG["package\nIdentity\nname · version · type · support"]
    PY --> PC["prism_config\nTool settings\ntheme · proxy · registry · branding"]
    PY --> BP["bundled_prisms\nSub-prism tiers\nbase + optional layers"]
    PY --> SU["setup\nFile installation\nfiles · directories · post_install"]
    PY --> UIF["user_info_fields\nUser input\nname · email · role · team"]
    PY --> DI["distribution\nSource\nlocal · remote · discoverable"]
    PY --> ME["metadata\nDiscovery\ntags · keywords · org_size"]

    style PY fill:#fff7ed,stroke:#f97316,color:#1e293b,font-weight:bold
    style PKG fill:#eef2ff,stroke:#6366f1,color:#1e293b
    style PC fill:#eef2ff,stroke:#6366f1,color:#1e293b
    style BP fill:#f0fdf4,stroke:#22c55e,color:#1e293b
    style SU fill:#eef2ff,stroke:#6366f1,color:#1e293b
    style UIF fill:#faf5ff,stroke:#a855f7,color:#1e293b
    style DI fill:#eef2ff,stroke:#6366f1,color:#1e293b
    style ME fill:#eef2ff,stroke:#6366f1,color:#1e293b
```

```yaml
package:          # 🔷 Identity — name, version, type, support
prism_config:     # ⚙️  Prism tool settings — theme, proxy, registry, branding
bundled_prisms:   # Hierarchical sub-prisms — base + optional tiers
setup:            # 📁 File installation steps
user_info_fields: # 👤 Info collected from the user at install time
distribution:     # 📦 Where this prism is sourced from
metadata:         # 🏷️  Tags, keywords, company size
```

---

## `package` — Identity

### Required

```yaml
package:
  name: "my-company-prism"    # kebab-case identifier
  version: "1.0.0"            # semantic version
  description: "..."          # one-sentence description
```

### Optional

```yaml
package:
  type: "company"             # personal | company | consulting | enterprise | academic | opensource | core
  author: "IT Team"
  homepage: "https://dev.mycompany.com"

  support:
    email: "devops@mycompany.com"
    slack: "#dev-support"
    github: "https://github.com/org/repo/issues"

  requires:
    onboarding_version: ">=1.0.0"
    python_version: ">=3.8"
    network: "company-vpn"    # optional — warn user if not met
```

---

## `prism_config` — Prism Tool Settings

Controls how the Prism tool itself behaves. Applied before any sub-prism merging.

```yaml
prism_config:
  theme: "ocean"    # ocean | purple | forest | sunset | midnight

  sources:
    - url: "local"
      name: "Built-in Prisms"
      type: "local"
    - url: "https://prism-registry.mycompany.com"
      name: "Internal Registry"
      type: "remote"
      auth_required: true

  npm_registry: "https://npm.mycompany.com"   # empty = npmjs.org
  unpkg_url: "https://cdn.mycompany.com/npm"  # empty = unpkg.com

  proxies:
    http: "http://proxy.mycompany.com:8080"
    https: "http://proxy.mycompany.com:8080"
    no_proxy: "localhost,127.0.0.1,.mycompany.com"

  branding:
    name: "My Company Prism"
    tagline: "Empowering [Company] Development"
    logo_url: "https://mycompany.com/assets/logo.svg"
    primary_color: "#1e3a8a"    # hex color
    secondary_color: "#f59e0b"
```

---

## `bundled_prisms` — Hierarchical Sub-Prisms

The heart of the inheritance system. Each key is a **tier** — a category of selectable sub-prisms. Tiers are merged in declaration order.

```yaml
bundled_prisms:
  # Base tier — REQUIRED sub-prisms, always applied
  base:
    - id: "company-base"
      name: "Company Base"
      description: "Company-wide settings"
      required: true                  # ← marks this as auto-applied
      config: "base/company.yaml"     # path relative to prism directory

  # Example optional tier — user picks one
  divisions:
    - id: "technology"
      name: "Technology Division"
      description: "IT and software engineering"
      config: "divisions/technology.yaml"

    - id: "digital"
      name: "Digital Division"
      config: "divisions/digital.yaml"

  # Another optional tier
  roles:
    - id: "software-engineer"
      name: "Software Engineer"
      config: "roles/software-engineer.yaml"
      tools:                          # informational — shown in UI
        - docker
        - kubernetes

  # Optional multi-select tier
  business_units:
    - id: "retail"
      name: "Retail Division"
      config: "business_units/retail.yaml"
```

### Sub-prism config file structure

Each config file referenced by `bundled_prisms` is plain YAML. Any keys it contains are deep-merged into the final configuration:

```yaml
# base/company.yaml
environment:
  proxy:
    http: "http://proxy.mycompany.com:8080"
  vpn:
    required: true

git:
  user:
    name: "${USER}"
    email: "${USER}@mycompany.com"

tools_required:
  - git
  - docker
  - kubectl

security:
  sso_required: true
  mfa_required: true
```

```yaml
# roles/devops-engineer.yaml
role:
  id: "devops-engineer"
  name: "DevOps Engineer"

tools_required:
  - terraform
  - ansible
  - helm

repositories:
  - name: "infrastructure"
    url: "https://github.mycompany.com/platform/infrastructure"
```

---

## `setup` — File Installation

Controls which files are copied from the prism directory to `config/` when the prism is installed.

```yaml
setup:
  install:
    target_dir: "config/"

    files:
      - source: "welcome.yaml"
        dest: "config/welcome.yaml"
        description: "Welcome message"

      - source: "resources.yaml"
        dest: "config/resources.yaml"

    directories:
      - source: "base/"
        dest: "config/base/"
      - source: "roles/"
        dest: "config/roles/"

  post_install:
    message: |
      💎 Prism installed!
      Next steps: ...
```

---

## `user_info_fields` — User Input

Defines what information to collect from the user during installation.

### Text input

```yaml
user_info_fields:
  - id: "name"
    label: "Full Name"
    type: "text"
    required: true
    placeholder: "Jane Developer"
    description: "Used for git commits"
```

### Email input

```yaml
  - id: "email"
    label: "Company Email"
    type: "email"
    required: true
    placeholder: "jane@mycompany.com"
    validation:
      pattern: ".*@mycompany\\.com$"
      message: "Must be a @mycompany.com email"
```

### Select dropdown

```yaml
  - id: "role"
    label: "Role"
    type: "select"
    required: true
    options:
      - "Software Engineer"
      - "DevOps Engineer"
      - "Data Engineer"
```

### URL input

```yaml
  - id: "portfolio_url"
    label: "Portfolio URL"
    type: "url"
    required: false
    placeholder: "https://janedev.com"
```

### Number input

```yaml
  - id: "employee_id"
    label: "Employee ID"
    type: "number"
    required: true
    min: 100000
    max: 999999
```

### Checkbox

```yaml
  - id: "agree_to_terms"
    label: "I agree to the terms"
    type: "checkbox"
    required: true
```

---

## `distribution` — Where the Prism Lives

```yaml
distribution:
  local:
    path: "prisms/my-company/"
    discoverable: true    # false = hidden from list

  git:
    url: "https://github.com/mycompany/prism-config"
    branch: "main"

  internal:
    url: "https://prism-registry.mycompany.com/my-company"
    auth_required: true
```

---

## `metadata` — Tags and Search

```yaml
metadata:
  tags:
    - company
    - template
    - enterprise

  keywords:
    - my-company
    - onboarding

  company_size: "medium"    # personal | small | medium | large | enterprise | academic | community

  regions: ["Global", "US", "EU"]

  security:
    classification: "internal-use-only"
    compliance:
      - sox
      - gdpr
      - hipaa

  last_updated: "2026-03-05"
  maintainers:
    - "DevOps Team"
```

---

## Minimal Complete Example

```yaml
package:
  name: "my-company-prism"
  version: "1.0.0"
  description: "My Company developer environment"
  type: "company"

prism_config:
  theme: "midnight"
  branding:
    name: "My Company Prism"
    primary_color: "#1e3a8a"

bundled_prisms:
  base:
    - id: "base"
      name: "My Company Base"
      required: true
      config: "base/my-company.yaml"

  teams:
    - id: "platform"
      name: "Platform Team"
      config: "teams/platform.yaml"

setup:
  install:
    target_dir: "config/"
    files:
      - source: "welcome.yaml"
        dest: "config/welcome.yaml"
    directories:
      - source: "base/"
        dest: "config/base/"

user_info_fields:
  - id: "name"
    label: "Full Name"
    type: "text"
    required: true
  - id: "email"
    label: "Email"
    type: "email"
    required: true

distribution:
  local:
    path: "prisms/my-company/"
    discoverable: true

metadata:
  tags: ["company", "template"]
  company_size: "medium"
  last_updated: "2026-03-05"
```

---

## Validation

```bash
# Validate a single prism
python3 scripts/package_validator.py prisms/my-company

# Validate all prisms
python3 scripts/package_validator.py

# Using package manager
python3 scripts/package_manager.py validate my-company
```

### Common Errors

**`Missing required field: package.name`**
```yaml
# Fix: add package.name
package:
  name: "my-prism"
```

**`Sub-prism config not found: roles/engineer.yaml`**
```bash
# Fix: create the referenced file
touch prisms/my-company/roles/engineer.yaml
```

**`Unknown theme 'blue'`**
```yaml
# Fix: use a supported theme
prism_config:
  theme: "ocean"   # ocean | purple | forest | sunset | midnight
```

---

## Resources

- [Sub-Prism Inheritance](../user-guide/config-inheritance.md)
- [Choosing a Prism](../user-guide/choosing-a-prism.md)
- [Creating Prisms](../user-guide/creating-configurations.md)
