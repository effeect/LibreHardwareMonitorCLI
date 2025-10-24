import libre_cli.libre_hardware_monitor_reporter 
import argparse
import time
import requests
import os

# For the rich table output integration
from rich.console import Console
from rich.table import Table
from rich.live import Live

def make_table(sensor_data):
    table = Table(title="LibreHardwareMonitor Sensor Data")
    table.add_column("Device", style="cyan", no_wrap=True)
    table.add_column("Sensor", style="magenta")
    table.add_column("Value", justify="right", style="green")

    for device, sensor, value in sensor_data:
        table.add_row(device, sensor, f"{float(value):.2f}")
    return table

if __name__ == "__main__":
    try :
        console = Console()
        parser = argparse.ArgumentParser(description='Check to see if any flags are present')
        # Rethink this
        # parser.add_argument('-t', action='store_true', help='If -t is present, will continue indefintely')
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
        args = parser.parse_args()

        # TLDR; if there is any hardware filter, then set those values in the LibreHardwareMonitorReporter init
        # If no hardware filter args are present, then just init all of them (which is how I would do it normally)
        if( args.CPU or args.GPU or args.Memory or args.Motherboard or args.Controller or args.Network or args.Storage):
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
        
        # Currently two routes in place
        # A simple cli output, designed for powershell and stuff
        # A Rich table output, more useful if you need to inspect it
        time_refresh = 5
        if args.time :
            time_refresh = args.time

        if args.no_table :
            while True : 
                console.print("Starting LibreHardwareMonitor with no table output...")
                sensor_data = LibreHardwareMonitorReport.get_sensor_data()
                console.log("Fetched sensor data:")
                try :
                    for device, sensor, value in sensor_data:
                            print(f"{device} | {sensor} | {float(value):.2f}")
                except KeyboardInterrupt :
                    print("Exiting on user request...")
                time.sleep(time_refresh)
        else :
            console.print("Starting LibreHardwareMonitor with table output...")
            with Live(make_table([]), refresh_per_second=1, console=console, screen=False) as live:
                while True:
                    sensor_data = LibreHardwareMonitorReport.get_sensor_data()
                    live.update(make_table(sensor_data))
                    time.sleep(time_refresh) 
    except KeyboardInterrupt :
        print("Exiting on user request...")