import io
import pytest
from rich.console import Console
from rich.layout import Layout

from display.table import make_table


def render(layout: Layout, width: int = 200, height: int = 50) -> str:
    """Render a Rich Layout to a plain string for inspection."""
    buf = io.StringIO()
    console = Console(file=buf, width=width, height=height, force_terminal=True, no_color=True)
    console.print(layout)
    return buf.getvalue()


def render_table(layout: Layout, width: int = 200) -> str:
    """Render only the inner Table (bypasses Layout ratio sizing issues in non-TTY context)."""
    buf = io.StringIO()
    console = Console(file=buf, width=width, force_terminal=True, no_color=True)
    console.print(layout["table"].renderable)
    return buf.getvalue()


def table_title(layout: Layout) -> str:
    return layout["table"].renderable.title


def make_rows(n: int) -> list:
    return [("CPU", f"Device {i}", f"Sensor {i}", f"{i}.0") for i in range(n)]


class TestMakeTable:
    def test_returns_layout_instance(self):
        assert isinstance(make_table([]), Layout)

    def test_empty_data_gives_one_page(self):
        assert "Page 1/1" in render(make_table([]))

    def test_first_page_shows_first_rows(self):
        data = make_rows(25)
        layout = make_table(data, page=0, rows_per_page=20)
        assert "Page 1/2" in table_title(layout)
        text = render_table(layout)
        assert "Sensor 0" in text

    def test_second_page_shows_remaining_rows(self):
        data = make_rows(25)
        layout = make_table(data, page=1, rows_per_page=20)
        assert "Page 2/2" in table_title(layout)
        text = render_table(layout)
        assert "Sensor 20" in text
        assert "Sensor 0" not in text

    def test_page_clamps_negative_to_first(self):
        data = make_rows(5)
        assert "Page 1/1" in table_title(make_table(data, page=-99))

    def test_page_clamps_above_max_to_last(self):
        data = make_rows(25)
        assert "Page 2/2" in table_title(make_table(data, page=999, rows_per_page=20))

    def test_countdown_positive_shows_timer(self):
        assert "Next refresh in:" in render(make_table([], countdown=10))

    def test_countdown_zero_shows_refreshing(self):
        assert "Refreshing..." in render(make_table([], countdown=0))

    def test_all_filters_false_shows_all_keyword(self):
        filters = {k: False for k in
                   ["CPU", "GPU", "Memory", "Motherboard", "Controller", "Network", "Storage", "quit"]}
        assert "All" in render(make_table([], filters=filters))

    def test_mixed_filters_lists_inactive(self):
        filters = {"CPU": True, "GPU": False, "Memory": True, "Motherboard": False,
                   "Controller": False, "Network": False, "Storage": False, "quit": False}
        text = render(make_table([], filters=filters))
        assert "CPU" in text
        assert "Inactive" in text
        assert "GPU" in text

    def test_none_filters_returns_valid_layout(self):
        layout = make_table([], filters=None)
        assert isinstance(layout, Layout)
        assert "Page 1/1" in render(layout)
