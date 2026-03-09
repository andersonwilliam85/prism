#!/usr/bin/env python3
"""
Web UI for Dev Onboarding Installer

Launches a local web interface for configuring and running the installer.

Usage:
    python3 install-ui.py

    Opens browser to: http://localhost:5555
"""

import threading
import webbrowser
from pathlib import Path

from prism.ui.app import create_app

ROOT_DIR = Path(__file__).parent

# Create the app via HD composition root
app = create_app(prisms_dir=ROOT_DIR / "prisms")


def open_browser():
    """Open browser after short delay."""
    import time

    time.sleep(1.5)
    webbrowser.open("http://localhost:5555")


if __name__ == "__main__":
    print("\n  Starting Dev Onboarding UI...")
    print("     Opening browser to http://localhost:5555\n")

    # Open browser in background
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Flask
    app.run(host="localhost", port=5555, debug=False)
