"""Flask app factory — creates the app and registers blueprints.

This is the Experience layer: it composes all API flows into a
single application, wires DI via Container, and serves the UI.

Volatility: low — app wiring is stable; routes evolve via blueprints.
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template

from prism.container import Container

TEMPLATE_DIR = Path(__file__).parent / "templates"


def create_app(prisms_dir: Path | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        prisms_dir: Path to the prisms directory. Defaults to repo root / prisms.
    """
    app = Flask(__name__, template_folder=str(TEMPLATE_DIR))

    # Build the DI container — single source of truth for all wiring
    container = Container(prisms_dir=prisms_dir)
    app.config["container"] = container
    app.config["prisms_dir"] = container._prisms_dir

    # Register blueprints (API flows)
    from prism.ui.api.configuration import configuration_bp
    from prism.ui.api.installation import installation_bp
    from prism.ui.api.packages import packages_bp
    from prism.ui.api.validation import validation_bp

    app.register_blueprint(packages_bp)
    app.register_blueprint(installation_bp)
    app.register_blueprint(validation_bp)
    app.register_blueprint(configuration_bp)

    # Index route — serves the installer UI
    @app.route("/")
    def index():
        return render_template("index.html")

    return app
