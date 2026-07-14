"""
Pytest configuration and fixtures for Appium parallel tests.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parallel_runner import ParallelTestRunner


def pytest_addoption(parser):
    parser.addoption("--udid", action="store", default=None, help="Device UDID")
    parser.addoption("--appium-url", action="store", default="http://localhost:4723")
    parser.addoption("--caps", action="store", default="caps/android_sample.yaml")
    parser.addoption("--video", action="store_true", help="Record video")


@pytest.fixture(scope="session")
def appium_url(request):
    return request.config.getoption("--appium-url")


@pytest.fixture(scope="session")
def device_udid(request):
    return request.config.getoption("--udid")


@pytest.fixture(scope="session")
def caps_file(request):
    return request.config.getoption("--caps")


@pytest.fixture(scope="function")
def appium_driver(appium_url, device_udid, caps_file):
    """
    Pytest fixture that creates an Appium WebDriver for a specific device.
    Automatically quits after the test.
    """
    import yaml
    from appium import webdriver
    from appium.options.android import UiAutomator2Options

    if not device_udid:
        pytest.skip("No --udid provided")

    with open(caps_file) as f:
        caps = yaml.safe_load(f) or {}

    caps["udid"] = device_udid

    platform = caps.get("platformName", "").lower()
    if platform == "android":
        options = UiAutomator2Options()
        options.load_capabilities(caps)
    else:
        options = None

    driver = webdriver.Remote(appium_url, options=options or caps)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture(scope="function")
def parallel_runner(appium_url, caps_file):
    """Provides a ParallelTestRunner instance for advanced use."""
    return ParallelTestRunner(caps_file=caps_file, appium_url=appium_url)
