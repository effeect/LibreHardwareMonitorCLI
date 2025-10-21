"""
    Class Module for LibreHardwareMonitorReport
"""

import clr # Pythonnet to interface with .dlls
import os 
import sys
import glob

class LibreHardwareMonitorReporter:
    """
    Class to report hardware statistics using LibreHardwareMonitor
    """
    def __init__(self, cpu=True, gpu=True, memory=True, motherboard=True, controller=True, network=True, storage=True):
        self.NoneType = type(None)
        # Intializing Arrays to store the info
        self.results = []
        self.sensor_data = []

        # self variables to set what hardware to include/exclude. All enabled by default.
        # Might be useful if you are only interested in a specific bit of hardware
        self.cpu_enabled = cpu
        self.gpu_enabled = gpu
        self.memory_enabled = memory
        self.motherboard_enabled = motherboard
        self.controller_enabled = controller
        self.network_enabled = network
        self.storage_enabled = storage
        self.handler = self.initialize_handler()
    
    def initialize_handler(self):
        # In order to make this program easily buildable, we will use winget to setup LibreHardwareMonitor
        # The DLL will be located in the WinGet packages folder so we will grab it
        def find_librehardwaremonitor_dll():
            base_path = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'WinGet', 'Packages')
            pattern = os.path.join(base_path, 'LibreHardwareMonitor.LibreHardwareMonitor_*', 'LibreHardwareMonitorLib.dll')
            matches = glob.glob(pattern)
            # If theres a version in Windows, we will use that, if not we will use our own, GITHUB actions needed
            if matches:
                print("DLL found at: " + matches[0])
                return matches[0]  # Return the first match
            else:
                # To handle it when the module is being called from a different directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                return os.path.join(current_dir, 'LibreHardwareMonitorLib')

        # Path to LibreHardwareMonitorLib.dll, remove .dll from the end
        # To handle it when the module is being called from a different directory
        dll_path = find_librehardwaremonitor_dll()
        sys.path.append(os.path.dirname(dll_path))
        clr.AddReference(dll_path)
        self.results = []
        self.csv = []
        # Importing it like this due to the DLL nature
        from LibreHardwareMonitor import Hardware

        # Setting up the handle, all enabled by default
        self.handle = Hardware.Computer()
        self.handle.IsCpuEnabled = self.cpu_enabled
        self.handle.IsGpuEnabled = self.gpu_enabled
        self.handle.IsMemoryEnabled = self.memory_enabled
        self.handle.IsMotherboardEnabled = self.motherboard_enabled
        self.handle.IsControllerEnabled = self.controller_enabled
        self.handle.IsNetworkEnabled = self.network_enabled
        self.handle.IsStorageEnabled = self.storage_enabled
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