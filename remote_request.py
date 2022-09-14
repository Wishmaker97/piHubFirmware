import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import os
from WatthourMeter import WatthourMeter
from uuid import getnode as get_mac
import datetime
import logging.handlers as handlers
import logging
import time

from azure.iot.device import IoTHubDeviceClient, Message


DEBUG = True

MSG_TXT_GET_ID = '{{"cmd" : "get_meter_ids"}}'
MSG_TXT_SEND_REPORT = '{{ "data": {{"meter_reports": [{{"meter_id":"{meter_id}","timestamp":"{timestamp}","value":{value} }}]}}}}'


TOPIC=None
config_json = None

if __name__ == "__main__":

    while True: 
        try:
            print("hello")

        except Exception as err:
                logging.exception(msg=F"Requested meter list from server FAILED, {err}")
                if DEBUG : print(F"EXCEPTION : Requested meter list from server FAILED, {err}")