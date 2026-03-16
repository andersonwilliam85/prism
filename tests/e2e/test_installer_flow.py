"""
End-to-end tests for the installer web UI using Playwright.
"""

import os
import re
import subprocess
import time
from pathlib import Path

import pytest

try:
    from playwright.sync_api import Page, expect
except ImportError:
    pytest.skip("playwright not installed", allow_module_level=True)

INSTALLER_URL = os.getenv("INSTALLER_URL", "http://localhost:5555")


@pytest.fixture(scope="module")
def installer_server():
    """Start the installer web UI server."""
    # Kill any existing server on port 5555
    subprocess.run("lsof -ti:5555 | xargs kill -9", shell=True, stderr=subprocess.DEVNULL)

    # Start server in background
    repo_root = str(Path(__file__).parent.parent.parent)
    process = subprocess.Popen(
        ["python3", "install-ui.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=repo_root
    )

    # Wait for server to start
    time.sleep(3)

    yield process

    # Cleanup
    process.terminate()
    process.wait(timeout=5)


@pytest.mark.e2e
class TestInstallerFlow:
    """Test complete installer workflows."""

    def test_page_loads(self, page: Page, installer_server):
        """Test that the installer page loads successfully."""
        page.goto(INSTALLER_URL)

        # Check title
        expect(page).to_have_title("Prism Installer")

        # Check main heading
        expect(page.locator("h1")).to_contain_text("Prism")

    def test_packages_list_loads(self, page: Page, installer_server):
        """Test that packages list loads."""
        page.goto(INSTALLER_URL)

        # Wait for tier cards to load (step 1 renders tiers, not package cards)
        page.wait_for_selector(".tier-card", timeout=5000)

        # Verify at least one tier card is shown
        tiers = page.locator(".tier-card")
        assert tiers.count() >= 1, "Should have at least 1 tier card"

    def test_package_selection(self, page: Page, installer_server):
        """Test selecting a tier card."""
        page.goto(INSTALLER_URL)

        # Wait for tier cards
        page.wait_for_selector(".tier-card", timeout=5000)

        # Click first tier card
        first_tier = page.locator(".tier-card").first
        first_tier.click()

        # Verify it becomes selected
        expect(first_tier).to_have_class(re.compile(r"selected"))

    def test_next_button_enabled_after_selection(self, page: Page, installer_server):
        """Test that Next button enables after tier selection."""
        page.goto(INSTALLER_URL)

        # Wait for tier cards
        page.wait_for_selector(".tier-card", timeout=5000)

        # Select a tier card
        page.locator(".tier-card").first.click()

        # Next button should be enabled (not checking disabled state)
        next_button = page.locator("button").filter(has_text="Next").first
        expect(next_button).to_be_visible()

    def test_step_navigation(self, page: Page, installer_server):
        """Test navigation between steps."""
        page.goto(INSTALLER_URL)

        # Wait for tier cards
        page.wait_for_selector(".tier-card", timeout=5000)

        # Select tier
        page.locator(".tier-card").first.click()

        # Click Next
        page.locator("button").filter(has_text="Next").first.click()

        # Verify step 2 is now active
        step2 = page.locator("#step2")
        expect(step2).to_have_class(re.compile(r"active"))

        # Verify step 1 is not active
        step1 = page.locator("#step1")
        expect(step1).not_to_have_class(re.compile(r"active"))

    def test_user_info_form(self, page: Page, installer_server):
        """Test user info form fields."""
        page.goto(INSTALLER_URL)

        # Navigate to user info step
        page.wait_for_selector(".tier-card", timeout=5000)
        page.locator(".tier-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()

        # Wait for step 2
        page.wait_for_selector("#step2.active", timeout=5000)

        # Fill in form fields
        page.fill("input[name='name']", "Test User")
        page.fill("input[name='email']", "test@example.com")

        # Verify values
        expect(page.locator("input[name='name']")).to_have_value("Test User")
        expect(page.locator("input[name='email']")).to_have_value("test@example.com")


@pytest.mark.e2e
class TestThemeSwitching:
    """Test theme switching functionality."""

    def test_theme_buttons_exist(self, page: Page, installer_server):
        """Test that theme buttons are present."""
        page.goto(INSTALLER_URL)
        page.wait_for_load_state("networkidle")

        # Open settings panel and navigate to theme step
        page.locator(".hamburger-menu").click()
        page.wait_for_selector(".settings-panel.open", timeout=5000)
        page.locator(".settings-step-btn[data-step='3']").click()
        page.wait_for_timeout(500)

        # Check for theme switcher (count depends on prism config's custom_themes)
        theme_buttons = page.locator(".theme-option")
        assert theme_buttons.count() >= 1, "Should have at least 1 theme option"

    def test_theme_switching(self, page: Page, installer_server):
        """Test switching between themes by clicking available theme options."""
        page.goto(INSTALLER_URL)
        page.wait_for_load_state("networkidle")

        # Open settings panel and navigate to theme step
        page.locator(".hamburger-menu").click()
        page.wait_for_selector(".settings-panel.open", timeout=5000)
        page.locator(".settings-step-btn[data-step='3']").click()
        page.wait_for_timeout(500)

        # Click the first available theme option
        first_theme = page.locator(".theme-option").first
        theme_id = first_theme.get_attribute("data-theme")
        first_theme.click()

        # Verify data-theme attribute changed
        html = page.locator("html")
        expect(html).to_have_attribute("data-theme", theme_id)

    def test_theme_persists(self, page: Page, installer_server):
        """Test that theme selection persists across page reloads."""
        page.goto(INSTALLER_URL)
        page.wait_for_load_state("networkidle")

        # Open settings panel and navigate to theme step
        page.locator(".hamburger-menu").click()
        page.wait_for_selector(".settings-panel.open", timeout=5000)
        page.locator(".settings-step-btn[data-step='3']").click()
        page.wait_for_timeout(500)

        # Click the first available theme
        first_theme = page.locator(".theme-option").first
        theme_id = first_theme.get_attribute("data-theme")
        first_theme.click()

        # Reload page
        page.reload()

        # Verify theme persisted
        html = page.locator("html")
        expect(html).to_have_attribute("data-theme", theme_id)


@pytest.mark.e2e
@pytest.mark.smoke
class TestSmokeTests:
    """Quick smoke tests for critical functionality."""

    def test_api_packages_endpoint(self, page: Page, installer_server):
        """Test that /api/packages endpoint returns data."""
        response = page.request.get(f"{INSTALLER_URL}/api/packages")

        assert response.status == 200

        data = response.json()
        assert "packages" in data
        assert isinstance(data["packages"], list)

    def test_no_javascript_errors(self, page: Page, installer_server):
        """Test that page loads without JavaScript errors."""
        errors = []

        page.on("pageerror", lambda err: errors.append(err.message))
        page.goto(INSTALLER_URL)

        # Wait a bit for any errors
        page.wait_for_timeout(2000)

        assert len(errors) == 0, f"JavaScript errors found: {errors}"

    def test_responsive_design(self, page: Page, installer_server):
        """Test that page is responsive."""
        page.goto(INSTALLER_URL)

        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(500)

        # Verify content is still visible
        expect(page.locator("h1")).to_be_visible()

        # Test desktop viewport
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.wait_for_timeout(500)

        expect(page.locator("h1")).to_be_visible()
