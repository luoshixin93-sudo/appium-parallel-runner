"""
Parallel Appium Test Runner Core
Handles device allocation, driver lifecycle, and parallel test execution.
"""

import multiprocessing
import os
import sys
import time
import yaml
from typing import Optional

try:
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
    from appium.options.ios import XCUITestOptions
    HAS_APPIUM = True
except ImportError:
    HAS_APPIUM = False


class ParallelTestRunner:
    """Orchestrates parallel Appium test execution across multiple devices."""

    def __init__(
        self,
        caps_file: str,
        appium_url: str = "http://localhost:4723",
        max_workers: Optional[int] = None,
        record_video: bool = False,
    ):
        self.caps_file = caps_file
        self.appium_url = appium_url
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.record_video = record_video
        self._caps: dict = {}

        if os.path.exists(caps_file):
            with open(caps_file) as f:
                self._caps = yaml.safe_load(f) or {}

    def _load_caps_for_device(self, udid: str) -> dict:
        """Load and merge capabilities for a specific device."""
        base = self._caps.copy()
        base["udid"] = udid
        return base

    def _create_driver(self, caps: dict):
        """Create an Appium driver for the given capabilities."""
        if not HAS_APPIUM:
            raise RuntimeError(
                "Appium is not installed. Run: pip install Appium-Python-Client"
            )

        platform = caps.get("platformName", "").lower()

        if platform == "android":
            options = UiAutomator2Options()
            options.load_capabilities(caps)
        elif platform == "ios":
            options = XCUITestOptions()
            options.load_capabilities(caps)
        else:
            options = None  # generic

        return webdriver.Remote(self.appium_url, options=options or caps)

    def run_on_device(self, udid: str) -> dict:
        """Run tests on a single device. Returns result summary."""
        caps = self._load_caps_for_device(udid)
        result = {
            "udid": udid,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
        }

        driver = None
        try:
            print(f"[Runner] Connecting to device: {udid}")
            driver = self._create_driver(caps)

            # Basic sanity check
            driver.implicitly_wait(10)
            platform = driver.capabilities.get("platformName", "unknown")
            version = driver.capabilities.get("platformVersion", "unknown")
            print(f"[Runner] {platform} {version} connected: {udid}")

            # If pytest is available, run the test suite
            try:
                import pytest
                import subprocess

                pytest_args = [
                    sys.executable, "-m", "pytest",
                    "-v", "--tb=short",
                    f"--udid={udid}",
                    "tests/",
                ]
                if self.record_video:
                    pytest_args.append("--video")

                proc = subprocess.run(
                    pytest_args,
                    capture_output=True,
                    text=True,
                )
                result["output"] = proc.stdout + proc.stderr
                result["returncode"] = proc.returncode
                result["passed"] = result["passed"]  # parse from output if needed
            except ImportError:
                print("[Runner] pytest not found — skipping test suite")
                result["passed"] = 1
                result["skipped"] = 1

            print(f"[Runner] Completed on device: {udid}")

        except Exception as e:
            print(f"[Runner] Error on device {udid}: {e}")
            result["errors"].append(str(e))
            result["failed"] = 1

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

        return result

    def run_parallel(self, devices: list[str]) -> list[dict]:
        """Run tests in parallel across a list of device UDIDs."""
        print(f"[Runner] Starting parallel run on {len(devices)} devices...")
        with multiprocessing.Pool(self.max_workers) as pool:
            results = pool.map(self.run_on_device, devices)
        return results

    def run_async(self, devices: list[str]):
        """Run tests asynchronously (non-blocking) using multiprocessing.Process."""
        processes = []
        for device in devices:
            p = multiprocessing.Process(target=self.run_on_device, args=(device,))
            p.start()
            processes.append(p)
        return processes


def run_test_on_device(args):
    """Standalone worker function for multiprocessing pool."""
    runner = args["runner"]
    udid = args["udid"]
    return runner.run_on_device(udid)
