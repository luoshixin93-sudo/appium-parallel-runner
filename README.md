# Appium Parallel Runner

A lightweight Python framework for running Appium tests in parallel across multiple real Android and iOS devices. Built on top of `pytest` and `Appium-Python-Client`, this tool automates device allocation, test distribution, and result aggregation with minimal configuration.

## Features

- **Parallel Execution** — Distribute test cases across multiple devices simultaneously
- **Cross-Platform** — Supports both Android (UIAutomator2) and iOS (XCUITest) devices
- **Device Auto-Discovery** — Automatically detects connected devices via `adb` / `idevice_id`
- **Flexible Caps** — YAML-based desired capabilities configuration per device
- **HTML Reports** — Aggregated test results with pytest-html
- **Video Recording** — Captures device screen during test run (optional)
- **Retry Logic** — Built-in flaky test retry with configurable attempts

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Devices

Edit `caps/android_sample.yaml` or `caps/ios_sample.yaml`:

```yaml
platformName: Android
deviceName: Pixel_5
udid: "emulator-5554"        # or ADB serial
app: /path/to/app.apk
automationName: UIAutomator2
platformVersion: "14"
appPackage: com.example.app
appActivity: .MainActivity
```

### 3. Run Tests

```bash
# Run on all discovered devices in parallel
python run_parallel_tests.py --parallel

# Run on specific device UDID
python run_parallel_tests.py --udid emulator-5554

# Run with video recording
python run_parallel_tests.py --parallel --record-video
```

## Project Structure

```
appium-parallel-runner/
├── run_parallel_tests.py      # Main entry point
├── parallel_runner.py          # Core test orchestration
├── device_manager.py           # Device discovery & allocation
├── conftest.py                 # Pytest fixtures
├── caps/
│   ├── android_sample.yaml
│   └── ios_sample.yaml
├── tests/
│   └── test_sample.py
└── reports/
```

## Core Code

### `parallel_runner.py`

```python
import multiprocessing
from appium import webdriver
from appium.options.android import UiAutomator2Options
import yaml

class ParallelTestRunner:
    def __init__(self, caps_file: str, max_workers: int = None):
        with open(caps_file) as f:
            self.caps = yaml.safe_load(f)
        self.max_workers = max_workers or multiprocessing.cpu_count()

    def run(self, test_module: str):
        with multiprocessing.Pool(self.max_workers) as pool:
            results = pool.map(self._run_on_device, self._get_device_list())
        return results

    def _run_on_device(self, device_info: dict):
        options = UiAutomator2Options().load_capabilities(device_info)
        driver = webdriver.Remote("http://localhost:4723", options=options)
        try:
            # Test logic here
            driver.implicitly_wait(10)
            driver.find_element("accessibility id", "SomeElement")
        finally:
            driver.quit()
```

### `device_manager.py`

```python
import subprocess
import re

class DeviceManager:
    @staticmethod
    def get_android_devices() -> list[str]:
        out = subprocess.check_output(["adb", "devices"]).decode()
        serials = re.findall(r"^(\S+)\tdevice$", out, re.MULTILINE)
        return serials

    @staticmethod
    def get_ios_devices() -> list[str]:
        try:
            out = subprocess.check_output(["idevice_id", "-l"]).decode()
            return [line.strip() for line in out.strip().split("\n") if line.strip()]
        except FileNotFoundError:
            return []
```

## Requirements

```
Appium-Python-Client>=3.0.0
pytest>=7.4.0
pytest-xdist>=3.3.0
pytest-html>=4.0.0
PyYAML>=6.0
```

## License

MIT License — see LICENSE file.

---

Made with ❤️ for cloud phone automation → [qtphone.com](https://www.qtphone.com/)
