# Walmart Development Environment Configuration Package

**Version:** 1.0.0  
**Maintained by:** Walmart Engineering  
**Support:** #dev-tools-support on Slack  

## 📦 What's Included

This package contains the complete Walmart development environment configuration:

### Base Configuration
- **`base/walmart.yaml`** - Company-wide settings
  - Proxy: `http://sysproxy.wal-mart.com:8080`
  - GitHub Enterprise: `https://gecgithub01.walmart.com`
  - VPN requirements
  - WiFi recommendations (walmartwifi vs eagle)
  - Required tools (git, kubectl, gh, jq, yq)
  - Security/compliance settings

### Sub-Organizations
- **`orgs/walmart-us.yaml`** - Walmart US configuration
  - GCP projects (`walmart-us-*`)
  - BigQuery access
  - US-specific cloud accounts

### Departments
- **`departments/supply-chain.yaml`** - Supply Chain Technology
  - Python, Java, TypeScript stack
  - FastAPI, Spring Boot, React frameworks
  - PostgreSQL, BigQuery databases
  - DBeaver, PyCharm tools
  - Supply Chain Slack channels & resources

### Teams
- **`teams/receiving-systems.yaml`** - Receiving Systems Team
  - Team repositories
  - Skaffold, Helm for K8s dev
  - VSCode extensions
  - Team contacts & workflows
  - Branching conventions

### Resources & Welcome
- **`resources.yaml`** - Walmart internal links
  - DX, NDE, ME@Walmart, WMLink
  - Code Puppy, Artifactory
  - Confluence, Jira, GitHub, Slack
  - Element LLM Gateway
  - Cloud consoles

- **`welcome.yaml`** - Welcome page & guidance
  - Installation tips (walmartwifi!)
  - Troubleshooting (proxy issues, etc.)
  - Support contacts
  - Getting Started guide

## 🚀 Installation

### Option 1: Using Package Manager

```bash
cd dev-onboarding
python3 scripts/package_manager.py install walmart-config
```

### Option 2: Manual Installation

```bash
# Copy all config files
cp -r config-packages/walmart/base/* config/base/
cp -r config-packages/walmart/orgs/* config/orgs/
cp -r config-packages/walmart/departments/* config/departments/
cp -r config-packages/walmart/teams/* config/teams/
cp config-packages/walmart/welcome.yaml config/
cp config-packages/walmart/resources.yaml config/

# Update inheritance.yaml to point to Walmart configs
# Edit config/inheritance.yaml:
#   company file: "config/base/walmart.yaml"
```

## 📋 What Gets Installed

### For ALL Walmart Developers:
- ✅ Proxy configured (sysproxy.wal-mart.com:8080)
- ✅ GitHub Enterprise (gecgithub01.walmart.com)
- ✅ VPN setup guidance
- ✅ Core tools: git, kubectl, gh, jq, yq
- ✅ Artifactory for Maven, npm, pip
- ✅ Code Puppy (optional)

### For Walmart US Developers:
- ✅ GCP access (walmart-us projects)
- ✅ BigQuery CLI (bq)
- ✅ Google Cloud SDK (gcloud)

### For Supply Chain Developers:
- ✅ Python development stack
- ✅ DBeaver (database client)
- ✅ Supply Chain Slack channels
- ✅ WMS documentation links

### For Receiving Systems Team:
- ✅ Team repositories (receiving-api, receiving-ui, putaway-engine)
- ✅ Skaffold + Helm (K8s development)
- ✅ Team-specific VSCode extensions
- ✅ Manager/Tech Lead contacts
- ✅ Branching conventions (RECV-XXX)

## 🎯 Customization

### For Your Team

Create a team config file:

```yaml
# config/teams/your-team.yaml
team:
  id: "your-team"
  name: "Your Team Name"
  manager: "Your Manager"

repositories:
  - name: "your-repo"
    url: "https://gecgithub01.walmart.com/your-org/your-repo"

tools_required:
  - your-team-specific-tool
```

Add to `inheritance.yaml`:

```yaml
available_teams:
  - id: "your-team"
    name: "Your Team"
    file: "config/teams/your-team.yaml"
    department: "your-department"
```

### For Your Department

Similarly, create `config/departments/your-dept.yaml`

## ⚠️ Important Notes

### WiFi Connection
**Use `walmartwifi` network, NOT `eagle`!**

Eagle WiFi has known issues with:
- Homebrew installations
- npm package installs
- Some proxy configurations

Switch to `walmartwifi` if you encounter proxy errors.

### VPN Requirements
All Walmart development tools require:
- Pulse Secure VPN connection, OR
- Connection to Eagle/walmartwifi networks

**Code Puppy ONLY works on VPN/Eagle/walmartwifi!**

### GitHub Enterprise
Correct URL: `https://gecgithub01.walmart.com`

Add your SSH key at:
`https://gecgithub01.walmart.com/settings/keys`

## 🆘 Support

### IT Support
- **Slack:** #it-support
- **Email:** ithelpdesk@walmart.com
- **Phone:** 1-800-WALMART
- **Hours:** 24/7
- **For:** VPN, laptop, hardware, Windows issues

### Dev Tools Support
- **Slack:** #dev-tools-support
- **Confluence:** https://confluence.walmart.com/dev-tools
- **For:** GitHub, Artifactory, build tools

### Code Puppy Support
- **Slack:** #element-genai-support
- **Hours:** Business hours (8am-5pm CT)
- **For:** Code Puppy authentication, LLM issues

## 📝 Changelog

### v1.0.0 (2026-03-04)
- Initial package release
- Complete Walmart configuration hierarchy
- Walmart US sub-org config
- Supply Chain department config
- Receiving Systems team config
- Accurate GitHub Enterprise URL (gecgithub01.walmart.com)
- WiFi guidance (walmartwifi vs eagle)
- Welcome page with Walmart-specific tips

## 🔗 Related Resources

- **DX (Developer Experience):** https://dx.walmart.com
- **Code Puppy:** https://puppy.walmart.com
- **Artifactory:** https://artifactory.walmart.com
- **Confluence:** https://confluence.walmart.com
- **GitHub Enterprise:** https://gecgithub01.walmart.com

---

**Built with ❤️ by Walmart Engineering**
