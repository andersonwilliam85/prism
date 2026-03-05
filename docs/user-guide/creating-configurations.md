# Creating Configurations

Comprehensive guide to creating custom Prism configurations for your organization.

---

## Overview

Prism configurations are YAML-based packages that define:

- **Tools** to install (git, docker, kubernetes, etc.)
- **User information** fields to collect
- **Organizational hierarchy** (departments, teams, etc.)
- **Branding** (colors, logos, themes)
- **Repositories** to clone
- **Resources** to provide
- **Workflows** to enable

---

## Package Structure

### Basic Structure

```
prisms/my-company/
├── package.yaml          # Package metadata
├── package.json          # NPM package info (optional)
├── README.md             # Package documentation
├── base/
│   └── my-company.yaml   # Base configuration
├── orgs/                 # Sub-organizations (optional)
│   ├── engineering.yaml
│   └── product.yaml
├── teams/                # Teams (optional)
│   ├── platform.yaml
│   └── mobile.yaml
├── profiles/             # User profiles (optional)
│   ├── developer.yaml
│   └── manager.yaml
├── assets/               # Brand assets (optional)
│   ├── logo.png
│   └── colors.yaml
├── resources.yaml        # Company resources
└── welcome.yaml          # Welcome message
```

### Minimal Structure

For simple setups:

```
prisms/my-setup/
├── package.yaml
└── README.md
```

---

## Configuration Files

### package.yaml (Required)

Defines package metadata and configuration:

```yaml
package:
  # Required fields
  name: "my-company"
  version: "1.0.0"
  description: "My company development environment"
  
  # Optional: Brand assets
  assets:
    logo: "assets/logo.png"
    colors: "assets/colors.yaml"
  
  # Optional: Branding
  branding:
    primary_color: "#0066cc"
    secondary_color: "#ff9900"
    company_name: "My Company Inc."
  
  # Optional: User info fields
  user_info_fields:
    - name: "full_name"
      label: "Full Name"
      type: "text"
      required: true
    - name: "email"
      label: "Email Address"
      type: "email"
      required: true
    - name: "department"
      label: "Department"
      type: "select"
      options:
        - "Engineering"
        - "Product"
        - "Design"
      required: true
  
  # Optional: Tools to install
  tools:
    - git
    - docker
    - python
    - nodejs
    - kubernetes
  
  # Optional: Repositories to clone
  repositories:
    - url: "git@github.com:mycompany/backend.git"
      path: "~/Development/projects/backend"
    - url: "git@github.com:mycompany/frontend.git"
      path: "~/Development/projects/frontend"
  
  # Optional: Security settings
  security:
    sso_required: true
    vpn_required: true
    mfa_enabled: true
  
  # Optional: Compliance
  compliance:
    - "SOX"
    - "GDPR"
    - "HIPAA"
```

### package.json (Optional, for NPM)

For publishing to npm:

```json
{
  "name": "@prism/my-company-config",
  "version": "1.0.0",
  "description": "My Company Prism configuration",
  "main": "package.yaml",
  "keywords": ["prism", "config", "dev-environment"],
  "author": "Your Name",
  "license": "MIT",
  "prism": {
    "configFile": "package.yaml",
    "type": "enterprise"
  }
}
```

### README.md

Documentation for your package:

```markdown
# My Company Config

Prism configuration for My Company developers.

## What's Included

- Git, Docker, Python, Node.js
- Company repositories pre-cloned
- SSO and VPN configured
- Team-specific tool sets

## Usage

```bash
python3 install.py --package my-company
```

## Hierarchy

- Company (base)
  - Engineering (org)
    - Platform Team
    - Mobile Team
  - Product (org)
    - Growth Team
```

---

## Configuration Inheritance

### Base Configuration

**File**: `base/my-company.yaml`

Defines company-wide defaults:

```yaml
package:
  name: "my-company-base"
  
  tools:
    - git
    - docker
  
  security:
    sso: true
    vpn: true
  
  repositories:
    - url: "git@github.com:mycompany/shared.git"
      path: "~/Development/shared"
```

### Organization Override

**File**: `orgs/engineering.yaml`

Adds engineering-specific config:

```yaml
package:
  name: "engineering-org"
  
  # Adds to base tools
  tools:
    - kubernetes
    - terraform
  
  # Engineering-specific repos
  repositories:
    - url: "git@github.com:mycompany/infra.git"
      path: "~/Development/infra"
```

### Team Override

**File**: `teams/platform.yaml`

Adds team-specific config:

```yaml
package:
  name: "platform-team"
  
  # Platform team tools
  tools:
    - helm
    - istio
  
  # Platform repos
  repositories:
    - url: "git@github.com:mycompany/k8s-configs.git"
      path: "~/Development/platform/k8s"
```

### Merged Result

When user selects: **Company → Engineering → Platform**

```yaml
# Final merged configuration
package:
  name: "platform-team"
  
  tools:
    - git          # From base
    - docker       # From base
    - kubernetes   # From engineering
    - terraform    # From engineering
    - helm         # From platform
    - istio        # From platform
  
  security:
    sso: true      # From base
    vpn: true      # From base
  
  repositories:
    - url: "git@github.com:mycompany/shared.git"  # Base
    - url: "git@github.com:mycompany/infra.git"   # Engineering
    - url: "git@github.com:mycompany/k8s-configs.git"  # Platform
```

See [Config Inheritance](config-inheritance.md) for merge rules.

---

## Creating Your First Package

### Step 1: Choose a Template

```bash
# For small companies
cp -r prisms/acme-corp prisms/my-company

# For large enterprises
cp -r prisms/fortune500 prisms/my-enterprise

# For personal use
cp -r prisms/personal-dev prisms/my-setup
```

### Step 2: Edit Package Metadata

```bash
vim prisms/my-company/package.yaml
```

Update:
- `package.name`
- `package.description`
- `package.branding`
- `user_info_fields`

### Step 3: Customize Base Config

```bash
vim prisms/my-company/base/my-company.yaml
```

Define:
- Company-wide tools
- Base repositories
- Security settings
- Compliance requirements

### Step 4: Add Organizational Layers

```bash
# Create org configs
vim prisms/my-company/orgs/engineering.yaml
vim prisms/my-company/orgs/product.yaml

# Create team configs
vim prisms/my-company/teams/backend.yaml
vim prisms/my-company/teams/frontend.yaml
```

### Step 5: Add Branding

```bash
# Add logo
cp ~/Downloads/logo.png prisms/my-company/assets/

# Define colors
vim prisms/my-company/assets/colors.yaml
```

```yaml
# colors.yaml
colors:
  primary: "#0066cc"
  secondary: "#ff9900"
  accent: "#00cc66"
  background: "#ffffff"
  text: "#333333"
```

### Step 6: Validate

```bash
# Validate package structure
python3 scripts/package_validator.py prisms/my-company

# Should show:
# ✅ Package structure valid
# ✅ package.yaml valid
# ✅ All required fields present
```

### Step 7: Test Configuration

```bash
# Test base config
python3 scripts/config_merger.py \
  prisms/my-company/base/my-company.yaml

# Test with team override
python3 scripts/config_merger.py \
  prisms/my-company/base/my-company.yaml \
  prisms/my-company/teams/backend.yaml
```

### Step 8: Install and Test

```bash
# Launch web UI
make run

# Select your package
# Fill out user info
# Watch installation
```

---

## Advanced Configuration

### User Info Fields

Define custom fields to collect:

```yaml
user_info_fields:
  # Text input
  - name: "full_name"
    label: "Full Name"
    type: "text"
    required: true
    placeholder: "John Doe"
  
  # Email input
  - name: "email"
    label: "Email"
    type: "email"
    required: true
    validation: "^[a-z0-9._%+-]+@mycompany\\.com$"
  
  # Select dropdown
  - name: "department"
    label: "Department"
    type: "select"
    options:
      - "Engineering"
      - "Product"
      - "Design"
      - "Sales"
    required: true
  
  # Number input
  - name: "employee_id"
    label: "Employee ID"
    type: "number"
    required: true
    min: 100000
    max: 999999
  
  # Checkbox
  - name: "agree_to_terms"
    label: "I agree to the terms"
    type: "checkbox"
    required: true
```

### Tools Configuration

```yaml
tools:
  # Simple list
  - git
  - docker
  
  # With version specification
  - name: "python"
    version: "3.11"
  
  - name: "nodejs"
    version: "20.x"
  
  # With custom installation
  - name: "kubectl"
    install_command: "brew install kubectl"
  
  # Conditional tools
  - name: "xcode"
    platforms: ["macOS"]
  
  - name: "wsl"
    platforms: ["Windows"]
```

### Repository Configuration

```yaml
repositories:
  # Basic clone
  - url: "git@github.com:mycompany/backend.git"
    path: "~/Development/projects/backend"
  
  # With branch
  - url: "git@github.com:mycompany/frontend.git"
    path: "~/Development/projects/frontend"
    branch: "develop"
  
  # With post-clone setup
  - url: "git@github.com:mycompany/api.git"
    path: "~/Development/projects/api"
    post_clone:
      - "npm install"
      - "cp .env.example .env"
  
  # Shallow clone
  - url: "git@github.com:mycompany/docs.git"
    path: "~/Development/docs"
    depth: 1
```

### Resources Configuration

```yaml
resources:
  documentation:
    - name: "Developer Portal"
      url: "https://dev.mycompany.com"
    - name: "API Docs"
      url: "https://api.mycompany.com/docs"
  
  tools:
    - name: "Jira"
      url: "https://mycompany.atlassian.net"
    - name: "Confluence"
      url: "https://mycompany.atlassian.net/wiki"
  
  communication:
    - name: "Slack"
      url: "https://mycompany.slack.com"
    - name: "Teams"
      url: "https://teams.microsoft.com/mycompany"
```

---

## Examples

### Example 1: Minimal Personal Config

```yaml
# package.yaml
package:
  name: "my-setup"
  version: "1.0.0"
  description: "My personal dev setup"
  
  tools:
    - git
    - python
    - nodejs
  
  repositories:
    - url: "git@github.com:me/project.git"
      path: "~/Development/project"
```

### Example 2: Startup Config

```yaml
# package.yaml
package:
  name: "startup-dev"
  version: "1.0.0"
  description: "Startup dev environment"
  
  user_info_fields:
    - name: "name"
      label: "Name"
      type: "text"
      required: true
    - name: "email"
      label: "Email"
      type: "email"
      required: true
    - name: "role"
      label: "Role"
      type: "select"
      options: ["Engineer", "Designer", "PM"]
  
  tools:
    - git
    - docker
    - python
    - nodejs
    - postgresql
  
  repositories:
    - url: "git@github.com:startup/backend.git"
      path: "~/Development/backend"
    - url: "git@github.com:startup/frontend.git"
      path: "~/Development/frontend"
```

### Example 3: Enterprise Multi-Level

```yaml
# base/enterprise.yaml
package:
  name: "enterprise-base"
  
  security:
    sso: true
    vpn: true
    mfa: true
  
  tools:
    - git
    - docker
  
  compliance:
    - "SOX"
    - "GDPR"

---
# orgs/engineering.yaml
package:
  name: "engineering"
  
  tools:
    - kubernetes
    - terraform
    - jenkins

---
# teams/platform.yaml
package:
  name: "platform-team"
  
  tools:
    - helm
    - istio
    - prometheus
  
  repositories:
    - url: "git@github.enterprise.com:platform/k8s.git"
      path: "~/Development/platform/k8s"
```

---

## Publishing to NPM

### 1. Prepare Package

```bash
# Ensure package.json exists
cat > prisms/my-company/package.json << EOF
{
  "name": "@prism/my-company-config",
  "version": "1.0.0",
  "description": "My Company Prism configuration",
  "main": "package.yaml",
  "keywords": ["prism", "config"],
  "author": "Your Name",
  "license": "MIT"
}
EOF
```

### 2. Login to NPM

```bash
npm login
```

### 3. Publish

```bash
cd prisms/my-company
npm publish --access public
```

### 4. Use Published Package

```bash
python3 install.py --package @prism/my-company-config
```

See [NPM Packages](../reference/npm-packages.md) for details.

---

## Best Practices

### 1. Start Simple

Begin with minimal config, add complexity as needed.

### 2. Use Inheritance

Define common settings in base, override in teams.

### 3. Validate Often

Run validator after every change:
```bash
python3 scripts/package_validator.py prisms/my-company
```

### 4. Test Merging

Test all hierarchy combinations:
```bash
python3 scripts/config_merger.py base.yaml team.yaml
```

### 5. Document Everything

Write clear README for your package.

### 6. Version Properly

Use semantic versioning: `MAJOR.MINOR.PATCH`

### 7. Keep It DRY

Don't repeat configuration - use inheritance.

---

## Troubleshooting

### Validation Fails

**Error**: `Missing required field: name`

Ensure package.yaml has all required fields:
- `package.name`
- `package.version`
- `package.description`

### Merge Produces Unexpected Results

Check merge order - last config wins for scalar values.

See [Config Inheritance](config-inheritance.md) for merge rules.

### Assets Not Found

**Error**: `Asset not found: assets/logo.png`

Ensure file exists and path is correct in package.yaml.

---

## Next Steps

- 🔗 [Config Inheritance](config-inheritance.md) - Understand merging
- 📦 [Package System](../reference/package-system.md) - Technical details
- 📝 [Configuration Schema](../reference/configuration-schema.md) - Full YAML reference
- 🚀 [NPM Packages](../reference/npm-packages.md) - Distribution guide

---

**Questions?** [Open an issue](https://github.com/andersonwilliam85/prism/issues)
