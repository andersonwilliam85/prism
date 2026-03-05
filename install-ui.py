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
        
        <!-- Step 1: Welcome -->
        <div class="step active" id="step1">
            <h2>Welcome!</h2>
            <p>Let's set up your development environment in just a few steps.</p>
            
            <div class="alert alert-info" style="margin-top: 20px;">
                <strong>💡 Tip:</strong> This installer is idempotent - you can run it multiple times safely!
            </div>
            
            <div class="buttons">
                <div></div>
                <button class="btn-primary" onclick="nextStep()">Get Started →</button>
            </div>
        </div>
        
        <!-- Step 2: User Info -->
        <div class="step" id="step2">
            <h2>Your Information</h2>
            
            <div class="form-group">
                <label for="userName">Full Name</label>
                <input type="text" id="userName" placeholder="John Doe" required>
            </div>
            
            <div class="form-group">
                <label for="userEmail">Email</label>
                <input type="email" id="userEmail" placeholder="john.doe@company.com" required>
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
        
        function updateProgress() {
            const progress = (currentStep / totalSteps) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
        }
        
        function nextStep() {
            document.getElementById('step' + currentStep).classList.remove('active');
            currentStep++;
            document.getElementById('step' + currentStep).classList.add('active');
            updateProgress();
            
            // Load data for specific steps
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
            const name = document.getElementById('userName').value;
            const email = document.getElementById('userEmail').value;
            const subOrg = document.getElementById('subOrg').selectedOptions[0].text;
            const dept = document.getElementById('department').selectedOptions[0].text;
            
            document.getElementById('summary').innerHTML = `
                <p><strong>Name:</strong> ${name}</p>
                <p><strong>Email:</strong> ${email}</p>
                <p><strong>Organization:</strong> ${subOrg} / ${dept}</p>
                <p style="margin-top: 20px;"><strong>Tools to install:</strong> ~15 selected</p>
            `;
        }
        
        async function startInstall() {
            currentStep = 6;
            document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
            document.getElementById('step6').classList.add('active');
            updateProgress();
            
            // Simulate installation (replace with actual install logic)
            const logOutput = document.getElementById('logOutput');
            const steps = [
                'Detecting platform...',
                'Installing package manager...',
                'Installing git...',
                'Installing kubectl...',
                'Configuring Maven...',
                'Generating SSH key...',
                'Setting up documentation server...',
                'Installation complete!'
            ];
            
            for (let i = 0; i < steps.length; i++) {
                await new Promise(resolve => setTimeout(resolve, 1000));
                logOutput.innerHTML += `<div>✅ ${steps[i]}</div>`;
                logOutput.scrollTop = logOutput.scrollHeight;
            }
            
            // Go to complete
            await new Promise(resolve => setTimeout(resolve, 1000));
            currentStep = 7;
            document.getElementById('step6').classList.remove('active');
            document.getElementById('step7').classList.add('active');
            updateProgress();
        }
        
        // Initialize
        updateProgress();
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
    
    # TODO: Call actual installer with config
    # For now, just simulate
    
    return jsonify({"success": True, "message": "Installation started"})

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
