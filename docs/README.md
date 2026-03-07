# 💎 Prism Documentation

Complete documentation for Prism — the modular, hierarchical development environment installer.

---

## 📚 Documentation Structure

```
docs/
├── README.md                         # 👈 You are here!
├── getting-started/
│   ├── installation.md               # Install Prism
│   ├── quickstart.md                 # Up and running in minutes
│   └── choosing-a-prism.md           # Pick the right prism
├── user-guide/                       # Usage guides
│   ├── creating-configurations.md    # Author your own prism
│   ├── config-inheritance.md         # Sub-prism merging deep dive
│   ├── custom-registries.md          # Private registries
│   ├── settings-panel.md             # Web UI settings drawer
│   └── local-docs-server.md          # Local workspace discovery server
├── reference/                        # Technical specs
│   ├── configuration-schema.md       # Full package.yaml schema
│   ├── package-system.md             # Prism system internals
│   ├── npm-packages.md               # NPM distribution
│   ├── merge-strategies.md           # tools_required/selected/excluded + merge rules
│   └── bad-config-examples.md        # Common validation errors and fixes
└── contributor-guide/                # Contributing & CI/CD
    ├── contributing.md
    ├── testing.md
    ├── ci-cd.md
    └── publishing-prisms.md          # Publishing prisms to npm
```

---

## 🚀 Quick Start

**New user?** Start here:

1. [Installation](getting-started/installation.md) — Install dependencies, clone the repo
2. [Quickstart](getting-started/quickstart.md) — Up and running in minutes
3. [Choosing a Prism](getting-started/choosing-a-prism.md) — Find the right prism for your organization

---

## 📖 Getting Started

### [Choosing a Prism](getting-started/choosing-a-prism.md)

Complete catalog of pre-built prisms:

- 🏠 **Personal Dev** — Solo developers
- 🚀 **Startup** — Fast-moving teams (10–50)
- 🏢 **ACME Corp** — Small companies (100–1K)
- 🎯 **Consulting Firm** — Multi-client setups
- 🌐 **Fortune 500** — Enterprise (50K+)
- 🎓 **University** — Academic institutions
- 🌟 **Open Source** — Community projects

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

## 📚 Reference Documentation

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

---

## 💻 Contributor Guide

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

## 🎯 Common Tasks

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

**Publish to NPM**
→ [NPM Packages](reference/npm-packages.md)

**Set up CI/CD**
→ [CI/CD Pipeline](contributor-guide/ci-cd.md)

**Run tests**
→ [Testing](contributor-guide/testing.md)

---

## 🌟 Feature Highlights

### 💎 Prism System

Every prism is self-contained: identity, tool settings, and a hierarchy of composable sub-prisms.

```
💎 my-company.prism
 └── bundled_prisms
      ├── base         → required, applies to everyone
      ├── divisions    → user picks one
      └── roles        → user picks one
```

[Learn more](reference/package-system.md)

### 🌈 Sub-Prism Inheritance

Settings flow down through tiers. Later layers extend earlier ones — tools merge by union, environment settings deep-merge, git config overrides.

[Learn more](user-guide/config-inheritance.md)

### 7 Pre-Built Prisms

From solo developers to Fortune 500 enterprises.
[See all prisms](getting-started/choosing-a-prism.md)

### Beautiful Web UI

5 themes, real-time progress, responsive design.
[See screenshots](../README.md#features)

### Comprehensive Testing

Unit + CLI + E2E tests, coverage reports, Playwright traces.
[Learn more](contributor-guide/testing.md)

### Full CI/CD

GitHub Actions workflows, 3 environments, automated releases.
[Learn more](contributor-guide/ci-cd.md)

---

## 🎓 Learning Path

### Beginner

1. [Main README](../README.md) — What is Prism?
2. [Quickstart](getting-started/quickstart.md) — Install in minutes
3. [Choosing a Prism](getting-started/choosing-a-prism.md) — Pick your prism

### Intermediate

1. [Creating Configurations](user-guide/creating-configurations.md) — Author a custom prism
2. [Sub-Prism Inheritance](user-guide/config-inheritance.md) — Advanced merging
3. [Configuration Schema](reference/configuration-schema.md) — Full schema reference

### Advanced

1. [Prism System](reference/package-system.md) — System internals
2. [NPM Packages](reference/npm-packages.md) — Distribution
3. [Contributing](contributor-guide/contributing.md) — Join development

---

## 🚀 Next Steps

```bash
# Clone and install
git clone https://github.com/andersonwilliam85/prism.git
cd prism
pip3 install pyyaml flask rich

# Launch Web UI
python3 install-ui.py
# Opens at http://localhost:5555

# Or use the CLI
python3 install.py --prism personal-dev
```

---

**💎 Prism — Refract complexity into clarity**
