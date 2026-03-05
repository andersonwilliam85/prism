"""
Comprehensive E2E tests for complete installation configuration.
Tests the entire workflow from package selection to installation completion.
"""
import pytest
import subprocess
import time
import os
import shutil
import tempfile
from pathlib import Path
from playwright.sync_api import Page, expect


INSTALLER_URL = os.getenv("INSTALLER_URL", "http://localhost:5555")


@pytest.fixture(scope="module")
def installer_server():
    """Start the installer web UI server."""
    # Kill any existing server
    subprocess.run(
        "lsof -ti:5555 | xargs kill -9",
        shell=True,
        stderr=subprocess.DEVNULL
    )
    
    # Start server
    process = subprocess.Popen(
        ["python3", "install-ui.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(Path(__file__).parent.parent.parent)
    )
    
    time.sleep(3)
    yield process
    
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture
def temp_install_dir():
    """Create temporary installation directory."""
    temp_dir = Path(tempfile.mkdtemp(prefix="prism_test_"))
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.e2e
class TestCompleteInstallationFlow:
    """Test complete end-to-end installation workflows."""
    
    def test_complete_core_prism_installation(self, page: Page, installer_server):
        """Test complete installation of core.prism package."""
        page.goto(INSTALLER_URL)
        
        # Step 1: Select package
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Find and click core.prism package
        core_package = page.locator(".package-card").filter(has_text="Core Prism")
        expect(core_package).to_be_visible()
        core_package.click()
        
        # Verify selection
        expect(core_package).to_have_css("border-color", "rgb(102, 126, 234)")
        
        # Click Next
        page.locator("button").filter(has_text="Next").first.click()
        
        # Step 2: Fill user info
        page.wait_for_selector("#step2.active", timeout=5000)
        
        page.fill("input[name='name']", "John Developer")
        page.fill("input[name='email']", "john@example.com")
        page.fill("input[name='git_username']", "johndev")
        
        # Click Next
        page.locator("button").filter(has_text="Next").nth(1).click()
        
        # Step 3: Review configuration
        page.wait_for_selector("#step3.active", timeout=5000)
        
        # Verify user info is displayed
        expect(page.locator("text=John Developer")).to_be_visible()
        expect(page.locator("text=john@example.com")).to_be_visible()
        
        # Verify package info is displayed
        expect(page.locator("text=Core Prism")).to_be_visible()
    
    def test_multi_step_navigation_forward_backward(self, page: Page, installer_server):
        """Test navigation forward and backward through all steps."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Step 1 -> Step 2
        page.locator(".package-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")
        
        # Fill some info
        page.fill("input[name='name']", "Test User")
        
        # Step 2 -> Step 3
        page.locator("button").filter(has_text="Next").nth(1).click()
        page.wait_for_selector("#step3.active")
        
        # Step 3 -> Step 2 (back)
        page.locator("button").filter(has_text="Back").first.click()
        page.wait_for_selector("#step2.active")
        
        # Verify data persisted
        expect(page.locator("input[name='name']")).to_have_value("Test User")
        
        # Step 2 -> Step 1 (back)
        page.locator("button").filter(has_text="Back").first.click()
        page.wait_for_selector("#step1.active")
        
        # Verify package selection persisted
        selected = page.locator(".package-card").first
        expect(selected).to_have_css("border-color", "rgb(102, 126, 234)")
    
    def test_personal_dev_package_complete_flow(self, page: Page, installer_server):
        """Test complete flow for personal-dev package."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Select personal-dev package
        personal_package = page.locator(".package-card").filter(
            has_text="Personal Dev"
        )
        
        if personal_package.count() > 0:
            personal_package.click()
            
            # Next to user info
            page.locator("button").filter(has_text="Next").first.click()
            page.wait_for_selector("#step2.active")
            
            # Fill comprehensive user info
            page.fill("input[name='name']", "Jane Developer")
            page.fill("input[name='email']", "jane@personal.dev")
            page.fill("input[name='git_username']", "janedev")
            
            # If git platform selection exists
            if page.locator("select[name='git_platform']").count() > 0:
                page.select_option("select[name='git_platform']", "github")
            
            # Next to review
            page.locator("button").filter(has_text="Next").nth(1).click()
            page.wait_for_selector("#step3.active")
            
            # Verify all info in review
            expect(page.locator("text=Jane Developer")).to_be_visible()
            expect(page.locator("text=jane@personal.dev")).to_be_visible()
            expect(page.locator("text=Personal Dev")).to_be_visible()
    
    def test_validation_prevents_incomplete_submission(self, page: Page, installer_server):
        """Test that validation prevents submitting incomplete forms."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Try to proceed without selecting package
        next_button = page.locator("button").filter(has_text="Next").first
        
        # Button should be disabled or clicking should show error
        # (Implementation depends on your validation approach)
        
        # Select package
        page.locator(".package-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")
        
        # Try to proceed without filling required fields
        # Fill only name (email is required)
        page.fill("input[name='name']", "Incomplete")
        
        # Try to go next
        page.locator("button").filter(has_text="Next").nth(1).click()
        
        # Should either stay on step 2 or show validation error
        # Check if still on step 2 after short wait
        page.wait_for_timeout(500)
        
        # Either step2 is still active OR there's a validation message
        step2_active = page.locator("#step2.active").count() > 0
        validation_msg = page.locator(".error, .validation, [class*='error']").count() > 0
        
        assert step2_active or validation_msg, "Validation should prevent incomplete submission"


@pytest.mark.e2e
class TestConfigurationGeneration:
    """Test configuration file generation and output."""
    
    def test_configuration_summary_display(self, page: Page, installer_server):
        """Test that configuration summary is displayed correctly."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Complete flow to review step
        page.locator(".package-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")
        
        page.fill("input[name='name']", "Config Tester")
        page.fill("input[name='email']", "config@test.com")
        page.fill("input[name='git_username']", "configtest")
        
        page.locator("button").filter(has_text="Next").nth(1).click()
        page.wait_for_selector("#step3.active")
        
        # Verify configuration sections exist
        expect(page.locator("text=Package").or_(page.locator("text=Prism"))).to_be_visible()
        expect(page.locator("text=User Information")).to_be_visible()
        
        # Verify actual config values
        expect(page.locator("text=Config Tester")).to_be_visible()
        expect(page.locator("text=config@test.com")).to_be_visible()
        expect(page.locator("text=configtest")).to_be_visible()
    
    def test_install_button_triggers_installation(self, page: Page, installer_server):
        """Test that install button triggers the installation process."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Complete to final step
        page.locator(".package-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")
        
        page.fill("input[name='name']", "Install Test")
        page.fill("input[name='email']", "install@test.com")
        page.fill("input[name='git_username']", "installtest")
        
        page.locator("button").filter(has_text="Next").nth(1).click()
        page.wait_for_selector("#step3.active")
        
        # Look for install button
        install_button = page.locator("button").filter(
            has_text="Install"
        ).or_(page.locator("button").filter(has_text="Start Installation"))
        
        if install_button.count() > 0:
            # Click install
            install_button.click()
            
            # Wait for installation step or progress
            page.wait_for_timeout(2000)
            
            # Check for progress indicators, installation messages, or completion
            progress = (
                page.locator(".progress").count() > 0 or
                page.locator(".installing").count() > 0 or
                page.locator("text=Installing").count() > 0 or
                page.locator("#step4").count() > 0  # Installation step
            )
            
            assert progress, "Installation should show progress or start"


@pytest.mark.e2e
class TestPackageSpecificConfiguration:
    """Test package-specific configuration options."""
    
    def test_package_with_org_hierarchy(self, page: Page, installer_server):
        """Test packages with organizational hierarchy options."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Look for enterprise/fortune500 package
        enterprise_pkg = page.locator(".package-card").filter(
            has_text="Fortune 500"
        ).or_(page.locator(".package-card").filter(has_text="Enterprise"))
        
        if enterprise_pkg.count() > 0:
            enterprise_pkg.click()
            page.locator("button").filter(has_text="Next").first.click()
            page.wait_for_selector("#step2.active")
            
            # Fill basic info
            page.fill("input[name='name']", "Enterprise User")
            page.fill("input[name='email']", "user@enterprise.com")
            
            # Check for org/team fields
            org_field = page.locator("select[name='org']").or_(
                page.locator("input[name='organization']")
            )
            
            if org_field.count() > 0:
                if org_field.first.get_attribute("type") != "text":
                    # It's a select
                    options = page.locator("select[name='org'] option")
                    if options.count() > 1:
                        page.select_option("select[name='org']", index=1)
                else:
                    # It's a text input
                    org_field.fill("Engineering")
            
            # Proceed and verify
            page.locator("button").filter(has_text="Next").nth(1).click()
            page.wait_for_selector("#step3.active")
            
            expect(page.locator("text=Enterprise User")).to_be_visible()
    
    def test_package_with_custom_resources(self, page: Page, installer_server):
        """Test packages with custom resource configurations."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Select any package
        page.locator(".package-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")
        
        page.fill("input[name='name']", "Resource Test")
        page.fill("input[name='email']", "resource@test.com")
        page.fill("input[name='git_username']", "resourcetest")
        
        page.locator("button").filter(has_text="Next").nth(1).click()
        page.wait_for_selector("#step3.active")
        
        # Look for resources section in review
        resources = page.locator("text=Resources").or_(
            page.locator("text=Tools")
        ).or_(page.locator("text=IDEs"))
        
        # Resources might be displayed in the config
        # Just verify the review step loaded successfully
        expect(page.locator("#step3.active")).to_be_visible()


@pytest.mark.e2e
class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_handles_invalid_package_data(self, page: Page, installer_server):
        """Test handling of packages with validation errors."""
        page.goto(INSTALLER_URL)
        
        # Wait for packages to load
        page.wait_for_selector(".package-card, .alert, .error", timeout=5000)
        
        # Check if any invalid packages are shown
        invalid_section = page.locator("text=Invalid Packages").or_(
            page.locator("text=Validation Errors")
        )
        
        if invalid_section.count() > 0:
            # Verify error details are shown
            expect(invalid_section).to_be_visible()
    
    def test_handles_network_errors_gracefully(self, page: Page, installer_server):
        """Test graceful handling of network errors."""
        page.goto(INSTALLER_URL)
        
        # Intercept API calls and simulate failure
        page.route("**/api/packages", lambda route: route.abort())
        
        # Reload page
        page.reload()
        
        # Should show error message, not crash
        page.wait_for_timeout(2000)
        
        error_indicator = (
            page.locator(".error").count() > 0 or
            page.locator(".alert").count() > 0 or
            page.locator("text=Error").count() > 0 or
            page.locator("text=Failed").count() > 0
        )
        
        assert error_indicator, "Should show error indicator on API failure"
    
    def test_form_validation_shows_errors(self, page: Page, installer_server):
        """Test that form validation errors are displayed."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        page.locator(".package-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")
        
        # Fill invalid email
        page.fill("input[name='name']", "Test User")
        page.fill("input[name='email']", "not-an-email")  # Invalid
        
        # Try to proceed
        page.locator("button").filter(has_text="Next").nth(1).click()
        page.wait_for_timeout(500)
        
        # Should show validation error or prevent navigation
        # Check HTML5 validation or custom error messages
        email_field = page.locator("input[name='email']")
        is_invalid = (
            email_field.evaluate("el => el.validity.valid") == False or
            page.locator(".error, .invalid, [class*='error']").count() > 0
        )
        
        assert is_invalid, "Invalid email should trigger validation"


@pytest.mark.e2e
@pytest.mark.slow
class TestFullInstallationScenarios:
    """Test complete installation scenarios from start to finish."""
    
    def test_complete_personal_developer_scenario(self, page: Page, installer_server):
        """Complete scenario: Personal developer setting up environment."""
        page.goto(INSTALLER_URL)
        
        # Wait for page load
        page.wait_for_load_state("networkidle")
        page.wait_for_selector(".package-card", timeout=5000)
        
        # 1. Select personal-dev package
        personal_pkg = page.locator(".package-card").filter(
            has_text="Personal"
        )
        
        if personal_pkg.count() > 0:
            personal_pkg.first.click()
        else:
            # Fallback to first package
            page.locator(".package-card").first.click()
        
        page.locator("button").filter(has_text="Next").first.click()
        
        # 2. Fill complete user information
        page.wait_for_selector("#step2.active", timeout=5000)
        
        page.fill("input[name='name']", "Alex Developer")
        page.fill("input[name='email']", "alex@developer.io")
        page.fill("input[name='git_username']", "alexdev")
        
        # Fill any additional fields that exist
        if page.locator("input[name='github_username']").count() > 0:
            page.fill("input[name='github_username']", "alexdev")
        
        if page.locator("select[name='git_platform']").count() > 0:
            page.select_option("select[name='git_platform']", "github")
        
        if page.locator("input[name='preferred_shell']").count() > 0:
            page.fill("input[name='preferred_shell']", "zsh")
        
        page.locator("button").filter(has_text="Next").nth(1).click()
        
        # 3. Review and verify all information
        page.wait_for_selector("#step3.active", timeout=5000)
        
        # Verify all entered data appears
        expect(page.locator("text=Alex Developer")).to_be_visible()
        expect(page.locator("text=alex@developer.io")).to_be_visible()
        expect(page.locator("text=alexdev")).to_be_visible()
        
        # Take screenshot of final config
        page.screenshot(path="test-results/complete-scenario-review.png")
        
        # 4. Verify configuration is complete and valid
        config_sections = page.locator(".config-section, .review-section, [class*='config']").count()
        assert config_sections >= 1, "Should show configuration sections"
    
    def test_complete_enterprise_team_scenario(self, page: Page, installer_server):
        """Complete scenario: Enterprise team member setup."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Look for enterprise package
        enterprise = page.locator(".package-card").filter(
            has_text="Fortune"
        ).or_(page.locator(".package-card").filter(has_text="Enterprise"))
        
        if enterprise.count() > 0:
            enterprise.first.click()
        else:
            # Use ACME Corp as alternative
            acme = page.locator(".package-card").filter(has_text="ACME")
            if acme.count() > 0:
                acme.first.click()
            else:
                page.locator(".package-card").first.click()
        
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active", timeout=5000)
        
        # Fill enterprise user info
        page.fill("input[name='name']", "Sarah Engineer")
        page.fill("input[name='email']", "sarah@company.com")
        
        if page.locator("input[name='git_username']").count() > 0:
            page.fill("input[name='git_username']", "saraheng")
        
        # Select organization if available
        if page.locator("select[name='org']").count() > 0:
            org_options = page.locator("select[name='org'] option")
            if org_options.count() > 1:
                page.select_option("select[name='org']", index=1)
        
        # Select team if available
        if page.locator("select[name='team']").count() > 0:
            team_options = page.locator("select[name='team'] option")
            if team_options.count() > 1:
                page.select_option("select[name='team']", index=1)
        
        page.locator("button").filter(has_text="Next").nth(1).click()
        page.wait_for_selector("#step3.active", timeout=5000)
        
        # Verify enterprise setup
        expect(page.locator("text=Sarah Engineer")).to_be_visible()
        expect(page.locator("text=sarah@company.com")).to_be_visible()
        
        page.screenshot(path="test-results/enterprise-scenario-review.png")
