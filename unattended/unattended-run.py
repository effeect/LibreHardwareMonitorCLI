"""
    Module to print out the results of LibreHardwareMonitorReporter continuously.

    Useful for powershell/ansible related operations

"""
import libre_cli.libre_hardware_monitor_reporter as libre_cli
import time

def unattended_run(librehardware_monitor_reporter : libre_cli.LibreHardwareMonitorReporter):
    """
    Runs the LibreHardwareMonitorReporter in unattended mode, continuously fetching and printing data.
    
    This will run indefintekly until interrupted by the user."""
    try :
        while True :
            librehardware_monitor_reporter.get_sensor_data()
            for i in librehardware_monitor_reporter.results:
                print(i)
            time.sleep(10)
    except KeyboardInterrupt:
        # When being shut down, close the handle
        librehardware_monitor_reporter.handler.Close()
        print("LibreHardwareMonitor closed.")
        print("Exiting...")