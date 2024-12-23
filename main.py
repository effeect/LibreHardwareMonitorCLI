
"""
    This module uses a LibreHardwareMonitorLib.dll to extract info out for Powershell to handle
"""
import os
import clr #pythonnet
import System

def configure_runtime():
    setup = System.AppDomainSetup()
    setup.DisallowCodeDownload = True
    AppDomain = System.AppDomain.CreateDomain("MyDomain", None, setup)

    return AppDomain
    
NoneType = type(None)

def initialize():
    app_domain = configure_runtime()
    file = "LibreHardwareMonitorLib"
    clr.AddReference(file)
    from LibreHardwareMonitor import Hardware

    handle = Hardware.Computer()
    handle.IsCpuEnabled = True
    handle.IsGpuEnabled = True
    handle.IsMemoryEnabled = True
    handle.IsMotherboardEnabled = True
    handle.IsControllerEnabled = True
    handle.IsNetworkEnabled = True
    handle.IsStorageEnabled = True
    handle.Open()
    handle.Close()
    handle.Open()
    return handle

def fetch_stats(handle):
    data = []

    for i in handle.Hardware:
        i.Update()
        for sensor in i.Sensors:
            parse_sensor(sensor)

        for j in i.SubHardware:
            j.Update()
            for subsensor in j.Sensors:
               parse_sensor(subsensor)

    return data

def parse_sensor(sensor):
    results = []
    if sensor.Value is not None:
        result =(f"{sensor.Hardware.Name} ",
                f"{sensor.Name} ",
                f"{sensor.Value}")
        print(f"{result}")

def get_cpu_temp(data):
    NoneType = type(None)

    for x in data:
        if(type(x) != NoneType):
            if("CPU Package" in x[0][1]):
                print(f"{x[0][1]} : {x[0][2]}")
        

if __name__ == "__main__":
    HardwareHandle = initialize()
    fetch_stats(HardwareHandle)