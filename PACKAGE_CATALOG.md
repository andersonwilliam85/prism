# 📦 Config Package Catalog

**8 complete config packages covering every organization type**

---

## 🎯 Quick Selector

**What type of organization are you?**

| You Are... | Use Package | Size | Hierarchy |
|-----------|-------------|------|----------|
| 🏠 Freelancer/Indie Dev | `personal-dev-config` | 1 person | Flat |
| 🚀 Startup | `startup-config` | 10-50 | Flat |
| 🏢 Small Company | `acme-corp-config` | 50-500 | 2 levels |
| 🎯 Consulting Firm | `consulting-firm-config` | Variable | By client |
| 🏭 Large Enterprise | `walmart-config` | 5,000-50,000 | 4 levels |
| 🌐 Fortune 500 | `fortune500-config` | 50,000+ | 5 levels |
| 🎓 University | `university-config` | Variable | Depts → Labs |
| 🌟 Open Source Project | `opensource-project-config` | Community | Flat |

---

## 📦 Package Details

### 1. 🏠 personal-dev-config

**Perfect for:** Freelancers, indie developers, students, personal projects

**What you get:**
- 5 platform profiles (GitHub, GitLab, Bitbucket, Gitea, Multi)
- 60+ free developer resources
- Minimal user info (name, email, platform)
- No corporate bureaucracy!

**User fields:**
- Name
- Email
- Platform preference

**Installation:**
```bash
python3 scripts/package_manager.py install personal-dev-config
```

**Tags:** `recommended`, `personal`, `freelance`, `indie`

---

### 2. 🚀 startup-config

**Perfect for:** Seed/Series A startups, YC companies, fast-moving teams

**What you get:**
- Flat structure (no hierarchy!)
- Move fast philosophy
- Direct access to everything
- Modern tool stack

**User fields:**
- Name (just first name!)
- Email
- GitHub username
- Slack handle
- Role (optional)

**Philosophy:**
> "Move fast and ship on day 1. No approvals, no bureaucracy."

**Installation:**
```bash
python3 scripts/package_manager.py install startup-config
```

**Tags:** `recommended`, `startup`, `small-team`, `fast-moving`

---

### 3. 🏢 acme-corp-config

**Perfect for:** Small-medium companies (100-1000 employees)

**What you get:**
- Simple 2-level hierarchy
- 1 sub-org, 1 team example
- Easy to customize template
- Minimal complexity

**User fields:**
- Full name
- Corporate email
- Department
- Team

**Structure:**
```
ACME Corp
└── Engineering
    └── Payments Team
```

**Installation:**
```bash
python3 scripts/package_manager.py install acme-corp-config
```

**Tags:** `template`, `minimal`, `example`

---

### 4. 🎯 consulting-firm-config

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
python3 scripts/package_manager.py install consulting-firm-config
```

**Tags:** `consulting`, `agency`, `multi-client`

---

### 5. 🏭 walmart-config

**Perfect for:** Large enterprises (5,000-50,000 employees)

**What you get:**
- Complete 4-level hierarchy
- Real-world enterprise example
- GitHub Enterprise integration
- Corporate proxy config

**User fields:**
- Full name
- Corporate email (@walmart.com)
- LDAP username (optional)
- Employee ID (optional)
- Cost center (optional)

**Structure:**
```
Walmart
└── Walmart US
    └── Supply Chain
        └── Receiving Systems
```

**Use as:** Real enterprise template

**Installation:**
```bash
python3 scripts/package_manager.py install walmart-config
```

**Tags:** `walmart`, `enterprise`, `complete`, `hierarchical`

---

### 6. 🌐 fortune500-config

**Perfect for:** Fortune 500, multinational corporations (50,000+ employees)

**What you get:**
- Complex 5-level hierarchy
- Multi-region support
- Manager approval workflows
- Enterprise security (SSO, SAML)

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
            └── Kubernetes Platform Team
```

**Features:**
- Office location tracking
- Manager-based approvals
- Cost center allocation
- Compliance (SOX, GDPR)

**Installation:**
```bash
python3 scripts/package_manager.py install fortune500-config
```

**Tags:** `recommended`, `enterprise`, `fortune500`, `large-scale`

---

### 7. 🎓 university-config

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
python3 scripts/package_manager.py install university-config
```

**Tags:** `education`, `university`, `research`, `academic`

---

### 8. 🌟 opensource-project-config

**Perfect for:** Open source projects, community-driven development

**What you get:**
- Welcoming to first-time contributors
- Flat community structure
- Transparent processes
- Global collaboration

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

**Community:**
- Discord (real-time)
- GitHub Discussions (async)
- Issues (bugs/features)
- Pull Requests (code)

**Installation:**
```bash
git clone https://github.com/YOUR-USERNAME/project.git
cd project
python3 scripts/package_manager.py install opensource-project-config
```

**Tags:** `recommended`, `opensource`, `community`, `welcoming`

---

## 🎨 Customization

### Start from Template

**For small companies:**
```bash
cp -r config-packages/acme-corp-config config-packages/mycompany-config
# Edit package.yaml and configs
```

**For large enterprises:**
```bash
cp -r config-packages/fortune500-config config-packages/mycompany-config
# Customize hierarchy and fields
```

### Create from Scratch

```bash
python3 scripts/package_manager.py create mycompany-config
# Follow the prompts
```

---

## 📊 Comparison Matrix

| Feature | Personal | Startup | ACME | Consulting | Walmart | Fortune500 | University | OSS |
|---------|----------|---------|------|------------|---------|------------|------------|-----|
| **Hierarchy Levels** | 0 | 1 | 2 | 1 (clients) | 4 | 5 | 2 | 0 |
| **User Fields** | 3 | 5 | 4 | 5 | 6 | 6 | 6 | 5 |
| **Org Size** | 1 | 10-50 | 100-1K | Variable | 5K-50K | 50K+ | Variable | Community |
| **Approval Workflows** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Multi-client** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Complexity** | Low | Low | Medium | Medium | High | Very High | Medium | Low |
| **Recommended** | ✅ | ✅ | - | - | - | ✅ | - | ✅ |

---

## 🚀 Getting Started

### List all packages

```bash
python3 scripts/package_manager.py list
```

### Get package info

```bash
python3 scripts/package_manager.py info startup-config
```

### Install a package

```bash
python3 scripts/package_manager.py install startup-config
```

### Run the installer

```bash
python3 install-ui.py
```

---

## 🎯 Which Package Should I Use?

### Individual Developer
→ **personal-dev-config**

### Startup Team
→ **startup-config**

### Growing Company
→ **acme-corp-config** (customize it!)

### Consulting Firm
→ **consulting-firm-config**

### Enterprise
→ **walmart-config** or **fortune500-config**

### University
→ **university-config**

### Open Source
→ **opensource-project-config**

---

**📦 8 packages. Every organization type covered. Ready to ship!** 🚀
