---
layout: default
title: Home
---

# Prism Documentation

Complete documentation for Prism — the modular, hierarchical development environment installer. See [About Prism](about.md) for an overview.

---

## Documentation Structure

```
docs/
├── index.md                              # This page
├── getting-started/
│   ├── installation.md                   # Install Prism
│   ├── quickstart.md                     # Up and running in minutes
│   └── choosing-a-prism.md              # Pick the right prism
├── user-guide/
│   ├── creating-configurations.md        # Author your own prism
│   ├── config-inheritance.md             # Sub-prism merging deep dive
│   ├── custom-registries.md              # Private registries
│   ├── settings-panel.md                 # Web UI settings drawer
│   ├── local-docs-server.md              # Local workspace discovery server
│   ├── themes.md                         # Theme system and customization
│   └── cascading-dropdowns.md            # Cascading field dependencies
├── reference/
│   ├── architecture.md                   # VBD-inspired layered architecture
│   ├── configuration-schema.md           # Full package.yaml schema
│   ├── package-system.md                 # Prism system internals
│   ├── npm-packages.md                   # NPM distribution
│   ├── merge-strategies.md               # tools merge rules
│   ├── bad-config-examples.md            # Common validation errors and fixes
│   ├── rollback-system.md                # Installation rollback
│   └── privilege-separation.md           # Sudo / privilege separation
└── contributor-guide/
    ├── contributing.md
    ├── testing.md
    ├── ci-cd.md
    └── publishing-prisms.md              # Publishing prisms to npm
```

---

## Quick Start

**New user?** Start here:

1. [Installation](getting-started/installation.md) — Install dependencies, clone the repo
2. [Quickstart](getting-started/quickstart.md) — Up and running in minutes
3. [Choosing a Prism](getting-started/choosing-a-prism.md) — Find the right prism for your organization

---

## Getting Started

### [Choosing a Prism](getting-started/choosing-a-prism.md)

Complete catalog of pre-built prisms:

- **Personal Dev** — Solo developers
- **Startup** — Fast-moving teams (10–50)
- **ACME Corp** — Small companies (100–1K)
- **Consulting Firm** — Multi-client setups
- **Fortune 500** — Enterprise (50K+)
- **University** — Academic institutions
- **Open Source** — Community projects

**Includes:** Decision tree, comparison matrix, installation commands

### [Creating Configurations](user-guide/creating-configurations.md)

Step-by-step guide to authoring a custom prism:

- Prism structure — `package.yaml`, sub-prism tiers, YAML config files
- `prism_config` — themes, proxies, registries, branding
- `bundled_prisms` — defining base and optional tiers
- Writing sub-prism YAML files
- Validation and testing

**Perfect for:** IT teams creating company-specific prisms

### [Sub-Prism Inheritance](user-guide/config-inheritance.md)

Deep dive into hierarchical configuration merging:

- How sub-prisms merge (base → division → role → team)
- Merge strategies: union, deep_merge, override, append
- Conflict resolution
- Examples and visualizations

**Perfect for:** Understanding multi-level configuration

### [Custom Registries](user-guide/custom-registries.md)

Setting up private NPM registries:

- Corporate package registries
- Authentication and security
- Hosting your own registry
- Integration with Prism

**Perfect for:** Enterprise and air-gapped deployments

---

## User Guide

### [Themes](user-guide/themes.md)

Customize the installer UI appearance:

- 5 built-in themes (Ocean, Purple, Forest, Sunset, Midnight)
- Custom theme definitions with 5 gradient color slots
- Persistence via localStorage
- Configuration through `prism_config` or the settings panel

### [Cascading Dropdowns](user-guide/cascading-dropdowns.md)

Dynamic field dependencies in the installer UI:

- Parent-child field relationships via `depends_on`
- Filtered option lists via `option_map`
- Topological dependency resolution
- Example: division → team cascading

### [Settings Panel](user-guide/settings-panel.md)

Web UI settings drawer for registry, CDN, and language overrides.

### [Local Docs Server](user-guide/local-docs-server.md)

Post-install documentation server for browsing your workspace configuration.

---

## Reference Documentation

### [Architecture](reference/architecture.md)

VBD-inspired layered architecture:

- Managers (the "what"), Engines (the "how"), Accessors (the "where")
- Dependency injection via `container.py`
- Complete component inventory

**Perfect for:** Contributors and anyone extending Prism

### [Configuration Schema](reference/configuration-schema.md)

Complete `package.yaml` schema reference:

- `package` — identity fields
- `prism_config` — tool settings (theme, proxy, registry, branding)
- `bundled_prisms` — hierarchical sub-prism tiers
- `setup` — file installation steps
- `user_info_fields` — user input types (text, email, select, number, checkbox)
- `distribution` — where the prism lives
- `metadata` — tags, keywords, company size

**Perfect for:** Writing and validating prisms

### [Prism System](reference/package-system.md)

Technical deep-dive into the prism system:

- Prism structure and format
- Metadata and manifests
- Discovery, loading, and validation
- Sub-prism merge algorithms
- CLI reference

**Perfect for:** Advanced customization and troubleshooting

### [NPM Packages](reference/npm-packages.md)

Distributing prisms via NPM:

- package.json requirements
- Publishing workflow
- Versioning strategy
- Private registries
- Installation from NPM

**Perfect for:** Distributing prisms to teams

### [Rollback System](reference/rollback-system.md)

Installation rollback and crash recovery:

- Action tracking (files, directories, commands, packages, config changes)
- LIFO undo sequences
- State persistence to JSON temp files
- Auto-rollback vs explicit rollback

**Perfect for:** Understanding installation safety guarantees

### [Privilege Separation](reference/privilege-separation.md)

Sudo session management and two-phase install:

- Normal operations first, then privileged operations
- Crypto token sessions with TTL and lockout
- Password never in args or logs

**Perfect for:** Understanding Prism's security model

---

## Contributor Guide

### [Contributing](contributor-guide/contributing.md)

How to contribute to Prism:

- Development setup
- Code style and standards
- Commit conventions
- PR workflow and code review

### [Testing](contributor-guide/testing.md)

Comprehensive testing guide:

- Test types (unit, CLI, E2E, integration)
- Running tests (Makefile commands)
- Writing tests — templates and best practices
- Coverage reports and CI integration

### [CI/CD Pipeline](contributor-guide/ci-cd.md)

Complete CI/CD automation:

- GitHub Actions workflows
- Branch protection rules
- Development workflow (dev → stage → main)
- Release process and Makefile commands

### [Publishing Prisms](contributor-guide/publishing-prisms.md)

End-to-end guide to publishing a prism package to npm:

- Preparing `package.json` for npm
- Dry-run and publish workflow
- Versioning strategy
- Private registry publishing

---

## Common Tasks

### I want to...

**Choose a prism for my team**
→ [Choosing a Prism](getting-started/choosing-a-prism.md)

**Create a custom prism**
→ [Creating Configurations](user-guide/creating-configurations.md)

**Understand how sub-prisms merge**
→ [Sub-Prism Inheritance](user-guide/config-inheritance.md)

**Validate my package.yaml**
→ [Configuration Schema](reference/configuration-schema.md)

**Set up a private registry**
→ [Custom Registries](user-guide/custom-registries.md)

**Customize the UI theme**
→ [Themes](user-guide/themes.md)

**Set up cascading dropdowns**
→ [Cascading Dropdowns](user-guide/cascading-dropdowns.md)

**Understand the architecture**
→ [Architecture](reference/architecture.md)

**Publish to NPM**
→ [NPM Packages](reference/npm-packages.md)

**Set up CI/CD**
→ [CI/CD Pipeline](contributor-guide/ci-cd.md)

**Run tests**
→ [Testing](contributor-guide/testing.md)

---

## Feature Highlights

### Prism System

Every prism is self-contained: identity, tool settings, and a hierarchy of composable sub-prisms.

```
my-company.prism
 └── bundled_prisms
      ├── base         → required, applies to everyone
      ├── divisions    → user picks one
      └── roles        → user picks one
```

[Learn more](reference/package-system.md)

### Sub-Prism Inheritance

Settings flow down through tiers. Later layers extend earlier ones — tools merge by union, environment settings deep-merge, git config overrides.

[Learn more](user-guide/config-inheritance.md)

### 7 Pre-Built Prisms

From solo developers to Fortune 500 enterprises.
[See all prisms](getting-started/choosing-a-prism.md)

### Beautiful Web UI

5 themes, real-time progress, responsive design.
[Customize themes](user-guide/themes.md)

### Cascading Dropdowns

Dynamic field dependencies — selecting a division filters available teams automatically.
[Learn more](user-guide/cascading-dropdowns.md)

### Installation Rollback

Every action is tracked. If something fails, Prism unwinds changes in LIFO order.
[Learn more](reference/rollback-system.md)

### Privilege Separation

Normal operations run first, then privileged steps require explicit sudo approval.
[Learn more](reference/privilege-separation.md)

### VBD Architecture

Clean layered design: Managers (the "what"), Engines (the "how"), Accessors (the "where").
[Learn more](reference/architecture.md)

### Comprehensive Testing

Unit + CLI + E2E tests, coverage reports, Playwright traces.
[Learn more](contributor-guide/testing.md)

### Full CI/CD

GitHub Actions workflows, 3 environments, automated releases.
[Learn more](contributor-guide/ci-cd.md)

---

## Learning Path

### Beginner

1. [Main README](https://github.com/andersonwilliam85/prism#readme) — What is Prism?
2. [Quickstart](getting-started/quickstart.md) — Install in minutes
3. [Choosing a Prism](getting-started/choosing-a-prism.md) — Pick your prism

### Intermediate

1. [Creating Configurations](user-guide/creating-configurations.md) — Author a custom prism
2. [Sub-Prism Inheritance](user-guide/config-inheritance.md) — Advanced merging
3. [Configuration Schema](reference/configuration-schema.md) — Full schema reference

### Advanced

1. [Architecture](reference/architecture.md) — System design
2. [Prism System](reference/package-system.md) — System internals
3. [NPM Packages](reference/npm-packages.md) — Distribution
4. [Contributing](contributor-guide/contributing.md) — Join development

---

## Next Steps

```bash
# Clone and install
git clone https://github.com/andersonwilliam85/prism.git
cd prism
pip3 install pyyaml flask rich

# Launch Web UI
python3 install-ui.py
# Opens at http://localhost:5555

# Or use the CLI
python3 install.py --prism prism
```

---

**Prism — Refract complexity into clarity**
