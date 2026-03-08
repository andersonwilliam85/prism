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
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

import yaml
from flask import Flask, jsonify, render_template_string, request, send_from_directory

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
    <title>Prism Installer</title>
    <link rel="icon" type="image/png" sizes="32x32" href="/assets/branding/prism_dark_32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/assets/branding/prism_dark_16.png">
    <style>
        :root {
            /* Ocean Blue Theme (Default) */
            --gradient-1: #0093E9;
            --gradient-2: #80D0C7;
            --gradient-3: #13547a;
            --gradient-4: #009ffd;
            --gradient-5: #2a2a72;
        }
        
        /* Theme Definitions */
        [data-theme="ocean"] {
            --gradient-1: #0093E9;
            --gradient-2: #80D0C7;
            --gradient-3: #13547a;
            --gradient-4: #009ffd;
            --gradient-5: #2a2a72;
        }
        
        [data-theme="purple"] {
            --gradient-1: #667eea;
            --gradient-2: #764ba2;
            --gradient-3: #f093fb;
            --gradient-4: #4facfe;
            --gradient-5: #00f2fe;
        }
        
        [data-theme="forest"] {
            --gradient-1: #134E5E;
            --gradient-2: #71B280;
            --gradient-3: #56ab2f;
            --gradient-4: #a8e063;
            --gradient-5: #0f9b0f;
        }
        
        [data-theme="sunset"] {
            --gradient-1: #f12711;
            --gradient-2: #f5af19;
            --gradient-3: #ff6a00;
            --gradient-4: #ee0979;
            --gradient-5: #ff512f;
        }
        
        [data-theme="midnight"] {
            --gradient-1: #2c3e50;
            --gradient-2: #3498db;
            --gradient-3: #34495e;
            --gradient-4: #2980b9;
            --gradient-5: #1abc9c;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, 
                var(--gradient-1) 0%, 
                var(--gradient-2) 25%, 
                var(--gradient-3) 50%, 
                var(--gradient-4) 75%, 
                var(--gradient-5) 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            transition: background 0.5s ease;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.5) inset;
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
            background: linear-gradient(135deg, 
                var(--gradient-1) 0%, 
                var(--gradient-2) 25%, 
                var(--gradient-3) 50%, 
                var(--gradient-4) 75%, 
                var(--gradient-5) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
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
            background: linear-gradient(135deg, 
                var(--gradient-1) 0%, 
                var(--gradient-2) 50%, 
                var(--gradient-3) 100%);
            color: white;
            position: relative;
            overflow: hidden;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }
        
        .btn-secondary {
            background: rgba(224, 224, 224, 0.8);
            backdrop-filter: blur(10px);
            color: #333;
        }
        
        .btn-secondary:hover {
            background: rgba(208, 208, 208, 0.9);
        }
        
        .progress-bar {
            height: 6px;
            background: rgba(224, 224, 224, 0.5);
            border-radius: 3px;
            margin-bottom: 30px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg,
                var(--gradient-1) 0%, 
                var(--gradient-2) 25%, 
                var(--gradient-3) 50%, 
                var(--gradient-4) 75%, 
                var(--gradient-5) 100%);
            background-size: 200% 100%;
            animation: progressShimmer 2s ease infinite;
            transition: width 0.5s;
        }
        
        @keyframes progressShimmer {
            0% { background-position: 0% 0%; }
            50% { background-position: 100% 0%; }
            100% { background-position: 0% 0%; }
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
            border-top: 4px solid var(--gradient-1);
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
        
        /* Hamburger Menu */
        .hamburger-menu {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 10000;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 12px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .hamburger-menu:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
        }
        
        .hamburger-icon {
            width: 24px;
            height: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
        }
        
        .hamburger-icon span {
            display: block;
            height: 3px;
            background: linear-gradient(135deg, var(--gradient-1), var(--gradient-2));
            border-radius: 2px;
            transition: all 0.3s ease;
        }
        
        .hamburger-menu.open .hamburger-icon span:nth-child(1) {
            transform: rotate(45deg) translate(7px, 7px);
        }
        
        .hamburger-menu.open .hamburger-icon span:nth-child(2) {
            opacity: 0;
        }
        
        .hamburger-menu.open .hamburger-icon span:nth-child(3) {
            transform: rotate(-45deg) translate(7px, -7px);
        }
        
        /* Settings Panel */
        .settings-panel {
            position: fixed;
            top: 0;
            left: -450px;
            width: 450px;
            height: 100vh;
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(20px);
            box-shadow: 4px 0 20px rgba(0, 0, 0, 0.2);
            transition: left 0.3s ease;
            z-index: 9999;
            overflow-y: auto;
            padding: 0;
            display: flex;
            flex-direction: column;
        }
        
        .settings-panel.open {
            left: 0;
        }
        
        .settings-header {
            padding: 20px;
            padding-top: 60px;
            background: linear-gradient(135deg, var(--gradient-1), var(--gradient-2));
            color: white;
        }
        
        .settings-panel h2 {
            color: white;
            margin: 0 0 10px 0;
            font-size: 1.5em;
        }
        
        .settings-panel .subtitle {
            color: rgba(255, 255, 255, 0.9);
            font-size: 0.9em;
        }
        
        /* Step Navigation */
        .settings-steps {
            display: flex;
            padding: 15px 20px;
            background: rgba(0, 0, 0, 0.03);
            border-bottom: 1px solid #e0e0e0;
            overflow-x: auto;
            gap: 10px;
        }
        
        .settings-step-btn {
            padding: 8px 16px;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 20px;
            cursor: pointer;
            white-space: nowrap;
            font-size: 0.85em;
            transition: all 0.3s ease;
            flex-shrink: 0;
        }
        
        .settings-step-btn:hover {
            border-color: var(--gradient-1);
            transform: translateY(-2px);
        }
        
        .settings-step-btn.active {
            background: linear-gradient(135deg, var(--gradient-1), var(--gradient-2));
            color: white;
            border-color: transparent;
        }
        
        .settings-step-btn.completed {
            border-color: #10b981;
            background: #f0fdf4;
        }
        
        /* Settings Content */
        .settings-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        
        .settings-step-content {
            display: none;
        }
        
        .settings-step-content.active {
            display: block;
            animation: fadeIn 0.3s;
        }
        
        .settings-section {
            margin-bottom: 25px;
        }
        
        .settings-section h4 {
            color: #333;
            font-size: 1em;
            margin-bottom: 10px;
        }
        
        .settings-section p {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
        }
        
        /* Theme Grid in Settings */
        .theme-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 10px;
        }
        
        .theme-option {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }
        
        .theme-option:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .theme-option.active {
            border-color: var(--gradient-1);
            box-shadow: 0 0 0 3px rgba(0, 147, 233, 0.2);
        }
        
        .theme-preview {
            width: 100%;
            height: 40px;
            border-radius: 6px;
            margin-bottom: 8px;
        }
        
        .theme-preview.ocean {
            background: linear-gradient(135deg, #0093E9, #80D0C7);
        }
        
        .theme-preview.purple {
            background: linear-gradient(135deg, #667eea, #764ba2);
        }
        
        .theme-preview.forest {
            background: linear-gradient(135deg, #134E5E, #71B280);
        }
        
        .theme-preview.sunset {
            background: linear-gradient(135deg, #f12711, #f5af19);
        }
        
        .theme-preview.midnight {
            background: linear-gradient(135deg, #2c3e50, #3498db);
        }
        
        .theme-name {
            font-size: 0.85em;
            color: #666;
            font-weight: 600;
        }
        
        /* Prism Source Input */
        .prism-source-input {
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }
        
        .prism-source-input input {
            flex: 1;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 0.9em;
        }
        
        .prism-source-input button {
            padding: 10px 20px;
            background: linear-gradient(135deg, var(--gradient-1), var(--gradient-2));
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .prism-source-input button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        .prism-sources-list {
            margin-top: 15px;
        }
        
        .prism-source-item {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .prism-source-item .source-url {
            font-size: 0.85em;
            color: #666;
            font-family: 'Courier New', monospace;
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .prism-source-item .remove-btn {
            background: #ef4444;
            color: white;
            border: none;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
            transition: all 0.2s ease;
        }
        
        .prism-source-item .remove-btn:hover {
            background: #dc2626;
        }
        
        /* Overlay for settings panel */
        .settings-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 9998;
        }
        
        .settings-overlay.open {
            opacity: 1;
            visibility: visible;
        }
        

    </style>
</head>
<body>
    <!-- Settings Overlay -->
    <div class="settings-overlay" id="settingsOverlay" onclick="toggleSettings()"></div>
    
    <!-- Hamburger Menu -->
    <div class="hamburger-menu" id="hamburgerMenu" onclick="toggleSettings()">
        <div class="hamburger-icon">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>
    
    <!-- Settings Panel -->
    <div class="settings-panel" id="settingsPanel">
        <!-- Header -->
        <div class="settings-header">
            <h2>⚙️ Configure Prism</h2>
            <p class="subtitle">Set up your installation preferences</p>
        </div>
        
        <!-- Step Navigation -->
        <div class="settings-steps">
            <button class="settings-step-btn active" data-step="1" onclick="goToSettingsStep(1)">
                1. Select Prism
            </button>
            <button class="settings-step-btn" data-step="2" onclick="goToSettingsStep(2)">
                2. Package Repos
            </button>
            <button class="settings-step-btn" data-step="3" onclick="goToSettingsStep(3)">
                3. Theme
            </button>
            <button class="settings-step-btn" data-step="4" onclick="goToSettingsStep(4)">
                4. Advanced
            </button>
        </div>
        
        <!-- Settings Content -->
        <div class="settings-content">
            <!-- Step 1: Select Prism -->
            <div class="settings-step-content active" id="settingsStep1">
                <h3>🔷 Select Your Setup Prism</h3>
                <p style="color: #666; margin-bottom: 20px;">Choose which configuration prism to install. This will configure your development environment.</p>
                
                <div id="settingsPrismList" style="max-height: 400px; overflow-y: auto;">
                    <!-- Prisms will be loaded here -->
                    <p style="color: #999; text-align: center; padding: 40px;">Loading prisms...</p>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #f0f9ff; border-left: 4px solid #0093E9; border-radius: 4px;">
                    <p style="font-size: 0.9em; margin: 0;"><strong>💡 Tip:</strong> You can add more prism sources in the next step!</p>
                </div>
            </div>
            
            <!-- Step 2: Package Repositories -->
            <div class="settings-step-content" id="settingsStep2">
                <h3>📦 Package Repositories</h3>
                <p style="color: #666; margin-bottom: 20px;">Configure where to load prisms and packages from</p>
                
                <div class="settings-section">
                    <h4 style="font-size: 1em; margin-bottom: 10px;">🔷 Prism Sources</h4>
                    <p style="font-size: 0.9em; color: #666; margin-bottom: 15px;">Add registries or URLs to load additional setup prisms</p>
                    <div class="prism-source-input">
                        <input type="text" id="prismSourceUrl" placeholder="https://registry.example.com/prisms" />
                        <button onclick="addPrismSource()">Add</button>
                    </div>
                    <div class="prism-sources-list" id="prismSourcesList" style="margin-top: 15px;">
                        <!-- Sources populated by JS -->
                    </div>
                </div>
                
                <div class="settings-section" style="margin-top: 30px;">
                    <h4 style="font-size: 1em; margin-bottom: 10px;">📦 npm Registry</h4>
                    <p style="font-size: 0.9em; color: #666; margin-bottom: 15px;">Configure custom npm registry for corporate/air-gapped environments</p>
                    <div class="form-group">
                        <label for="settingsNpmRegistry">Registry URL</label>
                        <input type="text" id="settingsNpmRegistry" placeholder="https://registry.npmjs.org" />
                    </div>
                </div>
            </div>
            
            <!-- Step 3: Theme -->
            <div class="settings-step-content" id="settingsStep3">
                <h3>🎨 Choose Your Theme</h3>
                <p style="color: #666; margin-bottom: 20px;">Select your preferred color scheme</p>
                
                <div class="theme-grid">
                    <div class="theme-option active" data-theme="ocean" onclick="selectTheme('ocean')">
                        <div class="theme-preview ocean"></div>
                        <div class="theme-name">Ocean Blue</div>
                    </div>
                    <div class="theme-option" data-theme="purple" onclick="selectTheme('purple')">
                        <div class="theme-preview purple"></div>
                        <div class="theme-name">Purple Haze</div>
                    </div>
                    <div class="theme-option" data-theme="forest" onclick="selectTheme('forest')">
                        <div class="theme-preview forest"></div>
                        <div class="theme-name">Forest Green</div>
                    </div>
                    <div class="theme-option" data-theme="sunset" onclick="selectTheme('sunset')">
                        <div class="theme-preview sunset"></div>
                        <div class="theme-name">Sunset Orange</div>
                    </div>
                    <div class="theme-option" data-theme="midnight" onclick="selectTheme('midnight')">
                        <div class="theme-preview midnight"></div>
                        <div class="theme-name">Midnight Dark</div>
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #f0f9ff; border-left: 4px solid #0093E9; border-radius: 4px;">
                    <p style="font-size: 0.9em; margin: 0;"><strong>💡 Tip:</strong> Your theme choice is saved automatically and persists across sessions!</p>
                </div>
            </div>
            
            <!-- Step 4: Advanced -->
            <div class="settings-step-content" id="settingsStep4">
                <h3>⚙️ Advanced Configuration</h3>
                <p style="color: #666; margin-bottom: 20px;">Additional settings and information</p>
                
                <div class="settings-section">
                    <h4 style="font-size: 1em; margin-bottom: 10px;">💾 Configuration Export/Import</h4>
                    <p style="font-size: 0.9em; color: #666; margin-bottom: 15px;">Share your Prism configuration with others</p>
                    <div style="display: flex; gap: 10px;">
                        <button class="btn-secondary" onclick="exportPrismConfig()" style="flex: 1;">📤 Export Config</button>
                        <button class="btn-secondary" onclick="importPrismConfig()" style="flex: 1;">📥 Import Config</button>
                    </div>
                </div>
                
                <div class="settings-section" style="margin-top: 30px;">
                    <h4 style="font-size: 1em; margin-bottom: 10px;">🔄 Reset Configuration</h4>
                    <p style="font-size: 0.9em; color: #666; margin-bottom: 15px;">Reset all Prism settings to defaults</p>
                    <button class="btn-secondary" onclick="resetPrismConfig()" style="background: #ef4444; color: white; width: 100%;">Reset to Defaults</button>
                </div>
                
                <div class="settings-section" style="margin-top: 30px;">
                    <h4 style="font-size: 1em; margin-bottom: 10px;">ℹ️ About Prism</h4>
                    <p style="font-size: 0.85em; color: #666;">Light refracts through configuration - infinite possibilities</p>
                    <p style="font-size: 0.85em; color: #999;">Version: 1.0.0</p>
                    <p style="font-size: 0.85em; color: #999;">Architecture: Meta-Prism (Self-Configuring)</p>
                </div>
            </div>
        </div>
        
        <!-- Action Buttons -->
        <div style="padding: 20px; border-top: 1px solid #e0e0e0; background: white;">
            <div style="display: flex; gap: 10px;">
                <button class="btn-secondary" onclick="toggleSettings()" style="flex: 1;">Close</button>
                <button class="btn-primary" onclick="applySettingsAndContinue()" style="flex: 2;">Apply & Continue →</button>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="header">
            <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
                <img src="/assets/branding/prism_light_128.png" alt="Prism" id="brandingLogo" style="height: 48px; width: auto;">
                <h1 id="brandingTitle" style="margin: 0;">Prism</h1>
            </div>
            <p class="subtitle" id="brandingTagline">Refract complexity into clarity</p>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill" style="width: 20%"></div>
        </div>
        
        <!-- Step 1: Prism Selection -->
        <div class="step active" id="step1">
            <h2>🔷 Choose Your Prism</h2>
            <p>Select the prism that best fits your needs:</p>
            
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
            
            <!-- Invalid packages section -->
            <div id="invalidPackagesSection" style="margin-top: 30px; display: none;">
                <details style="padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 8px;">
                    <summary style="cursor: pointer; font-weight: 600; color: #856404;">
                        ⚠️ <span id="invalidPackagesCount">0</span> Invalid Prism(s) - Click to View
                    </summary>
                    <div id="invalidPackagesList" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #ffeaa7;">
                        <!-- Populated by JS -->
                    </div>
                </details>
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
        
        <!-- Step 3: Prism Tiers (bundled_prisms optional selections) -->
        <div class="step" id="step3">
            <h2>Configuration Tiers</h2>
            <p style="color: #666; margin-bottom: 20px;">Select your optional configuration layers. Required tiers are applied automatically.</p>

            <div id="prismTiersContainer">
                <!-- Populated dynamically by loadPrismTiers() -->
                <p style="color: #999;">Loading tier options...</p>
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
            <h2>✨ Ready to Refract!</h2>
            
            <div id="summary">
                <!-- Populated by JS -->
            </div>
            
            <!-- Configuration Validation Section -->
            <div id="configValidationSection" style="margin-top: 20px; display: none;">
                <h3>Configuration Validation</h3>
                <button class="btn-secondary" onclick="validateConfigs()" id="validateBtn">
                    🔍 Validate Configurations
                </button>
                <div id="validationResults" style="margin-top: 15px;">
                    <!-- Validation results will appear here -->
                </div>
            </div>
            
            <div class="alert alert-warning" style="margin-top: 20px;">
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
        // ========================================
        // PRISM CONFIGURATION (Meta-Prism)
        // ========================================
        
        // Default Prism Configuration
        const DEFAULT_PRISM_CONFIG = {
            theme: 'ocean',
            sources: [
                { url: 'local', name: 'Built-in Prisms', type: 'local' }
            ],
            npmRegistry: '',
            unpkgUrl: ''
        };
        
        // Load Prism Configuration
        function loadPrismConfig() {
            const saved = localStorage.getItem('prismConfig');
            return saved ? JSON.parse(saved) : DEFAULT_PRISM_CONFIG;
        }
        
        // Save Prism Configuration
        function savePrismConfig(config) {
            localStorage.setItem('prismConfig', JSON.stringify(config));
        }
        
        // Current config
        let prismConfig = loadPrismConfig();
        
        // ========================================
        // SETTINGS PANEL
        // ========================================
        
        let currentSettingsStep = 1;
        
        function toggleSettings() {
            const panel = document.getElementById('settingsPanel');
            const overlay = document.getElementById('settingsOverlay');
            const hamburger = document.getElementById('hamburgerMenu');
            
            const isOpening = !panel.classList.contains('open');
            
            panel.classList.toggle('open');
            overlay.classList.toggle('open');
            hamburger.classList.toggle('open');
            
            // If opening, load prisms into step 1
            if (isOpening) {
                loadPrismsIntoSettings();
            }
        }
        
        function goToSettingsStep(stepNum) {
            currentSettingsStep = stepNum;
            
            // Update step buttons
            document.querySelectorAll('.settings-step-btn').forEach(btn => {
                const btnStep = parseInt(btn.dataset.step);
                if (btnStep === stepNum) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
            
            // Update step content
            document.querySelectorAll('.settings-step-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById('settingsStep' + stepNum).classList.add('active');
        }
        
        function loadPrismsIntoSettings() {
            const container = document.getElementById('settingsPrismList');
            
            // Show the prisms from the main packages data
            if (typeof packages !== 'undefined' && packages.length > 0) {
                let html = '';
                packages.forEach(pkg => {
                    const isSelected = selectedPackage === pkg.name;
                    html += `
                        <div class="package-option ${isSelected ? 'active' : ''}" onclick="selectPrismFromSettings('${pkg.name}')" style="margin-bottom: 15px; padding: 15px; border: 2px solid ${isSelected ? 'var(--gradient-1)' : '#e0e0e0'}; border-radius: 8px; cursor: pointer; transition: all 0.3s ease;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="font-size: 2em;">${pkg.emoji}</span>
                                <div style="flex: 1;">
                                    <div style="font-weight: 600; font-size: 1.1em; margin-bottom: 5px;">${pkg.title}</div>
                                    <div style="font-size: 0.9em; color: #666;">${pkg.description}</div>
                                </div>
                                ${isSelected ? '<span style="color: #10b981; font-weight: 600;">✓ Selected</span>' : ''}
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p style="color: #999; text-align: center; padding: 40px;">Loading prisms...</p>';
            }
        }
        
        function selectPrismFromSettings(prismName) {
            selectedPackage = prismName;
            loadPrismsIntoSettings();
        }
        
        function applySettingsAndContinue() {
            // Save all settings
            const npmReg = document.getElementById('settingsNpmRegistry').value.trim();
            if (npmReg) {
                prismConfig.npmRegistry = npmReg;
                savePrismConfig(prismConfig);
            }
            
            // Close settings panel
            toggleSettings();
            
            // If a prism is selected, proceed with installation
            if (selectedPackage) {
                // Trigger the package selection
                selectPackage(selectedPackage);
            }
        }
        
        function exportPrismConfig() {
            const config = JSON.stringify(prismConfig, null, 2);
            const blob = new Blob([config], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'prism-config.json';
            a.click();
            URL.revokeObjectURL(url);
        }
        
        function importPrismConfig() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'application/json';
            input.onchange = (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        try {
                            const config = JSON.parse(event.target.result);
                            prismConfig = config;
                            savePrismConfig(config);
                            
                            // Apply theme
                            document.documentElement.setAttribute('data-theme', config.theme);
                            
                            // Reload UI
                            location.reload();
                        } catch (err) {
                            alert('Invalid config file: ' + err.message);
                        }
                    };
                    reader.readAsText(file);
                }
            };
            input.click();
        }
        
        function resetPrismConfig() {
            if (confirm('Are you sure you want to reset all Prism settings to defaults? This cannot be undone.')) {
                prismConfig = {...DEFAULT_PRISM_CONFIG};
                savePrismConfig(prismConfig);
                location.reload();
            }
        }
        
        function selectTheme(themeName) {
            // Update theme
            document.documentElement.setAttribute('data-theme', themeName);
            
            // Update active state in settings
            document.querySelectorAll('.theme-option').forEach(opt => {
                if (opt.dataset.theme === themeName) {
                    opt.classList.add('active');
                } else {
                    opt.classList.remove('active');
                }
            });
            
            // Save to config
            prismConfig.theme = themeName;
            savePrismConfig(prismConfig);
        }
        
        function addPrismSource() {
            const input = document.getElementById('prismSourceUrl');
            const url = input.value.trim();
            
            if (!url) {
                alert('Please enter a valid URL');
                return;
            }
            
            // Add to config
            prismConfig.sources.push({
                url: url,
                name: url,
                type: 'remote'
            });
            savePrismConfig(prismConfig);
            
            // Clear input
            input.value = '';
            
            // Refresh UI
            renderPrismSources();
            
            // Reload prisms from all sources
            loadPackages();
        }
        
        function removePrismSource(index) {
            prismConfig.sources.splice(index, 1);
            savePrismConfig(prismConfig);
            renderPrismSources();
            loadPackages();
        }
        
        function renderPrismSources() {
            const list = document.getElementById('prismSourcesList');
            list.innerHTML = '';
            
            prismConfig.sources.forEach((source, index) => {
                if (source.type === 'local') {
                    list.innerHTML += `
                        <div class="prism-source-item">
                            <span class="source-url">🔷 ${source.name}</span>
                            <span style="font-size: 0.75em; color: #10b981; font-weight: 600;">DEFAULT</span>
                        </div>
                    `;
                } else {
                    list.innerHTML += `
                        <div class="prism-source-item">
                            <span class="source-url">${source.url}</span>
                            <button class="remove-btn" onclick="removePrismSource(${index})">Remove</button>
                        </div>
                    `;
                }
            });
        }
        
        function saveRegistryConfig() {
            const npmRegistry = document.getElementById('npmRegistry').value.trim();
            
            prismConfig.npmRegistry = npmRegistry;
            savePrismConfig(prismConfig);
            
            alert('✅ Registry configuration saved!');
        }
        
        // Initialize Prism Configuration on load
        (function() {
            // Apply saved theme
            document.documentElement.setAttribute('data-theme', prismConfig.theme);
            
            // Set active theme in settings
            document.querySelectorAll('.theme-option').forEach(opt => {
                if (opt.dataset.theme === prismConfig.theme) {
                    opt.classList.add('active');
                } else {
                    opt.classList.remove('active');
                }
            });
            
            // Render prism sources
            renderPrismSources();
            
            // Set registry values (both in main UI and settings)
            if (prismConfig.npmRegistry) {
                const npmReg = document.getElementById('npmRegistry');
                if (npmReg) npmReg.value = prismConfig.npmRegistry;
                
                const settingsNpmReg = document.getElementById('settingsNpmRegistry');
                if (settingsNpmReg) settingsNpmReg.value = prismConfig.npmRegistry;
            }
        })();
        
        // ========================================
        // INSTALLATION FLOW
        // ========================================
        
        let currentStep = 1;
        const totalSteps = 7;
        let selectedPackage = null;
        let hasOrganizations = false;
        let hasTools = false;
        
        // Determine which steps are active
        function getNextActiveStep(current) {
            let next = current + 1;
            
            // Skip organization step if no organizations
            if (next === 3 && !hasOrganizations) next++;
            // Skip tools step if no tools
            if (next === 4 && !hasTools) next++;
            
            return next;
        }
        
        function getPrevActiveStep(current) {
            let prev = current - 1;
            
            // Skip tools step if no tools (going backwards)
            if (prev === 4 && !hasTools) prev--;
            // Skip organization step if no organizations (going backwards)
            if (prev === 3 && !hasOrganizations) prev--;
            
            return prev;
        }
        
        function updateProgress() {
            const progress = (currentStep / totalSteps) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
        }
        
        function nextStep() {
            // Validate package selection on step 1
            if (currentStep === 1 && !selectedPackage) {
                alert('Please select a prism!');
                return;
            }
            
            document.getElementById('step' + currentStep).classList.remove('active');
            const next = getNextActiveStep(currentStep);
            currentStep = next;
            document.getElementById('step' + currentStep).classList.add('active');
            updateProgress();
            
            // Load data for specific steps
            if (currentStep === 2) loadUserInfoFields();  // Load dynamic fields
            if (currentStep === 3) loadPrismTiers();
            if (currentStep === 4) loadTools();
            if (currentStep === 5) showSummary();
        }
        
        function prevStep() {
            document.getElementById('step' + currentStep).classList.remove('active');
            const prev = getPrevActiveStep(currentStep);
            currentStep = prev;
            document.getElementById('step' + currentStep).classList.add('active');
            updateProgress();
        }
        
        // Track selected sub-prisms: { tierName: subPrismId }
        const selectedSubPrisms = {};

        async function loadPrismTiers() {
            const container = document.getElementById('prismTiersContainer');

            try {
                const response = await fetch(`/api/package/${selectedPackage}/tiers`);
                const data = await response.json();

                if (data.error || !data.optional_tiers || data.optional_tiers.length === 0) {
                    // No optional tiers — skip step automatically
                    hasOrganizations = false;
                    nextStep();
                    return;
                }

                hasOrganizations = true;
                container.innerHTML = '';

                data.optional_tiers.forEach(tier => {
                    const tierDiv = document.createElement('div');
                    tierDiv.className = 'form-group';

                    const label = document.createElement('label');
                    label.textContent = tier.label + (tier.required ? ' *' : '');
                    label.setAttribute('for', 'tier_' + tier.name);

                    const select = document.createElement('select');
                    select.id = 'tier_' + tier.name;
                    select.setAttribute('data-tier', tier.name);

                    const noneOpt = document.createElement('option');
                    noneOpt.value = '';
                    noneOpt.textContent = '(None)';
                    select.appendChild(noneOpt);

                    tier.options.forEach(opt => {
                        const o = document.createElement('option');
                        o.value = opt.id;
                        o.textContent = opt.name + (opt.description ? ' — ' + opt.description : '');
                        select.appendChild(o);
                    });

                    select.addEventListener('change', () => {
                        if (select.value) {
                            selectedSubPrisms[tier.name] = select.value;
                        } else {
                            delete selectedSubPrisms[tier.name];
                        }
                    });

                    tierDiv.appendChild(label);
                    tierDiv.appendChild(select);
                    container.appendChild(tierDiv);
                });
            } catch (err) {
                container.innerHTML = `<p style="color:#ef4444;">Failed to load tiers: ${err.message}</p>`;
            }
        }
        
        async function loadTools() {
            // Get package-specific metadata
            const metadataResponse = await fetch(`/api/package/${selectedPackage}/metadata`);
            const metadata = await metadataResponse.json();
            
            // Check if THIS package has tools
            hasTools = metadata.has_tools;
            
            if (!hasTools) {
                // Skip this step automatically - this package doesn't use tools
                nextStep();
                return;
            }
            
            // Load actual tools data
            const response = await fetch('/api/tools');
            const data = await response.json();
            
            const toolsList = document.getElementById('toolsList');
            toolsList.innerHTML = '';
            
            if (data.tools && data.tools.length > 0) {
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
        }
        
        async function showSummary() {
            // Fetch package metadata to know what to show
            const metadataResponse = await fetch(`/api/package/${selectedPackage}/metadata`);
            const metadata = await metadataResponse.json();
            
            // Collect all user info field values
            const userInfoFields = document.querySelectorAll('#userInfoFields input');
            let userInfoHTML = '';
            userInfoFields.forEach(input => {
                if (input.value) {
                    const label = input.previousElementSibling?.previousElementSibling?.textContent.replace('*', '').trim() || input.name;
                    userInfoHTML += `<p><strong>${label}:</strong> ${input.value}</p>`;
                }
            });
            
            // Build summary based on what this prism actually has
            let summaryHTML = `
                <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(240, 147, 251, 0.05) 100%); padding: 20px; border-radius: 12px; border: 2px solid transparent; background-clip: padding-box; position: relative;">
                    <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%); border-radius: 10px; opacity: 0.1; z-index: -1;"></div>
                    <h3 style="margin-top: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">🔷 ${metadata.display_name || selectedPackage}</h3>
                    ${metadata.description ? `<p style="color: #666; margin-bottom: 20px;">${metadata.description}</p>` : ''}
                    <hr style="border-color: rgba(102, 126, 234, 0.2);">
            `;
            
            // User Information section (always shown if there are fields)
            if (userInfoHTML) {
                summaryHTML += `
                    <h4>👤 User Information:</h4>
                    <div style="background: white; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
                        ${userInfoHTML}
                    </div>
                `;
            }
            
            // Configuration Tiers section (bundled_prisms optional selections)
            if (hasOrganizations && Object.keys(selectedSubPrisms).length > 0) {
                let tierRows = '';
                for (const [tierName, subId] of Object.entries(selectedSubPrisms)) {
                    const select = document.getElementById('tier_' + tierName);
                    const label = select ? (select.options[select.selectedIndex]?.text || subId) : subId;
                    const tierLabel = tierName.charAt(0).toUpperCase() + tierName.slice(1).replace(/_/g, ' ');
                    tierRows += `<p><strong>${tierLabel}:</strong> ${label}</p>`;
                }
                summaryHTML += `
                    <h4>🔷 Configuration Tiers:</h4>
                    <div style="background: white; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
                        ${tierRows}
                    </div>
                `;
            } else if (hasOrganizations) {
                summaryHTML += `
                    <h4>🔷 Configuration Tiers:</h4>
                    <div style="background: white; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
                        <p style="color: #999;"><em>No optional tiers selected (required tiers applied automatically)</em></p>
                    </div>
                `;
            }

            // Tools section (only if package has tools)
            if (metadata.has_tools) {
                const toolCheckboxes = document.querySelectorAll('#toolsList input[type="checkbox"]:checked');
                const selectedTools = Array.from(toolCheckboxes).map(cb => cb.nextElementSibling?.textContent || '').filter(t => t);
                
                summaryHTML += `
                    <h4>🛠️ Tools:</h4>
                    <div style="background: white; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
                        ${selectedTools.length > 0 ? 
                            `<p><strong>${selectedTools.length} tool(s) selected:</strong> ${selectedTools.join(', ')}</p>` : 
                            `<p style="color: #999;"><em>No tools selected</em></p>`
                        }
                    </div>
                `;
            }
            
            summaryHTML += '</div>';
            
            document.getElementById('summary').innerHTML = summaryHTML;
            
            // Show validation section
            document.getElementById('configValidationSection').style.display = 'block';
        }
        
        async function validateConfigs() {
            const btn = document.getElementById('validateBtn');
            const resultsDiv = document.getElementById('validationResults');
            
            // Show loading state
            btn.disabled = true;
            btn.textContent = '⏳ Validating...';
            resultsDiv.innerHTML = '<p style="color: #666;">Validating prism...</p>';
            
            try {
                const response = await fetch(`/api/package/${selectedPackage}/validate-configs`);
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `
                        <div class="alert alert-warning">
                            <strong>❌ Validation Error</strong><br>
                            ${data.error}
                        </div>
                    `;
                    btn.disabled = false;
                    btn.textContent = '🔍 Validate Configurations';
                    return;
                }
                
                const summary = data.summary;
                
                if (data.valid) {
                    // All configs valid
                    resultsDiv.innerHTML = `
                        <div class="alert alert-info" style="background: #d4edda; border-color: #c3e6cb; color: #155724;">
                            <strong>✅ Prism Valid!</strong><br>
                            <div style="margin-top: 10px; font-size: 0.9em;">
                                📊 Validated ${summary.total_files} file(s)<br>
                                ${summary.total_warnings > 0 ? `⚠️ ${summary.total_warnings} warning(s) - review recommended` : ''}
                            </div>
                        </div>
                    `;
                } else {
                    // Some configs invalid
                    let errorDetails = '';
                    if (data.results) {
                        data.results.forEach(result => {
                            if (!result.valid) {
                                errorDetails += `
                                    <div style="margin-top: 10px; padding: 10px; background: #f8d7da; border-left: 3px solid #dc3545; border-radius: 4px;">
                                        <strong>📄 ${result.file}</strong>
                                        <ul style="margin: 5px 0 0 20px; font-size: 0.9em;">
                                            ${result.errors.map(err => `<li>${err}</li>`).join('')}
                                        </ul>
                                    </div>
                                `;
                            }
                        });
                    }
                    
                    resultsDiv.innerHTML = `
                        <div class="alert alert-warning" style="background: #fff3cd; border-color: #ffc107; color: #856404;">
                            <strong>⚠️ Configuration Validation Failed</strong><br>
                            <div style="margin-top: 10px; font-size: 0.9em;">
                                ❌ ${summary.invalid_files} of ${summary.total_files} files have errors<br>
                                📋 ${summary.total_errors} error(s) found
                            </div>
                            <details style="margin-top: 15px;">
                                <summary style="cursor: pointer; font-weight: 600;">📋 View Error Details</summary>
                                ${errorDetails}
                            </details>
                            <div style="margin-top: 15px; padding: 10px; background: #fff; border-radius: 4px;">
                                <strong>🔧 What to do:</strong><br>
                                These errors won't prevent installation, but may cause issues.<br>
                                Contact your admin or fix the prism files before installing.
                            </div>
                        </div>
                    `;
                }
            } catch (error) {
                resultsDiv.innerHTML = `
                    <div class="alert alert-warning">
                        <strong>❌ Failed to validate</strong><br>
                        ${error.message}
                    </div>
                `;
            }
            
            // Re-enable button
            btn.disabled = false;
            btn.textContent = '🔍 Validate Configurations';
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
                        unpkgUrl: unpkgUrl,
                        selectedSubPrisms: selectedSubPrisms
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Show all progress messages
                    if (result.progress) {
                        for (let msg of result.progress) {
                            const emoji = {
                                'success': '✅',
                                'error': '❌',
                                'warning': '⚠️',
                                'info': 'ℹ️'
                            }[msg.level] || 'ℹ️';
                            
                            const color = {
                                'success': '#10b981',
                                'error': '#ef4444',
                                'warning': '#f59e0b',
                                'info': '#3b82f6'
                            }[msg.level] || '#3b82f6';
                            
                            logOutput.innerHTML += `<div style="color: ${color};">${emoji} ${msg.message}</div>`;
                            logOutput.scrollTop = logOutput.scrollHeight;
                            await new Promise(resolve => setTimeout(resolve, 100));
                        }
                    }
                    
                    logOutput.innerHTML += `<div style="color: #10b981; margin-top: 20px;">✅ <strong>Installation complete!</strong></div>`;
                    if (result.workspace) {
                        logOutput.innerHTML += `<div style="margin-top: 10px;">📁 Workspace: ${result.workspace}</div>`;
                    }
                    
                    // Go to complete
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    currentStep = 7;
                    document.getElementById('step6').classList.remove('active');
                    document.getElementById('step7').classList.add('active');
                    updateProgress();
                } else {
                    logOutput.innerHTML += `<div style="color: #ef4444; margin-top: 20px;">❌ <strong>Error:</strong> ${result.error}</div>`;
                }
            } catch (error) {
                logOutput.innerHTML += `<div style="color: #ef4444; margin-top: 20px;">❌ <strong>Error:</strong> ${error.message}</div>`;
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
                            <strong>⚠️ Could not load prisms from registry</strong><br>
                            Using local prisms. Error: ${data.error}
                        </div>
                    `;
                }
                
                const packagesList = document.getElementById('packagesList');
                
                // Show stats if available
                if (data.stats) {
                    console.log(`📊 Package stats: ${data.stats.valid} valid, ${data.stats.invalid} invalid (${data.stats.total} total)`);
                }
                
                // Render valid packages
                if (data.packages && data.packages.length > 0) {
                    packagesList.innerHTML = '';

                    // Sort: default prism first, then alphabetical
                    const sorted = [...data.packages].sort((a, b) => {
                        if (a.default && !b.default) return -1;
                        if (!a.default && b.default) return 1;
                        return a.name.localeCompare(b.name);
                    });

                    sorted.forEach(pkg => {
                        const displayName = pkg.displayName || pkg.name || pkg.id;
                        const description = pkg.description || 'No description available';
                        const version = pkg.version || 'latest';
                        const source = pkg.source || 'local';
                        const sourceIcon = source === 'npm' ? '🌐' : '📁';
                        const sourceBadge = `<span style="background: ${source === 'npm' ? '#10b981' : '#6b7280'}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">${sourceIcon} ${source}</span>`;
                        
                        // Show warnings badge if any
                        let warningsBadge = '';
                        if (pkg.warnings && pkg.warnings.length > 0) {
                            warningsBadge = `<span style="background: #ffc107; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-left: 5px;">⚠️ ${pkg.warnings.length} warning(s)</span>`;
                        }
                        
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
                                            <strong>Source:</strong> ${sourceBadge}${warningsBadge}
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
                            <strong>⚠️ No valid prisms found!</strong><br>
                            Please check your registry configuration or ensure local prisms exist.
                        </div>
                    `;
                }
                
                // Auto-select the default prism if one exists
                const defaultPkg = data.packages.find(pkg => pkg.default);
                if (defaultPkg) {
                    await selectPackage(defaultPkg.id);
                }

                // Render invalid packages section
                if (data.invalid_packages && data.invalid_packages.length > 0) {
                    const invalidSection = document.getElementById('invalidPackagesSection');
                    const invalidList = document.getElementById('invalidPackagesList');
                    const invalidCount = document.getElementById('invalidPackagesCount');
                    
                    invalidSection.style.display = 'block';
                    invalidCount.textContent = data.invalid_packages.length;
                    
                    invalidList.innerHTML = '';
                    data.invalid_packages.forEach(pkg => {
                        let errorsHtml = '<ul style="margin: 10px 0; padding-left: 20px; color: #721c24;">';
                        pkg.errors.forEach(error => {
                            errorsHtml += `<li>${error}</li>`;
                        });
                        errorsHtml += '</ul>';
                        
                        invalidList.innerHTML += `
                            <div style="background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                                <h4 style="margin: 0 0 5px 0; color: #721c24;">❌ ${pkg.name}</h4>
                                <p style="margin: 0 0 10px 0; color: #856404; font-size: 0.9em;">📁 ${pkg.path}</p>
                                <div style="font-size: 0.9em;">
                                    <strong style="color: #721c24;">Errors:</strong>
                                    ${errorsHtml}
                                </div>
                            </div>
                        `;
                    });
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
        
        async function selectPackage(packageName) {
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
            
            // Load and apply prism_config from selected package
            await loadAndApplyPrismConfig(packageName);
        }
        
        async function loadAndApplyPrismConfig(packageName) {
            try {
                const response = await fetch(`/api/package/${packageName}/config`);
                const data = await response.json();
                
                if (data.prism_config) {
                    console.log(`📦 Applying prism_config from ${packageName}:`, data.prism_config);
                    
                    // Apply theme if specified
                    if (data.prism_config.theme) {
                        const theme = data.prism_config.theme;
                        document.documentElement.setAttribute('data-theme', theme);
                        
                        // Update theme selection in settings
                        document.querySelectorAll('.theme-option').forEach(opt => {
                            if (opt.dataset.theme === theme) {
                                opt.classList.add('active');
                            } else {
                                opt.classList.remove('active');
                            }
                        });
                        
                        // Save to prismConfig
                        prismConfig.theme = theme;
                        savePrismConfig(prismConfig);
                    }
                    
                    // Apply sources if specified
                    if (data.prism_config.sources && data.prism_config.sources.length > 0) {
                        // Merge with existing sources (don't duplicate)
                        data.prism_config.sources.forEach(newSource => {
                            const exists = prismConfig.sources.some(s => s.url === newSource.url);
                            if (!exists && newSource.type !== 'local') {  // Don't duplicate local
                                prismConfig.sources.push(newSource);
                            }
                        });
                        savePrismConfig(prismConfig);
                        renderPrismSources();
                    }
                    
                    // Apply npm registry if specified
                    if (data.prism_config.npm_registry) {
                        prismConfig.npmRegistry = data.prism_config.npm_registry;
                        savePrismConfig(prismConfig);
                        
                        const npmReg = document.getElementById('npmRegistry');
                        if (npmReg) npmReg.value = data.prism_config.npm_registry;
                        
                        const settingsNpmReg = document.getElementById('settingsNpmRegistry');
                        if (settingsNpmReg) settingsNpmReg.value = data.prism_config.npm_registry;
                    }
                    
                    // Apply branding if specified
                    if (data.prism_config.branding) {
                        const branding = data.prism_config.branding;

                        if (branding.name) {
                            document.getElementById('brandingTitle').textContent = branding.name;
                            document.title = branding.name + ' Installer';
                        }

                        if (branding.tagline) {
                            document.getElementById('brandingTagline').textContent = branding.tagline;
                        }

                        if (branding.primary_color) {
                            document.documentElement.style.setProperty('--gradient-1', branding.primary_color);
                            document.documentElement.style.setProperty('--gradient-4', branding.primary_color);
                        }

                        if (branding.secondary_color) {
                            document.documentElement.style.setProperty('--gradient-2', branding.secondary_color);
                        }
                    }

                    // Show notification that config was applied
                    console.log(`✅ Prism configuration from ${packageName} applied successfully`);
                } else {
                    console.log(`ℹ️ No prism_config found in ${packageName}, using default configuration`);
                }
            } catch (error) {
                console.error(`Failed to load prism_config for ${packageName}:`, error);
                // Don't block - just use default config
            }
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


def _find_package(package_name):
    """Find a package by name or directory name. Returns (pkg_dict, pkg_path) or (None, None)."""
    import sys

    sys.path.insert(0, str(Path(__file__).parent / "scripts"))
    from package_manager import PackageManager

    pm = PackageManager(root_dir=ROOT_DIR)
    packages = pm.discover_packages()
    # Try exact name match first, then directory name match
    pkg = next((p for p in packages if p["name"] == package_name), None)
    if not pkg:
        pkg = next((p for p in packages if Path(p["path"]).name == package_name), None)
    if not pkg:
        return None, None
    pkg_path = Path(pkg["path"])
    return pkg, pkg_path


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    """Serve static assets (branding, etc.)"""
    return send_from_directory(ROOT_DIR / "assets", filename)


@app.route("/")
def index():
    """Main installer UI"""
    return render_template_string(INDEX_HTML)


@app.route("/api/packages")
def get_packages():
    """Get available config packages with validation"""
    import sys

    sys.path.insert(0, str(Path(__file__).parent / "scripts"))

    try:
        from package_validator import validate_all_packages

        packages_dir = ROOT_DIR / "prisms"
        valid_packages, invalid_packages = validate_all_packages(packages_dir)

        # Format valid packages
        formatted_valid = []
        for pkg in valid_packages:
            formatted_valid.append(
                {
                    "id": pkg["id"],
                    "name": pkg["name"],
                    "displayName": pkg["name"].replace("-config", "").replace("-", " ").title(),
                    "description": pkg["description"],
                    "version": pkg["version"],
                    "source": "local",
                    "path": pkg["path"],
                    "warnings": pkg.get("warnings", []),
                    "default": pkg.get("default", False),
                }
            )

        # Format invalid packages
        formatted_invalid = []
        for pkg in invalid_packages:
            formatted_invalid.append(
                {
                    "id": pkg["id"],
                    "name": pkg["name"],
                    "description": pkg["description"],
                    "errors": pkg["errors"],
                    "path": pkg["path"],
                }
            )

        return jsonify(
            {
                "packages": formatted_valid,
                "invalid_packages": formatted_invalid,
                "stats": {
                    "valid": len(valid_packages),
                    "invalid": len(invalid_packages),
                    "total": len(valid_packages) + len(invalid_packages),
                },
            }
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"packages": [], "invalid_packages": [], "error": str(e)})


@app.route("/api/package/<package_id>/validate-configs")
def validate_package_configs(package_id):
    """Validate all configuration files in a package"""
    import sys

    sys.path.insert(0, str(Path(__file__).parent / "scripts"))

    try:
        from config_validator import PackageConfigValidator

        packages_dir = ROOT_DIR / "prisms"
        package_path = packages_dir / package_id

        if not package_path.exists():
            return jsonify({"valid": False, "error": f"Package not found: {package_id}"})

        # Run validation
        validator = PackageConfigValidator(package_path)
        all_valid, results = validator.validate_package_configs()
        summary = validator.get_summary(results)

        return jsonify({"valid": all_valid, "summary": summary, "results": results})
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"valid": False, "error": str(e)})


@app.route("/api/package/<package_name>/metadata")
def get_package_metadata(package_name):
    """Get package metadata (what sections/features are available)"""
    import yaml

    try:
        pkg, pkg_path = _find_package(package_name)

        if not pkg:
            return jsonify({"error": "Package not found"})

        # Load package.yaml
        pkg_yaml_path = pkg_path / "package.yaml"

        if not pkg_yaml_path.exists():
            return jsonify({"error": "package.yaml not found"})

        with open(pkg_yaml_path) as f:
            pkg_config = yaml.safe_load(f)

        package_section = pkg_config.get("package", {})
        bundled_prisms = pkg_config.get("bundled_prisms", {})

        # Detect optional tiers (tiers where not all items are required)
        has_tiers = bool(bundled_prisms)
        has_optional_tiers = any(
            any(not item.get("required", False) for item in items)
            for items in bundled_prisms.values()
            if isinstance(items, list)
        )

        # Check for tools in merged config
        has_tools = (
            "tools_required" in pkg_config
            or "tools_selected" in pkg_config
            or "tools" in package_section
            or "tools" in pkg_config
        )

        # Get user info fields count
        user_fields = pkg_config.get("user_info_fields", package_section.get("user_info_fields", []))

        # Get package display info
        display_name = package_section.get("name", package_name)
        description = package_section.get("description", "")

        metadata = {
            "name": package_name,
            "display_name": display_name,
            "description": description,
            "has_tiers": has_tiers,
            "has_optional_tiers": has_optional_tiers,
            # Legacy compat fields (always False now — use tiers API instead)
            "has_sub_orgs": False,
            "has_departments": False,
            "has_teams": False,
            "has_tools": has_tools,
            "user_fields_count": len(user_fields or []),
            "package_type": package_section.get("type", "company"),
        }

        return jsonify(metadata)
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)})


@app.route("/api/package/<package_name>/tiers")
def get_package_tiers(package_name):
    """Return the bundled_prisms tier structure for a package (optional tiers only)."""
    import yaml

    try:
        pkg, pkg_path = _find_package(package_name)

        if not pkg:
            return jsonify({"error": "Package not found", "optional_tiers": []})

        pkg_yaml_path = pkg_path / "package.yaml"

        if not pkg_yaml_path.exists():
            return jsonify({"error": "package.yaml not found", "optional_tiers": []})

        with open(pkg_yaml_path) as f:
            pkg_config = yaml.safe_load(f)

        bundled_prisms = pkg_config.get("bundled_prisms", {})

        # Collect optional tiers (tiers that have at least one non-required item)
        optional_tiers = []
        for tier_name, items in bundled_prisms.items():
            if not isinstance(items, list):
                continue
            optional_items = [item for item in items if not item.get("required", False)]
            if not optional_items:
                continue  # skip fully-required tiers
            optional_tiers.append(
                {
                    "name": tier_name,
                    "label": tier_name.replace("_", " ").title(),
                    "required": False,
                    "options": [
                        {
                            "id": item.get("id", ""),
                            "name": item.get("name", item.get("id", "")),
                            "description": item.get("description", ""),
                        }
                        for item in optional_items
                    ],
                }
            )

        return jsonify({"optional_tiers": optional_tiers})

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e), "optional_tiers": []})


@app.route("/api/package/<package_name>/user-fields")
def get_user_fields(package_name):
    """Get user info fields for a specific package"""
    import yaml

    try:
        pkg, pkg_path = _find_package(package_name)

        if not pkg:
            return jsonify({"fields": [], "error": "Package not found"})

        # Load package.yaml to get user_info_fields
        pkg_yaml_path = pkg_path / "package.yaml"

        if not pkg_yaml_path.exists():
            return jsonify({"fields": [], "error": "package.yaml not found"})

        with open(pkg_yaml_path) as f:
            pkg_config = yaml.safe_load(f)

        # Get user_info_fields from package config (can be at root or under 'package')
        fields = pkg_config.get("user_info_fields", pkg_config.get("package", {}).get("user_info_fields", []))

        # If no fields defined, use defaults
        if not fields:
            fields = [
                {"id": "name", "label": "Full Name", "type": "text", "required": True, "placeholder": "John Doe"},
                {
                    "id": "email",
                    "label": "Email",
                    "type": "email",
                    "required": True,
                    "placeholder": "john.doe@example.com",
                },
            ]

        return jsonify({"fields": fields})
    except Exception as e:
        return jsonify({"fields": [], "error": str(e)})


@app.route("/api/package/<package_name>/config")
def get_package_config(package_name):
    """Get prism_config from a package for meta-prism configuration"""
    import yaml

    try:
        pkg, pkg_path = _find_package(package_name)

        if not pkg:
            return jsonify({"prism_config": None, "error": "Package not found"})

        # Load package.yaml to get prism_config
        pkg_yaml_path = pkg_path / "package.yaml"

        if not pkg_yaml_path.exists():
            return jsonify({"prism_config": None, "error": "package.yaml not found"})

        with open(pkg_yaml_path) as f:
            pkg_config = yaml.safe_load(f)

        # Get prism_config section
        prism_config = pkg_config.get("prism_config", None)

        return jsonify({"prism_config": prism_config, "package_name": package_name})
    except Exception as e:
        return jsonify({"prism_config": None, "error": str(e)})


@app.route("/api/organizations")
def get_organizations():
    """Get available organizations from config"""
    # Load from inheritance.yaml
    inheritance_path = CONFIG_DIR / "inheritance.yaml"

    if not inheritance_path.exists():
        return jsonify({"sub_orgs": [], "departments": [], "teams": []})

    with open(inheritance_path) as f:
        config = yaml.safe_load(f)

    return jsonify(
        {
            "sub_orgs": config.get("available_sub_orgs", []),
            "departments": config.get("available_departments", []),
            "teams": config.get("available_teams", []),
        }
    )


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
        tools.append(
            {
                "id": tool_id,
                "name": tool_id.replace("-", " ").title(),
                "description": tool_config.get("description", ""),
                "required": tool_config.get("required", False),
            }
        )

    return jsonify({"tools": tools})


@app.route("/api/install", methods=["POST"])
def install():
    """Run the actual installation"""
    data = request.json

    try:
        import sys

        sys.path.insert(0, str(ROOT_DIR / "scripts"))
        sys.path.insert(0, str(ROOT_DIR))
        from npm_package_fetcher import fetch_package

        from installer_engine import InstallationEngine

        prism_id = (data.get("package") or "").strip()
        user_info = data.get("userInfo", {})
        registry = data.get("registry", None)
        unpkg_url = data.get("unpkgUrl", None)
        selected_sub_prisms = data.get("selectedSubPrisms", {})
        tools_selected = data.get("toolsSelected", [])
        tools_excluded = data.get("toolsExcluded", [])

        # Reject empty prism id immediately
        if not prism_id:
            return jsonify({"success": False, "error": "No prism specified"}), 400

        # Set registry env vars if provided
        if registry:
            os.environ["PRISM_NPM_REGISTRY"] = registry
        if unpkg_url:
            os.environ["PRISM_UNPKG_URL"] = unpkg_url

        # Resolve package path: try local first, then remote fetch
        local_path = ROOT_DIR / "prisms" / prism_id
        package_path = None

        if local_path.exists() and (local_path / "package.yaml").exists():
            package_path = str(local_path)
        else:
            npm_name = prism_id if prism_id.startswith("@prism/") else f"@prism/{prism_id}"
            dest_dir = ROOT_DIR / "temp_install" / prism_id
            dest_dir.parent.mkdir(exist_ok=True)
            try:
                result = fetch_package(npm_name, "latest", str(dest_dir), unpkg_url)
                if result:
                    package_path = result
            except Exception as e:
                print(f"Package fetch failed: {e}")

        if not package_path:
            return jsonify({"success": False, "error": f"Prism not found: {prism_id}"}), 404

        # Run full installation using shared engine
        progress_log = []

        def progress_callback(step, message, level):
            """Collect progress messages"""
            progress_log.append({"step": step, "message": message, "level": level})

        engine = InstallationEngine(
            config_package=package_path,
            user_info=user_info,
            selected_sub_prisms=selected_sub_prisms,
            tools_selected=tools_selected,
            tools_excluded=tools_excluded,
            progress_callback=progress_callback,
        )

        # Run installation
        engine.install()

        return jsonify(
            {
                "success": True,
                "message": "Installation completed successfully!",
                "workspace": str(engine.workspace),
                "progress": progress_log,
            }
        )

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
