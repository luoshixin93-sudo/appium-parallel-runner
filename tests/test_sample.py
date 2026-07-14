"""
Sample Appium test cases for parallel execution.
Run with: pytest tests/ --udid=<device-udid> --appium-url=http://localhost:4723
"""

import pytest


class TestSampleApp:
    """Basic test suite demonstrating Appium parallel test execution."""

    def test_session_started(self, appium_driver):
        """Verify the Appium session starts successfully."""
        assert appium_driver is not None
        platform = appium_driver.capabilities.get("platformName", "unknown")
        assert platform in ("Android", "iOS"), f"Unexpected platform: {platform}"

    def test_device_info(self, appium_driver):
        """Verify device information is available."""
        caps = appium_driver.capabilities
        assert caps.get("deviceName"), "deviceName not found in capabilities"
        assert caps.get("platformName"), "platformName not found in capabilities"

    def test_screen_size(self, appium_driver):
        """Verify the device screen size can be read."""
        size = appium_driver.get_window_size()
        assert size["width"] > 0
        assert size["height"] > 0

    def test_page_source(self, appium_driver):
        """Verify page source can be retrieved."""
        source = appium_driver.page_source
        assert source is not None
        assert "<" in source  # XML-like page source expected

    @pytest.mark.skip(reason="Requires an app with known elements")
    def test_known_element(self, appium_driver):
        """Example: test a specific element in your app."""
        el = appium_driver.find_element("accessibility id", "my-button")
        el.click()
