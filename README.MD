# LibreHardwareMonitorReporter

This is a Python project that wraps around the LibreHardwareMonitor.dll files in order to allow a CLI, this may be useful in situations where you need to send system info/diagonistics into an Influx database or just see what the CPU temps are

# How to Use
There are two ways of using this. 

- You can either use the releases and run the librehardware monitor executable and get output of all the sensors.
- Implement the it as a library and use it in conjunction with other python files

Please note the following :
- By default, all the potenial sensor configs are turned on (will add a feature to disable/configure)
- When running this, please make sure you run this with Admin permissions as certain things will not be shown, I've often found Intel CPU Temps are not shown when running without admin privs

TODO: 
- Allow parameters to modify certain settings and output
- Add better examples of putting the data into an Influx Database

Many thanks to the LibreHardwareMonitor team : https://github.com/LibreHardwareMonitor/LibreHardwareMonitor

