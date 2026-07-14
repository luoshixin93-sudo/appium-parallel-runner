"""
Device Manager — Auto-discovers and manages Android/iOS devices.
"""

import subprocess
import re
import platform
from typing import List


class DeviceManager:
    """Utility class for discovering connected mobile devices."""

    @staticmethod
    def get_android_devices() -> List[str]:
        """
        Return a list of connected Android device UDIDs via `adb devices`.
        Only returns devices in 'device' state (not 'unauthorized' or 'offline').
        """
        try:
            out = subprocess.check_output(
                ["adb", "devices"],
                stderr=subprocess.DEVNULL,
            ).decode("utf-8", errors="replace")
        except (subprocess.SubprocessError, FileNotFoundError):
            return []

        serials = re.findall(r"^(\S+)\tdevice$", out, re.MULTILINE)
        return serials

    @staticmethod
    def get_ios_devices() -> List[str]:
        """
        Return a list of connected iOS device UDIDs via `idevice_id -l`.
        Requires libimobiledevice to be installed.
        """
        if platform.system() != "Darwin" and platform.system() != "Linux":
            return []

        try:
            out = subprocess.check_output(
                ["idevice_id", "-l"],
                stderr=subprocess.DEVNULL,
            ).decode("utf-8", errors="replace")
            devices = [line.strip() for line in out.strip().split("\n") if line.strip()]
            return devices
        except (subprocess.SubprocessError, FileNotFoundError):
            return []

    @staticmethod
    def get_all_devices() -> List[str]:
        """Return all connected Android + iOS devices."""
        return DeviceManager.get_android_devices() + DeviceManager.get_ios_devices()

    @staticmethod
    def get_device_info(udid: str) -> dict:
        """Get basic info about a connected device."""
        info = {"udid": udid, "platform": "unknown", "status": "unknown"}

        try:
            # Try Android first
            out = subprocess.check_output(
                ["adb", "-s", udid, "shell", "getprop", "ro.build.version.release"],
                stderr=subprocess.DEVNULL,
            ).decode("utf-8", errors="replace").strip()
            info["platform"] = "Android"
            info["version"] = out
            info["status"] = "connected"
        except subprocess.SubprocessError:
            # Not an Android device
            info["status"] = "unknown"

        return info

    @staticmethod
    def kill_adb_server():
        """Kill and restart the ADB server (useful when devices show as offline)."""
        try:
            subprocess.check_call(["adb", "kill-server"], stderr=subprocess.DEVNULL)
            subprocess.check_call(["adb", "start-server"], stderr=subprocess.DEVNULL)
            return True
        except subprocess.SubprocessError:
            return False

    @staticmethod
    def is_android_available() -> bool:
        """Check if ADB is available on the system."""
        try:
            subprocess.check_output(["adb", "version"], stderr=subprocess.DEVNULL)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    @staticmethod
    def is_ios_available() -> bool:
        """Check if libimobiledevice is available on the system."""
        try:
            subprocess.check_output(
                ["idevice_id", "-l"], stderr=subprocess.DEVNULL
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
