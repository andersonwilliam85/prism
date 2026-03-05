# Core Prism

The minimal base configuration that works for everyone.

## Overview

Core Prism is the default, minimal configuration for any developer. It provides a clean starting point without any organization-specific settings.

## What's Included

- **Base Configuration**: Minimal dev environment setup
- **Welcome Page**: Generic welcome message
- **Resources**: Basic developer resources
- **Default Theme**: Ocean Blue

## Use Cases

- **Individual Developers**: Simple, no-frills setup
- **Template/Starting Point**: Fork this to create custom prisms
- **Testing**: Quick setup for testing Prism itself

## Installation

1. Select "Core Prism" from the installer
2. Fill in basic info (name, email, git username)
3. Install!

## Customization

This prism is designed to be forked and customized:

```bash
cp -r prisms/core.prism prisms/my-custom.prism
cd prisms/my-custom.prism
# Edit package.yaml to customize
```

## Configuration

### Prism Meta-Configuration

```yaml
prism_config:
  theme: "ocean"  # Default theme
  sources:
    - url: "local"
      name: "Built-in Prisms"
      type: "local"
  npm_registry: ""  # Use default
```

### User Info Fields

- Name (required)
- Email (required)
- Git Username (required)

## License

MIT
