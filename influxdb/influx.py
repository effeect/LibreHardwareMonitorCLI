from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime

class influx_manager:
    def __init__(self,url,token,org,bucket):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket

        # Initialize client
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def write_data(self,data_point):
        # POINT DATA HERE
        point = Point(data_point[0]) \
        .tag("component", data_point[1]) \
        .tag("sensor", data_point[2]) \
        .field("value", data_point[3]) \
        .time(datetime.datetime.utcnow())
        self.write_api.write(bucket=self.bucket, org=self.org, record=point)

    def exit(self):
        self.client.close()
