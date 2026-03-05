# Config Package System

**Modular, distributable, version-controlled configuration packages for dev onboarding.**

## 🎯 Overview

The Config Package System allows companies to create, distribute, and install complete development environment configurations as self-contained packages.

### Key Benefits

✅ **Modular** - Install only what you need  
✅ **Distributable** - Share via git, registry, or local files  
✅ **Version-controlled** - Track changes over time  
✅ **Hierarchical** - Company → Org → Dept → Team inheritance  
✅ **Discoverable** - Auto-find packages in `config-packages/`  
✅ **Validatable** - Check package structure before install  

---

## 📦 Available Packages

### Example Configs (ACME Corp & Personal Dev)
**Package:** `walmart-config`  
**Type:** Company (large enterprise)  
**Includes:**
- Complete base configuration
- 1 sub-org (Walmart US)
- 1 department (Supply Chain)
- 1 team (Receiving Systems)
- Welcome page with Walmart-specific guidance
- Resource links to internal tools
- GitHub Enterprise (gecgithub01.walmart.com)
- Proxy, VPN, WiFi guidance

### ACME Corp Config (Template)
**Package:** `acme-corp-config`  
**Type:** Company (medium-sized template)  
**Includes:**
- Minimal base configuration
- 1 sub-org (Engineering)
- 1 team (Platform Team)
- Simple welcome page
- Basic resources
- **Use as template for your own company!**

---

## 🚀 Quick Start

### List Available Packages

```bash
python3 scripts/package_manager.py list
```

**Output:**
```
📦 Available Config Packages

  📦 walmart-config (v1.0.0)
     Complete Walmart development environment configuration
     Type: company | Size: large | Author: Walmart Engineering
     Tags: walmart, enterprise, complete, hierarchical

  📦 acme-corp-config (v1.0.0)
     ACME Corp dev environment (example template)
     Type: company | Size: medium | Author: ACME Corp IT Team
     Tags: example, template, minimal

  Total: 2 package(s)
```

### Get Package Info

```bash
python3 scripts/package_manager.py info walmart-config
```

### Install a Package

```bash
python3 scripts/package_manager.py install walmart-config
```

**What happens:**
1. Copies config files to `config/`
2. Installs base, orgs, departments, teams
3. Installs welcome page and resources
4. Shows post-install message

### Validate Package

```bash
python3 scripts/package_manager.py validate walmart-config
```

### Search Packages

```bash
python3 scripts/package_manager.py search walmart
```

---

## 🏭 Create Your Own Package

### Option 1: Use Scaffold Generator

```bash
python3 scripts/package_manager.py create mycompany-config --company "My Company"
```

**Creates:**
```
config-packages/mycompany/
├── package.yaml         # Package metadata
├── README.md            # Documentation
├── welcome.yaml         # Welcome page
├── resources.yaml       # Company resources
├── base/
│   └── mycompany.yaml   # Base config
├── orgs/
│   └── (empty - add your orgs)
└── teams/
    └── (empty - add your teams)
```

### Option 2: Copy Template

```bash
cp -r config-packages/acme-corp config-packages/mycompany
cd config-packages/mycompany

# Edit package.yaml
# Edit base config
# Add your orgs/teams
```

### Option 3: Start from Walmart Package

For large enterprises:

```bash
cp -r config-packages/walmart config-packages/mycompany
cd config-packages/mycompany

# Use Walmart structure as template
# Replace all Walmart-specific content
```

---

## 📝 Package Structure

### Minimal Package (like ACME)

```
mycompany/
├── package.yaml          # REQUIRED: Package metadata
├── README.md             # Recommended: Documentation
├── welcome.yaml          # Optional: Welcome page content
├── resources.yaml        # Optional: Company resources
└── base/
    └── mycompany.yaml    # REQUIRED: Base company config
```

### Complete Package (like Walmart)

```
mycompany/
├── package.yaml
├── README.md
├── welcome.yaml
├── resources.yaml
├── base/
│   └── mycompany.yaml
├── orgs/
│   ├── mycompany-us.yaml
│   ├── mycompany-eu.yaml
│   └── mycompany-asia.yaml
├── departments/
│   ├── engineering.yaml
│   ├── product.yaml
│   └── data.yaml
└── teams/
    ├── platform-team.yaml
    ├── mobile-team.yaml
    └── data-platform.yaml
```

---

## ⚙️ Package Metadata (package.yaml)

### Required Fields

```yaml
package:
  name: "mycompany-config"           # REQUIRED
  version: "1.0.0"                   # REQUIRED (semver)
  description: "My Company config"   # REQUIRED
  type: "company"                    # REQUIRED: company|sub-org|department|team
  
  install:                           # REQUIRED
    target_dir: "config/"
    files:
      - source: "welcome.yaml"
        dest: "config/welcome.yaml"
    directories:
      - source: "base/"
        dest: "config/base/"
```

### Optional Fields

```yaml
package:
  author: "My Company IT Team"
  homepage: "https://dev.mycompany.com"
  
  support:
    email: "devops@mycompany.com"
    slack: "#dev-support"
  
  requires:
    onboarding_version: ">=1.0.0"
    python_version: ">=3.8"
  
  post_install:
    message: |
      🎉 Package installed!
      Next steps: ...

contents:
  base_config: "base/mycompany.yaml"
  welcome_page: "welcome.yaml"
  
  sub_orgs:
    - id: "mycompany-us"
      name: "My Company US"
      file: "orgs/mycompany-us.yaml"

distribution:
  local:
    path: "config-packages/mycompany/"
    discoverable: true
  
  git:
    url: "https://github.com/mycompany/dev-config"
    branch: "main"

metadata:
  tags: ["mycompany", "enterprise"]
  company_size: "medium"  # small|medium|large|enterprise
  last_updated: "2026-03-04"
  maintainers:
    - "DevOps Team"
```

---

## 🔧 CLI Commands

### List All Packages

```bash
python3 scripts/package_manager.py list
```

Shows all discoverable packages in `config-packages/`

### Package Info

```bash
python3 scripts/package_manager.py info <package-name>
```

Shows detailed information:
- Version, author, homepage
- Support contacts
- Sub-orgs, departments, teams included
- Tags and metadata

### Install Package

```bash
python3 scripts/package_manager.py install <package-name>

# Dry run (show what would be installed)
python3 scripts/package_manager.py install <package-name> --dry-run

# From custom source
python3 scripts/package_manager.py install <package-name> --source /path/to/package
```

### Validate Package

```bash
python3 scripts/package_manager.py validate <package-name>
```

Checks:
- ✅ package.yaml exists and is valid YAML
- ✅ Required fields present
- ✅ Source files/directories exist
- ✅ Install config is valid

### Search Packages

```bash
python3 scripts/package_manager.py search <query>
```

Searches:
- Package names
- Descriptions
- Tags

### Create New Package

```bash
python3 scripts/package_manager.py create <package-name>

# With custom company name
python3 scripts/package_manager.py create mycompany-config --company "My Company Inc"
```

Creates scaffold with:
- package.yaml template
- Base config
- Welcome page
- Resources file
- README
- Directory structure

---

## 🔄 Workflow: Creating & Distributing Packages

### For Large Enterprises (Walmart-style)

#### 1. Create Package Structure

```bash
python3 scripts/package_manager.py create mycompany-config --company "My Company"
cd config-packages/mycompany
```

#### 2. Customize Base Config

Edit `base/mycompany.yaml`:

```yaml
company:
  name: "My Company"
  domain: "mycompany.com"

environment:
  proxy:
    http: "http://proxy.mycompany.com:8080"
  vpn:
    required: true
    name: "My Company VPN"

git:
  enterprise:
    enterprise_url: "https://github.mycompany.com"

tools_required:
  - git
  - docker
  - kubectl

cloud:
  aws:
    accounts:
      - name: "mycompany-prod"
        id: "123456789012"
```

#### 3. Add Sub-Organizations

Create `orgs/mycompany-us.yaml`:

```yaml
sub_org:
  id: "mycompany-us"
  name: "My Company US"

cloud:
  gcp:
    projects:
      - "mycompany-us-prod"
      - "mycompany-us-dev"

tools_required:
  - gcloud
  - bq
```

#### 4. Add Departments

Create `departments/engineering.yaml`:

```yaml
department:
  id: "engineering"
  name: "Engineering"
  sub_org: "mycompany-us"

tech_stack:
  languages:
    - Python
    - TypeScript
    - Java
  
  frameworks:
    - FastAPI
    - React
    - Spring Boot

tools_required:
  - vscode
  - postman
```

#### 5. Add Teams

Create `teams/platform-team.yaml`:

```yaml
team:
  id: "platform-team"
  name: "Platform Engineering"
  department: "engineering"
  manager: "Jane Smith"
  slack_channel: "#platform-team"

repositories:
  - name: "platform-api"
    url: "https://github.mycompany.com/platform/api"
  - name: "platform-ui"
    url: "https://github.mycompany.com/platform/ui"

tools_required:
  - terraform
  - helm
  - skaffold
```

#### 6. Customize Welcome Page

Edit `welcome.yaml` with company-specific:
- Welcome message
- Getting started steps
- Installation guidance (network, VPN, etc.)
- Troubleshooting tips
- Support contacts

#### 7. Update Resources

Edit `resources.yaml` with links to:
- Internal documentation
- Developer portals
- CI/CD systems
- Communication tools
- Cloud consoles

#### 8. Validate Package

```bash
cd ../../
python3 scripts/package_manager.py validate mycompany-config
```

#### 9. Test Installation

```bash
# Dry run first
python3 scripts/package_manager.py install mycompany-config --dry-run

# Actual install
python3 scripts/package_manager.py install mycompany-config
```

#### 10. Distribute

**Option A: Git Repository**

```bash
cd config-packages/mycompany
git init
git add .
git commit -m "Initial My Company config package"
git remote add origin https://github.mycompany.com/devtools/config-package
git push -u origin main
```

Update `package.yaml`:
```yaml
distribution:
  git:
    url: "https://github.mycompany.com/devtools/config-package"
    branch: "main"
```

**Option B: Package Registry** (future)

```bash
python3 scripts/package_manager.py publish mycompany-config
```

**Option C: Local Distribution**

Zip and share:
```bash
tar -czf mycompany-config-v1.0.0.tar.gz config-packages/mycompany/
```

---

## 📋 Best Practices

### 1. Versioning

Use [Semantic Versioning](https://semver.org/):
- **1.0.0** - Initial release
- **1.0.1** - Bug fixes (typos, broken links)
- **1.1.0** - New features (add team, add tool)
- **2.0.0** - Breaking changes (restructure, remove team)

### 2. Documentation

Always include:
- ✅ README.md - What's included, how to install
- ✅ CHANGELOG.md - Version history
- ✅ Comments in YAML files

### 3. Testing

Before distributing:
```bash
# Validate structure
python3 scripts/package_manager.py validate mycompany-config

# Dry run install
python3 scripts/package_manager.py install mycompany-config --dry-run

# Test install in clean environment
rm -rf config/
python3 scripts/package_manager.py install mycompany-config
```

### 4. Maintenance

- 📅 Review quarterly
- ✅ Update proxy URLs when they change
- ✅ Add new teams as they form
- ✅ Remove deprecated tools
- ✅ Keep support contacts current

### 5. Security

⚠️ **Never include in packages:**
- API keys or secrets
- Personal information
- Private SSH keys
- Internal-only URLs (in public repos)

✅ **Use environment variables:**
```yaml
git:
  user:
    name: "${USER}"
    email: "${USER}@mycompany.com"
```

---

## 💡 Use Cases

### 1. Company-Wide Rollout

"We need to onboard 100 new engineers this quarter."

```bash
# Create company package once
python3 scripts/package_manager.py create acmecorp-config

# Customize for your company
# ...

# Distribute to all new hires
# They just run:
python3 scripts/package_manager.py install acmecorp-config
python3 install-ui.py
```

### 2. Team-Specific Onboarding

"We have 5 different engineering teams with different stacks."

Create one package with all teams:
```
acmecorp/
├── base/acmecorp.yaml       # Company-wide
├── teams/mobile-team.yaml  # Mobile (Swift, Kotlin)
├── teams/web-team.yaml     # Web (React, TypeScript)
├── teams/ml-team.yaml      # ML (Python, TensorFlow)
└── teams/platform-team.yaml # Platform (Go, K8s)
```

New hire selects their team in installer UI.

### 3. Multi-Region Companies

"We have offices in US, EU, and APAC with different cloud accounts."

```
mycompany/
├── base/mycompany.yaml
├── orgs/mycompany-us.yaml    # US cloud accounts
├── orgs/mycompany-eu.yaml    # EU cloud accounts, GDPR tools
└── orgs/mycompany-apac.yaml  # APAC cloud accounts
```

### 4. Contractor vs Employee

Different configs for different access levels:

```bash
# Full employee package
python3 scripts/package_manager.py install mycompany-employee-config

# Limited contractor package
python3 scripts/package_manager.py install mycompany-contractor-config
```

---

## 🔗 Integration

### With HR Systems

```python
# Auto-install based on employee data
import subprocess
import json

# Get employee info from HR API
employee = get_employee_from_hr_api(employee_id)

# Determine package
if employee['division'] == 'Walmart US':
    if employee['department'] == 'Supply Chain':
        package = 'walmart-config'

subprocess.run([
    'python3', 'scripts/package_manager.py', 
    'install', package
])
```

### With CI/CD

Auto-test package on every commit:

```yaml
# .github/workflows/validate-package.yml
name: Validate Config Package

on: [push]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate
        run: |
          python3 scripts/package_manager.py validate mycompany-config
```

---

## 🔮 Future Enhancements

### Package Registry

```bash
# Publish to registry
python3 scripts/package_manager.py publish mycompany-config

# Install from registry
python3 scripts/package_manager.py install mycompany-config --registry https://packages.mycompany.com
```

### Dependency Management

```yaml
package:
  name: "platform-team-config"
  dependencies:
    - "mycompany-config>=1.0.0"  # Requires base config
    - "engineering-dept-config>=2.0.0"
```

### Auto-Updates

```bash
# Check for updates
python3 scripts/package_manager.py update --check

# Update installed packages
python3 scripts/package_manager.py update --all
```

---

## ❓ FAQ

### Q: Can I have multiple packages installed?

**A:** Yes! Packages install to the same `config/` directory. Later packages override earlier ones. Order:
1. Install base company package
2. Install team-specific package (if any)
3. User customizes `config/user-profile.yaml`

### Q: How do I update an installed package?

**A:** Re-run install:
```bash
python3 scripts/package_manager.py install mycompany-config
```

Files are overwritten with new versions.

### Q: Can I create a package for just my team?

**A:** Yes! Set `type: "team"` in package.yaml and only include team-specific configs.

### Q: What's the difference between a package and the config/ directory?

**A:**
- **Package** = Source (in `config-packages/`)
- **Config** = Installed (in `config/`)

Packages are templates. Configs are the installed, active files.

---

## 🐶 Support

For help:
1. Check package README: `config-packages/<package-name>/README.md`
2. Validate package: `python3 scripts/package_manager.py validate <name>`
3. Create an issue on GitHub
4. Contact package maintainer (see `package.yaml` → `metadata` → `maintainers`)

---

**Built with ❤️ for scalable, maintainable dev onboarding**
