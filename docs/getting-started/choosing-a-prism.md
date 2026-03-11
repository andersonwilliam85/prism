---
layout: default
title: Choosing a Prism
---

# Choosing a Prism

Complete guide to selecting the right Prism configuration for your organization.

---

## Quick Selector

**What type of organization are you?**

| Organization Type | Prism | Team Size | Hierarchy | Complexity |
|---|---|---|---|---|
| Freelancer / Indie Dev | `prism` | 1 | Flat | Low |
| Startup | `startup` | 10–50 | Roles + Stacks | Low |
| Small/Medium Company | `acme-corp` | 100–1K | Org → Team | Medium |
| Consulting Firm | `consulting-firm` | Variable | By client | Medium |
| Fortune 500 | `fortune500` | 50K+ | Division → Role | High |
| University | `university` | Variable | Dept → User type | Medium |
| Open Source | `opensource` | Community | Flat | Low |

---

## How Prisms Work

Each prism contains:
- **`prism_config`** — Prism tool settings (theme, proxy, registry, branding)
- **`bundled_prisms`** — A hierarchy of sub-prisms you select from at install time
- **`user_info_fields`** — The information collected from you

During installation, required sub-prisms (like the base configuration) are applied automatically. Optional tiers (like roles, divisions, or teams) let you pick the one that matches your context. All selected sub-prisms are **deep-merged** in order, so each layer inherits and extends the previous one.

```
Prism
 ├── prism_config   (theme, proxy, registry)
 └── bundled_prisms
      ├── base       → always applied
      ├── [tier-2]   → user selects one
      └── [tier-3]   → user selects one (optional)
```

---

## Available Prisms

### 1. Personal Developer (`prism`)

**Perfect for:** Freelancers, indie developers, students, personal projects

**What you get:**
- 5 platform profiles (GitHub, GitLab, Bitbucket, Gitea, Multi-platform)
- 60+ free developer resources
- Minimal user info — no corporate bureaucracy

**Sub-prism tiers:**
- **base** (required) — core development setup
- **profiles** (pick one) — your git platform of choice

**Installation:**
```bash
python3 install.py --prism prism
```

---

### 2. Startup (`startup`)

**Perfect for:** Seed/Series A startups, fast-moving teams

**What you get:**
- Role-based configuration (full-stack, frontend, backend)
- Optional tech stack sub-prisms (MERN, JAMstack, Rails)
- Move-fast philosophy — no bureaucracy

**Sub-prism tiers:**
- **base** (required) — startup core setup
- **roles** (pick one) — your engineering role
- **stacks** (optional) — your tech stack

**Installation:**
```bash
python3 install.py --prism startup
```

---

### 3. Small/Medium Company (`acme-corp`)

**Perfect for:** Growing companies (100–1000 employees)

**What you get:**
- 2-level hierarchy: sub-org → team
- Customizable template — replace ACME Corp with your company
- Enterprise git (GitHub Enterprise)

**Sub-prism tiers:**
- **base** (required) — company-wide settings
- **orgs** (pick one) — your sub-organization
- **teams** (pick one) — your team

**Structure:**
```
Company (base)
└── Sub-Org (orgs)
    └── Team (teams)
```

**Installation:**
```bash
python3 install.py --prism acme-corp
```

---

### 4. Consulting Firm (`consulting-firm`)

**Perfect for:** Consulting firms, agencies, professional services

**What you get:**
- Per-client configuration with compliance settings
- Supports FinTech (SOX/PCI-DSS), Healthcare (HIPAA), Retail (PCI-DSS)
- Context-switching between client projects

**Sub-prism tiers:**
- **base** (required) — firm-wide setup
- **clients** (pick one) — your active client engagement

**Installation:**
```bash
python3 install.py --prism consulting-firm
```

---

### 5. Fortune 500 (`fortune500`)

**Perfect for:** Enterprise corporations (50,000+ employees)

**What you get:**
- Multi-tier hierarchy: division → role → business unit
- Enterprise security (SSO, MFA, VPN)
- Compliance templates (SOX, GDPR, HIPAA, PCI-DSS)

**Sub-prism tiers:**
- **base** (required) — enterprise-wide settings
- **divisions** (pick one) — Technology, Digital, Data & Analytics
- **roles** (pick one) — Software Engineer, DevOps, Data Engineer, etc.
- **business_units** (optional) — Retail, Finance, Healthcare

**Installation:**
```bash
python3 install.py --prism fortune500
```

---

### 6. University (`university`)

**Perfect for:** Universities, research institutions, academic labs

**What you get:**
- User-type sub-prisms: Student, Faculty, Researcher, IT Staff
- Department configurations (CS, Engineering, Data Science, Math)
- Course-specific configs with starter repositories

**Sub-prism tiers:**
- **base** (required) — university-wide setup
- **user_type** (pick one) — Student, Faculty, Researcher, Staff
- **departments** (optional) — your academic department
- **courses** (optional) — your current courses

**Installation:**
```bash
python3 install.py --prism university
```

---

### 7. Open Source (`opensource`)

**Perfect for:** Open source project maintainers and contributors

**What you get:**
- Minimal, welcoming contributor setup
- Community-focused workflow
- No corporate overhead

**Sub-prism tiers:**
- **base** (required) — open source contributor setup

**Installation:**
```bash
python3 install.py --prism opensource
```

---

## Comparison Matrix

| Feature | Personal | Startup | ACME | Consulting | Fortune500 | University | OSS |
|---|---|---|---|---|---|---|---|
| **Sub-prism tiers** | 2 | 3 | 3 | 2 | 4 | 4 | 1 |
| **User info fields** | 4 | 4 | 3 | 5 | 7 | 6 | 5 |
| **Typical size** | 1 | 10–50 | 100–1K | Variable | 50K+ | Variable | Community |
| **Compliance** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Multi-client** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Complexity** | Low | Low | Medium | Medium | High | Medium | Low |

---

## Decision Tree

**Are you working alone?**
→ Yes: **`prism`**

**Are you a consulting firm with multiple clients?**
→ Yes: **`consulting-firm`**

**Are you in academia or research?**
→ Yes: **`university`**

**Is your project open source and community-driven?**
→ Yes: **`opensource`**

**How many employees?**
- 1–50: **`startup`**
- 50–500: **`acme-corp`** (customize it!)
- 500–5,000: **`acme-corp`** (customize heavily)
- 5,000+: **`fortune500`**

---

## Customization Guide

All prisms are templates. Copy and customize:

```bash
# Copy a prism as your starting point
cp -r prisms/acme-corp prisms/my-company

# Edit to match your organization
vim prisms/my-company/package.yaml
vim prisms/my-company/base/my-company.yaml

# Add your sub-prisms (orgs, teams, etc.)
# Validate
python3 scripts/package_manager.py validate my-company

# Test
python3 install.py --prism my-company
```

See [Creating Prisms](creating-configurations.md) for a full guide.

---

## CLI Commands

```bash
# List all available prisms
python3 scripts/package_manager.py list

# Get detailed info about a prism
python3 scripts/package_manager.py info <prism-name>

# Install via CLI
python3 install.py --prism <prism-name>

# Install via Web UI
make run
```

---

**Questions?** [Open an issue](https://github.com/andersonwilliam85/prism/issues)
