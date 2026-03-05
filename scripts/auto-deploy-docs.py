#!/usr/bin/env python3
"""
Auto-Deploy Documentation Server

This script automatically builds and deploys your personal documentation server.
Fully standalone documentation generator!

Run after initial setup completes, or manually: python3 auto-deploy-docs.py
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime
import yaml

# Rich for beautiful output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Install 'rich' for better output: pip install rich")

console = Console() if RICH_AVAILABLE else None

def print_banner():
    """Print welcome banner"""
    if RICH_AVAILABLE:
        console.print(Panel(
            "[bold blue]📚 Documentation Server Setup[/bold blue]\n\n"
            "Building your personal knowledge base!\n"
            "This will auto-scan your ~/Development folder and create\n"
            "a searchable documentation site with career tracking.",
            title="🚀 Auto-Deploy",
            border_style="blue"
        ))
    else:
        print("\n" + "="*60)
        print("📚 Documentation Server Setup")
        print("Building your personal knowledge base!")
        print("="*60 + "\n")

def run_command(cmd, cwd=None, check=True):
    """Run shell command and return result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_dependencies():
    """Check if required dependencies are installed"""
    if RICH_AVAILABLE:
        console.print("\n[yellow]Checking dependencies...[/yellow]")
    else:
        print("\nChecking dependencies...")
    
    missing = []
    
    # Check Python
    success, stdout, _ = run_command("python3 --version", check=False)
    if not success:
        missing.append("python3")
    
    # Check pip
    success, stdout, _ = run_command("pip3 --version", check=False)
    if not success:
        missing.append("pip3")
    
    if missing:
        print(f"❌ Missing: {', '.join(missing)}")
        print("   Please install these first!")
        return False
    
    if RICH_AVAILABLE:
        console.print("[green]✅ All system dependencies found![/green]")
    else:
        print("✅ All system dependencies found!")
    
    return True

def install_python_packages():
    """Install required Python packages"""
    if RICH_AVAILABLE:
        console.print("\n[yellow]Installing Python packages...[/yellow]")
    else:
        print("\nInstalling Python packages...")
    
    packages = [
        "mkdocs-material",
        "pymdown-extensions",
        "mkdocs-mermaid2-plugin",
        "GitPython",
        "pyyaml",
        "watchdog"
    ]
    
    # Check if proxy configured in package (company-specific)
    env = os.environ.copy()
    # Proxy settings should come from package config, not hardcoded
    # if "proxy" in config:
    #     env["HTTP_PROXY"] = config["proxy"]["http"]
    #     env["HTTPS_PROXY"] = config["proxy"]["https"]
    
    cmd = f"pip3 install {' '.join(packages)} --quiet"
    success, stdout, stderr = run_command(cmd, check=False)
    
    if not success:
        print(f"❌ Failed to install packages: {stderr}")
        print("   Try manually: pip3 install mkdocs-material pymdown-extensions")
        return False
    
    if RICH_AVAILABLE:
        console.print("[green]✅ Python packages installed![/green]")
    else:
        print("✅ Python packages installed!")
    
    return True

def load_user_profile():
    """Load user profile from config"""
    config_path = Path(__file__).parent.parent / "config" / "user-profile.yaml"
    
    if not config_path.exists():
        return {"user": {"name": "Developer", "email": ""}}
    
    with open(config_path) as f:
        return yaml.safe_load(f)

def load_resources():
    """Load company resources from config"""
    resources_path = Path(__file__).parent.parent / "config" / "resources.yaml"
    
    if not resources_path.exists():
        return {"company": {"name": "Company"}, "resources": {}}
    
    with open(resources_path) as f:
        return yaml.safe_load(f)

def setup_docs_structure():
    """Create documentation folder structure"""
    if RICH_AVAILABLE:
        console.print("\n[yellow]Setting up docs structure...[/yellow]")
    else:
        print("\nSetting up docs structure...")
    
    dev_root = Path.home() / "Development"
    docs_server = dev_root / "tooling" / "dev-docs-server"
    
    # Create directories
    directories = [
        docs_server / "docs",
        docs_server / "docs" / "projects",
        docs_server / "docs" / "experiments",
        docs_server / "docs" / "learning",
        docs_server / "docs" / "career",
        docs_server / "overrides" / "assets" / "stylesheets",
        docs_server / "plugins",
        docs_server / "scripts",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    if RICH_AVAILABLE:
        console.print("[green]✅ Docs structure created![/green]")
    else:
        print("✅ Docs structure created!")
    
    return docs_server

def generate_index_page(docs_server, user_profile, resources_config, welcome_config):
    """Generate homepage for docs using configurable welcome content"""
    user_name = user_profile.get("user", {}).get("name", "Developer")
    company_name = welcome_config.get("company", {}).get("name", "Company")
    
    # Welcome content from config
    welcome = welcome_config.get("welcome", {})
    title = welcome.get("title", "Welcome to Your Dev Environment")
    subtitle = welcome.get("subtitle", "Your development environment is ready!")
    hero_message = welcome.get("hero_message", "This is your personal knowledge base.")
    
    # Getting Started section
    getting_started_html = ""
    getting_started = welcome.get("getting_started", {})
    if getting_started:
        getting_started_html = f"\n## {getting_started.get('title', '🎯 Getting Started')}\n\n"
        for item in getting_started.get("items", []):
            icon = item.get("icon", "•")
            text = item.get("text", "")
            link = item.get("link", "")
            if link:
                getting_started_html += f"- {icon} [{text}]({link})\n"
            else:
                getting_started_html += f"- {icon} {text}\n"
    
    # Quick Tips section
    quick_tips_html = ""
    quick_tips = welcome.get("quick_tips", {})
    if quick_tips:
        quick_tips_html = f"\n## {quick_tips.get('title', '💡 Pro Tips')}\n\n"
        for item in quick_tips.get("items", []):
            tip_type = item.get("type", "tip")
            text = item.get("text", "")
            link = item.get("link", "")
            
            # Map type to admonition style
            admonition_map = {
                "critical": "danger",
                "tip": "tip",
                "success": "success",
                "info": "info",
                "warning": "warning"
            }
            admonition = admonition_map.get(tip_type, "tip")
            
            if link:
                quick_tips_html += f'!!! {admonition}\n    {text} [Learn more]({link})\n\n'
            else:
                quick_tips_html += f'!!! {admonition}\n    {text}\n\n'
    
    # Build resource links sections
    resource_sections = ""
    for category, items in resources_config.get("resources", {}).items():
        section_title = category.replace("_", " ").title()
        resource_sections += f"\n### {section_title}\n\n"
        
        for item in items:
            icon = item.get("icon", "🔗")
            name = item.get("name", "")
            url = item.get("url", "#")
            desc = item.get("description", "")
            
            resource_sections += f"- **{icon} [{name}]({url})** - {desc}\n"
    
    index_content = f"""# Welcome to Your Dev Environment Docs

**{user_name}'s Personal Knowledge Base**

---

## 🚀 Quick Links

<div class="grid cards" markdown>

-   :material-folder-open: **Projects**

    ---

    Active work, team projects, and completed initiatives

    [:octicons-arrow-right-24: Browse Projects](projects/index.md)

-   :material-flask: **Experiments**

    ---

    POCs, spike work, and technical explorations

    [:octicons-arrow-right-24: View Experiments](experiments/index.md)

-   :material-school: **Learning**

    ---

    Courses, tutorials, and skill development

    [:octicons-arrow-right-24: Learning Path](learning/index.md)

-   :material-trophy: **Career**

    ---

    Goals, wins, 1-on-1s, and professional growth

    [:octicons-arrow-right-24: Career Dashboard](career/index.md)

</div>

---

## 🔗 {company_name} Resources

{resource_sections}

---

## 📊 Environment Overview

**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

| Category | Count |
|----------|-------|
| Projects | *Auto-scanning...* |
| Experiments | *Auto-scanning...* |
| Learning | *Auto-scanning...* |

---

## 🎯 Recent Activity

*Auto-generated from your git activity*

---

## 💡 Quick Tips

!!! tip "Search Everything"
    Use the search bar (top right) to find anything across all your projects!

!!! info "Auto-Updates"
    This site auto-refreshes every 5 minutes to reflect new projects and docs.

!!! success "Career Tracking"
    Visit the [Career Dashboard](career/index.md) to log wins, track goals, and prep for 1-on-1s!
"""
    
    index_path = docs_server / "docs" / "index.md"
    index_path.write_text(index_content)
    
    return index_path

def generate_career_dashboard(docs_server, user_profile):
    """Generate career tracking page"""
    career_data = user_profile.get("career", {})
    
    career_content = f"""# 🎯 Career Dashboard

**Your Professional Growth Hub**

---

## 👤 Current Role

| Aspect | Details |
|--------|----------|
| **Title** | {career_data.get('role', {}).get('title', 'Not set')} |
| **Level** | {career_data.get('role', {}).get('level', 'Not set')} |
| **Team** | {career_data.get('role', {}).get('team', 'Not set')} |
| **Since** | {career_data.get('role', {}).get('start_date', 'Not set')} |

---

## 🎯 Goals

### Short-Term (This Quarter)

!!! note "Set Your Goals"
    Edit `~/Development/tooling/dev-docs-server/config/user-profile.yaml` to add goals!

*Goals will appear here once configured*

### Long-Term (1-2 Years)

*Goals will appear here once configured*

---

## 🏆 Recent Wins

!!! success "Track Your Accomplishments"
    Log wins regularly - they're invaluable for performance reviews!

*Wins will appear here once logged*

### How to Add a Win

```yaml
# In config/user-profile.yaml
career:
  wins:
    - title: "Shipped Supplier Receiving System"
      date: "2026-03-05"
      description: "Built VBD architecture system with K8s deployment"
      impact: "Reduced processing time by 40%"
            evidence: "https://github.com/yourteam/your-project"
      tags: ["technical", "architecture", "kubernetes"]
```

---

## 📚 Learning & Development

### Courses in Progress

*Courses will appear here once added*

### Skills to Develop

*Skills will appear here once configured*

---

## 🤝 1-on-1 Notes

!!! tip "Prepare for 1-on-1s"
    Keep running notes here to make meetings more productive!

*Meeting notes will appear here once logged*

---

## 📝 Performance Review Prep

*Review prep will appear here when configured*

---

## 🎓 Mentorship

### Mentors

*Mentors will appear here once configured*

### Mentees

*Mentees will appear here once configured*
"""
    
    career_path = docs_server / "docs" / "career" / "index.md"
    career_path.write_text(career_content)
    
    return career_path

def generate_mkdocs_config(docs_server, user_profile):
    """Generate mkdocs.yml configuration"""
    user_name = user_profile.get("user", {}).get("name", "Developer")
    
    config = f"""site_name: {user_name}'s Dev Docs
site_description: Personal development environment documentation

theme:
  name: material
  custom_dir: overrides/
  palette:
    - scheme: default
      primary: custom
      accent: custom
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: custom
      accent: custom
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - navigation.instant
    - search.suggest
    - search.highlight
    - search.share
    - content.code.copy
    - content.code.annotate
  icon:
    repo: fontawesome/brands/github

extra_css:
    - assets/stylesheets/company.css

extra_javascript:
    - assets/javascripts/theme-switcher.js

plugins:
  - search:
      lang: en
  - mermaid2:
      version: 10.6.0

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true
  - admonition
  - pymdownx.details
  - attr_list
  - md_in_html
  - pymdownx.emoji:
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
  - def_list
  - footnotes
  - tables

nav:
  - Home: index.md
  - Projects:
      - projects/index.md
  - Experiments:
      - experiments/index.md
  - Learning:
      - learning/index.md
  - Career:
      - career/index.md
"""
    
    config_path = docs_server / "mkdocs.yml"
    config_path.write_text(config)
    
    return config_path

def generate_company_css(docs_server):
    """Generate company-branded CSS with customizable themes"""
    css_content = """/* Prism Documentation Themes - Customizable Color Schemes */

/* Ocean Blue Theme (Default) */
:root {
  /* Ocean Blue Colors */
  --prism-primary: #0093E9;
  --prism-secondary: #80D0C7;
  --prism-accent: #009ffd;
  --prism-gradient-1: #0093E9;
  --prism-gradient-2: #80D0C7;
  --prism-gradient-3: #13547a;
  --prism-gradient-4: #009ffd;
  --prism-gradient-5: #2a2a72;
  
  /* MkDocs theme integration */
  --md-primary-fg-color: var(--prism-primary);
  --md-primary-fg-color--light: var(--prism-secondary);
  --md-primary-fg-color--dark: var(--prism-gradient-3);
  --md-accent-fg-color: var(--prism-accent);
  
  /* Background */
  --md-primary-bg-color: #ffffff;
  --md-default-bg-color: #fafafa;
  
  /* Text */
  --md-default-fg-color: #4a4a4a;
  --md-default-fg-color--light: #757575;
  
  /* Success/Error */
  --md-success-fg-color: #10b981;
  --md-error-fg-color: #ef4444;
  --md-warning-fg-color: #f59e0b;
}

/* Purple Haze Theme */
[data-prism-theme="purple"] {
  --prism-primary: #667eea;
  --prism-secondary: #764ba2;
  --prism-accent: #f093fb;
  --prism-gradient-1: #667eea;
  --prism-gradient-2: #764ba2;
  --prism-gradient-3: #f093fb;
  --prism-gradient-4: #4facfe;
  --prism-gradient-5: #00f2fe;
  
  --md-primary-fg-color: var(--prism-primary);
  --md-primary-fg-color--light: var(--prism-secondary);
  --md-primary-fg-color--dark: #4a5bb5;
  --md-accent-fg-color: var(--prism-accent);
}

/* Forest Green Theme */
[data-prism-theme="forest"] {
  --prism-primary: #134E5E;
  --prism-secondary: #71B280;
  --prism-accent: #56ab2f;
  --prism-gradient-1: #134E5E;
  --prism-gradient-2: #71B280;
  --prism-gradient-3: #56ab2f;
  --prism-gradient-4: #a8e063;
  --prism-gradient-5: #0f9b0f;
  
  --md-primary-fg-color: var(--prism-primary);
  --md-primary-fg-color--light: var(--prism-secondary);
  --md-primary-fg-color--dark: #0d3a47;
  --md-accent-fg-color: var(--prism-accent);
}

/* Sunset Orange Theme */
[data-prism-theme="sunset"] {
  --prism-primary: #f12711;
  --prism-secondary: #f5af19;
  --prism-accent: #ff6a00;
  --prism-gradient-1: #f12711;
  --prism-gradient-2: #f5af19;
  --prism-gradient-3: #ff6a00;
  --prism-gradient-4: #ee0979;
  --prism-gradient-5: #ff512f;
  
  --md-primary-fg-color: var(--prism-primary);
  --md-primary-fg-color--light: var(--prism-secondary);
  --md-primary-fg-color--dark: #c11f0e;
  --md-accent-fg-color: var(--prism-accent);
}

/* Midnight Dark Theme */
[data-prism-theme="midnight"] {
  --prism-primary: #2c3e50;
  --prism-secondary: #3498db;
  --prism-accent: #1abc9c;
  --prism-gradient-1: #2c3e50;
  --prism-gradient-2: #3498db;
  --prism-gradient-3: #34495e;
  --prism-gradient-4: #2980b9;
  --prism-gradient-5: #1abc9c;
  
  --md-primary-fg-color: var(--prism-primary);
  --md-primary-fg-color--light: var(--prism-secondary);
  --md-primary-fg-color--dark: #1a252f;
  --md-accent-fg-color: var(--prism-accent);
}

/* Dark mode overrides */
[data-md-color-scheme="slate"] {
  --md-primary-bg-color: #1a1a1a;
  --md-default-bg-color: #121212;
  --md-default-fg-color: #e0e0e0;
  --md-default-fg-color--light: #b0b0b0;
}

/* Custom header with gradient */
.md-header {
  background: linear-gradient(135deg, 
    var(--prism-gradient-1) 0%, 
    var(--prism-gradient-2) 50%, 
    var(--prism-gradient-3) 100%);
}

/* Gradient accent on hover */
.md-nav__link:hover {
  border-left: 3px solid var(--md-accent-fg-color);
}

.md-nav__link--active {
  border-left: 3px solid var(--md-primary-fg-color);
}

/* Card grid for homepage */
.grid.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.grid.cards > div {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, 
    rgba(0, 147, 233, 0.02) 0%, 
    rgba(128, 208, 199, 0.02) 100%);
}

[data-prism-theme="purple"] .grid.cards > div {
  background: linear-gradient(135deg, 
    rgba(102, 126, 234, 0.02) 0%, 
    rgba(240, 147, 251, 0.02) 100%);
}

[data-prism-theme="forest"] .grid.cards > div {
  background: linear-gradient(135deg, 
    rgba(19, 78, 94, 0.02) 0%, 
    rgba(113, 178, 128, 0.02) 100%);
}

[data-prism-theme="sunset"] .grid.cards > div {
  background: linear-gradient(135deg, 
    rgba(241, 39, 17, 0.02) 0%, 
    rgba(245, 175, 25, 0.02) 100%);
}

[data-prism-theme="midnight"] .grid.cards > div {
  background: linear-gradient(135deg, 
    rgba(44, 62, 80, 0.02) 0%, 
    rgba(52, 152, 219, 0.02) 100%);
}

.grid.cards > div:hover {
  border-color: var(--md-accent-fg-color);
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Theme Switcher (inject via JavaScript) */
.prism-theme-switcher {
  position: fixed;
  bottom: 20px;
  right: 20px;
  display: flex;
  gap: 8px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 8px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
}

.prism-theme-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.prism-theme-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.prism-theme-btn.active {
  box-shadow: 0 0 0 3px white, 0 0 0 5px var(--md-primary-fg-color);
  transform: scale(1.05);
}

.prism-theme-btn[data-theme="ocean"] {
  background: linear-gradient(135deg, #0093E9, #80D0C7);
}

.prism-theme-btn[data-theme="purple"] {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.prism-theme-btn[data-theme="forest"] {
  background: linear-gradient(135deg, #134E5E, #71B280);
}

.prism-theme-btn[data-theme="sunset"] {
  background: linear-gradient(135deg, #f12711, #f5af19);
}

.prism-theme-btn[data-theme="midnight"] {
  background: linear-gradient(135deg, #2c3e50, #3498db);
}

/* Smooth theme transitions */
:root,
[data-prism-theme],
.md-header,
.grid.cards > div {
  transition: background 0.5s ease, border-color 0.3s ease;
}
"""
    
    css_path = docs_server / "overrides" / "assets" / "stylesheets" / "company.css"
    css_path.write_text(css_content)
    
    return css_path

def generate_theme_switcher_js(docs_server):
    """Generate theme switcher JavaScript"""
    js_content = """// Prism Theme Switcher for MkDocs
(function() {
    'use strict';
    
    const themes = [
        { name: 'ocean', title: 'Ocean Blue' },
        { name: 'purple', title: 'Purple Haze' },
        { name: 'forest', title: 'Forest Green' },
        { name: 'sunset', title: 'Sunset Orange' },
        { name: 'midnight', title: 'Midnight Dark' }
    ];
    
    // Get saved theme or default to ocean
    const savedTheme = localStorage.getItem('prismDocsTheme') || 'ocean';
    
    // Apply theme on load
    function applyTheme(themeName) {
        document.documentElement.setAttribute('data-prism-theme', themeName);
    }
    
    // Create theme switcher UI
    function createThemeSwitcher() {
        const switcher = document.createElement('div');
        switcher.className = 'prism-theme-switcher';
        switcher.setAttribute('role', 'group');
        switcher.setAttribute('aria-label', 'Theme Switcher');
        
        themes.forEach(theme => {
            const btn = document.createElement('button');
            btn.className = 'prism-theme-btn';
            btn.setAttribute('data-theme', theme.name);
            btn.setAttribute('title', theme.title);
            btn.setAttribute('aria-label', theme.title + ' Theme');
            
            if (theme.name === savedTheme) {
                btn.classList.add('active');
            }
            
            btn.addEventListener('click', function() {
                const selectedTheme = this.getAttribute('data-theme');
                
                // Update theme
                applyTheme(selectedTheme);
                
                // Update active state
                document.querySelectorAll('.prism-theme-btn').forEach(b => {
                    b.classList.remove('active');
                });
                this.classList.add('active');
                
                // Save preference
                localStorage.setItem('prismDocsTheme', selectedTheme);
            });
            
            switcher.appendChild(btn);
        });
        
        document.body.appendChild(switcher);
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            applyTheme(savedTheme);
            createThemeSwitcher();
        });
    } else {
        applyTheme(savedTheme);
        createThemeSwitcher();
    }
})();
"""
    
    # Create javascripts directory
    js_dir = docs_server / "overrides" / "assets" / "javascripts"
    js_dir.mkdir(parents=True, exist_ok=True)
    
    js_path = js_dir / "theme-switcher.js"
    js_path.write_text(js_content)
    
    return js_path

def build_docs(docs_server):
    """Build the documentation site"""
    if RICH_AVAILABLE:
        console.print("\n[yellow]Building documentation site...[/yellow]")
    else:
        print("\nBuilding documentation site...")
    
    success, stdout, stderr = run_command("mkdocs build", cwd=docs_server, check=False)
    
    if not success:
        print(f"❌ Build failed: {stderr}")
        return False
    
    if RICH_AVAILABLE:
        console.print("[green]✅ Documentation built successfully![/green]")
    else:
        print("✅ Documentation built successfully!")
    
    return True

def start_docs_server(docs_server, open_browser=True):
    """Start the documentation server"""
    if RICH_AVAILABLE:
        console.print("\n[yellow]Starting documentation server...[/yellow]")
    else:
        print("\nStarting documentation server...")
    
    # Start server in background
    import webbrowser
    
    if RICH_AVAILABLE:
        console.print("\n[bold green]🎉 Documentation Server is Ready![/bold green]")
        console.print("\n📖 Access your docs at: [bold blue]http://localhost:8000[/bold blue]")
        console.print("\n[dim]Press Ctrl+C to stop the server[/dim]")
    else:
        print("\n🎉 Documentation Server is Ready!")
        print("\n📖 Access at: http://localhost:8000")
        print("\nPress Ctrl+C to stop the server")
    
    if open_browser:
        time.sleep(2)
        webbrowser.open("http://localhost:8000")
    
    # Start server (blocking)
    try:
        subprocess.run(["mkdocs", "serve"], cwd=docs_server)
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("\n[yellow]Server stopped[/yellow]")
        else:
            print("\nServer stopped")

def update_progress(task_name):
    """Update setup progress tracker"""
    config_path = Path(__file__).parent.parent / "config" / "user-profile.yaml"
    
    if not config_path.exists():
        return
    
    with open(config_path) as f:
        profile = yaml.safe_load(f)
    
    if "setup_progress" not in profile:
        profile["setup_progress"] = {"tasks": {}}
    
    if task_name not in profile["setup_progress"]["tasks"]:
        profile["setup_progress"]["tasks"][task_name] = {}
    
    profile["setup_progress"]["tasks"][task_name]["completed"] = True
    profile["setup_progress"]["tasks"][task_name]["timestamp"] = datetime.now().isoformat()
    profile["setup_progress"]["last_updated"] = datetime.now().isoformat()
    
    with open(config_path, 'w') as f:
        yaml.dump(profile, f, default_flow_style=False, sort_keys=False)

def main():
    """Main deployment function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Install Python packages
    if not install_python_packages():
        sys.exit(1)
    
    update_progress("install_mkdocs_dependencies")
    
    # Load user profile
    user_profile = load_user_profile()
    
    # Load resources and welcome config
    resources_config = load_resources()
    welcome_config = load_welcome_config()
    
    # Setup docs structure
    docs_server = setup_docs_structure()
    update_progress("create_docs_structure")
    
    # Generate pages
    if RICH_AVAILABLE:
        console.print("\n[yellow]Generating documentation pages...[/yellow]")
    else:
        print("\nGenerating documentation pages...")
    
    generate_index_page(docs_server, user_profile, resources_config, welcome_config)
    generate_career_dashboard(docs_server, user_profile)
    generate_mkdocs_config(docs_server, user_profile)
    generate_company_css(docs_server)
    generate_theme_switcher_js(docs_server)
    
    # Create placeholder pages
    (docs_server / "docs" / "projects" / "index.md").write_text("# Projects\n\n*Auto-scanning your projects...*")
    (docs_server / "docs" / "experiments" / "index.md").write_text("# Experiments\n\n*Auto-scanning your experiments...*")
    (docs_server / "docs" / "learning" / "index.md").write_text("# Learning\n\n*Auto-scanning your learning materials...*")
    
    if RICH_AVAILABLE:
        console.print("[green]✅ Pages generated![/green]")
    else:
        print("✅ Pages generated!")
    
    update_progress("generate_initial_docs")
    
    # Build docs
    if not build_docs(docs_server):
        sys.exit(1)
    
    update_progress("build_docs_site")
    
    # Mark overall setup as complete
    config_path = Path(__file__).parent.parent / "config" / "user-profile.yaml"
    if config_path.exists():
        with open(config_path) as f:
            profile = yaml.safe_load(f)
        
        if "setup_progress" in profile:
            profile["setup_progress"]["tasks"]["setup_docs_server"]["completed"] = True
            profile["setup_progress"]["tasks"]["setup_docs_server"]["timestamp"] = datetime.now().isoformat()
        
        with open(config_path, 'w') as f:
            yaml.dump(profile, f, default_flow_style=False, sort_keys=False)
    
    # Start server
    start_docs_server(docs_server)

if __name__ == "__main__":
    main()
'w') as f:
            yaml.dump(profile, f, default_flow_style=False, sort_keys=False)
    
    # Start server
    start_docs_server(docs_server)

if __name__ == "__main__":
    main()
