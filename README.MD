# LibreHardwareMonitorReporter

![CLI Image](https://i.imgur.com/cFmRKtx.png)

This is a Python CLI project that wraps around the LibreHardwareMonitor.dll files in order to allow CLI use cases. 
- Allow users to get sensor data from their hardware on Windows with a simple terminal, with optional Rich Table support
- Allow users to integrate the sensor data into their own projects, has support for sending to InfluxDB!
- This solution is available as an all-in-one executable, just hit run!

# Setup

You can download the latest release from the releases page: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases

## Arguements :
By design, you will not need to enter in any arguements in order to use the cli. However if you want to make some specific customisations before runtime or add influx support. Please read on :

### General :
- `--no-table` : If this is set, the output will be a simple console output, otherwise it will use Rich to display a table of the sensor data
- `--time <seconds>` : This is the time interval between each data 

### Libre-Config : 
The following options can be used to filter the sensors displayed. If none are set, all sensors will be shown. This is useful as certain CPUs may have hundreads of sensors (eg. a high end server CPU).
- `--CPU` : If this is set, only CPU related sensors will be shown
- `--GPU` : If this is set, only GPU related sensors will be shown 
- `--RAM` : If this is set, only RAM related sensors will be shown
- `--MOTHERBOARD` : If this is set, only Mainboard related sensors will be shown
- `--CONTROLLER` : If this is set, only Controller related sensors will be shown
- `--NETWORK` : If this is set, only Network related sensors will be shown
- `--STORAGE` : If this is set, only Storage related sensors will be shown

### Influx Config :
Tested on a InfluxDB2 container but the following solution should work in most environments, enter in the following :
- `--influx-url "<YOUR-ADDRESS"` : URL for the influx address, port number also needed
- `--token "<YOUR-TOKEN>"` : Token for the setup, can be an admin token but works with normal tokens fine
- `--org "<org>"` : Organisation for the setup
- `--bucket "<bucket>"` : Bucket for the setup

# For Devs/Advanced Users :
If you are not interested in any of the table stuff and just want to grab specific things from the Library in other projects and be done. Simply use the `libre_hardware_monitor_reporter.py` file in the `libre_cli` folder and initialize the class like so :
```python
from libre_cli.libre_hardware_monitor_reporter import LibreHardwareMonitorReporter
# Initialise the reporter, note that you can optionally pass in filter parameters here as well, but I would leave it at the default
LibreHardwareMonitorReport = LibreHardwareMonitorReporter()
sensor_data = LibreHardwareMonitorReport.get_sensor_data()
```

# Building your own executable (not required)
If you want to build your own executable from scratch. You will need to have PyInstaller and the libremonitorlib dll files and run the following command : 
`python -m PyInstaller --onefile --name "LibreMonitor" .\main.py --add-binary ".\libre_cli\LibreHardwareMonitorLib.dll;libre_cli" --add-binary ".\libre_cli\Aga.Controls.dll;libre_cli" --add-binary ".\libre_cli\HidSharp.dll;libre_cli"`

Please note the following :
- When running this, please make sure you run this with Admin permissions as certain things will not be shown, I've often found Intel CPU Temps are not shown when running without admin privs
- Add better examples of putting the data into an Influx Database

Many thanks to the LibreHardwareMonitor team : https://github.com/LibreHardwareMonitor/LibreHardwareMonitor

