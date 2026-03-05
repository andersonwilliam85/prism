#!/usr/bin/env python3
"""
Core Installation Engine

Shared installation logic used by both CLI and Web UI installers.
Handles platform detection, tool installation, configuration, and progress tracking.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import json

try:
    import yaml
except ImportError:
    print("⚠️  PyYAML not installed. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml"], check=False)
    import yaml


class InstallationEngine:
    """Core installation engine for Prism setup"""
    
    def __init__(self, config_package=None, user_info=None, progress_callback=None):
        """
        Initialize installation engine
        
        Args:
            config_package: Path to config package or package name
            user_info: Dict of user information
            progress_callback: Optional callback(step, message, level) for progress updates
        """
        self.root_dir = Path(__file__).parent
        self.config_package = config_package
        self.user_info = user_info or {}
        self.progress_callback = progress_callback
        self.platform_name, self.platform_detail = self._detect_platform()
        self.home = Path.home()
        self.workspace = self.home / "workspace"
        
    def log(self, step, message, level="info"):
        """Log a message and call progress callback"""
        prefix = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }.get(level, "ℹ️")
        
        full_message = f"{prefix} {message}"
        print(full_message)
        
        if self.progress_callback:
            self.progress_callback(step, message, level)
    
    def _detect_platform(self):
        """Detect operating system"""
        system = platform.system().lower()
        
        if system == "darwin":
            machine = platform.machine()
            return "mac", "Apple Silicon" if machine == "arm64" else "Intel"
        elif system == "windows":
            return "windows", platform.version()
        elif system == "linux":
            # Check if Ubuntu
            try:
                with open("/etc/os-release") as f:
                    if "ubuntu" in f.read().lower():
                        return "ubuntu", platform.version()
            except:
                pass
            return "linux", platform.version()
        else:
            return "unknown", ""
    
    def run_command(self, cmd, check=True, shell=False, capture_output=False):
        """Run a shell command safely"""
        try:
            if isinstance(cmd, str) and not shell:
                cmd = cmd.split()
            
            result = subprocess.run(
                cmd,
                check=check,
                shell=shell,
                capture_output=capture_output,
                text=True
            )
            return result
        except subprocess.CalledProcessError as e:
            self.log("command", f"Command failed: {e}", "error")
            if check:
                raise
            return None
    
    def install(self):
        """Run full installation process"""
        steps = [
            ("platform", self.step_detect_platform),
            ("package_manager", self.step_install_package_manager),
            ("folder_structure", self.step_create_folder_structure),
            ("git", self.step_install_git),
            ("git_config", self.step_configure_git),
            ("ssh_keys", self.step_generate_ssh_keys),
            ("tools", self.step_install_tools),
            ("config_package", self.step_apply_config_package),
            ("finalize", self.step_finalize),
        ]
        
        for step_name, step_func in steps:
            try:
                self.log(step_name, f"Starting: {step_name.replace('_', ' ').title()}")
                step_func()
                self.log(step_name, f"Completed: {step_name.replace('_', ' ').title()}", "success")
            except Exception as e:
                self.log(step_name, f"Failed: {str(e)}", "error")
                raise
        
        return True
    
    def step_detect_platform(self):
        """Step 1: Detect platform"""
        self.log("platform", f"Detected: {self.platform_name} ({self.platform_detail})")
        
        if self.platform_name == "unknown":
            raise Exception("Unsupported platform")
    
    def step_install_package_manager(self):
        """Step 2: Install package manager if needed"""
        if self.platform_name == "mac":
            # Check if homebrew is installed
            if shutil.which("brew"):
                self.log("package_manager", "Homebrew already installed", "success")
                return
            
            self.log("package_manager", "Installing Homebrew...")
            install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            self.run_command(install_cmd, shell=True)
            
        elif self.platform_name == "windows":
            # Check if chocolatey is installed
            if shutil.which("choco"):
                self.log("package_manager", "Chocolatey already installed", "success")
                return
            
            self.log("package_manager", "Installing Chocolatey...")
            install_cmd = 'powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://community.chocolatey.org/install.ps1\'))"'
            self.run_command(install_cmd, shell=True)
            
        elif self.platform_name == "ubuntu":
            self.log("package_manager", "Using apt (built-in)", "success")
            # Update package list
            self.run_command("sudo apt-get update", shell=True)
    
    def step_create_folder_structure(self):
        """Step 3: Create workspace folder structure"""
        folders = [
            self.workspace,
            self.workspace / "projects",
            self.workspace / "experiments",
            self.workspace / "learning",
            self.workspace / "archived",
            self.workspace / "docs",
            self.workspace / "tooling",
        ]
        
        for folder in folders:
            if not folder.exists():
                folder.mkdir(parents=True)
                self.log("folder_structure", f"Created: {folder.relative_to(self.home)}")
            else:
                self.log("folder_structure", f"Exists: {folder.relative_to(self.home)}")
    
    def step_install_git(self):
        """Step 4: Install Git"""
        if shutil.which("git"):
            version = self.run_command("git --version", capture_output=True).stdout.strip()
            self.log("git", f"Git already installed: {version}", "success")
            return
        
        self.log("git", "Installing Git...")
        
        if self.platform_name == "mac":
            self.run_command("brew install git")
        elif self.platform_name == "windows":
            self.run_command("choco install git -y", shell=True)
        elif self.platform_name == "ubuntu":
            self.run_command("sudo apt-get install -y git", shell=True)
    
    def step_configure_git(self):
        """Step 5: Configure Git"""
        name = self.user_info.get('name', self.user_info.get('full_name', ''))
        email = self.user_info.get('email', self.user_info.get('work_email', ''))
        
        if not name or not email:
            self.log("git_config", "Skipping git config (no user info provided)", "warning")
            return
        
        self.log("git_config", f"Configuring Git for {name} <{email}>")
        
        self.run_command(f'git config --global user.name "{name}"', shell=True)
        self.run_command(f'git config --global user.email "{email}"', shell=True)
        self.run_command('git config --global init.defaultBranch main', shell=True)
        self.run_command('git config --global pull.rebase false', shell=True)
    
    def step_generate_ssh_keys(self):
        """Step 6: Generate SSH keys if needed"""
        ssh_dir = self.home / ".ssh"
        ssh_key = ssh_dir / "id_ed25519"
        
        if ssh_key.exists():
            self.log("ssh_keys", "SSH key already exists", "success")
            return
        
        ssh_dir.mkdir(exist_ok=True, mode=0o700)
        
        email = self.user_info.get('email', self.user_info.get('work_email', 'user@example.com'))
        self.log("ssh_keys", f"Generating SSH key for {email}")
        
        self.run_command(
            f'ssh-keygen -t ed25519 -C "{email}" -f {ssh_key} -N ""',
            shell=True
        )
        
        self.log("ssh_keys", f"SSH key generated: {ssh_key}", "success")
        self.log("ssh_keys", f"Public key: {ssh_key}.pub", "info")
    
    def step_install_tools(self):
        """Step 7: Install additional tools"""
        # Read tools from config package if available
        tools = self._get_tools_from_package()
        
        if not tools:
            self.log("tools", "No additional tools to install", "info")
            return
        
        for tool in tools:
            self._install_tool(tool)
    
    def _get_tools_from_package(self):
        """Get tools list from config package"""
        if not self.config_package:
            return []
        
        # Try to read package.yaml
        package_path = Path(self.config_package)
        if not package_path.exists():
            return []
        
        package_yaml = package_path / "package.yaml"
        if not package_yaml.exists():
            return []
        
        try:
            with open(package_yaml) as f:
                pkg_config = yaml.safe_load(f)
                return pkg_config.get('tools', [])
        except:
            return []
    
    def _install_tool(self, tool):
        """Install a single tool"""
        tool_name = tool if isinstance(tool, str) else tool.get('name')
        
        if shutil.which(tool_name):
            self.log("tools", f"{tool_name} already installed", "success")
            return
        
        self.log("tools", f"Installing {tool_name}...")
        
        try:
            if self.platform_name == "mac":
                self.run_command(f"brew install {tool_name}")
            elif self.platform_name == "windows":
                self.run_command(f"choco install {tool_name} -y", shell=True)
            elif self.platform_name == "ubuntu":
                self.run_command(f"sudo apt-get install -y {tool_name}", shell=True)
        except:
            self.log("tools", f"Failed to install {tool_name}", "warning")
    
    def step_apply_config_package(self):
        """Step 8: Apply configuration from package"""
        if not self.config_package:
            self.log("config_package", "No config package specified", "warning")
            return
        
        package_path = Path(self.config_package)
        if not package_path.exists():
            self.log("config_package", f"Package not found: {package_path}", "error")
            return
        
        # Copy package files to workspace/docs
        dest = self.workspace / "docs" / "config"
        if dest.exists():
            shutil.rmtree(dest)
        
        shutil.copytree(package_path, dest)
        self.log("config_package", f"Config package copied to {dest.relative_to(self.home)}", "success")
        
        # Save user info
        user_config_file = dest / "user-info.yaml"
        with open(user_config_file, 'w') as f:
            yaml.dump(self.user_info, f)
        
        self.log("config_package", "User info saved", "success")
    
    def step_finalize(self):
        """Step 9: Finalize installation"""
        # Create a completion marker
        marker = self.workspace / ".prism_installed"
        marker.write_text(json.dumps({
            "installed_at": datetime.now().isoformat(),
            "platform": self.platform_name,
            "package": str(self.config_package) if self.config_package else None,
            "user": self.user_info.get('name', self.user_info.get('full_name', 'Unknown'))
        }, indent=2))
        
        self.log("finalize", "Installation complete! 🎉", "success")
        self.log("finalize", f"Workspace: {self.workspace}", "info")
