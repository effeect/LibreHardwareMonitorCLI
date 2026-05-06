import sys
import threading
import libre_cli.libre_hardware_monitor_reporter
import argparse
import math
import time
# For Windows key press detection
import msvcrt
from typing import Optional

# For Influx Integration
from influxdb.influx import InfluxManager

# For the rich table output integration
from rich.console import Console
from rich.live import Live

from display.table import make_table


_EXTENDED_KEY_MAP = {
    '\x4b': 'LEFT',
    '\x4d': 'RIGHT',
    '\x48': 'UP',
    '\x50': 'DOWN',
}

def get_keypress() -> Optional[str]:
    """Non-blocking key capture. Arrow keys are returned as 'LEFT'/'RIGHT'/'UP'/'DOWN'."""
    if sys.platform == "win32":
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ('\x00', '\xe0'):
                # Extended key: consume the scan-code byte and map it to a name.
                ch2 = msvcrt.getwch()
                return _EXTENDED_KEY_MAP.get(ch2)
            return ch
    return None


def key_listener(filters: dict, reporter=None, refresh_event: Optional[threading.Event] = None,
                 state: Optional[dict] = None) -> None:
    """Thread that listens for key presses and toggles filters or changes page."""
    console = Console()
    key_map = {
        "c": "CPU",
        "g": "GPU",
        "m": "Memory",
        "b": "Motherboard",
        "n": "Network",
        "s": "Storage",
    }

    while True:
        key = get_keypress()
        if key:
            if key.lower() == "q":
                console.print("[red]Quitting...[/red]")
                filters["quit"] = True
                break
            if key == "LEFT" and state is not None:
                state["page"] = max(0, state["page"] - 1)
                if refresh_event:
                    refresh_event.set()
            elif key == "RIGHT" and state is not None:
                state["page"] = state["page"] + 1  # upper clamp applied in main loop
                if refresh_event:
                    refresh_event.set()
            elif key.lower() in key_map:
                target = key_map[key.lower()]
                filters[target] = not filters[target]
                status = "ON" if filters[target] else "OFF"
                console.print(f"[cyan]{target}[/cyan] toggled [bold]{status}[/bold]")
                if reporter:
                    any_active = any(filters[k] for k in key_map.values())
                    if any_active:
                        reporter.set_hardware_filter(
                            cpu=filters["CPU"],
                            gpu=filters["GPU"],
                            memory=filters["Memory"],
                            motherboard=filters["Motherboard"],
                            controller=filters["Controller"],
                            network=filters["Network"],
                            storage=filters["Storage"],
                        )
                    else:
                        # No filters active means no restriction — show all hardware
                        reporter.set_hardware_filter(
                            cpu=True, gpu=True, memory=True, motherboard=True,
                            controller=True, network=True, storage=True,
                        )
                if refresh_event:
                    refresh_event.set()

        time.sleep(0.1)


if __name__ == "__main__":
    try:
        console = Console()
        parser = argparse.ArgumentParser(description='Check to see if any flags are present')
        use_influx = False
        # InfluxDB args
        parser.add_argument('--influx-url', type=str, help='InfluxDBv2 server URL')
        parser.add_argument('--token', type=str, help='InfluxDBv2 authentication token')
        parser.add_argument('--org', type=str, help='InfluxDBv2 organization')
        parser.add_argument('--bucket', type=str, help='InfluxDBv2 bucket')

        # Hardware filter args — all enabled by default when none are specified
        parser.add_argument('--CPU', action='store_true', help='If --CPU is present, will only report CPU sensors')
        parser.add_argument('--GPU', action='store_true', help='If --GPU is present, will only report GPU sensors')
        parser.add_argument('--Memory', action='store_true', help='If --Memory is present, will only report Memory sensors')
        parser.add_argument('--Motherboard', action='store_true', help='If --Motherboard is present, will only report Motherboard sensors')
        parser.add_argument('--Controller', action='store_true', help='If --Controller is present, will only report Controller sensors')
        parser.add_argument('--Network', action='store_true', help='If --Network is present, will only report Network sensors')
        parser.add_argument('--Storage', action='store_true', help='If --Storage is present, will only report Storage sensors')
        parser.add_argument("--no-table", action="store_true", help="If --no-table is present, will print in raw python format")
        parser.add_argument("--time", type=int, help="Time in seconds for how long something should take to refresh")

        args = parser.parse_args()

        filters = {
            "CPU": args.CPU,
            "GPU": args.GPU,
            "Memory": args.Memory,
            "Motherboard": args.Motherboard,
            "Controller": args.Controller,
            "Network": args.Network,
            "Storage": args.Storage,
            "quit": False,
        }

        # Warn if only some InfluxDB flags are provided
        influx_args = {"--influx-url": args.influx_url, "--token": args.token, "--org": args.org, "--bucket": args.bucket}
        provided = [k for k, v in influx_args.items() if v]
        missing = [k for k, v in influx_args.items() if not v]
        influx_man: Optional[InfluxManager] = None
        if len(provided) == 4:
            use_influx = True
            influx_man = InfluxManager(args.influx_url, args.token, args.org, args.bucket)
        elif provided:
            console.print(f"[yellow]Warning: InfluxDB requires all four flags. Provided: {provided}. Missing: {missing}. InfluxDB disabled.[/yellow]")

        if args.CPU or args.GPU or args.Memory or args.Motherboard or args.Controller or args.Network or args.Storage:
            LibreHardwareMonitorReport = libre_cli.libre_hardware_monitor_reporter.LibreHardwareMonitorReporter(
                cpu=args.CPU,
                gpu=args.GPU,
                memory=args.Memory,
                motherboard=args.Motherboard,
                controller=args.Controller,
                network=args.Network,
                storage=args.Storage
            )
        else:
            LibreHardwareMonitorReport = libre_cli.libre_hardware_monitor_reporter.LibreHardwareMonitorReporter()

        state = {"page": 0}
        refresh_event = threading.Event()
        threading.Thread(
            target=key_listener,
            args=(filters, LibreHardwareMonitorReport, refresh_event, state),
            daemon=True
        ).start()

        time_refresh = args.time if args.time and args.time > 0 else 5

        if args.no_table:
            console.print("Starting LibreHardwareMonitor with no table output...")
            while True:
                sensor_data = LibreHardwareMonitorReport.get_sensor_data()
                console.log("Fetched sensor data:")
                try:
                    for filter_type, device, sensor, value in sensor_data:
                        print(f" {filter_type} | {device} | {sensor} | {float(value):.2f}")
                        if influx_man:
                            influx_man.write_data([filter_type, device, sensor, float(value)])
                except KeyboardInterrupt:
                    print("Exiting on user request...")
                time.sleep(time_refresh)
        else:
            sensor_data: list = []
            next_refresh = time.monotonic() + time_refresh

            with Live(make_table([], filters, countdown=time_refresh), refresh_per_second=2, console=console, screen=True) as live:
                while not filters["quit"]:
                    rows_per_page = max(5, console.size.height - 20)
                    total_pages = max(1, math.ceil(len(sensor_data) / rows_per_page))
                    state["page"] = min(state["page"], total_pages - 1)

                    remaining = max(0, int(next_refresh - time.monotonic()))
                    live.update(make_table(sensor_data, filters, countdown=remaining,
                                           page=state["page"], rows_per_page=rows_per_page))

                    triggered = refresh_event.wait(timeout=1.0)
                    refresh_event.clear()

                    if triggered or time.monotonic() >= next_refresh:
                        sensor_data = LibreHardwareMonitorReport.get_sensor_data()
                        if influx_man:
                            for filter_type, device, sensor, value in sensor_data:
                                influx_man.write_data([filter_type, device, sensor, float(value)])
                        next_refresh = time.monotonic() + time_refresh

    except KeyboardInterrupt:
        print("Exiting on user request...")
