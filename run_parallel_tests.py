#!/usr/bin/env python3
"""
Appium Parallel Test Runner
Entry point for running Appium tests across multiple devices in parallel.
"""

import argparse
import sys
import os
import multiprocessing

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parallel_runner import ParallelTestRunner
from device_manager import DeviceManager


def parse_args():
    parser = argparse.ArgumentParser(description="Run Appium tests in parallel")
    parser.add_argument(
        "--caps",
        default="caps/android_sample.yaml",
        help="Path to YAML capabilities file",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel across all devices",
    )
    parser.add_argument(
        "--udid",
        type=str,
        default=None,
        help="Run on specific device UDID only",
    )
    parser.add_argument(
        "--record-video",
        action="store_true",
        help="Enable screen recording during test run",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum number of parallel workers",
    )
    parser.add_argument(
        "--appium-url",
        type=str,
        default="http://localhost:4723",
        help="Appium server URL",
    )
    parser.add_argument(
        "pytest_args",
        nargs="*",
        default=[],
        help="Additional arguments to pass to pytest",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Auto-detect devices
    android_devs = DeviceManager.get_android_devices()
    ios_devs = DeviceManager.get_ios_devices()

    all_devices = android_devs + ios_devs

    print(f"[Appium Parallel Runner] Android devices: {android_devs}")
    print(f"[Appium Parallel Runner] iOS devices: {ios_devs}")

    if not all_devices:
        print("[!] No devices found. Ensure ADB is running or iOS devices are connected.")
        sys.exit(1)

    runner = ParallelTestRunner(
        caps_file=args.caps,
        appium_url=args.appium_url,
        max_workers=args.max_workers or len(all_devices),
        record_video=args.record_video,
    )

    if args.udid:
        # Run on specific device
        results = runner.run_on_device(args.udid)
    elif args.parallel:
        # Run on all devices in parallel
        results = runner.run_parallel(all_devices)
    else:
        print("[!] Use --parallel or --udid to specify test targets.")
        sys.exit(1)

    print(f"[Appium Parallel Runner] Completed: {len(results)} test suites ran.")
    for r in results:
        print(f"  Device {r['udid']}: {r['passed']} passed, {r['failed']} failed")

    sys.exit(0)


if __name__ == "__main__":
    main()
