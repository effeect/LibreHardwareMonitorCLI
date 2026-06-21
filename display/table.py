import math
from typing import Optional

from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def make_table(sensor_data: list, filters: Optional[dict] = None,
               countdown: int = 0, page: int = 0, rows_per_page: int = 20) -> Layout:
    """Builds a rich layout with countdown, filter status, pagination, and sensor data table."""
    if filters is None:
        filters = {
            "CPU": True,
            "GPU": True,
            "Memory": True,
            "Motherboard": True,
            "Controller": True,
            "Network": True,
            "Storage": True,
            "quit": False,
        }

    active_filters = [key for key, val in filters.items() if val and key != "quit"]
    inactive_filters = [key for key, val in filters.items() if not val and key != "quit"]

    total_pages = max(1, math.ceil(len(sensor_data) / rows_per_page))
    page = min(max(0, page), total_pages - 1)
    start = page * rows_per_page
    visible = sensor_data[start : start + rows_per_page]

    countdown_text = Text()
    if countdown > 0:
        countdown_text.append("Next refresh in: ", style="bold yellow")
        countdown_text.append(f"{countdown}s", style="bold cyan")
    else:
        countdown_text.append("Refreshing...", style="bold green")

    filter_key = Text()
    filter_key.append("Press keys to toggle filters: ", style="bold yellow")
    filter_key.append(
        " [c] CPU  [g] GPU  [m] Memory  [b] Motherboard  [n] Network  [s] Storage"
        "  [←] Prev page  [→] Next page  [q] Quit",
        style="bold white",
    )

    filter_text = Text()
    filter_text.append("Active Filters: ", style="bold yellow")
    if active_filters:
        filter_text.append(", ".join(active_filters), style="bold green")
        if inactive_filters:
            filter_text.append(f"   (Inactive: {', '.join(inactive_filters)})", style="dim")
    else:
        filter_text.append("All", style="bold green")

    table = Table(
        title=f"LibreHardwareMonitor Sensor Data — Page {page + 1}/{total_pages}  ({len(sensor_data)} rows total)",
        expand=True,
    )
    table.add_column("Type", style="yellow", no_wrap=True)
    table.add_column("Device", style="cyan", no_wrap=True)
    table.add_column("Sensor", style="magenta")
    table.add_column("Value", justify="right", style="green")

    for filter_type, device, sensor, value in visible:
        table.add_row(filter_type, device, sensor, f"{value}")

    layout = Layout()
    layout.split_column(
        Layout(Panel(countdown_text, title="Refresh", border_style="cyan"), size=3),
        Layout(Panel(filter_key), size=3),
        Layout(Panel(filter_text, title="Filter Status", border_style="blue"), size=3),
        Layout(name="table", ratio=1),
    )
    layout["table"].update(table)

    return layout
