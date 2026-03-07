"""Shared fixtures for Prism tests."""

from __future__ import annotations

import pytest
from pathlib import Path


@pytest.fixture
def prisms_dir() -> Path:
    """Path to the bundled prisms directory."""
    return Path(__file__).parent.parent / "prisms"


@pytest.fixture
def sample_user_info() -> dict[str, str]:
    return {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "github_username": "janedoe",
    }


@pytest.fixture
def sample_package_config() -> dict:
    return {
        "package": {
            "name": "test-prism",
            "version": "1.0.0",
            "description": "A test prism",
            "type": "prism",
        },
        "prism_config": {
            "theme": "ocean",
        },
        "user_info_fields": [
            {"id": "full_name", "label": "Full Name", "type": "text", "required": True},
            {"id": "email", "label": "Email", "type": "email", "required": True},
        ],
    }
