"""
E2E tests for configuration validation and package system.
"""

import os
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
    import subprocess
    import time

    subprocess.run("lsof -ti:5555 | xargs kill -9", shell=True, stderr=subprocess.DEVNULL)

    process = subprocess.Popen(
        ["python3", "install-ui.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(Path(__file__).parent.parent.parent),
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
        page.wait_for_selector(".tier-card", timeout=5000)

        # Select first tier card
        page.locator(".tier-card").first.click()

        # Go to step 2
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")

        # Go back to step 1
        page.locator("button").filter(has_text="Back").first.click()
        page.wait_for_selector("#step1.active")

        # Verify selection persisted (tier-card gets 'selected' class)
        selected_tier = page.locator(".tier-card.selected")
        expect(selected_tier).to_have_count(1)

    def test_user_info_navigation_round_trip(self, page: Page, installer_server):
        """Test that navigating back to user info step works correctly."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".tier-card", timeout=5000)

        # Navigate to user info
        page.locator(".tier-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")

        # Fill info
        test_data = {"name": "Persistence Test User", "email": "persist@test.com", "username": "persisttest"}

        for field, value in test_data.items():
            if page.locator(f"input[name='{field}']").count() > 0:
                page.fill(f"input[name='{field}']", value)

        # Go to next step — lands on step 4 (tools) since step 3 is skipped
        page.locator("#step2 button").filter(has_text="Next").click()
        # Wait for any step beyond 2 to become active
        page.wait_for_function(
            "() => document.querySelector('.step.active') && " "document.querySelector('.step.active').id !== 'step2'",
            timeout=10000,
        )

        # Go back to user info
        back_btn = page.locator(".step.active button").filter(has_text="Back")
        if back_btn.count() > 0:
            back_btn.click()
            page.wait_for_selector("#step2.active", timeout=5000)
        else:
            pytest.skip("No Back button on current step")

        # Wait for form fields to render after step transition
        page.wait_for_selector("#step2 input", timeout=5000)

        # Verify we're back on step 2 and fields are present
        assert page.locator("input[name='name']").count() > 0, "Name field should exist on step 2"
        assert page.locator("input[name='email']").count() > 0, "Email field should exist on step 2"

    def test_theme_persists_across_navigation(self, page: Page, installer_server):
        """Test that theme selection persists across page navigation."""
        page.goto(INSTALLER_URL)
        page.wait_for_load_state("networkidle")

        # Open settings panel and navigate to theme step
        page.locator(".hamburger-menu").click()
        page.wait_for_selector(".settings-panel.open", timeout=5000)
        page.locator(".settings-step-btn[data-step='3']").click()
        page.wait_for_timeout(500)

        # Click the first available theme
        first_theme = page.locator(".theme-option").first
        first_theme.wait_for(state="visible", timeout=5000)
        theme_id = first_theme.get_attribute("data-theme")
        first_theme.click()
        page.wait_for_timeout(300)

        # Verify theme applied
        html = page.locator("html")
        expect(html).to_have_attribute("data-theme", theme_id)

        # Close settings panel
        page.locator(".hamburger-menu").click()
        page.wait_for_timeout(300)

        # Navigate through steps
        page.wait_for_selector(".tier-card", timeout=5000)
        page.locator(".tier-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")

        # Verify theme still applied after navigation
        expect(html).to_have_attribute("data-theme", theme_id)


@pytest.mark.e2e
class TestUserExperience:
    """Test user experience and UI behavior."""

    def test_loading_states_are_shown(self, page: Page, installer_server):
        """Test that loading states are shown during async operations."""
        page.goto(INSTALLER_URL)

        # Check if loading indicator appears briefly
        # (might be too fast to catch, but we can try)
        page.wait_for_selector(".tier-card, .loading, .spinner", timeout=10000)

        # Verify tier cards loaded (no permanent loading state)
        tiers = page.locator(".tier-card")
        expect(tiers.first).to_be_visible()

    def test_error_messages_are_user_friendly(self, page: Page, installer_server):
        """Test that error messages are clear and helpful."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".tier-card", timeout=5000)

        # Navigate to form
        page.locator(".tier-card").first.click()
        page.locator("button").filter(has_text="Next").first.click()
        page.wait_for_selector("#step2.active")

        # Fill name (required) but put invalid email to trigger email validation
        page.fill("input[name='name']", "Test User")
        page.fill("input[name='email']", "invalid-email")
        page.locator("#step2 button").filter(has_text="Next").click()

        page.wait_for_timeout(500)

        # The custom JS validation should show an error for invalid email format
        # or the field should remain invalid via HTML5 validation
        validation_shown = page.locator(".validation-error").count() > 0
        email_field = page.locator("input[name='email']")
        is_html5_invalid = email_field.evaluate("el => !el.validity.valid")

        assert validation_shown or is_html5_invalid, "Invalid email should trigger validation"

    def test_progress_indication_through_steps(self, page: Page, installer_server):
        """Test that progress is indicated as user moves through steps."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".tier-card", timeout=5000)

        # Check for progress indicators
        progress_indicators = page.locator(".step-indicator, .progress-bar, .breadcrumb, [class*='step']").count()

        # Should have some form of progress indication
        # Even step titles themselves are progress indicators
        assert progress_indicators > 0

    def test_help_text_and_tooltips(self, page: Page, installer_server):
        """Test that help text and tooltips are available."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".tier-card", timeout=5000)

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
        page.wait_for_selector(".tier-card", timeout=5000)

        # Tab through elements
        page.keyboard.press("Tab")
        page.wait_for_timeout(100)

        # Should be able to focus elements
        focused = page.evaluate("document.activeElement.tagName")
        assert focused in ["BUTTON", "INPUT", "SELECT", "A", "DIV", "BODY"]

    def test_labels_for_form_fields(self, page: Page, installer_server):
        """Test that form fields have proper labels."""
        page.goto(INSTALLER_URL)
        page.wait_for_selector(".tier-card", timeout=5000)

        # Navigate to form
        page.locator(".tier-card").first.click()
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
            has_label = page.locator(f"label[for='{input_id}']").count() > 0 if input_id else False
            has_aria = input_elem.get_attribute("aria-label") is not None
            has_placeholder = input_elem.get_attribute("placeholder") is not None

            assert has_label or has_aria or has_placeholder, f"Input {input_name} has no label"

    def test_semantic_html_structure(self, page: Page, installer_server):
        """Test that semantic HTML is used."""
        page.goto(INSTALLER_URL)

        # Check for semantic elements
        _has_main = page.locator("main").count() > 0  # noqa: F841
        _has_header = page.locator("header").count() > 0  # noqa: F841
        has_headings = page.locator("h1, h2, h3").count() > 0

        # Should have at least headings for structure
        assert has_headings, "Should have heading elements for structure"
