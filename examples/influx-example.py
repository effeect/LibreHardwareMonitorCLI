"""
    Example script that will dump all the info out of the dll and print it out
"""
from libre_cli.libre_hardware_monitor_reporter import LibreHardwareMonitorReporter
import time
import argparse
import requests 

def send_to_influxdb(data, influx_url, token, org, bucket):
    """
    Sends sensor data to an InfluxDBv2 server.
    """
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "text/plain; charset=utf-8"
    }
    # This will take the payload from here and format it into an InfluxDB request 
    #payload = ""
    #for sensor in data:
        # Format data in InfluxDB line protocol
    #    payload += f"{sensor[0]},type={sensor[1]}, value={sensor[2]}\n"
        # payload += f"{sensor.Hardware.Name},type={sensor.Name} value={sensor.Value}\n"

    # Convert the data to line protocol
    lines = []
    timestamp_ms = int(time.time() * 1000)

    for sensor_name, metric_name, value in data:
        try:
            metric_clean = metric_name.replace(" ", "_").lower()
            sensor_name_clean = sensor_name.replace(" ", "_").lower()
            line = f"sensor_metrics,sensor_name={sensor_name_clean} {metric_clean}={float(value)}"
            lines.append(line)
        except ValueError:
            print(f"Skipping invalid value: {value} for {metric_name}")

    payload = "\n".join(lines)

    try:
        response = requests.post(
            f"{influx_url}/api/v2/write?org={org}&bucket={bucket}&precision=s",
            headers=headers,
            data=payload
        )
        if response.status_code == 204:
            print("Data successfully written to InfluxDB.")
        else:
            print(f"Failed to write to InfluxDB: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending data to InfluxDB: {e}")

if __name__ == "__main__":
    try :
        parser = argparse.ArgumentParser(description='Check to see if any flags are present')
        parser.add_argument('-t', action='store_true', help='If -t is present, will continue indefintely')
        # InfluxDB stuff
        parser.add_argument('--influx-url', type=str, help='InfluxDBv2 server URL')
        parser.add_argument('--token', type=str, help='InfluxDBv2 authentication token')
        parser.add_argument('--org', type=str, help='InfluxDBv2 organization')
        parser.add_argument('--bucket', type=str, help='InfluxDBv2 bucket')
        # Parse the arguments
        args = parser.parse_args()
        # Access the value of the -t argument
        print("Starting LibreHardwareMonitor...")
        LibreHardwareMonitorReport = LibreHardwareMonitorReporter()
        # If arg.t is present, report indefintely
        if args.t :
            while True :
                LibreHardwareMonitorReport.get_sensor_data()
                for i in LibreHardwareMonitorReport.results:
                    print(i)
                time.sleep(10)
                # Send data to InfluxDB if credentials are provided
                if args.influx_url and args.token and args.org and args.bucket:
                    send_to_influxdb(
                        LibreHardwareMonitorReport.results,
                        args.influx_url,
                        args.token,
                        args.org,
                        args.bucket
                    )
        else :
            LibreHardwareMonitorReport.get_sensor_data()
            for i in LibreHardwareMonitorReport.results:
                print(i)
            # Send data to InfluxDB if credentials are provided
            if args.influx_url and args.token and args.org and args.bucket:
                send_to_influxdb(
                    LibreHardwareMonitorReport.results,
                    args.influx_url,
                    args.token,
                    args.org,
                    args.bucket
                )
            print("Completed")

    except KeyboardInterrupt:
        # When being shut down, close the handle
        LibreHardwareMonitorReport.handler.Close()
        print("LibreHardwareMonitor closed.")
        print("Exiting...")