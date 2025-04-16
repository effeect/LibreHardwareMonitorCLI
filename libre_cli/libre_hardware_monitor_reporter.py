"""
    This class uses LibreHardwareMonitorLib.dll and puts it in a CLI format
"""
import clr #pythonnet
import os 
import sys 

class LibreHardwareMonitorReporter:
    """
        Creates a LibreHardwareMonitor Handler and allows a call back in order to get all the info
    """
    def __init__(self):
        self.NoneType = type(None)
        self.results = []
        self.sensor_data = []
        # Creates a running process of librehardwaremonitor to be accessed at any point
        self.handler = self.handler_setup()

    def handler_setup(self):
        # Path to LibreHardwareMonitorLib.dll, remove .dll from the end

        # To handle it when the module is being called from a different directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dll_path = os.path.join(current_dir, 'LibreHardwareMonitorLib')
        sys.path.append(current_dir)
        self.file = "LibreHardwareMonitorLib"
        clr.AddReference(self.file)
        self.results = []
        self.csv = []
        # Importing it like this due to the DLL nature
        from LibreHardwareMonitor import Hardware

        # Setting up the handle, all enabled by default
        self.handle = Hardware.Computer()
        self.handle.IsCpuEnabled = True
        self.handle.IsGpuEnabled = True
        self.handle.IsMemoryEnabled = True
        self.handle.IsMotherboardEnabled = True
        self.handle.IsControllerEnabled = True
        self.handle.IsNetworkEnabled = True
        self.handle.IsStorageEnabled = True
        self.handle.Open()
        self.handle.Close()
        self.handle.Open()
        return self.handle

    def fetch_stats(self,handle,results):
        """Fetches all the Hardware and stats"""
        for i in handle.Hardware:
            i.Update()
            for sensor in i.Sensors:
                self.parse_sensor(sensor,results)
            for j in i.SubHardware:
                j.Update()
                for subsensor in j.Sensors:
                    self.parse_sensor(subsensor,results)
        return results

    def parse_sensor(self,sensor,results):
        """Gets all the possible results"""
        if sensor.Value is not None:
            value = (f"{sensor.Hardware.Name}",
                    f"{sensor.Name}",
                    f"{sensor.Value}")
            results.append(value)

            
    def get_sensor_data(self):
        self.results = [] # Clear previous results
        self.sensor_data = self.fetch_stats(self.handler,self.results)
        return self.sensor_data

# Below is an example of how you could use this in a script
# This is not necessary if you are using this as a module

if __name__ == "__main__":
    import time
    try :
        print("Starting LibreHardwareMonitor...")
        LibreHardwareMonitorReport = LibreHardwareMonitorReporter()
        while True :
            LibreHardwareMonitorReport.get_sensor_data()
            for i in LibreHardwareMonitorReport.results:
                print(i)
            time.sleep(10)
    except KeyboardInterrupt:
        # When being shut down, close the handle
        LibreHardwareMonitorReport.handler.Close()
        print("LibreHardwareMonitor closed.")
        print("Exiting...")
       
