from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime


class InfluxManager:
    def __init__(self, url: str, token: str, org: str, bucket: str) -> None:
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket

        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        except Exception as e:
            print(f"[InfluxDB] Failed to connect: {e}")
            raise

    def write_data(self, data_point: list) -> None:
        point = Point(data_point[0]) \
            .tag("component", data_point[1]) \
            .tag("sensor", data_point[2]) \
            .field("value", data_point[3]) \
            .time(datetime.datetime.utcnow())
        try:
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        except Exception as e:
            print(f"[InfluxDB] Write failed: {e}")

    def exit(self) -> None:
        self.client.close()
