# Prism Documentation

Complete documentation for Prism Package Manager - the flexible development environment installer.

---

## 📚 Documentation Structure

```
docs/
├── README.md                    # 👈 You are here!
├── user-guide/                  # Getting started & usage
│   ├── choosing-a-package.md
│   ├── creating-configurations.md
│   ├── config-inheritance.md
│   └── custom-registries.md
├── reference/                   # Technical specs
│   ├── configuration-schema.md
│   ├── package-system.md
│   └── npm-packages.md
└── development/                 # Contributing & CI/CD
    ├── contributing.md
    ├── testing.md
    └── ci-cd.md
```

---

## 🚀 Quick Start

**New user?** Start here:

1. [Choosing a Package](user-guide/choosing-a-package.md) - Find the right config for your organization
2. [Installation Guide](../README.md#installation) - Install Prism
3. [Creating Configurations](user-guide/creating-configurations.md) - Customize for your needs

---

## 📖 User Guide

Perfect for users and administrators configuring Prism for their teams.

### [Choosing a Package](user-guide/choosing-a-package.md)

Complete catalog of 7 pre-built configuration packages:

- 🏠 **Personal Dev** - Solo developers
- 🚀 **Startup** - Fast-moving teams (10-50)
- 🏢 **ACME Corp** - Small companies (100-1K)
- 🎯 **Consulting Firm** - Multi-client setups
- 🌐 **Fortune 500** - Enterprise (50K+)
- 🎓 **University** - Academic institutions
- 🌟 **Open Source** - Community projects

**Includes:** Decision tree, comparison matrix, installation commands

### [Creating Configurations](user-guide/creating-configurations.md)

Step-by-step guide to creating custom Prism packages:

- Package structure and organization
- Configuration files (package.yaml, base/, orgs/, teams/)
- User info fields
- Tools and repositories
- Branding and assets
- Publishing to NPM

**Perfect for:** Creating company-specific configurations

### [Config Inheritance](user-guide/config-inheritance.md)

Deep dive into configuration merging and hierarchy:

- How configs merge (base → org → team)
- Merge rules for scalars, arrays, objects
- Override strategies
- Conflict resolution
- Examples and visualizations

**Perfect for:** Understanding multi-level configurations

### [Custom Registries](user-guide/custom-registries.md)

Setting up private NPM registries:

- Corporate package registries
- Authentication and security
- Hosting your own registry
- Integration with Prism

**Perfect for:** Enterprise deployments

---

## 📚 Reference Documentation

Technical specifications and API details.

### [Configuration Schema](reference/configuration-schema.md)

Complete YAML schema reference:

- All available fields and types
- User info field types (text, email, select, number, checkbox)
- Tools configuration (simple & complex)
- Repositories configuration
- Security and compliance
- Validation rules
- Examples

**Perfect for:** Writing and validating configurations

### [Package System](reference/package-system.md)

Technical deep-dive into the package system:

- Package structure and format
- Metadata and manifests
- Loading and validation
- Merge algorithms
- NPM integration

**Perfect for:** Advanced customization and troubleshooting

### [NPM Packages](reference/npm-packages.md)

Publishing configurations to NPM:

- package.json requirements
- Publishing workflow
- Versioning strategy
- Private registries
- Installation from NPM

**Perfect for:** Distributing configurations

---

## 💻 Development Documentation

For contributors and maintainers.

### [Contributing](development/contributing.md)

How to contribute to Prism:

- Development setup
- Code style and standards
- Commit conventions
- PR workflow
- Code review process
- Release process

**Perfect for:** Open source contributors

### [Testing](development/testing.md)

Comprehensive testing guide:

- Test types (unit, CLI, E2E, integration)
- Running tests (Makefile commands)
- Playwright dashboards and trace viewer
- Writing tests (templates and best practices)
- Coverage reports
- CI integration
- Debugging

**Perfect for:** Testing new features

### [CI/CD Pipeline](development/ci-cd.md)

Complete CI/CD automation:

- GitHub Actions workflows (4 workflows)
- Branch protection rules
- Development workflow (dev → stage → main)
- Release process
- Makefile commands (40+ commands)
- Monitoring and troubleshooting

**Perfect for:** Setting up automation

---

## 🎯 Common Tasks

### I want to...

**Choose a package for my team**
→ [Choosing a Package](user-guide/choosing-a-package.md)

**Create a custom configuration**
→ [Creating Configurations](user-guide/creating-configurations.md)

**Understand how configs merge**
→ [Config Inheritance](user-guide/config-inheritance.md)

**Validate my package.yaml**
→ [Configuration Schema](reference/configuration-schema.md)

**Publish to NPM**
→ [NPM Packages](reference/npm-packages.md)

**Set up CI/CD**
→ [CI/CD Pipeline](development/ci-cd.md)

**Run tests**
→ [Testing](development/testing.md)

**Contribute code**
→ [Contributing](development/contributing.md)

---

## 🌟 Feature Highlights

### Multi-Level Hierarchy

```
Company
└── Engineering (org)
    └── Platform Team
```

Base configs → org overrides → team overrides  
[Learn more](user-guide/config-inheritance.md)

### 7 Pre-Built Packages

From solo developers to Fortune 500 enterprises.  
[See all packages](user-guide/choosing-a-package.md)

### Beautiful Web UI

5 themes, real-time progress, responsive design.  
[See screenshots](../README.md#features)

### NPM Integration

Distribute configs via npm: `npm install @prism/my-config`  
[Learn more](reference/npm-packages.md)

### Comprehensive Testing

72 tests (unit + CLI + E2E), >80% coverage, Playwright traces.  
[Learn more](development/testing.md)

### Full CI/CD

4 GitHub Actions workflows, 3 environments, automated releases.  
[Learn more](development/ci-cd.md)

---

## 📊 Documentation Stats

- **9 documents** (3 user guide, 3 reference, 3 development)
- **3 categories** (getting started, technical, contributing)
- **40+ Makefile commands** documented
- **72 tests** described
- **7 packages** cataloged

---

## 🔗 External Resources

### Project Links

- **GitHub**: [github.com/andersonwilliam85/prism](https://github.com/andersonwilliam85/prism)
- **Issues**: [Report bugs or request features](https://github.com/andersonwilliam85/prism/issues)
- **Discussions**: [Ask questions](https://github.com/andersonwilliam85/prism/discussions)

### Related Documentation

- **Main README**: [../README.md](../README.md) - Project overview
- **Makefile**: [../Makefile](../Makefile) - All 40+ commands
- **CONTRIBUTING**: [development/contributing.md](development/contributing.md) - How to contribute

---

## 🤝 Contributing

Found a documentation issue? Want to improve docs?

1. **Documentation bugs**: [Open an issue](https://github.com/andersonwilliam85/prism/issues/new)
2. **Documentation improvements**: Submit a PR!
3. **Questions**: [Start a discussion](https://github.com/andersonwilliam85/prism/discussions)

See [Contributing Guide](development/contributing.md) for details.

---

## 📝 Documentation Style Guide

When writing or updating documentation:

- ✅ Use clear, concise language
- ✅ Include code examples
- ✅ Add emoji for visual hierarchy (sparingly!)
- ✅ Cross-link related docs
- ✅ Keep examples up-to-date
- ✅ Test all commands before documenting

---

## 🎓 Learning Path

### Beginner

1. [Main README](../README.md) - What is Prism?
2. [Choosing a Package](user-guide/choosing-a-package.md) - Pick a package
3. Install and run! 🚀

### Intermediate

1. [Creating Configurations](user-guide/creating-configurations.md) - Custom configs
2. [Config Inheritance](user-guide/config-inheritance.md) - Advanced merging
3. [Configuration Schema](reference/configuration-schema.md) - All options

### Advanced

1. [Package System](reference/package-system.md) - System internals
2. [NPM Packages](reference/npm-packages.md) - Distribution
3. [Contributing](development/contributing.md) - Join development

### Maintainer

1. [Testing](development/testing.md) - Test suite
2. [CI/CD Pipeline](development/ci-cd.md) - Automation
3. [Custom Registries](user-guide/custom-registries.md) - Enterprise

---

## 🚀 Next Steps

**Ready to get started?**

```bash
# Install Prism
git clone https://github.com/andersonwilliam85/prism.git
cd prism

# Quick start
make dev

# Open browser to http://localhost:5555
# Select a package and follow prompts!
```

**Questions?** Check out:
- [FAQ](../README.md#faq)
- [Troubleshooting](development/testing.md#troubleshooting)
- [GitHub Discussions](https://github.com/andersonwilliam85/prism/discussions)

---

**Last updated:** 2025-01-XX  
**Version:** 1.0.0  
**Documentation coverage:** 100% ✨
