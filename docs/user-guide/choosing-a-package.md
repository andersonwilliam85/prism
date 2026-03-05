# Choosing a Package

Complete guide to selecting the right Prism configuration package for your organization.

---

## Quick Selector

**What type of organization are you?**

| Organization Type | Package | Team Size | Hierarchy | Complexity |
|-------------------|---------|-----------|-----------|------------|
| 🏠 Freelancer/Indie Dev | `personal-dev` | 1 | Flat | Low |
| 🚀 Startup | `startup` | 10-50 | 1 level | Low |
| 🏢 Small Company | `acme-corp` | 100-1K | 2 levels | Medium |
| 🎯 Consulting Firm | `consulting-firm` | Variable | By client | Medium |
| 🌐 Fortune 500 | `fortune500` | 50K+ | 5 levels | Very High |
| 🎓 University | `university` | Variable | Dept → Lab | Medium |
| 🌟 Open Source | `opensource` | Community | Flat | Low |

---

## Available Packages

### 1. 🏠 Personal Developer (`personal-dev`)

**Perfect for:** Freelancers, indie developers, students, personal projects

**What you get:**
- 5 platform profiles (GitHub, GitLab, Bitbucket, Gitea, Multi-platform)
- 60+ free developer resources
- Minimal user info (name, email, platform)
- No corporate bureaucracy

**User fields:**
- Name
- Email
- Platform preference

**Installation:**
```bash
python3 install.py --package personal-dev
```

**Best for:**
- Solo developers
- Learning and experimentation
- Side projects
- Open source contributors

---

### 2. 🚀 Startup (`startup`)

**Perfect for:** Seed/Series A startups, YC companies, fast-moving teams

**What you get:**
- Flat structure (no hierarchy!)
- Move-fast philosophy
- Direct access to everything
- Modern development stack

**User fields:**
- Name (first name is fine!)
- Email
- GitHub username
- Slack handle
- Role (optional)

**Philosophy:**
> "Move fast and ship on day 1. No approvals, no bureaucracy."

**Installation:**
```bash
python3 install.py --package startup
```

**Best for:**
- Small, fast-moving teams
- Minimal process overhead
- Everyone wears multiple hats
- Rapid iteration culture

---

### 3. 🏢 Small/Medium Company (`acme-corp`)

**Perfect for:** Growing companies (100-1000 employees)

**What you get:**
- Simple 2-level hierarchy (departments → teams)
- Customizable template
- Minimal complexity
- Room to grow

**User fields:**
- Full name
- Corporate email
- Department
- Team

**Structure:**
```
Company
└── Engineering
    ├── Platform Team
    └── Product Team
```

**Installation:**
```bash
python3 install.py --package acme-corp
```

**Best for:**
- Companies with departments and teams
- Need for some structure
- Not yet enterprise-scale
- Template for customization

---

### 4. 🎯 Consulting Firm (`consulting-firm`)

**Perfect for:** Consulting firms, agencies, professional services

**What you get:**
- Multi-client support
- Client-specific configurations
- Time tracking integration
- Context switching tools

**User fields:**
- Full name
- Company email
- Consultant ID
- Primary client
- Time tracking system

**Structure:**
```
Consulting Firm
└── Clients
    ├── FinTech Client (SOX, PCI-DSS)
    ├── Healthcare Client (HIPAA)
    └── Retail Client (PCI-DSS)
```

**Features:**
- Per-client tool requirements
- Client-specific compliance
- NDA/security per client

**Installation:**
```bash
python3 install.py --package consulting-firm
```

**Best for:**
- Multiple client engagements
- Different compliance per client
- Billable hour tracking
- Context switching between projects

---

### 5. 🌐 Fortune 500 (`fortune500`)

**Perfect for:** Enterprise corporations (50,000+ employees)

**What you get:**
- Complex 5-level hierarchy
- Multi-region support
- Manager approval workflows
- Enterprise security (SSO, SAML, MFA)

**User fields:**
- Full name
- Corporate email
- Employee ID (6-digit)
- Manager email
- Office location
- Cost center

**Structure:**
```
Enterprise
└── Business Units
    └── Engineering
        └── Cloud Infrastructure
            └── Platform Services
                └── Kubernetes Team
```

**Features:**
- Office location tracking
- Manager-based approvals
- Cost center allocation
- Compliance (SOX, GDPR, HIPAA)

**Installation:**
```bash
python3 install.py --package fortune500
```

**Best for:**
- Large multinational corporations
- Complex org structures
- Heavy compliance requirements
- Enterprise security standards

---

### 6. 🎓 University (`university`)

**Perfect for:** Universities, research institutions, academic labs

**What you get:**
- Academic structure (Departments → Labs)
- Student/Professor/Researcher roles
- GitHub Education Pack integration
- HPC cluster access

**User fields:**
- Full name
- University email (@university.edu)
- Student/Employee ID
- Role (Student, Professor, Researcher)
- Department
- Advisor/Supervisor (optional)

**Structure:**
```
University
└── Departments
    └── Computer Science
        └── Labs
            ├── Machine Learning Lab
            ├── Systems & Networking Lab
            └── Security Research Lab
```

**Resources:**
- GitHub Education Pack (free!)
- High-performance computing
- Academic journals
- Research databases

**Installation:**
```bash
python3 install.py --package university
```

**Best for:**
- Academic institutions
- Research labs
- Teaching environments
- Student projects

---

### 7. 🌟 Open Source (`opensource`)

**Perfect for:** Open source projects, community-driven development

**What you get:**
- Welcoming to first-time contributors
- Flat community structure
- Transparent processes
- Global collaboration tools

**User fields:**
- Name (how should we call you?)
- Email (for git commits)
- GitHub username
- Timezone (optional)
- Contribution interest (optional)

**Philosophy:**
> "Everyone is welcome! Every contribution counts! 💚"

**Contributing workflow:**
1. Read CONTRIBUTING.md
2. Find 'good first issue'
3. Join Discord/Discussions
4. Fork & make changes
5. Submit PR!

**Community channels:**
- Discord (real-time chat)
- GitHub Discussions (async forum)
- Issues (bugs/features)
- Pull Requests (code review)

**Installation:**
```bash
python3 install.py --package opensource
```

**Best for:**
- Community-driven projects
- Open source maintainers
- Contributor onboarding
- Transparent development

---

## Comparison Matrix

| Feature | Personal | Startup | ACME | Consulting | Fortune500 | University | OSS |
|---------|----------|---------|------|------------|------------|------------|-----|
| **Hierarchy Levels** | 0 | 1 | 2 | 1 (clients) | 5 | 2 | 0 |
| **User Info Fields** | 3 | 5 | 4 | 5 | 6 | 6 | 5 |
| **Typical Size** | 1 | 10-50 | 100-1K | Variable | 50K+ | Variable | Community |
| **Approval Workflows** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Multi-client** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Complexity** | Low | Low | Medium | Medium | Very High | Medium | Low |
| **Recommended For** | Solo | Seed-A | Series B+ | Services | Enterprise | Academic | Community |

---

## Decision Tree

### Start Here

**Are you working alone?**
→ Yes: **`personal-dev`**
→ No: Continue

**Are you a consulting firm with multiple clients?**
→ Yes: **`consulting-firm`**
→ No: Continue

**Are you in academia or research?**
→ Yes: **`university`**
→ No: Continue

**Is your project open source and community-driven?**
→ Yes: **`opensource`**
→ No: Continue

**How many employees?**
- 1-50: **`startup`**
- 50-500: **`acme-corp`** (customize it!)
- 500-5,000: **`acme-corp`** (customize heavily)
- 5,000+: **`fortune500`**

---

## Customization Guide

### Starting from a Template

All packages can be customized! Here's how:

```bash
# Copy a template
cp -r prisms/acme-corp prisms/my-company

# Edit to match your organization
vim prisms/my-company/package.yaml
vim prisms/my-company/base/my-company.yaml

# Validate
python3 scripts/package_validator.py prisms/my-company

# Test
python3 install.py --package my-company
```

### Which Template to Start From

| Your Org | Start From | Reason |
|----------|-----------|--------|
| Small company (< 500) | `acme-corp` | Simple 2-level hierarchy |
| Large enterprise | `fortune500` | Complex multi-level structure |
| Consulting | `consulting-firm` | Multi-client architecture |
| Personal | `personal-dev` | Minimal, no hierarchy |
| Academic | `university` | Department/Lab structure |
| Open Source | `opensource` | Community-focused |

See [Creating Configurations](creating-configurations.md) for detailed customization guide.

---

## Installation Commands

### List Available Packages

```bash
python3 scripts/package_manager.py list
```

### Get Package Info

```bash
python3 scripts/package_manager.py info <package-name>
```

### Install Package

```bash
# Via CLI
python3 install.py --package <package-name>

# Via Web UI
make run
# Then select package in browser
```

---

## Next Steps

**Package selected?** Great! Now:

1. **Install**: `python3 install.py --package <name>`
2. **Customize**: See [Creating Configurations](creating-configurations.md)
3. **Understand merging**: See [Config Inheritance](config-inheritance.md)
4. **Publish**: See [NPM Packages](../reference/npm-packages.md)

---

**Need help choosing?** [Open an issue](https://github.com/andersonwilliam85/prism/issues)
