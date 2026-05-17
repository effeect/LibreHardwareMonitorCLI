# LibreHardwareMonitorReporter

![CLI Image](https://i.imgur.com/cFmRKtx.png)

This is a Python CLI project that wraps around the LibreHardwareMonitor.dll files in order to allow CLI use cases. 
- Allow users to get sensor data from their hardware on Windows with a simple terminal, with optional Rich Table support
- Allow users to integrate the sensor data into their own projects, has support for sending to InfluxDB!
- This solution is available as an all-in-one executable, just hit run!

# Setup

You can download the latest release (`LibreMonitor.exe`) from the [Releases page](../../releases/latest).

> **Run as Administrator** for full sensor visibility — some sensors (e.g. Intel CPU temperatures) are only accessible with elevated privileges.

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

Pre-built binaries are published automatically on each versioned release via GitHub Actions. If you want to build locally:

1. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

2. Download the latest LibreHardwareMonitor release and extract its DLLs into `libre_cli/`.

3. Run PyInstaller using the included spec file:

   ```sh
   python -m PyInstaller LibreMonitor.spec
   ```

The spec file automatically picks up all `.dll` files present in `libre_cli/`, so no manual `--add-binary` flags are needed. The output will be at `dist/LibreMonitor.exe`.

Many thanks to the LibreHardwareMonitor team : https://github.com/LibreHardwareMonitor/LibreHardwareMonitor

