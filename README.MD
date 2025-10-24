# LibreHardwareMonitorReporter

This is a Python project that wraps around the LibreHardwareMonitor.dll files in order to allow CLI usecases. There are a few purposes of this program:
- Allow users to get sensor data from their hardware in a simple way
- Allow users to integrate the sensor data into their own python projects

# For EXE Users
You can download the latest release from the releases page : https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases
# Arguements
- `--no-table` : If this is set, the output will be a simple console output, otherwise it will use Rich to display a table of the sensor data
- `--time <seconds>` : This is the time interval between each data 

The following options can be used to filter the sensors displayed. If none are set, all sensors will be shown. This is useful as certain CPUs may have hundreads of sensors (eg. a high end server CPU).
- `--CPU` : If this is set, only CPU related sensors will be shown
- `--GPU` : If this is set, only GPU related sensors will be shown 
- `--RAM` : If this is set, only RAM related sensors will be shown
- `--MOTHERBOARD` : If this is set, only Mainboard related sensors will be shown
- `--CONTROLLER` : If this is set, only Controller related sensors will be shown
- `--NETWORK` : If this is set, only Network related sensors will be shown
- `--STORAGE` : If this is set, only Storage related sensors will be shown

# For Python Users/Devs :
If you are not interested with any of the table stuff and just want to grab specifc things from the Library in other projects and be done. Simply use the `libre_hardware_monitor_reporter.py` file in the `libre_cli` folder and initialize the class like so :
```python
from libre_cli.libre_hardware_monitor_reporter import LibreHardwareMonitorReporter
# Intialize the reporter, note that you can optionaly pass in filter parameters here as well, but I would leave it at the default
LibreHardwareMonitorReport = LibreHardwareMonitorReporter()
sensor_data = LibreHardwareMonitorReport.get_sensor_data()
```

Please note the following :
- When running this, please make sure you run this with Admin permissions as certain things will not be shown, I've often found Intel CPU Temps are not shown when running without admin privs

- Add better examples of putting the data into an Influx Database

Many thanks to the LibreHardwareMonitor team : https://github.com/LibreHardwareMonitor/LibreHardwareMonitor

