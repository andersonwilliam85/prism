# ACME Corp Config Package (Example Template)

**Version:** 1.0.0  
**Type:** Example / Template  

This is a **minimal example** of a company configuration package. Use it as a template to create your own!

## 📚 What's Included

### Minimal Structure
- **Base company config** - Proxy, VPN, Git, tools
- **One sub-org** - Engineering division example
- **One team** - Platform team example
- **Welcome page** - Company-specific welcome content
- **Resources** - Internal links and tools

## 🚀 How to Use as Template

### 1. Copy this package
```bash
cp -r config-packages/acme-corp config-packages/your-company
cd config-packages/your-company
```

### 2. Customize package.yaml
```yaml
package:
  name: "your-company-config"
  description: "Your Company dev environment"
  author: "Your IT Team"
  homepage: "https://dev.yourcompany.com"
```

### 3. Update base config
Edit `base/your-company.yaml`:
- Company name and domain
- Proxy settings (if any)
- GitHub Enterprise URL
- Required tools
- Cloud accounts

### 4. Add your orgs/teams
Create files in:
- `orgs/` - Your divisions/business units
- `departments/` - Engineering departments
- `teams/` - Individual teams

### 5. Customize welcome page
Edit `welcome.yaml`:
- Welcome message
- Getting started steps
- Installation guidance
- Support contacts
- Company branding

### 6. Update resources
Edit `resources.yaml`:
- Internal tools and links
- Documentation sites
- Communication platforms

### 7. Test installation
```bash
cd ../../  # Back to dev-onboarding root
python3 scripts/package_manager.py install your-company-config
```

## 📋 Package Structure

```
acme-corp/
├── package.yaml          # Package metadata
├── README.md             # This file
├── welcome.yaml          # Welcome page content
├── resources.yaml        # Company resources
├── base/
│   └── acme-corp.yaml    # Company base config
├── orgs/
│   └── acme-engineering.yaml
└── teams/
    └── platform-team.yaml
```

## 🎯 Minimal vs Complete

**This package (minimal):**
- 1 base config
- 1 sub-org
- 1 team
- ~6 files

**Walmart package (complete):**
- 1 base config
- Multiple sub-orgs
- Multiple departments
- Multiple teams
- Detailed welcome guidance
- Troubleshooting docs
- ~15+ files

**Choose what fits your company size!**

---

**Built with ❤️ as an example template**
