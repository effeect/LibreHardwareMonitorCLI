import sys
from unittest.mock import MagicMock

# Stub Windows-only and .NET-dependent modules before any project code is imported.
# This allows the test suite to run on Linux/WSL without the DLL or msvcrt.
for _mod in [
    "clr",
    "msvcrt",
    "LibreHardwareMonitor",
    "LibreHardwareMonitor.Hardware",
    "influxdb_client",
    "influxdb_client.client",
    "influxdb_client.client.write_api",
]:
    sys.modules.setdefault(_mod, MagicMock())

import pytest

# Fake data for testing purposes
@pytest.fixture
def sample_sensor_data() -> list:
    return [
        ("CPU", "Intel Core i7", "CPU Core #1", "45.0"),
        ("CPU", "Intel Core i7", "CPU Package", "50.0"),
        ("GPU", "NVIDIA RTX 3080", "GPU Core", "65.0"),
        ("Memory", "Generic Memory", "Virtual Memory Used", "8192.0"),
    ]


@pytest.fixture
def default_filters() -> dict:
    return {
        "CPU": True,
        "GPU": True,
        "Memory": True,
        "Motherboard": True,
        "Controller": True,
        "Network": True,
        "Storage": True,
        "quit": False,
    }
