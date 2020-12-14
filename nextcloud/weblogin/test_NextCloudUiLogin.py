#!/usr/bin/python3
# Generated by Selenium IDE
#import pytest
import time
from datetime import datetime
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from influxdb import InfluxDBClient
import configparser
import argparse


class TestNCOberonLogin():
  def setup_method(self, method):
    self.driver = webdriver.Firefox()
    self.NC_url = config.get("NextCloud", "baseUrl")
    self.NC_login_suffix = config.get("NextCloud", "loginSuffix", fallback="/login")
    self.NC_user = config.get("NextCloud", "ncUser")
    self.NC_password = config.get("NextCloud", "ncPassword")
    self.NC_fileIndex = config.get("NextCloud", "fileIndex", fallback=3)
    self.NC_loginForm = config.get("NextCloud", "loginForm", fallback="submit")
    self.NC_logout_text = config.get("NextCloud", "logoutText", fallback="Log out")
    self.NC_logout_confirm_link_text = config.get("NextCloud", "logoutConfirmLinkText", fallback="Forgot password?")
    self.influx_host = config.get("Influx", "host")
    self.influx_port = config.get("Influx", "port")
    self.influx_database = config.get("Influx", "database")
    self.influx_myhostname = config.get("Influx", "myhostname")
    self.influx_measurement = config.get("Influx", "measurement")
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_nCOberonLogin(self):
    sleepTime = 2.0
    startTime = time.time()
    # We make one try-catch block for all browser operations to finally catch any failure
    # at the end to ensure correct closing of files and processes
    try:
        self.driver.get(self.NC_url + self.NC_login_suffix)
        entryPageTime = time.time()
        self.driver.set_window_size(1800, 1020)
        self.driver.find_element(By.ID, "user").click()
        self.driver.find_element(By.ID, "user").send_keys(self.NC_user)
        self.driver.find_element(By.ID, "password").send_keys(self.NC_password)
        self.driver.find_element(By.ID, self.NC_loginForm).click()
        WebDriverWait(self.driver, 30000).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "tr:nth-child(%s) .innernametext" %self.NC_fileIndex)))
        loginSucceedTime = time.time()
        self.driver.find_element(By.CSS_SELECTOR, "tr:nth-child(%s) .innernametext" %self.NC_fileIndex).click()
        WebDriverWait(self.driver, 30000).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".header-close")))
        self.driver.find_element(By.CSS_SELECTOR, ".header-close").click()
        WebDriverWait(self.driver, 30000).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".avatardiv > img")))
        showDoneTime = time.time()
        # without sleep, sometimes message "not clickable / obscured by other item" appears.
        time.sleep(sleepTime)
        self.driver.find_element(By.CSS_SELECTOR, ".avatardiv > img").click()
        WebDriverWait(self.driver, 30000).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, self.NC_logout_text)))
        self.driver.find_element(By.LINK_TEXT, self.NC_logout_text).click()
        #WebDriverWait(self.driver, 30000).until(expected_conditions.presence_of_element_located((By.ID, "user")))
        WebDriverWait(self.driver, 30000).until(expected_conditions.presence_of_element_located((By.LINK_TEXT, self.NC_logout_confirm_link_text)))
    except Exception as e:
        print(
            "Error running selenium test on %s. Message: %s"
            % (self.NC_url, e)
            )
        return None
    # Done
    doneTime = time.time()
    entryPageDuration = entryPageTime - startTime
    loginTimeDuration = loginSucceedTime - entryPageTime
    showDocumentDuration = showDoneTime - loginSucceedTime
    logoutDuration = doneTime - showDoneTime - sleepTime
    totalDuration = doneTime - startTime - sleepTime
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    json_body = [
    {
        "measurement": self.influx_measurement,
        "tags": {
            "agent": "selenium",
            "host": self.influx_myhostname
        },
        "time": current_time,
        "fields": {
            "entryPage": entryPageDuration,
            "login": loginTimeDuration,
            "showDocument": showDocumentDuration,
            "logout": logoutDuration,
            "total": totalDuration
        }
    }
    ]
    try:
        client = InfluxDBClient(host=self.influx_host, port=self.influx_port)
        client.switch_database(self.influx_database)
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

testClass = TestNCOberonLogin()

testClass.setup_method("")
testClass.test_nCOberonLogin()
testClass.teardown_method("")
