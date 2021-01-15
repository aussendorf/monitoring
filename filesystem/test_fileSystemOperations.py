#!/usr/bin/python3
import time
from datetime import datetime
import json
from influxdb import InfluxDBClient
import configparser
import argparse
import os

class TestFileSystemOperations():
  def setup_method(self, method):
    self.FS_config = config['FS']
    self.filePrefix = self.FS_config['testDir'] + "/" + "fstest_" + str(os.getpid()) + "_"
    self.influx_host = config.get("Influx", "host")
    self.influx_port = config.get("Influx", "port")
    self.influx_database = config.get("Influx", "database")
    self.influx_myhostname = config.get("Influx", "myhostname")
    self.influx_measurement = config.get("Influx", "measurement")
    self.fileNames = []
    for i in range(int(self.FS_config['numFiles'])):
        self.fileNames.append(self.filePrefix+str(i))
  
  def teardown_method(self, method):
    pass
  
  def test_FS(self):
    # We use the current unix-timestamp as identificator for our statement
    ts = int(time.time())
    startTime = time.time()
    fh=[] # file handles
    try:
        for i in range(int(self.FS_config['numFiles'])):
            fh.append (open(self.fileNames[i], 'xb'))
    except Exception as e:
        print(
            "Error creating files. Message: %s"
            % (e)
            )
        return None
    CreateTime = time.time()
    try:
        for f in fh:
            myContent = b"\0" * int(self.FS_config['fileSize'])
            f.write(myContent)
    except Exception as e:
        print(
            "Error writing to files. Message: %s"
            % (e)
            )
        return None
    WriteTime = time.time()
    try:
        for f in fh:
            f.close()
    except Exception as e:
        print(
            "Error closing files. Message: %s"
            % (e)
            )
        return None
    CloseTime = time.time()
    try:
        for f in self.fileNames:
            os.remove(f)
        DeleteTime =time.time()
    except Exception as e:
        print(
            "Error deleting files. Message: %s"
            % (e)
            )
        return None
    doneTime = time.time()
    createTimeDuration = CreateTime - startTime
    writeDuration = WriteTime - CreateTime
    closeDuration = CloseTime - WriteTime
    deleteDuration = DeleteTime - CloseTime
    totalDuration = DeleteTime - startTime

    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    json_body = [
    {
        "measurement": self.influx_measurement,
        "tags": {
            "agent": "Filesystem",
            "host": self.influx_myhostname
        },
        "time": current_time,
        "fields": {
            "create": createTimeDuration,
            "write": writeDuration,
            "close": closeDuration,
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

testClass = TestFileSystemOperations()

testClass.setup_method("")
testClass.test_FS()
testClass.teardown_method("")
