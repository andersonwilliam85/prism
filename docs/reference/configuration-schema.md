# Configuration Schema

Complete YAML schema reference for Prism configuration packages.

---

## Overview

Prism configurations are defined in YAML files with a well-defined schema. This document describes all available fields, their types, and usage.

---

## Package Metadata (`package.yaml`)

### Required Fields

```yaml
package:
  name: string              # Package identifier (kebab-case)
  version: string           # Semantic version (1.0.0)
  description: string       # Short description
```

### Optional Fields

```yaml
package:
  # Brand assets
  assets:
    logo: string           # Path to logo file
    colors: string         # Path to colors.yaml
  
  # Branding
  branding:
    primary_color: string  # Hex color (#0066cc)
    secondary_color: string
    company_name: string
  
  # User info fields to collect
  user_info_fields:
    - name: string         # Field identifier
      label: string        # Display label
      type: string         # text|email|select|number|checkbox
      required: boolean
      options: [string]    # For select type
      validation: string   # Regex pattern
      placeholder: string
      min: number          # For number type
      max: number
  
  # Tools to install
  tools:
    - string               # Simple: "git"
    - name: string         # Complex: with version
      version: string
      install_command: string
      platforms: [string]  # macOS, Windows, Linux
  
  # Repositories to clone
  repositories:
    - url: string          # Git URL
      path: string         # Local path
      branch: string       # Optional branch
      depth: number        # Shallow clone depth
      post_clone: [string] # Post-clone commands
  
  # Security settings
  security:
    sso_required: boolean
    vpn_required: boolean
    mfa_enabled: boolean
  
  # Compliance
  compliance: [string]     # ["SOX", "GDPR", "HIPAA"]
```

---

## Field Types

### String

Plain text value:

```yaml
name: "my-package"
description: "My package description"
```

### Boolean

True or false:

```yaml
required: true
sso_required: false
```

### Number

Integer or float:

```yaml
version: 1.0
min: 100000
max: 999999
depth: 1
```

### Array

List of values:

```yaml
tools:
  - git
  - docker
  - python

compliance:
  - "SOX"
  - "GDPR"
```

### Object

Nested key-value pairs:

```yaml
branding:
  primary_color: "#0066cc"
  secondary_color: "#ff9900"
  company_name: "My Company"
```

---

## User Info Fields

### Text Input

```yaml
user_info_fields:
  - name: "full_name"
    label: "Full Name"
    type: "text"
    required: true
    placeholder: "John Doe"
```

### Email Input

```yaml
user_info_fields:
  - name: "email"
    label: "Email Address"
    type: "email"
    required: true
    validation: "^[a-z0-9._%+-]+@company\\.com$"
```

### Select Dropdown

```yaml
user_info_fields:
  - name: "department"
    label: "Department"
    type: "select"
    options:
      - "Engineering"
      - "Product"
      - "Design"
    required: true
```

### Number Input

```yaml
user_info_fields:
  - name: "employee_id"
    label: "Employee ID"
    type: "number"
    required: true
    min: 100000
    max: 999999
```

### Checkbox

```yaml
user_info_fields:
  - name: "agree_to_terms"
    label: "I agree to the terms"
    type: "checkbox"
    required: true
```

---

## Tools Configuration

### Simple Format

```yaml
tools:
  - git
  - docker
  - python
  - nodejs
```

### Complex Format

```yaml
tools:
  # With version
  - name: "python"
    version: "3.11"
  
  # With custom install command
  - name: "kubectl"
    install_command: "brew install kubectl"
  
  # Platform-specific
  - name: "xcode"
    platforms: ["macOS"]
  
  - name: "wsl"
    platforms: ["Windows"]
```

---

## Repositories Configuration

### Basic Clone

```yaml
repositories:
  - url: "git@github.com:mycompany/backend.git"
    path: "~/Development/projects/backend"
```

### With Branch

```yaml
repositories:
  - url: "git@github.com:mycompany/frontend.git"
    path: "~/Development/projects/frontend"
    branch: "develop"
```

### With Post-Clone Setup

```yaml
repositories:
  - url: "git@github.com:mycompany/api.git"
    path: "~/Development/projects/api"
    post_clone:
      - "npm install"
      - "cp .env.example .env"
```

### Shallow Clone

```yaml
repositories:
  - url: "git@github.com:mycompany/docs.git"
    path: "~/Development/docs"
    depth: 1
```

---

## Assets Configuration

### Logo

```yaml
package:
  assets:
    logo: "assets/logo.png"
```

Supported formats: PNG, JPG, SVG  
Recommended size: 200x200px

### Colors

```yaml
# package.yaml
package:
  assets:
    colors: "assets/colors.yaml"

# assets/colors.yaml
colors:
  primary: "#0066cc"
  secondary: "#ff9900"
  accent: "#00cc66"
  background: "#ffffff"
  text: "#333333"
```

---

## Branding Configuration

```yaml
package:
  branding:
    primary_color: "#0066cc"      # Main brand color
    secondary_color: "#ff9900"    # Accent color
    company_name: "My Company Inc."
```

---

## Security Configuration

```yaml
package:
  security:
    sso_required: true    # Single sign-on required
    vpn_required: true    # VPN connection required
    mfa_enabled: true     # Multi-factor authentication
```

---

## Compliance Configuration

```yaml
package:
  compliance:
    - "SOX"      # Sarbanes-Oxley
    - "GDPR"     # General Data Protection Regulation
    - "HIPAA"    # Health Insurance Portability
    - "PCI-DSS"  # Payment Card Industry
```

---

## Configuration Hierarchy

### Base Configuration

```yaml
# prisms/company/base/company.yaml
package:
  name: "company-base"
  
  tools:
    - git
    - docker
  
  security:
    sso: true
    vpn: true
```

### Organization Override

```yaml
# prisms/company/orgs/engineering.yaml
package:
  name: "engineering-org"
  
  # Adds to base tools
  tools:
    - kubernetes
    - terraform
```

### Team Override

```yaml
# prisms/company/teams/platform.yaml
package:
  name: "platform-team"
  
  # Adds team-specific tools
  tools:
    - helm
    - istio
```

See [Config Inheritance](../user-guide/config-inheritance.md) for merge rules.

---

## Resources Configuration

```yaml
# resources.yaml
resources:
  documentation:
    - name: "Developer Portal"
      url: "https://dev.company.com"
    - name: "API Docs"
      url: "https://api.company.com/docs"
  
  tools:
    - name: "Jira"
      url: "https://company.atlassian.net"
    - name: "Confluence"
      url: "https://company.atlassian.net/wiki"
  
  communication:
    - name: "Slack"
      url: "https://company.slack.com"
```

---

## Welcome Message

```yaml
# welcome.yaml
welcome:
  title: "Welcome to My Company!"
  message: |
    Welcome to the team! This setup will configure your
    development environment with all the tools and
    repositories you need to get started.
  
  getting_started:
    - "Review the developer portal"
    - "Join #engineering on Slack"
    - "Attend team standup (daily at 10am)"
    - "Read the contributing guide"
```

---

## NPM Package Metadata (`package.json`)

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

---

## Validation Rules

### Required Fields

- `package.name` - Must be present
- `package.version` - Must be semver format
- `package.description` - Must be present

### Field Constraints

- `name` - Lowercase, hyphens allowed, no spaces
- `version` - Must match `\d+\.\d+\.\d+` pattern
- `primary_color` - Must be valid hex color (#RRGGBB)
- `email` validation - Must match RFC 5322 format

### File References

- `assets.logo` - File must exist
- `assets.colors` - File must exist and be valid YAML

---

## Examples

### Minimal Configuration

```yaml
package:
  name: "my-setup"
  version: "1.0.0"
  description: "My personal dev setup"
  
  tools:
    - git
    - python
```

### Complete Configuration

```yaml
package:
  name: "my-company"
  version: "1.0.0"
  description: "My Company dev environment"
  
  assets:
    logo: "assets/logo.png"
    colors: "assets/colors.yaml"
  
  branding:
    primary_color: "#0066cc"
    secondary_color: "#ff9900"
    company_name: "My Company Inc."
  
  user_info_fields:
    - name: "full_name"
      label: "Full Name"
      type: "text"
      required: true
    - name: "email"
      label: "Email"
      type: "email"
      required: true
    - name: "department"
      label: "Department"
      type: "select"
      options: ["Engineering", "Product", "Design"]
      required: true
  
  tools:
    - git
    - docker
    - name: "python"
      version: "3.11"
    - name: "kubectl"
      platforms: ["macOS", "Linux"]
  
  repositories:
    - url: "git@github.com:mycompany/backend.git"
      path: "~/Development/backend"
      post_clone:
        - "npm install"
  
  security:
    sso_required: true
    vpn_required: true
    mfa_enabled: true
  
  compliance:
    - "SOX"
    - "GDPR"
```

---

## Validation

### Validate Package

```bash
python3 scripts/package_validator.py prisms/my-company
```

### Common Errors

**Error:** `Missing required field: name`
```yaml
# Fix: Add package.name
package:
  name: "my-package"  # ← Add this
```

**Error:** `Invalid version format`
```yaml
# Wrong
version: "1.0"

# Right
version: "1.0.0"
```

**Error:** `Asset not found: assets/logo.png`
```bash
# Fix: Ensure file exists
ls prisms/my-company/assets/logo.png
```

---

## Best Practices

1. **Use semantic versioning** - `MAJOR.MINOR.PATCH`
2. **Keep descriptions concise** - 1-2 sentences
3. **Validate references** - Ensure asset files exist
4. **Document custom fields** - Add descriptions to complex configs
5. **Test configurations** - Validate before deploying

---

## Resources

- [Creating Configurations](../user-guide/creating-configurations.md)
- [Config Inheritance](../user-guide/config-inheritance.md)
- [Package System](package-system.md)
- [NPM Packages](npm-packages.md)

---

**Questions?** [Open an issue](https://github.com/andersonwilliam85/prism/issues)
