#!/usr/bin/python3
import time
from datetime import datetime
import json
from influxdb import InfluxDBClient
import configparser
import argparse
import mysql.connector


class TestMySQLStatements():
  def setup_method(self, method):
    self.MySQL_config = config['MySQL']
    self.influx_host = config.get("Influx", "host")
    self.influx_port = config.get("Influx", "port")
    self.influx_database = config.get("Influx", "database")
    self.influx_myhostname = config.get("Influx", "myhostname")
    self.influx_measurement = config.get("Influx", "measurement")
    self.cnx = mysql.connector
    self.vars = {}
  
  def teardown_method(self, method):
      self.cnx.close()
  
  def test_MySQL(self):
    # We use the current unix-timestamp as identificator for our statement
    ts = int(time.time())
    add_stmt=("INSERT INTO %s (description,ts) values ('monitoring test',%d)" %(self.MySQL_config['table'], ts))
    select_stmt=("SELECT * FROM %s WHERE ts=%d" %(self.MySQL_config['table'], ts))
    delete_stmt=("DELETE FROM %s WHERE ts=%d" %(self.MySQL_config['table'], ts))
    startTime = time.time()
    # We make one try-catch block for all sql operations to finally catch any failure
    # at the end to ensure correct closing of files and processes
    try:
        self.cnx = mysql.connector.connect(user=self.MySQL_config['user'], password=self.MySQL_config['password'],
                              host=self.MySQL_config['host'],
                              database=self.MySQL_config['database']
                              )                  
        loginSucceedTime = time.time()
        cursor = self.cnx.cursor(buffered=True)
        cursor.execute(add_stmt)
        self.cnx.commit()
        InsertTime = time.time()
        cursor.execute(select_stmt)
        self.cnx.commit()
        SelectTime =time.time()
        cursor.execute(delete_stmt)
        self.cnx.commit()
        DeleteTime =time.time()
        
    except Exception as e:
        print(
            "Error running sql statement on %s. Message: %s"
            % (self.MySQL_config['host'], e)
            )
        return None
    # Done
    doneTime = time.time()
    loginTimeDuration = loginSucceedTime - startTime
    insertDuration = InsertTime - loginSucceedTime
    selectDuration = SelectTime - InsertTime
    deleteDuration = DeleteTime - SelectTime

    totalDuration = DeleteTime - startTime

    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    json_body = [
    {
        "measurement": self.influx_measurement,
        "tags": {
            "agent": "MySQL",
            "host": self.influx_myhostname
        },
        "time": current_time,
        "fields": {
            "connect": loginTimeDuration,
            "insert": insertDuration,
            "select": selectDuration,
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

testClass = TestMySQLStatements()

testClass.setup_method("")
testClass.test_MySQL()
testClass.teardown_method("")
