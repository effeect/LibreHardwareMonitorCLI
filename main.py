import libre_cli.libre_hardware_monitor_reporter 
import argparse
import time
import requests

if __name__ == "__main__":
    try :

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
        # Parse the arguments
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
        while True :
            sensor_data = LibreHardwareMonitorReport.get_sensor_data()
            print(sensor_data)
            time.sleep(10)  # Wait for 10 seconds before sending the next batch
    except KeyboardInterrupt :
        print("Exiting on user request...")