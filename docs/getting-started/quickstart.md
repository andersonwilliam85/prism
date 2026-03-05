# Quickstart

Get up and running with Prism in 5 minutes.

---

## 1. Install Prism

```bash
# Clone the repository
git clone https://github.com/andersonwilliam85/prism.git
cd prism

# Install dependencies
make install-dev

# Verify installation
make test
```

**✅ Installation complete!**

---

## 2. Choose Your Path

### Option A: Web UI (Recommended)

Beautiful visual installation wizard:

```bash
make run
# Opens browser at http://localhost:5555
```

**Features:**
- 🎭 Visual package selection
- 🧐 Step-by-step wizard
- 🎨 5 beautiful themes
- 📊 Live progress tracking

### Option B: Command Line

Prefer the terminal?

```bash
python3 install.py
# Follow interactive prompts
```

---

## 3. Select a Package

### For Individual Developers

```bash
# Personal dev environment
python3 install.py --package personal-dev
```

**Includes:**
- Minimal user info (name, email, platform)
- 5 platform profiles (GitHub, GitLab, etc.)
- 60+ free developer resources
- No corporate complexity

### For Startups

```bash
# Fast-moving team environment
python3 install.py --package startup
```

**Includes:**
- Flat structure (no hierarchy)
- Basic user info (name, email, role)
- Modern development tools
- Move-fast philosophy

### For Companies

```bash
# Enterprise environment
python3 install.py --package acme-corp
```

**Includes:**
- 2-level hierarchy (departments, teams)
- Corporate user info (full name, email, department)
- Customizable template
- Approval workflows

See all packages: [Choosing a Package](../user-guide/choosing-a-package.md)

---

## 4. Customize (Optional)

Want to create your own configuration?

```bash
# Copy a template
cp -r prisms/acme-corp prisms/my-company

# Edit the base config
vim prisms/my-company/base/my-company.yaml

# Validate
python3 scripts/package_validator.py prisms/my-company
```

See: [Creating Configurations](../user-guide/creating-configurations.md)

---

## 5. Test Your Configuration

### Validate Package

```bash
# Check for errors
python3 scripts/package_validator.py prisms/my-company

# Expected output:
# ✅ Package structure valid
# ✅ package.yaml valid
# ✅ All required fields present
# ✅ Assets exist
```

### Test Config Merging

```bash
# Merge base + team configs
python3 scripts/config_merger.py \
  prisms/my-company/base/my-company.yaml \
  prisms/my-company/teams/platform.yaml

# Shows merged result
```

### Run Tests

```bash
# Quick tests
make test

# Full test suite
make test-all
```

---

## Quick Reference

### Common Commands

```bash
# Start web UI
make run

# Run tests
make test

# Format code
make format

# Validate all packages
python3 scripts/package_validator.py --all

# List available packages
python3 scripts/package_manager.py list

# Get package info
python3 scripts/package_manager.py info personal-dev
```

### File Structure

```
prism/
├── prisms/              # Configuration packages
│   ├── personal-dev/
│   ├── startup/
│   ├── acme-corp/      # ← Copy this to start
│   └── my-company/    # Your custom package
├── scripts/            # Core tools
├── tests/              # Test suite
├── install-ui.py       # Web UI server
└── install.py          # CLI installer
```

### Configuration Inheritance

```yaml
# Base company config
package:
  name: "my-company"
  tools:
    - git
    - docker

# Team override (merges with base)
package:
  name: "platform-team"
  tools:
    - kubernetes  # Added to base tools
```

See: [Config Inheritance](../user-guide/config-inheritance.md)

---

## Examples

### Example 1: Personal Developer

```bash
# 1. Install Prism
git clone https://github.com/andersonwilliam85/prism.git
cd prism
make install-dev

# 2. Choose personal-dev package
make run
# Select "Personal Developer" in web UI

# 3. Enter your info
# - Name: John Doe
# - Email: john@example.com
# - Platform: GitHub

# 4. Install!
# Watch as Prism sets up your environment
```

### Example 2: Startup Team

```bash
# 1. Install Prism
git clone https://github.com/andersonwilliam85/prism.git
cd prism
make install-dev

# 2. CLI installation
python3 install.py --package startup

# 3. Answer prompts
# Name: Alice
# Email: alice@startup.com
# Role: Backend Engineer

# 4. Done!
```

### Example 3: Custom Company Config

```bash
# 1. Copy template
cp -r prisms/acme-corp prisms/techcorp

# 2. Edit base config
vim prisms/techcorp/base/techcorp.yaml

# Change company name, tools, settings

# 3. Add teams
vim prisms/techcorp/teams/backend-team.yaml
vim prisms/techcorp/teams/frontend-team.yaml

# 4. Validate
python3 scripts/package_validator.py prisms/techcorp

# 5. Test merge
python3 scripts/config_merger.py \
  prisms/techcorp/base/techcorp.yaml \
  prisms/techcorp/teams/backend-team.yaml

# 6. Install
make run
# Select "TechCorp" package
```

---

## Troubleshooting

### Web UI Won't Start

**Error**: `Address already in use`

```bash
# Use different port
python3 install-ui.py --port 8080
```

### Package Not Found

**Error**: `Package 'xyz' not found`

```bash
# List available packages
python3 scripts/package_manager.py list

# Check package directory exists
ls -la prisms/
```

### Validation Fails

**Error**: `Missing required field: name`

```bash
# Check package.yaml has required fields
cat prisms/my-package/package.yaml

# Required fields:
# - package.name
# - package.version
# - package.description
```

---

## Next Steps

Now that you're set up:

### Learn More

- 🎭 [Creating Configurations](../user-guide/creating-configurations.md) - Build custom configs
- 🔗 [Config Inheritance](../user-guide/config-inheritance.md) - How merging works
- 📦 [Package System](../reference/package-system.md) - Technical details

### Customize

- 🎨 [Choose a Package](../user-guide/choosing-a-package.md) - Find the right fit
- 🛠️ [Custom Registries](../user-guide/custom-registries.md) - Corporate npm
- 📝 [Configuration Schema](../reference/configuration-schema.md) - YAML reference

### Contribute

- 🔧 [Development Guide](../development/testing.md) - Run tests
- 🤝 [Contributing](../development/contributing.md) - Join the project
- 🚀 [CI/CD](../development/ci-cd.md) - Automation pipeline

---

**Questions?** [Open an issue](https://github.com/andersonwilliam85/prism/issues)

**Ready to dive deeper?** [First Configuration Guide](first-configuration.md)
