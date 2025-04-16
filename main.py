"""
    Example script that will dump all the info out of the dll and print it out
"""
from libre_cli.libre_hardware_monitor_reporter import LibreHardwareMonitorReporter
import time
import argparse

if __name__ == "__main__":
    try :
        parser = argparse.ArgumentParser(description='Check to see if any flags are present')
        parser.add_argument('-t', action='store_true', help='If -t is present, will continue indefintely')
        # Parse the arguments
        args = parser.parse_args()
        # Access the value of the -t argument
        print("Starting LibreHardwareMonitor...")
        LibreHardwareMonitorReport = LibreHardwareMonitorReporter()
        # If arg.t is present, report indefintely
        if args.t :
            while True :
                LibreHardwareMonitorReport.get_sensor_data()
                for i in LibreHardwareMonitorReport.results:
                    print(i)
                time.sleep(10)
        else :
            LibreHardwareMonitorReport.get_sensor_data()
            for i in LibreHardwareMonitorReport.results:
                print(i)
            print("Completed")
    except KeyboardInterrupt:
        # When being shut down, close the handle
        LibreHardwareMonitorReport.handler.Close()
        print("LibreHardwareMonitor closed.")
        print("Exiting...")