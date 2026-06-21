"""
    Class Module for LibreHardwareMonitorReport
"""

import clr  # Pythonnet to interface with .dlls
import os
import sys
import glob


class LibreHardwareMonitorReporter:
    """
    A class to report hardware statistics using LibreHardwareMonitor.

    Attributes:
        cpu_enabled (bool): Whether to include CPU statistics.
        gpu_enabled (bool): Whether to include GPU statistics.
        memory_enabled (bool): Whether to include memory statistics.
        motherboard_enabled (bool): Whether to include motherboard statistics.
        controller_enabled (bool): Whether to include controller statistics.
        network_enabled (bool): Whether to include network statistics.
        storage_enabled (bool): Whether to include storage statistics.
        results (list): Stores the fetched hardware statistics.
        sensor_data (list): Stores the parsed sensor data.
        handler: The LibreHardwareMonitor handler object.
    """
    def __init__(self, cpu: bool = True, gpu: bool = True, memory: bool = True,
                 motherboard: bool = True, controller: bool = True,
                 network: bool = True, storage: bool = True) -> None:
        """
        Initializes the LibreHardwareMonitorReporter class.

        Args:
            cpu (bool): Enable CPU statistics. Default is True.
            gpu (bool): Enable GPU statistics. Default is True.
            memory (bool): Enable memory statistics. Default is True.
            motherboard (bool): Enable motherboard statistics. Default is True.
            controller (bool): Enable controller statistics. Default is True.
            network (bool): Enable network statistics. Default is True.
            storage (bool): Enable storage statistics. Default is True.
        """
        self.NoneType = type(None)
        self.results: list = []
        self.sensor_data: list = []

        self.cpu_enabled = cpu
        self.gpu_enabled = gpu
        self.memory_enabled = memory
        self.motherboard_enabled = motherboard
        self.controller_enabled = controller
        self.network_enabled = network
        self.storage_enabled = storage
        self.handler = self.initialize_handler()

    def initialize_handler(self):
        """
        Initializes the LibreHardwareMonitor handler.

        This method locates the LibreHardwareMonitor DLL, loads it, and sets up the hardware
        components to be monitored.

        Returns:
            Hardware.Computer: The initialized LibreHardwareMonitor handler.
        """
        def find_librehardwaremonitor_dll() -> str:
            base_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Packages')
            pattern = os.path.join(base_path, 'LibreHardwareMonitor.LibreHardwareMonitor_*', 'LibreHardwareMonitorLib.dll')
            matches = glob.glob(pattern)
            if matches:
                return matches[0]
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, 'libre_cli', 'LibreHardwareMonitorLib.dll')
            current_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(current_dir, 'LibreHardwareMonitorLib.dll')

        dll_path = find_librehardwaremonitor_dll()
        sys.path.append(os.path.dirname(dll_path))

        try:
            clr.AddReference(dll_path)
            from LibreHardwareMonitor import Hardware
        except Exception as e:
            print(f"Error: Failed to load LibreHardwareMonitor DLL from '{dll_path}': {e}")
            print("Ensure LibreHardwareMonitorLib.dll is installed via WinGet or bundled alongside this executable.")
            sys.exit(1)

        self.results = []

        self.handle = Hardware.Computer()
        self.handle.IsCpuEnabled = self.cpu_enabled
        self.handle.IsGpuEnabled = self.gpu_enabled
        self.handle.IsMemoryEnabled = self.memory_enabled
        self.handle.IsMotherboardEnabled = self.motherboard_enabled
        self.handle.IsControllerEnabled = self.controller_enabled
        self.handle.IsNetworkEnabled = self.network_enabled
        self.handle.IsStorageEnabled = self.storage_enabled
        # LibreHardwareMonitor requires an Open/Close/Open cycle to correctly
        # initialize hardware detection on Windows before first sensor read.
        self.handle.Open()
        self.handle.Close()
        self.handle.Open()
        return self.handle

    def set_hardware_filter(self, cpu: bool = True, gpu: bool = True, memory: bool = True,
                            motherboard: bool = True, controller: bool = True,
                            network: bool = True, storage: bool = True) -> None:
        """
        Updates the hardware filter settings realtime, meant for rich table output with key listener.

        Args:
            cpu (bool): Enable CPU statistics.
            gpu (bool): Enable GPU statistics.
            memory (bool): Enable memory statistics.
            motherboard (bool): Enable motherboard statistics.
            controller (bool): Enable controller statistics.
            network (bool): Enable network statistics.
            storage (bool): Enable storage statistics.
        """
        self.cpu_enabled = cpu
        self.gpu_enabled = gpu
        self.memory_enabled = memory
        self.motherboard_enabled = motherboard
        self.controller_enabled = controller
        self.network_enabled = network
        self.storage_enabled = storage

        self.handle.IsCpuEnabled = self.cpu_enabled
        self.handle.IsGpuEnabled = self.gpu_enabled
        self.handle.IsMemoryEnabled = self.memory_enabled
        self.handle.IsMotherboardEnabled = self.motherboard_enabled
        self.handle.IsControllerEnabled = self.controller_enabled
        self.handle.IsNetworkEnabled = self.network_enabled
        self.handle.IsStorageEnabled = self.storage_enabled

    def fetch_stats(self, handle, results: list) -> list:
        """
        Fetches hardware statistics from the LibreHardwareMonitor handler.

        Args:
            handle: The LibreHardwareMonitor handler.
            results (list): A list to store the fetched statistics.

        Returns:
            list: The updated results list containing hardware statistics.
        """
        for i in handle.Hardware:
            i.Update()
            for sensor in i.Sensors:
                self.parse_sensor(sensor, results)
            for j in i.SubHardware:
                j.Update()
                for subsensor in j.Sensors:
                    self.parse_sensor(subsensor, results)
        return results

    def parse_sensor(self, sensor, results: list) -> None:
        """
        Parses a sensor and appends its data to the results list.

        Args:
            sensor: The sensor object to parse.
            results (list): The list to store parsed sensor data.
        """
        if sensor.Value is not None:
            value = (
                f"{sensor.Hardware.HardwareType}",
                f"{sensor.Hardware.Name}",
                f"{sensor.Name}",
                f"{sensor.Value}"
            )
            results.append(value)

    def get_sensor_data(self) -> list:
        """
        Fetches and returns the latest sensor data.

        Returns:
            list: A list of tuples containing sensor data.
        """
        self.results = []
        self.sensor_data = self.fetch_stats(self.handler, self.results)
        return self.sensor_data


# Below is an example of how you could use this in a script
# This is not necessary if you are using this as a module
if __name__ == "__main__":
    import time
    try:
        print("Starting LibreHardwareMonitor...")
        LibreHardwareMonitorReport = LibreHardwareMonitorReporter()
        while True:
            LibreHardwareMonitorReport.get_sensor_data()
            for i in LibreHardwareMonitorReport.results:
                print(i)
            time.sleep(10)
    except KeyboardInterrupt:
        LibreHardwareMonitorReport.handler.Close()
        print("LibreHardwareMonitor closed.")
        print("Exiting...")
