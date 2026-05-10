import sys
import threading
import pytest
from unittest.mock import patch, MagicMock

from main import get_keypress, key_listener


def _base_filters() -> dict:
    return {"CPU": True, "GPU": True, "Memory": True, "Motherboard": True,
            "Controller": True, "Network": True, "Storage": True, "quit": False}


def _run(filters, reporter=None, refresh_event=None, state=None, timeout=2.0) -> bool:
    """Run key_listener in a daemon thread; return True if it exited within timeout."""
    t = threading.Thread(target=key_listener, args=(filters, reporter, refresh_event, state))
    t.daemon = True
    t.start()
    t.join(timeout=timeout)
    return not t.is_alive()


class TestGetKeypress:
    def test_returns_none_on_non_win32(self):
        with patch.object(sys, "platform", "linux"):
            assert get_keypress() is None

    def test_returns_none_when_no_kbhit_on_win32(self):
        with patch.object(sys, "platform", "win32"):
            with patch("main.msvcrt") as m:
                m.kbhit.return_value = False
                assert get_keypress() is None

    def test_returns_char_on_win32_kbhit(self):
        with patch.object(sys, "platform", "win32"):
            with patch("main.msvcrt") as m:
                m.kbhit.return_value = True
                m.getwch.return_value = "a"
                assert get_keypress() == "a"

    def test_maps_left_arrow(self):
        with patch.object(sys, "platform", "win32"):
            with patch("main.msvcrt") as m:
                m.kbhit.return_value = True
                m.getwch.side_effect = ["\xe0", "\x4b"]
                assert get_keypress() == "LEFT"

    def test_maps_right_arrow(self):
        with patch.object(sys, "platform", "win32"):
            with patch("main.msvcrt") as m:
                m.kbhit.return_value = True
                m.getwch.side_effect = ["\xe0", "\x4d"]
                assert get_keypress() == "RIGHT"

    def test_maps_up_arrow(self):
        with patch.object(sys, "platform", "win32"):
            with patch("main.msvcrt") as m:
                m.kbhit.return_value = True
                m.getwch.side_effect = ["\xe0", "\x48"]
                assert get_keypress() == "UP"

    def test_maps_down_arrow(self):
        with patch.object(sys, "platform", "win32"):
            with patch("main.msvcrt") as m:
                m.kbhit.return_value = True
                m.getwch.side_effect = ["\xe0", "\x50"]
                assert get_keypress() == "DOWN"


class TestKeyListener:
    def test_quit_sets_flag_and_thread_exits(self):
        filters = _base_filters()
        with patch("main.get_keypress", side_effect=["q"]):
            with patch("main.time.sleep"):
                with patch("main.Console", return_value=MagicMock()):
                    exited = _run(filters)
        assert filters["quit"] is True
        assert exited

    def test_toggle_cpu_flips_filter(self):
        filters = _base_filters()
        with patch("main.get_keypress", side_effect=["c", "q"]):
            with patch("main.time.sleep"):
                with patch("main.Console", return_value=MagicMock()):
                    _run(filters)
        assert filters["CPU"] is False

    def test_toggle_gpu_flips_filter(self):
        filters = _base_filters()
        with patch("main.get_keypress", side_effect=["g", "q"]):
            with patch("main.time.sleep"):
                with patch("main.Console", return_value=MagicMock()):
                    _run(filters)
        assert filters["GPU"] is False

    def test_toggle_calls_reporter_set_hardware_filter(self):
        filters = _base_filters()
        mock_reporter = MagicMock()
        with patch("main.get_keypress", side_effect=["c", "q"]):
            with patch("main.time.sleep"):
                with patch("main.Console", return_value=MagicMock()):
                    _run(filters, reporter=mock_reporter)
        mock_reporter.set_hardware_filter.assert_called()

    def test_all_filters_off_calls_reporter_with_all_true(self):
        # Only CPU is active; toggling it off should make reporter receive all-True call.
        filters = {"CPU": True, "GPU": False, "Memory": False, "Motherboard": False,
                   "Controller": False, "Network": False, "Storage": False, "quit": False}
        mock_reporter = MagicMock()
        with patch("main.get_keypress", side_effect=["c", "q"]):
            with patch("main.time.sleep"):
                with patch("main.Console", return_value=MagicMock()):
                    _run(filters, reporter=mock_reporter)
        last_kwargs = mock_reporter.set_hardware_filter.call_args.kwargs
        assert last_kwargs["cpu"] is True
        assert last_kwargs["gpu"] is True

    def test_left_arrow_decrements_page(self):
        filters = _base_filters()
        state = {"page": 2}
        with patch("main.get_keypress", side_effect=["LEFT", "q"]):
            with patch("main.time.sleep"):
                with patch("main.Console", return_value=MagicMock()):
                    _run(filters, state=state)
        assert state["page"] == 1

    def test_left_arrow_clamps_at_zero(self):
        filters = _base_filters()
        state = {"page": 0}
        with patch("main.get_keypress", side_effect=["LEFT", "q"]):
            with patch("main.time.sleep"):
                with patch("main.Console", return_value=MagicMock()):
                    _run(filters, state=state)
        assert state["page"] == 0

    def test_right_arrow_increments_page(self):
        filters = _base_filters()
        state = {"page": 0}
        with patch("main.get_keypress", side_effect=["RIGHT", "q"]):
            with patch("main.time.sleep"):
                with patch("main.Console", return_value=MagicMock()):
                    _run(filters, state=state)
        assert state["page"] == 1

    def test_keypress_signals_refresh_event(self):
        filters = _base_filters()
        state = {"page": 0}
        refresh_event = MagicMock()
        with patch("main.get_keypress", side_effect=["RIGHT", "q"]):
            with patch("main.time.sleep"):
                with patch("main.Console", return_value=MagicMock()):
                    _run(filters, refresh_event=refresh_event, state=state)
        refresh_event.set.assert_called()

    def test_no_keypress_does_not_signal_event(self):
        filters = _base_filters()
        state = {"page": 0}
        refresh_event = MagicMock()
        # None → no action, then 'q' to exit
        with patch("main.get_keypress", side_effect=[None, "q"]):
            with patch("main.time.sleep"):
                with patch("main.Console", return_value=MagicMock()):
                    _run(filters, refresh_event=refresh_event, state=state)
        refresh_event.set.assert_not_called()
