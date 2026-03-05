# Walmart Prism 🏬

Walmart-specific enterprise development environment configuration.

## Overview

Walmart Prism provides a complete, secure, and compliant development environment for Walmart Global Tech associates. It includes multi-tier configuration, team setups, and enterprise tooling.

## Features

### 🎨 Walmart Theme
- Branded with Walmart blue (#0071ce) and spark (#ffc220)
- Professional enterprise appearance
- Consistent with Walmart brand guidelines

### 🔷 Bundled Setup Prisms

**Base (Everyone Gets This)**:
- Walmart base configuration
- VPN/Eagle WiFi setup
- Element LLM Gateway integration
- InfoSec compliance guidelines

**Roles (Choose One)**:
- Software Engineer (full dev environment)
- Data Scientist (Jupyter, BigQuery, ML tools)
- Product Manager (lightweight, collaboration tools)

**Organizations (Optional, Multi-Select)**:
- Global Tech
- Sam's Club Tech
- Walmart Connect

**Teams (Optional, Multi-Select)**:
- Element GenAI Team
- Code Puppy Team
- Custom teams

### 🔐 Security & Compliance

- **Network**: Requires Walmart VPN or Eagle WiFi
- **Data Handling**: Sensitive data permitted (no HIPAA patient data)
- **Registry**: Uses Walmart Artifactory for packages
- **Proxies**: Configured for Walmart network (sysproxy.wal-mart.com:8080)

### 📦 Package Sources

- Built-in prisms (local)
- Walmart Internal Prism Registry (`https://puppy.walmart.com/prism-registry`)
- Walmart Artifactory for npm packages

## Installation

1. **Connect to VPN/Eagle WiFi** (required!)
2. Select "Walmart Prism" from installer
3. Choose your role (Engineer, Data Scientist, PM)
4. Select organization(s)
5. Select team(s) if applicable
6. Fill in user info:
   - Full Name
   - Walmart Email (w0xxxxx@walmart.com)
   - User ID (w0xxxxx)
   - Slack handle
   - Role
   - Organization
   - Team

## Resources

### Support Channels
- **Code Puppy**: 
  - Slack: https://walmart.enterprise.slack.com/archives/C094Y1D24JY
  - Teams: [General Channel]
  - Marketplace: https://puppy.walmart.com/marketplace

- **Element GenAI**:
  - Slack: #element-genai-support
  - Documentation: https://element.walmart.com

### Training
- **Doghouse**: https://puppy.walmart.com/doghouse (Agentic workshops)
- **Confluence**: https://confluence.walmart.com/prism

## Configuration

### Prism Meta-Configuration

```yaml
prism_config:
  theme: "blue"  # Walmart blue
  sources:
    - url: "local"
      name: "Built-in Prisms"
      type: "local"
    - url: "https://puppy.walmart.com/prism-registry"
      name: "Walmart Internal Prism Registry"
      type: "remote"
      auth_requir  
  npm_registry: "https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple"
  npm_registry_insecure: true
  
  proxies:
    http: "http://sysproxy.wal-mart.com:8080"
    https: "http://sysproxy.wal-mart.com:8080"
```

### Bundled Prisms Structure

```
walmart.prism/
├── base/
│   └── walmart-base.yaml      # Core Walmart config
├── roles/
│   ├── engineer.yaml          # Software Engineer
│   ├── data-scientist.yaml    # Data Scientist
│   └── product-manager.yaml   # Product Manager
├── orgs/
│   ├── global-tech.yaml       # Global Tech
│   ├── sams-club.yaml         # Sam's Club
│   └── walmart-connect.yaml   # Walmart Connect
└── teams/
    ├── element-genai.yaml     # Element GenAI team
    └── code-puppy.yaml        # Code Puppy team
```

## Security Notes

⚠️ **CRITICAL**: Code Puppy ONLY works when connected to Walmart VPN or Eagle WiFi.

- All data stays within Walmart's network (Eagle)
- Element LLM Gateway prevents data leakage
- Sensitive data is permitted per InfoSec
- NO HIPAA patient data allowed

## Troubleshooting

### Can't connect to services
- ✅ Verify VPN/Eagle WiFi connection
- ✅ Check proxy settings
- ✅ Restart Code Puppy

### Authentication fails
- ✅ Ensure PingFed is working
- ✅ Re-authenticate if needed

### Package install fails
- ✅ Check Artifactory access
- ✅ Verify proxy configuration
- ✅ Try with `--allow-insecure-host` flag

## Customization for Your Team

Want to create a team-specific prism? Fork this!

```bash
cp -r prisms/walmart.prism prisms/my-team.prism
cd prisms/my-team.prism
# Edit package.yaml
# Add your team's specific configs
```

## License

Internal Use Only - Walmart Global Tech
