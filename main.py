import sys
import threading
import libre_cli.libre_hardware_monitor_reporter 
import argparse
import time
# For Windows key press detection
import msvcrt

# For the rich table output integration
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

def get_keypress():
    """Cross-platform non-blocking key capture"""
    if sys.platform == "win32":
        if msvcrt.kbhit():
            return msvcrt.getwch()
    return None

def key_listener(filters, reporter=None, refresh_event=None):
    """Thread that listens for key presses and toggles filters."""
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
            if key.lower() in key_map:
                target = key_map[key.lower()]
                filters[target] = not filters[target]
                status = "ON" if filters[target] else "OFF"
                console.print(f"[cyan]{target}[/cyan] toggled [bold]{status}[/bold]")
                if reporter:
                    reporter.set_hardware_filter(
                        cpu=filters["CPU"],
                        gpu=filters["GPU"],
                        memory=filters["Memory"],
                        motherboard=filters["Motherboard"],
                        controller=filters["Controller"],
                        network=filters["Network"],
                        storage=filters["Storage"],
                    )
                # Trigger a refresh on the sensor data when a key is pressed
                if refresh_event:
                    refresh_event.set()

        time.sleep(0.1)

def make_table(sensor_data, filters=None):
    """Builds a rich table with filter status displayed above."""
    # If none is specified, just turn on all filters
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

    layout = Layout()
    active_filters = [key for key, val in filters.items() if val and key != "quit"]
    inactive_filters = [key for key, val in filters.items() if not val and key != "quit"]
    filter_key = Text()
    filter_key.append("Press keys to toggle filters: ", style="bold yellow")
    filter_key.append(" [c] CPU  [g] GPU  [m] Memory  [b] Motherboard  [n] Network  [s] Storage  [q] Quit", style="bold white")
    filter_text = Text()
    filter_text.append("Active Filters: ", style="bold yellow")
    
    if active_filters:
        filter_text.append(", ".join(active_filters), style="bold green")
    else:
        filter_text.append("None", style="bold red")

    if inactive_filters:
        filter_text.append(f"   (Inactive: {', '.join(inactive_filters)})", style="dim")

    layout.split_column(
        Layout(Panel(filter_key), size=3),
        Layout(Panel(filter_text, title="Filter Status", border_style="blue"), size=3),
        Layout(name="table",ratio=1)
    )

    table = Table(title="LibreHardwareMonitor Sensor Data")
    table.add_column("Type", style="yellow", no_wrap=True)
    table.add_column("Device", style="cyan", no_wrap=True)
    table.add_column("Sensor", style="magenta")
    table.add_column("Value", justify="right", style="green")

    for filter_type, device, sensor, value in sensor_data:
        table.add_row(filter_type, device, sensor, f"{value}")

    layout["table"].update(table)

    return layout

if __name__ == "__main__":
    try :
        # Setting up Rich Console and Argparse for future use
        console = Console()
        parser = argparse.ArgumentParser(description='Check to see if any flags are present')
        
        # InfluxDB stuff
        parser.add_argument('--influx-url', type=str, help='InfluxDBv2 server URL')
        parser.add_argument('--token', type=str, help='InfluxDBv2 authentication token')
        parser.add_argument('--org', type=str, help='InfluxDBv2 organization')
        parser.add_argument('--bucket', type=str, help='InfluxDBv2 bucket')

        # Arguements to filter by hardware type, all enabled by default
        parser.add_argument('--CPU', action='store_true', help='If --CPU-only is present, will only report CPU sensors')
        parser.add_argument('--GPU', action='store_true', help='If --GPU-only is present, will only report GPU sensors')
        parser.add_argument('--Memory', action='store_true', help='If --Memory-only is present, will only report Memory sensors')
        parser.add_argument('--Motherboard', action='store_true', help='If --Motherboard-only is present, will only report Motherboard sensors')
        parser.add_argument('--Controller', action='store_true', help='If --Controller-only is present, will only report Controller sensors')
        parser.add_argument('--Network', action='store_true', help='If --Network-only is present, will only report Network sensors')
        parser.add_argument('--Storage', action='store_true', help='If --Storage-only is present, will only report Storage sensors')
        parser.add_argument("--no-table", action="store_true", help="If --no-table is present, will print in raw python format")
        parser.add_argument("--time", type=int, help="Time in seconds for how long something should take to refresh")

        # Parse the arguments  
        args = parser.parse_args()

        # Setting up initial filter dictionary for key listener thread
        filters = {
            "CPU": args.CPU if args.CPU else False,
            "GPU": args.GPU if args.GPU else False,
            "Memory": args.Memory if args.Memory else False,
            "Motherboard": args.Motherboard if args.Motherboard else False,
            "Controller": args.Controller if args.Controller else False,
            "Network": args.Network if args.Network else False,
            "Storage": args.Storage if args.Storage else False,
            "quit": False,
        }

        # TLDR; if there is any hardware filter, then set those values in the LibreHardwareMonitorReporter init
        # If no hardware filter args are present, then just init all of them (which is recommended)
        if(args.CPU or args.GPU or args.Memory or args.Motherboard or args.Controller or args.Network or args.Storage):
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
        
        refresh_event = threading.Event()
        # Launch key listener thread
        threading.Thread(
            target=key_listener,
            args=(filters, LibreHardwareMonitorReport, refresh_event),
            daemon=True
        ).start()
        # Time refresh setup, if no arg given, default to 5 seconds, otherwise set to argument value
        
        time_refresh = 5
        if args.time :
            time_refresh = args.time

        # If no-table is present, print raw output to console
        if args.no_table :
            console.print("Starting LibreHardwareMonitor with no table output...")
            while True : 
                sensor_data = LibreHardwareMonitorReport.get_sensor_data()
                console.log("Fetched sensor data:")
                try :
                    for filter_type, device, sensor, value in sensor_data:
                            print(f" {filter_type} | {device} | {sensor} | {float(value):.2f}")
                except KeyboardInterrupt :
                    print("Exiting on user request...")
                time.sleep(time_refresh)
        # Else, use rich to make a nice table output
        else :
            with Live(make_table([],filters), refresh_per_second=1, console=console, screen=True) as live:
                while not filters["quit"]:
                    sensor_data = LibreHardwareMonitorReport.get_sensor_data()
                    live.update(make_table(sensor_data, filters))
                    refresh_event.wait(timeout=time_refresh)
                    refresh_event.clear()
    except KeyboardInterrupt:
        print("Exiting on user request...")