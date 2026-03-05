# 💎 Prism

**Refract complexity into clarity**

*One-command setup for production-ready development environments*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)](https://github.com/andersonwilliam85/prism)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/andersonwilliam85/prism/actions)
[![Coverage](https://img.shields.io/badge/coverage-%3E90%25-brightgreen.svg)](https://github.com/andersonwilliam85/prism)

---

## The Problem

Setting up a new development machine is painful:

- ❌ Installing dozens of tools manually
- ❌ Remembering all the configuration steps
- ❌ Inconsistent environments across teams
- ❌ Lost productivity on day 1 (and beyond)
- ❌ No standardization = chaos

**I kept running into this.** Every new machine, every new project, every new team member - the same tedious setup over and over.

So I built **Prism**.

---

## The Solution

```bash
# Clone
git clone https://github.com/andersonwilliam85/prism.git
cd prism

# Run
python3 install.py

# Done! 🌈
```

**That's it.** One command gives you:

✔ **Beautiful Web UI** (visual package selection, step-by-step wizard, live progress)  
✔ **OR CLI installer** (if you prefer the terminal)  
✔ **Organized folder structure** (projects, experiments, learning, tooling)  
✔ **Essential dev tools** (Git, Docker, Python, Node.js, cloud CLIs, etc.)  
✔ **Git global config** + **SSH key generation**  
✔ **Documentation server** (MkDocs with branding, auto-scans your projects)  
✔ **Career management** (goals, wins, 1-on-1s, performance review prep)  
✔ **Progress tracking** (resume anytime, see what's done)  
✔ **CLI tools** (new-project, archive-project, find-project)  
✔ **Configurable packages** (company-specific, personal, open source)

---

## Why Prism?

### 🔬 **Scientific Precision**

Like a prism refracts white light into a rainbow, Prism takes complex setup chaos and transforms it into organized clarity.

### 🌈 **Beautiful Structure**

Your workspace isn't just functional - it's *beautiful*. Organized, documented, ready to impress.

### 💡 **Illuminating**

Never wonder "where did I put that?" or "how do I configure this?" again. Everything has its place.

### ✨ **Extensible**

Built with a package system. Use built-in configs or create your own. Personal, startup, enterprise - Prism adapts.

---

## Features

### 🌐 **Web UI Installer**

Gorgeous visual setup experience:

- **Package Gallery** - Browse configs with beautiful cards
- **Visual Wizard** - Step-by-step guided setup
- **Registry Configuration** - Support for corporate/custom npm registries
- **Live Progress** - Watch installation in real-time
- **Responsive Design** - Works on any screen size
- **Smart Validation** - Prevents configuration errors
- **Auto-launch** - Opens in your browser automatically

Launch with:
```bash
python3 install-ui.py
# or use the convenience script
./start_web_ui.sh
```

Opens automatically at: **http://localhost:5555**

### 💻 **CLI Installer**

Prefer the terminal?

- **Interactive Prompts** - Guided questions
- **Non-interactive Mode** - Use config files
- **Resume Capability** - Pick up where you left off
- **Status Checking** - See what's installed
- **Scriptable** - Automate deployments

Run with: `python3 install.py`

### 📁 **Smart Folder Structure**

```
~/Development/
├── projects/          # Active work
├── experiments/       # POCs, testing
├── learning/          # Tutorials, courses
├── tooling/           # Custom scripts
└── archive/           # Completed projects

~/Documentation/       # Auto-generated docs site
~/Career/              # Goals, wins, reviews
```

### 🛠️ **Tool Installation**

Automatically installs:
- Git, GitHub CLI
- Docker / Rancher Desktop
- Python, Node.js, Go
- Cloud CLIs (AWS, Azure, GCP)
- Kubernetes tools (kubectl, helm, skaffold)
- Editor configs (VS Code, Cursor, Zed)
- And more...

### 🎭 **Config Packages (via npm!)**

Choose from pre-built configurations published on npm:

- **@prism/personal-dev-config** - For freelancers & indie devs
- **@prism/startup-config** - Fast, lean, flexible
- **@prism/fortune500-config** - Enterprise-ready
- **@prism/university-config** - Research & teaching
- **@prism/opensource-config** - Community projects
- **@prism/consulting-config** - Multi-client setups
- **@prism/acme-corp-config** - Template for your company

**Packages are fetched from npm** (via unpkg CDN) automatically!  
No npm installation required. Works offline with local fallback.

**Custom Registry Support:**  
Use your own npm registry for corporate/air-gapped environments:

```bash
# Use custom registry
python3 install.py --npm-registry https://npm.mycompany.com

# Or set environment variable
export PRISM_NPM_REGISTRY=https://npm.mycompany.com
python3 install.py
```

See [Custom Registry Documentation](docs/CUSTOM_REGISTRY.md) for details.

### 📝 **Career Management**

Built-in tools for:
- Goal tracking
- Win logging (brag document)
- 1-on-1 prep
- Performance review material
- Resume updates

### 📊 **Progress Tracking**

Resume anytime:
```bash
python3 install.py --status   # See what's done
python3 install.py --resume   # Continue where you left off
```

---

## Installation Methods

### Prerequisites

- **Python 3.9+** (usually pre-installed on Mac/Linux)
- **Internet connection**
- **Flask** (for web UI - auto-installs if missing)

### 🌐 Web UI Installer (Recommended)

Beautiful, visual setup experience:

```bash
# 1. Clone the repo
git clone https://github.com/andersonwilliam85/prism.git
cd prism

# 2. Launch the web installer
python3 web_installer.py

# 3. Open your browser
# Automatically opens http://localhost:5000

# 4. Follow the visual wizard!
```

**Web UI Features:**

✨ **Package Selection** - Beautiful cards showing all available packages  
📋 **Step-by-Step Wizard** - Clear progress through 7 steps  
👤 **User Info** - Name, email, GitHub username  
🏢 **Organization Setup** - Department/team selection (if applicable)  
🛠️ **Tool Selection** - Visual checkboxes for tools to install  
✅ **Confirmation** - Review before installing  
📊 **Live Progress** - Real-time installation updates  
🎉 **Completion** - Success screen with next steps

### 💻 CLI Installer (Classic)

Prefer the terminal? No problem:

```bash
# 1. Clone the repo
git clone https://github.com/andersonwilliam85/prism.git
cd prism

# 2. Run the CLI installer
python3 install.py

# 3. Follow the prompts
# Choose your package, confirm settings, let it run

# 4. Done!
```

### Advanced Usage

#### Web UI Options

```bash
# Custom port
python3 web_installer.py --port 8080

# Debug mode
python3 web_installer.py --debug

# Specify host
python3 web_installer.py --host 0.0.0.0
```

#### CLI Options

```bash
# Non-interactive (use config file)
python3 install.py --config my-config.yaml

# Resume from checkpoint
python3 install.py --resume

# Check progress
python3 install.py --status

# Install specific package
python3 install.py --package personal-dev-config
```

---

## Screenshots

### Web UI Installer

**Package Selection:**
![Package Selection](assets/screenshots/package-selection.png)

Choose from personal, startup, enterprise, university, consulting, or open source configs.

**User Setup:**
![User Setup](assets/screenshots/user-setup.png)

Enter your details once, used throughout the setup.

**Tool Selection:**
![Tool Selection](assets/screenshots/tool-selection.png)

Pick exactly what you need - no bloat!

**Live Progress:**
![Installation Progress](assets/screenshots/progress.png)

Watch as Prism builds your perfect dev environment.

*(Screenshots coming soon - repo is brand new!)*

---

## Supported Platforms

- ✅ **macOS** (Intel & Apple Silicon)
- ✅ **Windows** 10/11
- ✅ **Linux** (Ubuntu 20.04+, Debian, Fedora)

---

## Package System

### Distributed via npm

All Prism config packages are published to **npm public registry** under the `@prism` scope!

**Benefits:**
- ✅ **No custom registry** - Uses public npm infrastructure
- ✅ **CDN delivery** - Fast global distribution via unpkg.com
- ✅ **No npm required** - Prism fetches packages directly from CDN
- ✅ **Versioned** - Semantic versioning built-in
- ✅ **Discoverable** - Searchable on npmjs.com
- ✅ **Offline fallback** - Local packages work too

### Browsing Packages

```bash
# List available packages (fetches from npm)
python3 scripts/npm_package_fetcher.py list

# Search on npm
npm search @prism

# Browse on npmjs.com
https://www.npmjs.com/search?q=%40prism
```

### Using Built-in Packages

Prism includes 7 pre-configured packages:

```bash
python3 scripts/package_manager.py list
```

### Creating Your Own

```bash
# Use the template
cp -r config-packages/acme-corp config-packages/my-company
cd config-packages/my-company

# Edit package.yaml
vim package.yaml

# Validate
python3 ../../scripts/package_manager.py validate my-company

# Install
python3 install.py --package my-company
```

See [Package Documentation](docs/CREATING_PACKAGES.md) for details.

---

## Configuration

### Package Structure

```yaml
# package.yaml
package:
  name: "my-company"
  version: "1.0.0"
  description: "My company dev environment"
  
  # NEW: Assets support!
  assets:
    logo: "assets/logo.png"
    colors: "assets/colors.yaml"
    
  branding:
    primary_color: "#4A90E2"
    secondary_color: "#9B59B6"
  
  tools:
    - git
    - docker
    - python
    - nodejs
    
  repositories:
    - url: "git@github.com:mycompany/backend.git"
      path: "~/Development/projects/backend"
```

Full schema: [docs/CONFIG_SCHEMA.md](docs/CONFIG_SCHEMA.md)

---

## CLI Tools

After installation, you get helpful commands:

```bash
# Create new project
new-project my-app

# Archive completed project
archive-project old-app

# Find projects
find-project search-term

# Launch docs site
mkdocs serve
```

---

## Documentation Server

Auto-generated docs with:

- 🏠 Homepage with project overview
- 📁 Auto-scanned project list
- 📚 Architecture diagrams (if present)
- 📝 README rendering
- 🎨 Custom branding (your logo, colors)

Launch: `mkdocs serve`  
Visit: `http://localhost:8000`

---

## The Story

I'm **Will Anderson**, and I kept hitting the same wall:

Every time I set up a new dev environment (new job, new machine, helping a teammate), I'd spend hours:

1. Installing tools I forgot about
2. Configuring git (again)
3. Generating SSH keys (again)
4. Creating folder structures
5. Cloning repos
6. Setting up docs

It was **tedious, error-prone, and wasteful**.

So one weekend, I started building a solution. Started with Claude Code helping me scaffold the basics. But I wanted more:

- **Standardized** - Everyone gets the same great setup
- **Extensible** - Works for solo devs AND Fortune 500
- **Beautiful** - Not just functional, *impressive*
- **Open source** - Everyone should benefit

Prism is the result. Built to solve my problem, shared to solve yours.

---

## Philosophy

### 💎 **Refract Complexity Into Clarity**

Complex setups become simple. Chaos becomes structure. Confusion becomes confidence.

### 🌈 **Beauty Through Structure**

Your dev environment should be as beautiful as the code you write.

### 💡 **Illuminate, Don't Dictate**

Prism provides structure but stays flexible. Use what you need, skip what you don't.

### ✨ **Open & Extensible**

Built on open principles. Fork it, extend it, make it yours.

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

### Ways to Help

- ⭐ Star the repo
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve docs
- 🎭 Create config packages
- 🔧 Submit PRs

---

## License

**MIT License** - See [LICENSE](LICENSE)

Copyright (c) 2025 William Anderson

---

## Acknowledgments

- Built with help from **Claude Code** (Anthropic)
- Inspired by frustration and necessity
- Made with ♥️ for developers everywhere

---

## Links

- **GitHub**: [github.com/andersonwilliam85/prism](https://github.com/andersonwilliam85/prism)
- **Issues**: [github.com/andersonwilliam85/prism/issues](https://github.com/andersonwilliam85/prism/issues)
- **Docs**: [Coming soon - GitHub Pages]
- **Packages**: [github.com/andersonwilliam85/prism-packages](https://github.com/andersonwilliam85/prism-packages)

---

## Support

Having issues? Found a bug?

1. Check [Issues](https://github.com/andersonwilliam85/prism/issues)
2. Search existing issues
3. Create a new issue with details

Pull requests welcome! 🚀

---

<p align="center">
  <strong>💎 Prism - Refract complexity into clarity</strong><br>
  Made with ♥️ by <a href="https://github.com/andersonwilliam85">William Anderson</a>
</p>
