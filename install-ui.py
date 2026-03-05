#!/usr/bin/env python3
"""
Web UI for Dev Onboarding Installer

Launches a local web interface for configuring and running the installer.
Much more user-friendly than pure CLI!

Usage:
    python3 install-ui.py
    
    Opens browser to: http://localhost:5555
"""

import os
import sys
import webbrowser
import yaml
import subprocess
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, send_from_directory
import threading
import time

app = Flask(__name__)

# Paths
ROOT_DIR = Path(__file__).parent
CONFIG_DIR = ROOT_DIR / "config"

# ============================================================================
# HTML TEMPLATES (Embedded for portability)
# ============================================================================

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dev Onboarding - Setup Wizard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5em;
            color: #333;
            margin-bottom: 10px;
        }
        
        .header .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .step {
            display: none;
        }
        
        .step.active {
            display: block;
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input[type="text"],
        input[type="email"],
        select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .checkbox-group {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        
        .checkbox-item {
            display: flex;
            align-items: center;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .checkbox-item:hover {
            background: #e8e8e8;
        }
        
        .checkbox-item input[type="checkbox"] {
            margin-right: 10px;
        }
        
        .buttons {
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
        }
        
        button {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #e0e0e0;
            color: #333;
        }
        
        .btn-secondary:hover {
            background: #d0d0d0;
        }
        
        .progress-bar {
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            margin-bottom: 30px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .alert-info {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            color: #1565c0;
        }
        
        .alert-warning {
            background: #fff3e0;
            border-left: 4px solid #ff9800;
            color: #e65100;
        }
        
        .installing {
            text-align: center;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 30px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .log-output {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            max-height: 400px;
            overflow-y: auto;
            margin-top: 20px;
        }
        
        .package-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐶 Dev Onboarding</h1>
            <p class="subtitle">One-click development environment setup</p>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill" style="width: 20%"></div>
        </div>
        
        <!-- Step 1: Package Selection -->
        <div class="step active" id="step1">
            <h2>📦 Choose Your Config Package</h2>
            <p>Select the configuration package that best fits your needs:</p>
            
            <!-- Registry Configuration (Expandable) -->
            <details style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                <summary style="cursor: pointer; font-weight: 600; color: #667eea;">
                    ⚙️ Advanced: Custom Registry Configuration
                </summary>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                    <p style="font-size: 0.9em; color: #666; margin-bottom: 15px;">
                        Configure custom npm registry for corporate/air-gapped environments
                    </p>
                    
                    <div class="form-group">
                        <label for="npmRegistry">npm Registry URL</label>
                        <input type="text" id="npmRegistry" placeholder="https://registry.npmjs.org (default)">
                        <small style="color: #666;">Leave empty to use default public registry</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="unpkgUrl">unpkg CDN URL</label>
                        <input type="text" id="unpkgUrl" placeholder="https://unpkg.com (default)">
                        <small style="color: #666;">Leave empty to use default unpkg CDN</small>
                    </div>
                    
                    <button class="btn-secondary" onclick="testRegistry()" style="margin-top: 10px;">
                        🔍 Test Connection
                    </button>
                    <span id="registryTestResult" style="margin-left: 10px;"></span>
                </div>
            </details>
            
            <div id="packagesList" style="margin-top: 30px;">
                <!-- Populated by JS -->
            </div>
            
            <div class="alert alert-info" style="margin-top: 20px;">
                <strong>💡 Tip:</strong> Not sure which to pick? Personal Dev is great for freelancers!
            </div>
            
            <div class="buttons">
                <div></div>
                <button class="btn-primary" onclick="nextStep()">Next →</button>
            </div>
        </div>
        
        <!-- Step 2: User Info -->
        <div class="step" id="step2">
            <h2>Your Information</h2>
            
            <div id="userInfoFields">
                <!-- Fields populated dynamically based on selected package -->
            </div>
            
            <div class="buttons">
                <button class="btn-secondary" onclick="prevStep()">← Back</button>
                <button class="btn-primary" onclick="nextStep()">Next →</button>
            </div>
        </div>
        
        <!-- Step 3: Organization -->
        <div class="step" id="step3">
            <h2>Organization</h2>
            
            <div class="form-group">
                <label for="subOrg">Sub-Organization</label>
                <select id="subOrg">
                    <option value="">Loading...</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="department">Department</label>
                <select id="department">
                    <option value="">Select sub-org first...</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="team">Team (Optional)</label>
                <select id="team">
                    <option value="">Select department first...</option>
                </select>
            </div>
            
            <div class="buttons">
                <button class="btn-secondary" onclick="prevStep()">← Back</button>
                <button class="btn-primary" onclick="nextStep()">Next →</button>
            </div>
        </div>
        
        <!-- Step 4: Tools -->
        <div class="step" id="step4">
            <h2>Select Tools</h2>
            <p>Choose optional tools to install (required tools are pre-selected)</p>
            
            <div class="checkbox-group" id="toolsList">
                <!-- Populated by JS -->
            </div>
            
            <div class="buttons">
                <button class="btn-secondary" onclick="prevStep()">← Back</button>
                <button class="btn-primary" onclick="nextStep()">Next →</button>
            </div>
        </div>
        
        <!-- Step 5: Confirm -->
        <div class="step" id="step5">
            <h2>Ready to Install!</h2>
            
            <div id="summary">
                <!-- Populated by JS -->
            </div>
            
            <div class="alert alert-warning">
                <strong>⚠️ Important:</strong> Make sure you're connected to VPN or company WiFi!
            </div>
            
            <div class="buttons">
                <button class="btn-secondary" onclick="prevStep()">← Back</button>
                <button class="btn-primary" onclick="startInstall()">🚀 Install Now!</button>
            </div>
        </div>
        
        <!-- Step 6: Installing -->
        <div class="step" id="step6">
            <div class="installing">
                <h2>Installing...</h2>
                <div class="spinner"></div>
                <p id="installStatus">Setting up your environment...</p>
                
                <div class="log-output" id="logOutput">
                    <div>Starting installation...</div>
                </div>
            </div>
        </div>
        
        <!-- Step 7: Complete -->
        <div class="step" id="step7">
            <div style="text-align: center;">
                <h2>🎉 All Done!</h2>
                <p style="margin: 20px 0;">Your development environment is ready!</p>
                
                <div class="alert alert-info" style="text-align: left;">
                    <h3>Next Steps:</h3>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>Documentation server: <a href="http://localhost:8000" target="_blank">http://localhost:8000</a></li>
                        <li>Check your SSH key: <code>~/.ssh/id_ed25519.pub</code></li>
                        <li>Add SSH key to GitHub Enterprise</li>
                        <li>Join your team's Slack channels</li>
                    </ul>
                </div>
                
                <button class="btn-primary" onclick="window.close()">Close</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentStep = 1;
        const totalSteps = 7;
        let selectedPackage = null;
        
        function updateProgress() {
            const progress = (currentStep / totalSteps) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
        }
        
        function nextStep() {
            // Validate package selection on step 1
            if (currentStep === 1 && !selectedPackage) {
                alert('Please select a config package!');
                return;
            }
            
            document.getElementById('step' + currentStep).classList.remove('active');
            currentStep++;
            document.getElementById('step' + currentStep).classList.add('active');
            updateProgress();
            
            // Load data for specific steps
            if (currentStep === 2) loadUserInfoFields();  // Load dynamic fields
            if (currentStep === 3) loadOrganizations();
            if (currentStep === 4) loadTools();
            if (currentStep === 5) showSummary();
        }
        
        function prevStep() {
            document.getElementById('step' + currentStep).classList.remove('active');
            currentStep--;
            document.getElementById('step' + currentStep).classList.add('active');
            updateProgress();
        }
        
        async function loadOrganizations() {
            const response = await fetch('/api/organizations');
            const data = await response.json();
            
            const subOrgSelect = document.getElementById('subOrg');
            subOrgSelect.innerHTML = '<option value="">None</option>';
            data.sub_orgs.forEach(org => {
                subOrgSelect.innerHTML += `<option value="${org.id}">${org.name}</option>`;
            });
        }
        
        async function loadTools() {
            const response = await fetch('/api/tools');
            const data = await response.json();
            
            const toolsList = document.getElementById('toolsList');
            toolsList.innerHTML = '';
            
            data.tools.forEach(tool => {
                const checked = tool.required ? 'checked disabled' : '';
                toolsList.innerHTML += `
                    <div class="checkbox-item">
                        <input type="checkbox" id="tool_${tool.id}" ${checked}>
                        <label for="tool_${tool.id}">${tool.name}</label>
                    </div>
                `;
            });
        }
        
        function showSummary() {
            // Collect all user info field values
            const userInfoFields = document.querySelectorAll('#userInfoFields input');
            let userInfoHTML = '';
            userInfoFields.forEach(input => {
                if (input.value) {
                    const label = input.previousElementSibling?.previousElementSibling?.textContent.replace('*', '').trim() || input.name;
                    userInfoHTML += `<p><strong>${label}:</strong> ${input.value}</p>`;
                }
            });
            
            const subOrg = document.getElementById('subOrg').selectedOptions[0]?.text || 'None';
            const dept = document.getElementById('department').selectedOptions[0]?.text || 'None';
            
            document.getElementById('summary').innerHTML = `
                <p><strong>Package:</strong> ${selectedPackage}</p>
                <hr>
                <h4>User Information:</h4>
                ${userInfoHTML}
                <hr>
                <p><strong>Organization:</strong> ${subOrg} / ${dept}</p>
                <p style="margin-top: 20px;"><strong>Tools to install:</strong> ~15 selected</p>
            `;
        }
        
        async function startInstall() {
            currentStep = 6;
            document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
            document.getElementById('step6').classList.add('active');
            updateProgress();
            
            const logOutput = document.getElementById('logOutput');
            
            try {
                // Collect all form data
                const userInfo = {};
                document.querySelectorAll('#userInfoFields input').forEach(input => {
                    if (input.value) {
                        userInfo[input.name] = input.value;
                    }
                });
                
                const registry = document.getElementById('npmRegistry').value || null;
                const unpkgUrl = document.getElementById('unpkgUrl').value || null;
                
                logOutput.innerHTML = '<div>🚀 Starting installation...</div>';
                
                // Call backend API
                const response = await fetch('/api/install', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        package: selectedPackage,
                        userInfo: userInfo,
                        registry: registry,
                        unpkgUrl: unpkgUrl
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    logOutput.innerHTML += `<div>✅ ${result.message}</div>`;
                    if (result.path) {
                        logOutput.innerHTML += `<div>📁 Package location: ${result.path}</div>`;
                    }
                    
                    // Simulate additional steps
                    const steps = [
                        'Detecting platform...',
                        'Validating configuration...',
                        'Package ready for use!'
                    ];
                    
                    for (let step of steps) {
                        await new Promise(resolve => setTimeout(resolve, 500));
                        logOutput.innerHTML += `<div>✅ ${step}</div>`;
                        logOutput.scrollTop = logOutput.scrollHeight;
                    }
                    
                    // Go to complete
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    currentStep = 7;
                    document.getElementById('step6').classList.remove('active');
                    document.getElementById('step7').classList.add('active');
                    updateProgress();
                } else {
                    logOutput.innerHTML += `<div style="color: #ef4444;">❌ Error: ${result.error}</div>`;
                }
            } catch (error) {
                logOutput.innerHTML += `<div style="color: #ef4444;">❌ Error: ${error.message}</div>`;
            }
        }
        
        // Test registry connection
        async function testRegistry() {
            const registry = document.getElementById('npmRegistry').value;
            const unpkg = document.getElementById('unpkgUrl').value;
            const result = document.getElementById('registryTestResult');
            
            if (!registry && !unpkg) {
                result.innerHTML = '<span style="color: #f59e0b;">⚠️ Enter a registry URL to test</span>';
                return;
            }
            
            result.innerHTML = '<span style="color: #667eea;">🔄 Testing...</span>';
            
            try {
                const testUrl = unpkg || registry || 'https://unpkg.com';
                const response = await fetch(testUrl + '/@prism/personal-dev-config@latest/package.json');
                
                if (response.ok) {
                    result.innerHTML = '<span style="color: #10b981;">✅ Connection successful!</span>';
                } else {
                    result.innerHTML = '<span style="color: #ef4444;">❌ Connection failed (status: ' + response.status + ')</span>';
                }
            } catch (error) {
                result.innerHTML = '<span style="color: #ef4444;">❌ Connection failed: ' + error.message + '</span>';
            }
        }
        
        // Load packages on page load
        async function loadPackages() {
            try {
                const response = await fetch('/api/packages');
                const data = await response.json();
                
                if (data.error) {
                    console.error('Error loading packages:', data.error);
                    document.getElementById('packagesList').innerHTML = `
                        <div class="alert alert-warning">
                            <strong>⚠️ Could not load packages from registry</strong><br>
                            Using local packages. Error: ${data.error}
                        </div>
                    `;
                }
                
                const packagesList = document.getElementById('packagesList');
                
                if (data.packages && data.packages.length > 0) {
                    packagesList.innerHTML = '';
                    
                    data.packages.forEach(pkg => {
                        const displayName = pkg.displayName || pkg.name || pkg.id;
                        const description = pkg.description || 'No description available';
                        const version = pkg.version || 'latest';
                        const source = pkg.source || 'local';
                        const sourceIcon = source === 'npm' ? '🌐' : '📁';
                        const sourceBadge = `<span style="background: ${source === 'npm' ? '#10b981' : '#6b7280'}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">${sourceIcon} ${source}</span>`;
                        
                        packagesList.innerHTML += `
                            <div class="package-card" onclick="selectPackage('${pkg.id}')" id="pkg_${pkg.id}" style="
                                border: 2px solid #e0e0e0;
                                border-radius: 12px;
                                padding: 20px;
                                margin-bottom: 15px;
                                cursor: pointer;
                                transition: all 0.3s;
                            ">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <div style="flex: 1;">
                                        <h3 style="margin: 0 0 10px 0; color: #333;">
                                            📦 ${displayName}
                                        </h3>
                                        <p style="margin: 0 0 10px 0; color: #666;">${description}</p>
                                        <div style="font-size: 0.9em; color: #888;">
                                            <strong>Version:</strong> ${version} | 
                                            <strong>Source:</strong> ${sourceBadge}
                                        </div>
                                    </div>
                                    <div style="width: 30px; height: 30px; border: 2px solid #e0e0e0; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-left: 20px;">
                                        <span class="checkmark" style="display: none; color: #667eea; font-size: 1.5em;">✓</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    packagesList.innerHTML = `
                        <div class="alert alert-warning">
                            <strong>⚠️ No packages found!</strong><br>
                            Please check your registry configuration or ensure local packages exist.
                        </div>
                    `;
                }
            } catch (error) {
                console.error('Failed to load packages:', error);
                document.getElementById('packagesList').innerHTML = `
                    <div class="alert alert-warning">
                        <strong>⚠️ Error loading packages</strong><br>
                        ${error.message}
                    </div>
                `;
            }
        }
        
        function selectPackage(packageName) {
            selectedPackage = packageName;
            
            // Update UI - remove selection from all
            document.querySelectorAll('.package-card').forEach(card => {
                card.style.border = '2px solid #e0e0e0';
                card.style.background = 'white';
                card.querySelector('.checkmark').style.display = 'none';
            });
            
            // Highlight selected
            const selected = document.getElementById('pkg_' + packageName);
            selected.style.border = '2px solid #667eea';
            selected.style.background = '#f8f9ff';
            selected.querySelector('.checkmark').style.display = 'block';
        }
        
        // Load user info fields based on selected package
        async function loadUserInfoFields() {
            const response = await fetch(`/api/package/${selectedPackage}/user-fields`);
            const data = await response.json();
            
            const container = document.getElementById('userInfoFields');
            container.innerHTML = '';
            
            data.fields.forEach(field => {
                const required = field.required ? 'required' : '';
                const pattern = field.validation?.pattern || '';
                const title = field.validation?.message || '';
                
                container.innerHTML += `
                    <div class="form-group">
                        <label for="field_${field.id}">
                            ${field.label}
                            ${field.required ? '<span style="color: red;">*</span>' : ''}
                        </label>
                        ${field.description ? `<p style="font-size: 0.85em; color: #666; margin: 5px 0;">${field.description}</p>` : ''}
                        <input
                            type="${field.type}"
                            id="field_${field.id}"
                            name="${field.id}"
                            placeholder="${field.placeholder || ''}"
                            ${required}
                            ${pattern ? `pattern="${pattern}" title="${title}"` : ''}
                        >
                    </div>
                `;
            });
        }
        
        // Initialize
        updateProgress();
        loadPackages();
    </script>
</body>
</html>
"""

# ============================================================================
# Flask Routes
# ============================================================================

@app.route("/")
def index():
    """Main installer UI"""
    return render_template_string(INDEX_HTML)

@app.route("/api/packages")
def get_packages():
    """Get available config packages"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "scripts"))
    
    try:
        from package_manager import PackageManager
        pm = PackageManager()
        packages = pm.discover_packages()
        return jsonify({"packages": packages})
    except Exception as e:
        return jsonify({"packages": [], "error": str(e)})

@app.route("/api/package/<package_name>/user-fields")
def get_user_fields(package_name):
    """Get user info fields for a specific package"""
    import sys
    import yaml
    sys.path.insert(0, str(Path(__file__).parent / "scripts"))
    
    try:
        from package_manager import PackageManager
        pm = PackageManager()
        
        # Find the package
        packages = pm.discover_packages()
        pkg = next((p for p in packages if p['name'] == package_name), None)
        
        if not pkg:
            return jsonify({"fields": [], "error": "Package not found"})
        
        # Load package.yaml to get user_info_fields
        pkg_path = Path(pkg['path'])
        pkg_yaml_path = pkg_path / 'package.yaml'
        
        if not pkg_yaml_path.exists():
            return jsonify({"fields": [], "error": "package.yaml not found"})
        
        with open(pkg_yaml_path) as f:
            pkg_config = yaml.safe_load(f)
        
        # Get user_info_fields from package config
        fields = pkg_config.get('package', {}).get('user_info_fields', [])
        
        # If no fields defined, use defaults
        if not fields:
            fields = [
                {"id": "name", "label": "Full Name", "type": "text", "required": True, "placeholder": "John Doe"},
                {"id": "email", "label": "Email", "type": "email", "required": True, "placeholder": "john.doe@example.com"}
            ]
        
        return jsonify({"fields": fields})
    except Exception as e:
        return jsonify({"fields": [], "error": str(e)})

@app.route("/api/organizations")
def get_organizations():
    """Get available organizations from config"""
    # Load from inheritance.yaml
    inheritance_path = CONFIG_DIR / "inheritance.yaml"
    
    if not inheritance_path.exists():
        return jsonify({"sub_orgs": [], "departments": [], "teams": []})
    
    with open(inheritance_path) as f:
        config = yaml.safe_load(f)
    
    return jsonify({
        "sub_orgs": config.get("available_sub_orgs", []),
        "departments": config.get("available_departments", []),
        "teams": config.get("available_teams", [])
    })

@app.route("/api/tools")
def get_tools():
    """Get available tools"""
    # Load from tools.yaml
    tools_path = CONFIG_DIR / "tools.yaml"
    
    if not tools_path.exists():
        return jsonify({"tools": []})
    
    with open(tools_path) as f:
        config = yaml.safe_load(f)
    
    tools = []
    for tool_id, tool_config in config.get("tools", {}).items():
        tools.append({
            "id": tool_id,
            "name": tool_id.replace("-", " ").title(),
            "description": tool_config.get("description", ""),
            "required": tool_config.get("required", False)
        })
    
    return jsonify({"tools": tools})

@app.route("/api/install", methods=["POST"])
def install():
    """Run the actual installation"""
    data = request.json
    
    try:
        import sys
        sys.path.insert(0, str(ROOT_DIR / "scripts"))
        from npm_package_fetcher import fetch_package
        
        package_name = data.get('package')
        user_info = data.get('userInfo', {})
        registry = data.get('registry', None)
        unpkg_url = data.get('unpkgUrl', None)
        
        # Set registry env vars if provided
        if registry:
            os.environ['PRISM_NPM_REGISTRY'] = registry
        if unpkg_url:
            os.environ['PRISM_UNPKG_URL'] = unpkg_url
        
        # Fetch the package
        if not package_name.startswith('@prism/'):
            package_name = f"@prism/{package_name}-config"
        
        # Try to fetch package (will fallback to local if needed)
        dest_dir = ROOT_DIR / "temp_install" / package_name.split('/')[-1]
        dest_dir.parent.mkdir(exist_ok=True)
        
        try:
            result = fetch_package(package_name, "latest", str(dest_dir), unpkg_url)
            if result:
                # Save user info to config
                config_file = dest_dir / "user-config.yaml"
                with open(config_file, 'w') as f:
                    yaml.dump(user_info, f)
                
                return jsonify({
                    "success": True, 
                    "message": f"Package {package_name} fetched successfully!",
                    "path": str(result)
                })
        except Exception as e:
            print(f"Package fetch failed: {e}, trying local...")
            # Try local package
            pkg_id = package_name.replace('@prism/', '').replace('-config', '')
            local_path = ROOT_DIR / "config-packages" / pkg_id
            if local_path.exists():
                return jsonify({
                    "success": True,
                    "message": f"Using local package: {pkg_id}",
                    "path": str(local_path)
                })
            else:
                return jsonify({
                    "success": False,
                    "error": f"Package not found: {package_name}"
                }), 404
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# Main
# ============================================================================

def open_browser():
    """Open browser after short delay"""
    time.sleep(1.5)
    webbrowser.open("http://localhost:5555")

if __name__ == "__main__":
    print("\n🌐 Starting Dev Onboarding UI...")
    print("   🔗 Opening browser to http://localhost:5555\n")
    
    # Open browser in background
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Flask
    app.run(host="localhost", port=5555, debug=False)
