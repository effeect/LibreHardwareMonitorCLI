import pytest
from unittest.mock import patch, MagicMock, call

from influxdb.influx import InfluxManager


def _make_mock_point():
    """Return a MagicMock that chains .tag/.field/.time calls like a real Point."""
    mp = MagicMock()
    mp.tag.return_value = mp
    mp.field.return_value = mp
    mp.time.return_value = mp
    return mp


@pytest.fixture
def mocked_client():
    """Patch InfluxDBClient for the duration of a test, yielding (cls, client, write_api)."""
    with patch("influxdb.influx.InfluxDBClient") as mock_cls:
        mock_client = MagicMock()
        mock_write_api = MagicMock()
        mock_client.write_api.return_value = mock_write_api
        mock_cls.return_value = mock_client
        yield mock_cls, mock_client, mock_write_api


class TestInfluxManagerInit:
    def test_creates_client_with_correct_args(self, mocked_client):
        mock_cls, _, _ = mocked_client
        InfluxManager(url="http://localhost:8086", token="tok", org="myorg", bucket="mybucket")
        mock_cls.assert_called_once_with(url="http://localhost:8086", token="tok", org="myorg")

    def test_raises_when_client_construction_fails(self):
        with patch("influxdb.influx.InfluxDBClient", side_effect=Exception("conn failed")):
            with pytest.raises(Exception, match="conn failed"):
                InfluxManager("http://x", "tok", "org", "bucket")


class TestInfluxManagerWriteData:
    def test_uses_correct_measurement(self, mocked_client):
        with patch("influxdb.influx.Point") as mock_point_cls:
            mock_point_cls.return_value = _make_mock_point()
            mgr = InfluxManager("http://x", "tok", "org", "bucket")
            mgr.write_data(["CPU", "Intel i7", "Temperature", 55.0])
            mock_point_cls.assert_called_once_with("CPU")

    def test_sets_component_and_sensor_tags(self, mocked_client):
        with patch("influxdb.influx.Point") as mock_point_cls:
            mp = _make_mock_point()
            mock_point_cls.return_value = mp
            mgr = InfluxManager("http://x", "tok", "org", "bucket")
            mgr.write_data(["CPU", "Intel i7", "Temperature", 55.0])
            mp.tag.assert_any_call("component", "Intel i7")
            mp.tag.assert_any_call("sensor", "Temperature")

    def test_sets_value_field(self, mocked_client):
        with patch("influxdb.influx.Point") as mock_point_cls:
            mp = _make_mock_point()
            mock_point_cls.return_value = mp
            mgr = InfluxManager("http://x", "tok", "org", "bucket")
            mgr.write_data(["CPU", "Intel i7", "Temperature", 55.0])
            mp.field.assert_called_once_with("value", 55.0)

    def test_silences_write_exception(self, mocked_client):
        _, _, mock_write_api = mocked_client
        mock_write_api.write.side_effect = Exception("write error")
        with patch("influxdb.influx.Point") as mock_point_cls:
            mock_point_cls.return_value = _make_mock_point()
            mgr = InfluxManager("http://x", "tok", "org", "bucket")
            mgr.write_data(["CPU", "Intel i7", "Temperature", 55.0])  # must not raise

    def test_prints_message_on_write_exception(self, mocked_client, capsys):
        _, _, mock_write_api = mocked_client
        mock_write_api.write.side_effect = Exception("write error")
        with patch("influxdb.influx.Point") as mock_point_cls:
            mock_point_cls.return_value = _make_mock_point()
            mgr = InfluxManager("http://x", "tok", "org", "bucket")
            mgr.write_data(["CPU", "Intel i7", "Temperature", 55.0])
        assert "Write failed" in capsys.readouterr().out


class TestInfluxManagerExit:
    def test_closes_client(self, mocked_client):
        _, mock_client, _ = mocked_client
        mgr = InfluxManager("http://x", "tok", "org", "bucket")
        mgr.exit()
        mock_client.close.assert_called_once()
