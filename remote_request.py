from dotenv import load_dotenv
import os
from uuid import getnode as get_mac
import datetime
import logging.handlers as handlers
import logging
import base64
import hmac
import hashlib
import json
import random

from azure.iot.device import IoTHubDeviceClient, Message


DEBUG = False
LOG = False

MSG_TXT_GET_ID = '{{"cmd" : "get_meter_ids"}}'
MSG_TXT_SEND_REPORT = '{{ "data": {{"meter_reports": [{{"meter_id":"{meter_id}","timestamp":"{timestamp}","value":{value} }}]}}}}'

command = ""
client = None

def derive_device_key(device_id, group_symmetric_key):
    """
    The unique device ID and the group master key should be encoded into "utf-8"
    After this the encoded group master key must be used to compute an HMAC-SHA256 of the encoded registration ID.
    Finally the result must be converted into Base64 format.
    The device key is the "utf-8" decoding of the above result.
    """
    message = device_id.encode("utf-8")
    signing_key = base64.b64decode(group_symmetric_key.encode("utf-8"))
    signed_hmac = hmac.HMAC(signing_key, message, hashlib.sha256)
    device_key_encoded = base64.b64encode(signed_hmac.digest())
    return device_key_encoded.decode("utf-8")


def message_received_handler(message):
    try:
        command_message = message.data.decode('utf8')
        command_json = json.loads(command_message)  
        if command_json["cmd"] == "get_meter_reports":
            if DEBUG : print("INFO : Need to send meter report immediately")
            send_meter_report(command_json["args"]["meter_ids"], client)

        elif command_json["cmd"] == "set_ntp_servers":
            if DEBUG : print("INFO : Need to update ntp servers immediately")
        else:
            if DEBUG : print("WARNING : command is not an allowed instruction")
    except Exception as err:
        if LOG : logging.exception(msg=F"remote request server failed to handle incomming command,\n {err}")
        if DEBUG : print(F"EXCEPTION : remote request server failed to handle incomming messsage,\n {err}")
                
def send_meter_report(smart_meter_list, client):
    print("### send_meter_report!!!!")

def main():

    load_dotenv('.env', override=True)

    DeviceId = str(os.getenv('DeviceId'))
    GroupSymmetricKey = str(os.getenv('GroupSymmetricKey'))
    HostName = str(os.getenv('HostName'))

    symmetricKey = derive_device_key(DeviceId, GroupSymmetricKey)
    client = IoTHubDeviceClient.create_from_symmetric_key(
            symmetric_key=symmetricKey,
            hostname=HostName,
            device_id=DeviceId
        )
    
    client.connect()
    if LOG : logging.info(msg=F"Connected to AZURE IoT server")
    if DEBUG : print("INFO : Connected to AZURE IoT server")
    try:
        ## adding timestamp to logfile
        if LOG : logging.info(F"Start Script to listen for remote requests")

        if DEBUG : print(F"INFO : Start Script  to listen for remote requests @ {datetime.datetime.now().isoformat()[:23]+'Z'} (ISO)\n")
        client.on_message_received = message_received_handler

        while True:            
            selection = input("Press Q to quit\n")
            if selection == "Q" or selection == "q":
                print("Quitting...")
                break
    
    except KeyboardInterrupt:
        if DEBUG : print(F"WARNING : IoTHubClient stopped by user @ {datetime.datetime.now().isoformat()[:23]+'Z'} (ISO)")
        if LOG : logging.warning(msg="IoTHubClient stopped by user")

    finally:        
        if DEBUG : print(F"WARNING : Shutting down IoTHubClient @ {datetime.datetime.now().isoformat()[:23]+'Z'} (ISO)")
        if LOG : logging.warning(msg="Shutting down IoTHubClient")
        client.shutdown()


if __name__ == "__main__":
    if LOG: 
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%m-%d-%Y %H:%M:%S')    
        log_handler = handlers.TimedRotatingFileHandler("logfiles/remote_request/logdata.log", when='midnight', encoding='utf-8',backupCount=30, interval=1)
        log_handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(log_handler)
        logger.setLevel(logging.DEBUG)

    main()