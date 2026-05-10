import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from libre_cli.libre_hardware_monitor_reporter import LibreHardwareMonitorReporter


def _make_reporter(**kwargs) -> LibreHardwareMonitorReporter:
    """Construct a reporter with initialize_handler bypassed (no DLL required)."""
    mock_handle = MagicMock()

    def fake_init(self):
        self.handle = mock_handle
        return mock_handle

    with patch.object(LibreHardwareMonitorReporter, "initialize_handler", fake_init):
        return LibreHardwareMonitorReporter(**kwargs)


@pytest.fixture
def reporter() -> LibreHardwareMonitorReporter:
    return _make_reporter()


def _make_sensor(value, hw_type="CPU", hw_name="Intel i7", name="Temperature"):
    sensor = MagicMock()
    sensor.Value = value
    sensor.Hardware.HardwareType = hw_type
    sensor.Hardware.Name = hw_name
    sensor.Name = name
    return sensor


class TestInit:
    def test_default_flags_all_true(self):
        r = _make_reporter()
        for attr in ("cpu_enabled", "gpu_enabled", "memory_enabled",
                     "motherboard_enabled", "controller_enabled",
                     "network_enabled", "storage_enabled"):
            assert getattr(r, attr) is True

    def test_custom_flags_stored(self):
        r = _make_reporter(cpu=False, memory=False)
        assert r.cpu_enabled is False
        assert r.memory_enabled is False
        assert r.gpu_enabled is True


class TestSetHardwareFilter:
    def test_updates_instance_flags(self, reporter):
        reporter.set_hardware_filter(cpu=False, gpu=False, memory=True,
                                     motherboard=False, controller=False,
                                     network=True, storage=False)
        assert reporter.cpu_enabled is False
        assert reporter.gpu_enabled is False
        assert reporter.memory_enabled is True
        assert reporter.network_enabled is True

    def test_updates_handle_attributes(self, reporter):
        reporter.set_hardware_filter(cpu=False, gpu=True, memory=False,
                                     motherboard=True, controller=False,
                                     network=False, storage=True)
        assert reporter.handle.IsCpuEnabled is False
        assert reporter.handle.IsGpuEnabled is True
        assert reporter.handle.IsMemoryEnabled is False
        assert reporter.handle.IsStorageEnabled is True


class TestParseSensor:
    def test_appends_tuple_for_valid_value(self, reporter):
        sensor = _make_sensor(42.5)
        results = []
        reporter.parse_sensor(sensor, results)
        assert results == [("CPU", "Intel i7", "Temperature", "42.5")]

    def test_skips_sensor_with_none_value(self, reporter):
        sensor = _make_sensor(None)
        results = []
        reporter.parse_sensor(sensor, results)
        assert results == []

    def test_tuple_values_are_strings(self, reporter):
        sensor = _make_sensor(99.9)
        results = []
        reporter.parse_sensor(sensor, results)
        assert all(isinstance(v, str) for v in results[0])


class TestFetchStats:
    def test_iterates_main_hardware_sensors(self, reporter):
        sensor = _make_sensor(75.0, hw_type="GPU", hw_name="RTX 3080", name="GPU Core")
        mock_hw = MagicMock()
        mock_hw.Sensors = [sensor]
        mock_hw.SubHardware = []
        reporter.handle.Hardware = [mock_hw]

        results = reporter.fetch_stats(reporter.handle, [])
        assert len(results) == 1
        assert results[0] == ("GPU", "RTX 3080", "GPU Core", "75.0")
        mock_hw.Update.assert_called_once()

    def test_processes_subhardware_sensors(self, reporter):
        subsensor = _make_sensor(55.0, name="CPU Core #0")
        mock_subhw = MagicMock()
        mock_subhw.Sensors = [subsensor]
        mock_hw = MagicMock()
        mock_hw.Sensors = []
        mock_hw.SubHardware = [mock_subhw]
        reporter.handle.Hardware = [mock_hw]

        results = reporter.fetch_stats(reporter.handle, [])
        assert len(results) == 1
        assert results[0][2] == "CPU Core #0"
        mock_subhw.Update.assert_called_once()

    def test_main_and_subhardware_combined(self, reporter):
        main_sensor = _make_sensor(80.0, name="Package")
        sub_sensor = _make_sensor(70.0, name="Core #0")
        mock_subhw = MagicMock()
        mock_subhw.Sensors = [sub_sensor]
        mock_hw = MagicMock()
        mock_hw.Sensors = [main_sensor]
        mock_hw.SubHardware = [mock_subhw]
        reporter.handle.Hardware = [mock_hw]

        results = reporter.fetch_stats(reporter.handle, [])
        assert len(results) == 2


class TestGetSensorData:
    def test_clears_stale_results_before_fetch(self, reporter):
        reporter.results = [("stale", "data", "x", "1.0")]
        reporter.handle.Hardware = []
        reporter.get_sensor_data()
        assert reporter.results == []

    def test_returns_fetched_data(self, reporter):
        sensor = _make_sensor(50.0)
        mock_hw = MagicMock()
        mock_hw.Sensors = [sensor]
        mock_hw.SubHardware = []
        reporter.handle.Hardware = [mock_hw]

        data = reporter.get_sensor_data()
        assert len(data) == 1


class TestInitializeHandler:
    def test_exits_with_code_1_on_dll_failure(self):
        with patch.dict(os.environ, {"LOCALAPPDATA": "/tmp/fake_no_dll"}):
            with patch.object(sys.modules["clr"], "AddReference",
                              side_effect=Exception("DLL not found")):
                with pytest.raises(SystemExit) as exc_info:
                    LibreHardwareMonitorReporter()
                assert exc_info.value.code == 1
