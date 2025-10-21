# LibreHardwareMonitorReporter

This is a Python project that wraps around the LibreHardwareMonitor.dll files in order to allow a CLI, this may be useful in situations where you need to send system info/diagonistics into an Influx database or need a way to call the 

# How to Install
There are two ways of using this.

# Python Module

# Bundled Windows App

# To Build
`python -m PyInstaller --onefile --name "LibreMonitor" .\libre_cli\libre_hardware_monitor_reporter.py --add-binary ".\libre_cli\LibreHardwareMonitorLib.dll;." --add-binary ".\libre_cli\Aga.Controls.dll;." --add-binary ".\libre_cli\HidSharp.dll;."`


Please note the following :
- By default, all the potenial sensor configs are turned on (will add a feature to disable/configure)
- When running this, please make sure you run this with Admin permissions as certain things will not be shown, I've often found Intel CPU Temps are not shown when running without admin privs
- The .dll files in librecli may need to be unblocked, will look into possible solutions

TODO: 
- Add examples of putting the data into an Influx Database
- Make it a downloadable module for Windows machines if possible
- Use GitHub actions to create a pyinstaller version of this for Homelabers

Many thanks to the LibreHardwareMonitor team : https://github.com/LibreHardwareMonitor/LibreHardwareMonitor
