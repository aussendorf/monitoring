#!/usr/bin/python3
import time
from datetime import datetime
import json
import redis
from influxdb import InfluxDBClient
import configparser
import argparse
import os

class TestRedisOperations():
  def setup_method(self, method):
    self.redis_config = config['RedisTest']
    self.redis_connect = config['RedisConnect']
    self.filePrefix = "redistest_" + str(os.getpid()) + "_"
    self.influx_host = config.get("Influx", "host")
    self.influx_port = config.get("Influx", "port")
    self.influx_database = config.get("Influx", "database")
    self.influx_myhostname = config.get("Influx", "myhostname")
    self.influx_measurement = config.get("Influx", "measurement")
    self.keyNames = []
    for i in range(int(self.redis_config['numKeys'])):
        self.keyNames.append(self.filePrefix+str(i))
  
  def teardown_method(self, method):
    pass
  
  def test_Redis(self):
    keyExp = self.redis_config['keyExpiration']
    startTime = time.time()
    r = redis.Redis(**self.redis_connect)
    connectTime = time.time()
    try:
        myContent = b"\0" * int(self.redis_config['keySize'])
        for k in self.keyNames:
            r.psetex (k, keyExp, myContent)
    except Exception as e:
        print(
            "Error setting Redis keys. Message: %s"
            % (e)
            )
        return None
    writeTime = time.time()
    try:
        for k in self.keyNames:
            r.get (k)
        readTime = time.time()
    except Exception as e:
        print(
            "Error reading keys. Message: %s"
            % (e)
            )
        return None
    readTime = time.time()
    try:
        for k in self.keyNames:
           r.delete (k)
        deleteTime = time.time()
    except Exception as e:
        print(
            "Error deleting keys. Message: %s"
            % (e)
            )
        return None

    doneTime = time.time()
    connectDuration = connectTime - startTime
    writeDuration = writeTime - connectTime
    readDuration = readTime - writeTime
    deleteDuration = deleteTime - readTime
    totalDuration = deleteTime - startTime

    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    json_body = [
    {
        "measurement": self.influx_measurement,
        "tags": {
            "agent": "Redis",
            "host": self.influx_myhostname
        },
        "time": current_time,
        "fields": {
            "connect": connectDuration,
            "write": writeDuration,
            "read": readDuration,
            "delete": deleteDuration,
            "total": totalDuration
        }
    }
    ]
    try:
        client = InfluxDBClient(host=self.influx_host, port=self.influx_port)
        client.switch_database(self.influx_database)
        #print(json_body)
        client.write_points(json_body)
    except Exception as e:
        print(
            "Error submitting results to %s. Message: %s"
            % (self.influx_host, e)
            )
        return None
 
parser = argparse.ArgumentParser()
parser.add_argument("configfile")
args = parser.parse_args()
config = configparser.ConfigParser()
config.read(args.configfile)

testClass = TestRedisOperations()

testClass.setup_method("")
testClass.test_Redis()
testClass.teardown_method("")
