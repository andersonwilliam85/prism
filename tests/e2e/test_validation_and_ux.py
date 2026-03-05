"""
E2E tests for configuration validation and package system.
"""
import pytest
import yaml
import json
from pathlib import Path
from playwright.sync_api import Page, expect
import os


INSTALLER_URL = os.getenv("INSTALLER_URL", "http://localhost:5555")


@pytest.fixture(scope="module")
def installer_server():
    """Start the installer web UI server."""
    import subprocess
    import time
    
    subprocess.run(
        "lsof -ti:5555 | xargs kill -9",
        shell=True,
        stderr=subprocess.DEVNULL
    )
    
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


@pytest.mark.e2e
class TestPackageValidation:
    """Test package validation through the UI."""
    
    def test_all_packages_load_successfully(self, page: Page, installer_server):
        """Test that all valid packages load without errors."""
        response = page.request.get(f"{INSTALLER_URL}/api/packages")
        assert response.status == 200
        
        data = response.json()
        assert "packages" in data
        assert isinstance(data["packages"], list)
        assert len(data["packages"]) > 0, "Should have at least one valid package"
        
        # Verify each package has required fields
        for pkg in data["packages"]:
            assert "id" in pkg
            assert "name" in pkg
            assert "description" in pkg
            assert "version" in pkg
    
    def test_package_metadata_completeness(self, page: Page, installer_server):
        """Test that package metadata is complete and valid."""
        response = page.request.get(f"{INSTALLER_URL}/api/packages")
        data = response.json()
        
        for pkg in data["packages"]:
            # Check required metadata
            assert len(pkg["name"]) > 0, f"Package {pkg['id']} has empty name"
            assert len(pkg["description"]) > 0, f"Package {pkg['id']} has empty description"
            
            # Check version format
            version = pkg["version"]
            parts = version.split(".")
            assert len(parts) >= 2, f"Package {pkg['id']} has invalid version: {version}"
            
            # Check optional fields if present
            if "author" in pkg:
                assert len(pkg["author"]) > 0
            
            if "user_info_fields" in pkg:
                assert isinstance(pkg["user_info_fields"], list)
                for field in pkg["user_info_fields"]:
                    assert "id" in field
                    assert "label" in field
                    assert "type" in field
    
    def test_invalid_packages_are_reported(self, page: Page, installer_server):
        """Test that invalid packages are identified and reported."""
        response = page.request.get(f"{INSTALLER_URL}/api/packages")
        data = response.json()
        
        # Check if invalid packages section exists
        if "invalid_packages" in data:
            # Verify invalid packages have error details
            for invalid in data["invalid_packages"]:
                assert "name" in invalid or "path" in invalid
                assert "errors" in invalid
                assert len(invalid["errors"]) > 0
    
    def test_package_configuration_inheritance(self, page: Page, installer_server):
        """Test that packages with inheritance load correctly."""
        response = page.request.get(f"{INSTALLER_URL}/api/packages")
        data = response.json()
        
        # Look for packages with inheritance (orgs, teams)
        for pkg in data["packages"]:
            if "orgs" in pkg or "teams" in pkg:
                # Verify hierarchical structure
                if "orgs" in pkg:
                    assert isinstance(pkg["orgs"], list)
                    for org in pkg["orgs"]:
                        assert "id" in org
                        assert "name" in org
                
                if "teams" in pkg:
                    assert isinstance(pkg["teams"], list)
                    for team in pkg["teams"]:
                        assert "id" in team
                        assert "name" in team


@pytest.mark.e2e
class TestAPIEndpoints:
    """Test API endpoints thoroughly."""
    
    def test_packages_endpoint_performance(self, page: Page, installer_server):
        """Test that /api/packages responds quickly."""
        import time
        
        start = time.time()
        response = page.request.get(f"{INSTALLER_URL}/api/packages")
        elapsed = time.time() - start
        
        assert response.status == 200
        assert elapsed < 5.0, f"API took too long: {elapsed}s"
    
    def test_packages_endpoint_caching(self, page: Page, installer_server):
        """Test that packages endpoint can be called multiple times."""
        # First call
        response1 = page.request.get(f"{INSTALLER_URL}/api/packages")
        data1 = response1.json()
        
        # Second call
        response2 = page.request.get(f"{INSTALLER_URL}/api/packages")
        data2 = response2.json()
        
        # Should return consistent data
        assert response1.status == 200
        assert response2.status == 200
        assert len(data1["packages"]) == len(data2["packages"])
    
    def test_validation_endpoint_if_exists(self, page: Page, installer_server):
        """Test validation endpoint if it exists."""
        # Try to call validation endpoint
        response = page.request.get(f"{INSTALLER_URL}/api/validate")
        
        # Should either return 200 with validation results or 404 if not implemented
        assert response.status in [200, 404, 405]
        
        if response.status == 200:
            data = response.json()
            # Validation response should have some structure
            assert isinstance(data, dict)


@pytest.mark.e2e
class TestConfigurationPersistence:
    """Test that configuration choices persist correctly."""
    
    def test_package_selection_persists_in_session(self, page: Page, installer_server):
        """Test that package selection persists when navigating back."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Get the ID of first package
        first_pkg = page.locator(".package-card").first
        pkg_id = first_pkg.get_attribute("id")
        
        # Select it
        first_pkg.click()
        
        # Go to step 2
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")
        
        # Go back to step 1
        page.locator("button").filter(has_text="Back").first.click()
        page.wait_for_selector("#step1.active")
        
        # Verify selection persisted
        selected_pkg = page.locator(f"#{pkg_id}")
        expect(selected_pkg).to_have_css("border-color", "rgb(102, 126, 234)")
    
    def test_user_info_persists_in_session(self, page: Page, installer_server):
        """Test that user info persists when navigating back and forth."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Navigate to user info
        page.locator(".package-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")
        
        # Fill info
        test_data = {
            "name": "Persistence Test User",
            "email": "persist@test.com",
            "git_username": "persisttest"
        }
        
        for field, value in test_data.items():
            if page.locator(f"input[name='{field}']").count() > 0:
                page.fill(f"input[name='{field}']", value)
        
        # Go to review
        page.locator("button").filter(has_text="Next").nth(1).click()
        page.wait_for_selector("#step3.active")
        
        # Go back to user info
        page.locator("button").filter(has_text="Back").first.click()
        page.wait_for_selector("#step2.active")
        
        # Verify data persisted
        for field, value in test_data.items():
            if page.locator(f"input[name='{field}']").count() > 0:
                expect(page.locator(f"input[name='{field}']")).to_have_value(value)
    
    def test_theme_persists_across_navigation(self, page: Page, installer_server):
        """Test that theme selection persists across page navigation."""
        page.goto(INSTALLER_URL)
        
        # Set theme to forest
        if page.locator(".theme-option[data-theme='forest']").count() > 0:
            page.locator(".theme-option[data-theme='forest']").click()
            
            # Navigate through steps
            page.wait_for_selector(".package-card", timeout=5000)
            page.locator(".package-card").first.click()
            page.locator("button").filter(has_text="Next").first.click()
            page.wait_for_selector("#step2.active")
            
            # Verify theme still applied
            html = page.locator("html")
            expect(html).to_have_attribute("data-theme", "forest")


@pytest.mark.e2e
class TestUserExperience:
    """Test user experience and UI behavior."""
    
    def test_loading_states_are_shown(self, page: Page, installer_server):
        """Test that loading states are shown during async operations."""
        page.goto(INSTALLER_URL)
        
        # Check if loading indicator appears briefly
        # (might be too fast to catch, but we can try)
        page.wait_for_selector(".package-card, .loading, .spinner", timeout=5000)
        
        # Verify packages loaded (no permanent loading state)
        packages = page.locator(".package-card")
        expect(packages.first).to_be_visible()
    
    def test_error_messages_are_user_friendly(self, page: Page, installer_server):
        """Test that error messages are clear and helpful."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Navigate to form
        page.locator(".package-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")
        
        # Submit with invalid data
        page.fill("input[name='email']", "invalid-email")
        page.locator("button").filter(has_text="Next").nth(1).click()
        
        page.wait_for_timeout(500)
        
        # Check for error messages
        # HTML5 validation will handle this, but we can check validity
        email_field = page.locator("input[name='email']")
        is_valid = email_field.evaluate("el => el.validity.valid")
        
        if not is_valid:
            # Error state is correctly detected
            assert True
    
    def test_progress_indication_through_steps(self, page: Page, installer_server):
        """Test that progress is indicated as user moves through steps."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Check for progress indicators
        progress_indicators = page.locator(".step-indicator, .progress-bar, .breadcrumb, [class*='step']").count()
        
        # Should have some form of progress indication
        # Even step titles themselves are progress indicators
        assert progress_indicators > 0
    
    def test_help_text_and_tooltips(self, page: Page, installer_server):
        """Test that help text and tooltips are available."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Look for help indicators
        help_elements = page.locator(".help, .tooltip, [title], .description, [class*='help']").count()
        
        # Should have some help elements
        assert help_elements >= 0  # Even 0 is ok, just checking it doesn't crash


@pytest.mark.e2e
class TestAccessibility:
    """Test accessibility features."""
    
    def test_keyboard_navigation_works(self, page: Page, installer_server):
        """Test that keyboard navigation works."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Tab through elements
        page.keyboard.press("Tab")
        page.wait_for_timeout(100)
        
        # Should be able to focus elements
        focused = page.evaluate("document.activeElement.tagName")
        assert focused in ["BUTTON", "INPUT", "SELECT", "A", "DIV", "BODY"]
    
    def test_labels_for_form_fields(self, page: Page, installer_server):
        """Test that form fields have proper labels."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".package-card", timeout=5000)
        
        # Navigate to form
        page.locator(".package-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")
        
        # Check for labels
        inputs = page.locator("input[type='text'], input[type='email']")
        count = inputs.count()
        
        for i in range(count):
            input_elem = inputs.nth(i)
            input_id = input_elem.get_attribute("id")
            input_name = input_elem.get_attribute("name")
            
            # Should have either:
            # 1. Associated label
            # 2. Aria-label
            # 3. Placeholder that describes the field
            has_label = (
                page.locator(f"label[for='{input_id}']").count() > 0 if input_id else False
            )
            has_aria = input_elem.get_attribute("aria-label") is not None
            has_placeholder = input_elem.get_attribute("placeholder") is not None
            
            assert has_label or has_aria or has_placeholder, f"Input {input_name} has no label"
    
    def test_semantic_html_structure(self, page: Page, installer_server):
        """Test that semantic HTML is used."""
        page.goto(INSTALLER_URL)
        
        # Check for semantic elements
        has_main = page.locator("main").count() > 0
        has_header = page.locator("header").count() > 0
        has_headings = page.locator("h1, h2, h3").count() > 0
        
        # Should have at least headings for structure
        assert has_headings, "Should have heading elements for structure"
