# LibreHardwareMonitorReporter

This is a Python project that wraps around the LibreHardwareMonitor.dll files in order to allow a CLI, this may be useful in situations where you need to send system info/diagonistics into an Influx database or anything for that matter.

There is currently one way of running this : 
- Cloning the repo and running the main.py file, make sure to run the requirements.txt

Can be run like this : 
`python3 ./main.py -t`

Please note the following :
- By default, all the potenial sensor configs are turned on (will add a feature to disable/configure)
- When running this, please make sure you run this with Admin permissions as certain things will not be shown, I've often found Intel CPU Temps are not shown when running without admin privs
- The .dll files in librecli may need to be unblocked, will look into possible solutions

TODO: 
- Add examples of putting the data into an Influx Database
- Make it a downloadable module for Windows machines if possible
- Use GitHub actions to create a pyinstaller version of this for Homelabers

Many thanks to the LibreHardwareMonitor team : https://github.com/LibreHardwareMonitor/LibreHardwareMonitor
