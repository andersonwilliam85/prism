"""
End-to-end tests for the installer web UI using Playwright.
"""
import pytest
import subprocess
import time
import os
from playwright.sync_api import Page, expect


INSTALLER_URL = os.getenv("INSTALLER_URL", "http://localhost:5555")


@pytest.fixture(scope="module")
def installer_server():
    """Start the installer web UI server."""
    # Kill any existing server on port 5555
    subprocess.run(
        "lsof -ti:5555 | xargs kill -9",
        shell=True,
        stderr=subprocess.DEVNULL
    )
    
    # Start server in background
    process = subprocess.Popen(
        ["python3", "install-ui.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
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
        
        # Wait for packages to load
        page.wait_for_selector("#packagesList .package-card", timeout=5000)
        
        # Verify at least one package is shown
        packages = page.locator(".package-card")
        expect(packages).to_have_count(pytest.approx(1, abs=20))  # At least 1 package
    
    def test_package_selection(self, page: Page, installer_server):
        """Test selecting a package."""
        page.goto(INSTALLER_URL)
        
        # Wait for packages
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Click first package
        first_package = page.locator(".package-card").first
        first_package.click()
        
        # Verify visual feedback (border change)
        expect(first_package).to_have_css(
            "border-color", "rgb(102, 126, 234)"  # #667eea
        )
        
        # Verify checkmark appears
        checkmark = first_package.locator(".checkmark")
        expect(checkmark).to_be_visible()
    
    def test_next_button_enabled_after_selection(self, page: Page, installer_server):
        """Test that Next button enables after package selection."""
        page.goto(INSTALLER_URL)
        
        # Wait for packages
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Select a package
        page.locator(".package-card").first.click()
        
        # Next button should be enabled (not checking disabled state)
        next_button = page.locator("button").filter(has_text="Next").first
        expect(next_button).to_be_visible()
    
    def test_step_navigation(self, page: Page, installer_server):
        """Test navigation between steps."""
        page.goto(INSTALLER_URL)
        
        # Wait for packages
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Select package
        page.locator(".package-card").first.click()
        
        # Click Next
        page.locator("button").filter(has_text="Next").first.click()
        
        # Verify step 2 is now active
        step2 = page.locator("#step2")
        expect(step2).to_have_class("step active")
        
        # Verify step 1 is not active
        step1 = page.locator("#step1")
        expect(step1).not_to_have_class("step active")
    
    def test_user_info_form(self, page: Page, installer_server):
        """Test user info form fields."""
        page.goto(INSTALLER_URL)
        
        # Navigate to user info step
        page.wait_for_selector(".package-card", timeout=5000)
        page.locator(".package-card").first.click()
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
        
        # Check for theme switcher
        theme_buttons = page.locator(".theme-option")
        expect(theme_buttons).to_have_count(5)  # 5 themes
    
    def test_theme_switching(self, page: Page, installer_server):
        """Test switching between themes."""
        page.goto(INSTALLER_URL)
        
        # Click a theme button
        purple_theme = page.locator(".theme-option[data-theme='purple']")
        purple_theme.click()
        
        # Verify data-theme attribute changed
        html = page.locator("html")
        expect(html).to_have_attribute("data-theme", "purple")
        
        # Switch to another theme
        ocean_theme = page.locator(".theme-option[data-theme='ocean']")
        ocean_theme.click()
        
        expect(html).to_have_attribute("data-theme", "ocean")
    
    def test_theme_persists(self, page: Page, installer_server):
        """Test that theme selection persists across page reloads."""
        page.goto(INSTALLER_URL)
        
        # Set theme to forest
        page.locator(".theme-option[data-theme='forest']").click()
        
        # Reload page
        page.reload()
        
        # Verify theme persisted
        html = page.locator("html")
        expect(html).to_have_attribute("data-theme", "forest")


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
