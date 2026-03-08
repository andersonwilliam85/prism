# Creating Prisms

Step-by-step guide to authoring a custom prism for your organization.

---

## Overview

A **prism** is a self-contained directory that defines how a development environment is configured. It has:

- **`package.yaml`** — the manifest: identity, prism tool settings, sub-prism hierarchy, setup, user fields
- **Sub-prism YAML files** — plain YAML files contributing settings that are deep-merged at install time
- **Optional support files** — `README.md`, `welcome.yaml`, `resources.yaml`

The key idea: a prism doesn't have one monolithic config. It has a **hierarchy of sub-prisms** (tiers) that the user selects from. The engine merges all selected sub-prisms into a final `merged-config.yaml` that drives tool installation, repo cloning, and git configuration.

---

## Prism Directory Structure

### Minimal prism

```
prisms/my-company/
├── package.yaml          # REQUIRED
├── README.md
└── base/
    └── my-company.yaml   # referenced by bundled_prisms.base
```

### Full hierarchical prism

```
prisms/my-company/
├── package.yaml
├── README.md
├── welcome.yaml
├── resources.yaml
├── base/
│   └── my-company.yaml         # Company-wide settings (required)
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

## `package.yaml` — The Manifest

The manifest has seven top-level sections:

```yaml
package:          # Identity
prism_config:     # Prism tool settings
bundled_prisms:   # Hierarchical sub-prism tiers
setup:            # File installation steps
user_info_fields: # User input collected at install time
distribution:     # Where this prism is sourced from
metadata:         # Tags, keywords, company size
```

### `package` — Identity

```yaml
package:
  name: "my-company-prism"    # kebab-case identifier
  version: "1.0.0"            # semantic version
  description: "My Company developer environment"
  type: "company"             # personal | company | consulting | enterprise | academic | opensource

  author: "IT Team"
  homepage: "https://dev.mycompany.com"

  support:
    email: "devops@mycompany.com"
    slack: "#dev-support"
    github: "https://github.com/mycompany/prism/issues"
```

### `prism_config` — Tool Settings

Controls how the Prism installer behaves. Applied before any sub-prism merging.

```yaml
prism_config:
  theme: "midnight"   # ocean | purple | forest | sunset | midnight

  npm_registry: "https://npm.mycompany.com"   # leave empty for npmjs.org
  unpkg_url: "https://cdn.mycompany.com/npm"  # leave empty for unpkg.com

  proxies:
    http: "http://proxy.mycompany.com:8080"
    https: "http://proxy.mycompany.com:8080"
    no_proxy: "localhost,127.0.0.1,.mycompany.com"

  branding:
    name: "My Company Prism"
    tagline: "Empowering My Company Development"
    logo_url: "https://mycompany.com/assets/logo.svg"
    primary_color: "#1e3a8a"
    secondary_color: "#f59e0b"
```

### `bundled_prisms` — Sub-Prism Hierarchy

This is the heart of the system. Each key is a **tier** — a category of selectable configurations. Tiers are merged in declaration order.

```yaml
bundled_prisms:
  # Base tier — always applied (required: true)
  base:
    - id: "company-base"
      name: "Company Base"
      description: "Company-wide settings: proxy, git, required tools"
      required: true
      config: "base/my-company.yaml"   # path relative to prism directory

  # Optional tier — user picks one
  divisions:
    - id: "technology"
      name: "Technology Division"
      description: "IT and software engineering"
      config: "divisions/technology.yaml"

    - id: "digital"
      name: "Digital Division"
      config: "divisions/digital.yaml"

  # Optional tier — user picks one
  roles:
    - id: "software-engineer"
      name: "Software Engineer"
      config: "roles/software-engineer.yaml"
      tools:             # informational — shown in web UI
        - docker
        - kubernetes

    - id: "devops-engineer"
      name: "DevOps Engineer"
      config: "roles/devops-engineer.yaml"
      tools:
        - terraform
        - ansible
        - helm
```

**Rules:**
- Sub-prisms with `required: true` are always merged, regardless of user selection
- Optional tiers present the user with a choice (one per tier by default)
- Tiers are merged in declaration order — later tiers can extend or override earlier ones

### `setup` — File Installation

Controls which files are copied to `config/` when the prism is installed.

```yaml
setup:
  install:
    target_dir: "config/"
    files:
      - source: "welcome.yaml"
        dest: "config/welcome.yaml"
      - source: "resources.yaml"
        dest: "config/resources.yaml"
    directories:
      - source: "base/"
        dest: "config/base/"
      - source: "roles/"
        dest: "config/roles/"
  post_install:
    message: |
      💎 My Company Prism installed!
      Next: connect to VPN and open Slack.
```

### `user_info_fields` — User Input

Defines what information to collect from the user at install time.

```yaml
user_info_fields:
  - id: "name"
    label: "Full Name"
    type: "text"
    required: true
    placeholder: "Jane Developer"
    description: "Used for git commits"

  - id: "email"
    label: "Company Email"
    type: "email"
    required: true
    placeholder: "jane@mycompany.com"
    validation:
      pattern: ".*@mycompany\\.com$"
      message: "Must be a @mycompany.com email"

  - id: "employee_id"
    label: "Employee ID"
    type: "number"
    required: true
    min: 100000
    max: 999999

  - id: "agree_to_terms"
    label: "I agree to the terms of service"
    type: "checkbox"
    required: true
```

Field types: `text`, `email`, `url`, `select`, `number`, `checkbox`

### `distribution` — Where the Prism Lives

```yaml
distribution:
  local:
    path: "prisms/my-company/"
    discoverable: true    # false = hidden from list

  git:
    url: "https://github.com/mycompany/prism-config"
    branch: "main"
```

### `metadata` — Tags and Search

```yaml
metadata:
  tags: [company, template]
  keywords: [my-company, onboarding]
  company_size: "medium"   # personal | small | medium | large | enterprise | academic | community
  regions: ["Global"]
  last_updated: "2026-03-05"
  maintainers: ["IT Team"]
```

---

## Writing Sub-Prism Config Files

Each file referenced by `bundled_prisms[tier][n].config` is plain YAML. Any keys it contains are deep-merged into the final configuration.

### Base sub-prism — `base/my-company.yaml`

Define company-wide defaults here. Everyone gets this.

```yaml
company:
  name: "My Company"
  domain: "mycompany.com"

environment:
  proxy:
    http: "http://proxy.mycompany.com:8080"
    https: "http://proxy.mycompany.com:8080"
    no_proxy: "localhost,.mycompany.com"
  vpn:
    required: true

git:
  user:
    name: "${USER}"
    email: "${USER}@mycompany.com"
  default_branch: "main"

tools_required:
  - git
  - docker
  - kubectl

security:
  sso_required: true
  mfa_required: true
```

### Division sub-prism — `divisions/technology.yaml`

Add division-specific tools and settings.

```yaml
division:
  id: "technology"
  name: "Technology Division"

tools_required:
  - vscode
  - kubernetes

tech_stack:
  languages: [Python, TypeScript, Java]
  platforms: [Kubernetes, AWS, GCP]
```

### Role sub-prism — `roles/devops-engineer.yaml`

Add role-specific tools and repositories.

```yaml
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
    path: "~/workspace/projects/infrastructure"
```

### Merge result

When a user selects the Technology division + DevOps Engineer role, the engine merges all three layers. Arrays (like `tools_required`) use **union** — duplicates removed, all unique values combined:

```yaml
tools_required:
  - git        # from base
  - docker     # from base
  - kubectl    # from base + division
  - vscode     # from division
  - terraform  # from role
  - ansible    # from role
  - helm       # from role
```

Environment and other nested objects use **deep_merge** — keys from later layers extend earlier layers without replacing them.

---

## Step-by-Step: Create Your First Prism

### Option A: Scaffold generator (fastest)

```bash
python3 scripts/package_manager.py create my-company --company "My Company Inc"
```

Creates the full directory structure with placeholder content. Then customize each file.

### Option B: Copy a template

```bash
# Small/medium company starting point
cp -r prisms/acme-corp prisms/my-company

# Enterprise starting point
cp -r prisms/fortune500.prism prisms/my-enterprise
```

### Option C: From scratch

**Step 1 — Create the directory**

```bash
mkdir -p prisms/my-company/base
```

**Step 2 — Write `package.yaml`**

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
      description: "Company-wide defaults"
      required: true
      config: "base/my-company.yaml"

  teams:
    - id: "platform"
      name: "Platform Team"
      config: "teams/platform.yaml"
    - id: "mobile"
      name: "Mobile Team"
      config: "teams/mobile.yaml"

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
    label: "Company Email"
    type: "email"
    required: true
    validation:
      pattern: ".*@mycompany\\.com$"
      message: "Must be a @mycompany.com address"

distribution:
  local:
    path: "prisms/my-company/"
    discoverable: true

metadata:
  tags: [company, template]
  company_size: "medium"
  last_updated: "2026-03-05"
```

**Step 3 — Write base config**

```bash
vim prisms/my-company/base/my-company.yaml
```

**Step 4 — Write team configs**

```bash
mkdir prisms/my-company/teams
vim prisms/my-company/teams/platform.yaml
vim prisms/my-company/teams/mobile.yaml
```

**Step 5 — Validate**

```bash
python3 scripts/package_manager.py validate my-company
```

Expected output:
```
✅ package.yaml valid
✅ Required fields present
✅ All bundled_prism config files found
✅ user_info_fields types valid
✅ Theme valid
```

**Step 6 — Dry-run install**

```bash
python3 scripts/package_manager.py install my-company --dry-run
```

**Step 7 — Full install**

```bash
python3 install.py --prism my-company
# Or via Web UI:
python3 install-ui.py
```

---

## Environment Variable Substitution

Use `${VAR}` and `${VAR:-default}` in sub-prism YAML:

```yaml
git:
  user:
    name: "${USER}"
    email: "${USER}@mycompany.com"

cloud:
  region: "${CLOUD_REGION:-us-central1}"
```

These are resolved at install time by the engine.

---

## Adding Resources and Welcome Content

### `welcome.yaml`

Displayed after install and in the web UI welcome screen.

```yaml
welcome:
  title: "Welcome to My Company!"
  message: |
    Your development environment is ready.

    Next steps:
    - Connect to VPN
    - Open Slack: https://mycompany.slack.com
    - Read the dev handbook: https://dev.mycompany.com
```

### `resources.yaml`

Links shown in the web UI resources panel.

```yaml
resources:
  documentation:
    - name: "Developer Portal"
      url: "https://dev.mycompany.com"
    - name: "API Docs"
      url: "https://api.mycompany.com/docs"

  communication:
    - name: "Slack"
      url: "https://mycompany.slack.com"

  tools:
    - name: "Jira"
      url: "https://mycompany.atlassian.net"
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

### 3. DRY — don't repeat configuration

Define common settings in `base`, extend in divisions and roles. Never copy the same tool list across multiple sub-prism files.

### 4. Security

Never include in prisms:
- API keys or secrets
- Personal SSH keys
- Private internal URLs (in public repos)

Use environment variable placeholders instead:
```yaml
git:
  user:
    email: "${USER}@mycompany.com"
```

### 5. Documentation

Always include:
- `README.md` — what's included, how to customize
- Comments in sub-prism YAML files explaining non-obvious settings

---

## Troubleshooting

**`Missing required field: package.name`**

Add `package.name` to your `package.yaml`.

**`Sub-prism config not found: roles/engineer.yaml`**

Create the referenced file, or fix the path in `bundled_prisms`.

**`Unknown theme 'blue'`**

Use a supported theme: `ocean`, `purple`, `forest`, `sunset`, `midnight`.

**Merge produces unexpected results**

Run the validator and check merge order — later tiers override earlier ones for scalar values, union-merge arrays, and deep-merge nested objects. See [Sub-Prism Inheritance](config-inheritance.md).

---

## Next Steps

- [Sub-Prism Inheritance](config-inheritance.md) — how merging works in detail
- [Configuration Schema](../reference/configuration-schema.md) — full `package.yaml` schema
- [Prism System](../reference/package-system.md) — CLI reference and internals
- [Custom Registries](custom-registries.md) — private/air-gapped deployments
