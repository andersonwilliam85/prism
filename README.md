# 🐶 Walmart Dev Environment Setup

**One-command setup for a production-ready development environment!**

## What This Does

Sets up a complete, standardized dev environment with:

✅ **Organized folder structure** (projects, experiments, learning, tooling)  
✅ **Essential dev tools** (Git, Rancher Desktop, Skaffold, Python, Node.js, Azure CLI, GCloud, etc.)  
✅ **Git global config** + **SSH key generation**  
✅ **Documentation server** (MkDocs with Walmart branding, auto-scans your projects)  
✅ **Career management system** (goals, wins, 1-on-1s, performance review prep)  
✅ **Progress tracking** (resume setup anytime, see what's done)  
✅ **CLI tools** (new-project, archive-project, find-project)  
✅ **Optional: Code Puppy** (AI coding assistant)  

## Supported Platforms

- ✅ macOS (Intel & Apple Silicon)
- ✅ Windows 10/11
- ✅ Ubuntu 20.04+

## Prerequisites

**Python 3.9+** (usually pre-installed on Mac/Ubuntu, download for Windows)

Check: `python3 --version` or `python --version`

## Quick Start

### 1. Download this package

```bash
# If you have git:
git clone https://github.com/walmart/dev-setup.git
cd walmart-dev-setup

# Or download and extract the ZIP
```

### 2. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Run the installer

```bash
python3 install.py
```

The installer will:
- Detect your OS
- Walk you through interactive setup
- Install selected tools
- Configure everything
- Generate onboarding docs

**Estimated time:** 10-15 minutes (depending on downloads)

## What Happens During Setup

The installer will:

1. **🔍 Detect your platform** (Mac/Windows/Ubuntu)
2. **💬 Collect your info** (name, email, team)
3. **📦 Install package manager** (brew/winget/apt if needed)
4. **🛠️ Install selected tools** (git, kubectl, etc.)
5. **⚙️ Configure git globally**
   - Set user.name and user.email
   - Add useful aliases (co, br, st, etc.)
   - Configure default branch (main)
6. **🔐 Generate SSH key** (ed25519)
   - Saves to ~/.ssh/id_ed25519
   - Shows public key to add to GitHub/GitLab
7. **📁 Create folder structure** (~/Development/*)
8. **🎯 Configure tools** (Maven, npm, pip with Walmart repos)
9. **📚 Build & launch docs server**
   - Auto-generates docs from your environment
   - Opens in browser at http://localhost:8000
   - Career dashboard ready to use!
10. **✅ Show next steps**

**Progress is saved** after each step - you can resume anytime!

## What Gets Installed

### Core Tools (Recommended)

| Tool | Purpose | Mac | Windows | Ubuntu |
|------|---------|-----|---------|--------|
| **Git** | Version control | brew | winget | apt |
| **Rancher Desktop** | Kubernetes (Docker alternative) | brew | installer | deb |
| **Skaffold** | K8s dev workflow | brew | chocolatey | binary |
| **Python 3.11+** | Backend development | brew | winget | apt |
| **Node.js 20 LTS** | Frontend development | brew | winget | nvm |

### Optional Tools

| Tool | Purpose | Status |
|------|---------|--------|
| **Code Puppy** | AI coding assistant | Available at puppy.walmart.com |

## Folder Structure Created

```
~/Development/
├── projects/          # Active team/assigned projects
├── experiments/       # POCs, spike work, testing ideas
├── learning/          # Courses, tutorials, skill-building
├── opensource/        # OSS contributions
├── tooling/           # Dev productivity tools & scripts
│   └── dev-docs-server/  # Documentation + Career tracking
├── archive/           # Completed/shelved work (by quarter)
└── docs/              # Cross-project documentation
```

## Post-Install Usage

### Start Documentation Server

```bash
cd ~/Development/tooling/dev-docs-server
./start-docs-server

# Or use the shortcut:
start-docs-server

# Opens at: http://localhost:8000
```

The docs server auto-scans your `~/Development/` folder and generates:
- Project listings with git status
- README previews
- Architecture docs (if present)
- Full-text search across all docs
- **Career dashboard** (goals, wins, 1-on-1 notes)

### Career Management

Your docs server includes a built-in career tracking system:

**Access it at:** http://localhost:8000/career/

#### Track Your Wins

Edit `~/Development/tooling/dev-docs-server/config/user-profile.yaml`:

```yaml
career:
  wins:
    - title: "Shipped Supplier Receiving System"
      date: "2026-03-05"
      description: "Built VBD architecture with K8s deployment"
      impact: "Reduced processing time by 40%"
      evidence: "https://github.walmart.com/myteam/supplier-receiving"
      tags: ["technical", "architecture", "kubernetes"]
```

Then refresh your docs - the win appears automatically!

#### Set Goals

```yaml
career:
  goals:
    short_term:
      - goal: "Master Kubernetes deployments"
        target_date: "2026-06-30"
        status: "in_progress"
        progress: 60
        notes: "Completed Skaffold training, building 3rd K8s project"
```

#### Log 1-on-1 Notes

```yaml
career:
  one_on_ones:
    - date: "2026-03-05"
      with: "Manager Name"
      topics: ["Q1 goals", "Promotion discussion"]
      action_items:
        - "Complete architecture certification"
        - "Lead next sprint planning"
      feedback_received: "Excellent work on supplier system"
```

#### Track Learning

```yaml
career:
  learning:
    courses_in_progress:
      - title: "Advanced Kubernetes"
        platform: "Udemy"
        progress: 75
        target_completion: "2026-04-01"
```

All of this data appears in your **Career Dashboard** for easy access!

### Create Projects

For now, manually create projects in the appropriate folder:

```bash
cd ~/Development/projects
mkdir my-new-api
cd my-new-api
git init
```

Your docs server will auto-discover it within 5 minutes!

### Archive Old Projects

```bash
archive-project old-dashboard

# Moves to: ~/Development/archive/2026-Q1/old-dashboard/
```

### Find Projects

```bash
find-project supplier

# Searches across all non-archived folders
```

## Rancher Desktop Configuration

The installer configures Rancher Desktop with:
- **Kubernetes**: v1.28.5 (or latest stable)
- **Container Runtime**: containerd (Docker-compatible)
- **Resources**: 8GB RAM, 4 CPUs (adjustable)

**Why Rancher over Docker Desktop?**
- Free for enterprise use
- Includes Kubernetes built-in
- Lighter weight
- Better K8s dev experience

## Skaffold Workflow

All K8s templates come with `skaffold.yaml` configured:

```bash
cd ~/Development/projects/my-app

# Development mode (hot reload)
skaffold dev

# One-time deploy
skaffold run

# Clean up
skaffold delete
```

## Customization

### Change Folder Structure

Edit `config/folder-structure.yaml` before running installer:

```yaml
root: ~/Development
folders:
  - projects
  - experiments
  - my-custom-folder  # Add your own!
```

### Add Custom Tools

Edit `config/tools.yaml`:

```yaml
tools:
  my-cli:
    description: "My custom CLI tool"
    mac:
      method: brew
      package: my-cli
    windows:
      method: winget
      package: MyCompany.MyCLI
```

### Skip Interactive Prompts

Create `.installer-config.yaml` with your preferences:

```yaml
dev_folder: ~/Development
tools:
  git: true
  rancher: true
  skaffold: true
  code_puppy: false
templates:
  - python-fastapi-vbd
  - react-walmart-ui
```

Then run: `python3 install.py --config .installer-config.yaml`

## Troubleshooting

### Check Setup Progress

```bash
python3 install.py --status

# Shows:
# ✅ Completed tasks
# ⏳ Pending tasks
# Timestamps for each step
```

### Resume Interrupted Setup

```bash
python3 install.py --resume

# Picks up where you left off!
# Progress is saved after each major step
```

### "Python not found"

**Mac/Ubuntu:**
```bash
python3 --version  # Try with '3'
```

**Windows:**
- Install from https://python.org
- Or use Microsoft Store version

### "Permission denied" on Mac/Ubuntu

```bash
sudo python3 install.py  # May need sudo for some installs
```

### Rancher Desktop won't start

1. Check system requirements (8GB+ RAM)
2. Ensure virtualization is enabled (BIOS setting)
3. On Windows: Enable WSL2

### Skaffold can't connect to cluster

```bash
# Verify Rancher is running
kubectl cluster-info

# Should show: Kubernetes control plane is running at...
```

## Uninstall

```bash
python3 install.py --uninstall

# Removes:
# - Installed tools (asks for confirmation)
# - CLI scripts from PATH
# - Does NOT remove ~/Development (your projects are safe!)
```

## Team Onboarding

### Package This for Your Team

```bash
# 1. Customize the config files
edit config/preferences.yaml
edit config/tools.yaml

# 2. Add your team's templates
cp -r my-company-template templates/

# 3. Create distributable package
./scripts/package.sh

# Creates: walmart-dev-setup-v1.0.0.zip
```

### Share with Team

**Option 1: Git repo (internal GitHub)**
```bash
git clone https://github.walmart.com/your-team/dev-setup.git
cd dev-setup
python3 install.py
```

**Option 2: ZIP file**
1. Download `walmart-dev-setup-v1.0.0.zip`
2. Extract and run `python3 install.py`

**Option 3: Confluence + SharePoint**
- Attach ZIP to Confluence page
- Link in team onboarding docs

## Contributing

Want to improve this installer?

1. Fork the repo
2. Make changes
3. Test on your platform
4. Submit PR with description

## Support

- **Slack**: #dev-environment-setup
- **Teams**: [Dev Tools Team](https://teams.microsoft.com/...)
- **Docs**: http://localhost:8000 (after setup)

## What's Next?

After setup completes, you'll see:

```
╔══════════════════════════════════════════════════════════╗
║                    🎉 Setup Complete! 🎉                 ║
╚══════════════════════════════════════════════════════════╝

🚀 Your development environment is ready!

📁 Folder structure:  ~/Development/
🔑 SSH key generated: ~/.ssh/id_ed25519.pub
📖 Docs server:       http://localhost:8000

═══════════════════════════════════════════════════════════

📋 Next Steps:

1. Add your SSH key to GitHub Enterprise:
   • Copy: ~/.ssh/id_ed25519.pub
   • Add at: https://github.walmart.com/settings/keys

2. Your documentation server is running!
   • Access at: http://localhost:8000
   • Bookmark the Career Dashboard: /career/

3. Start a project:
   cd ~/Development/projects
   mkdir my-first-project
   cd my-first-project
   git init
   
4. Track your first win:
   • Visit: http://localhost:8000/career/
   • Edit: ~/Development/tooling/dev-docs-server/config/user-profile.yaml
   • Add your accomplishment!

5. Optional: Install Code Puppy
   • Visit: https://puppy.walmart.com
   • AI coding assistant

═══════════════════════════════════════════════════════════

💡 Pro Tips:

• Run `start-docs-server` anytime to launch your docs
• Check progress: `python3 install.py --status`
• Your docs auto-refresh every 5 minutes
• Log wins regularly - great for performance reviews!

═══════════════════════════════════════════════════════════
```

Your browser will automatically open to your new documentation site!

---

## After Setup, check out:

1. **Documentation Homepage**: http://localhost:8000
2. **Career Dashboard**: http://localhost:8000/career/
3. **Onboarding docs**: `~/Development/docs/onboarding/`
4. **User profile config**: `~/Development/tooling/dev-docs-server/config/user-profile.yaml`

---

**Happy coding! 🚀**
🚀**
