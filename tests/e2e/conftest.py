"""E2E test fixtures using the HD Container.

Provides a Flask test client backed by the real Container (not mocks).
Tests use actual prism packages from the prisms/ directory.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from prism.ui.app import create_app


@pytest.fixture(scope="session")
def prisms_dir() -> Path:
    """Path to the real prisms directory."""
    return Path(__file__).parent.parent.parent / "prisms"


@pytest.fixture(scope="session")
def e2e_app(prisms_dir):
    """Flask app backed by real Container — session-scoped for performance."""
    app = create_app(prisms_dir=prisms_dir)
    app.config["TESTING"] = True
    return app


@pytest.fixture(scope="session")
def e2e_client(e2e_app):
    """Flask test client for e2e tests."""
    return e2e_app.test_client()
