from dotenv import load_dotenv
import os
from WatthourMeter import WatthourMeter
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


DEBUG = True

MSG_TXT_GET_ID = '{{"cmd" : "get_meter_ids"}}'
MSG_TXT_SEND_REPORT = '{{ "data": {{"meter_reports": [{{"meter_id":"{meter_id}","timestamp":"{timestamp}","value":{value} }}]}}}}'

command = ""

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
    global command
    command = message.data.decode('utf8')

    if DEBUG : print("INFO : New command (processing...): {}".format(command))
    logging.info(msg="New command (processing...): {}".format(command))   
    

def send_meter_report(smart_meter_list, client):
    try: 
        load_dotenv('.env', override=True)
        ## variable for holding all the data
        meter_reports = []
        meter_instance = WatthourMeter(str(os.getenv('COM_PORT')))

        ## iterate through the smart meters in the list ("meter_list")
        for smart_meter in smart_meter_list:
            
            ## variable for holding data of specific meter
            meter_report = {}

            smart_meter_address = [smart_meter[i:i + 2] for i in range(0, len(smart_meter), 2)][::-1]

            meter_report['meter_id'] = smart_meter
            meter_report['timestamp'] = datetime.datetime.now().isoformat()[:23]+'Z'
            
            ## try block for communication with Smart meter
            try:              
                
                meter_usage = meter_instance.getActivePower(smart_meter_address)
                
                # # dummy for testing
                # meter_usage = 100 + int(random.random() * 20)
                
                meter_report['value'] = int(meter_usage)

                logging.info(msg=F"smart meter id [{smart_meter}] returned {meter_usage}kWh @{meter_report['timestamp']}")
                if DEBUG : print(F"INFO : smart meter id [{smart_meter}] returned {meter_usage}kWh @{meter_report['timestamp']}")                   

            except Exception as err:
                meter_report['value'] = -1

                logging.exception(msg=F"Data retrieval from {smart_meter} was unsuccessfull")
                if DEBUG : print(F"EXCEPTION : Data retrieval from {smart_meter} was unsuccessfull")
            
            finally:
                meter_reports.append(meter_report)
        
        logging.info(msg=F"Got smart meter data from smart meters")
        if DEBUG : print("\nINFO : Got smart meter data from smart meters\n")

        for meter in meter_reports:
            try:                      
                msg_txt_formatted_send_report = MSG_TXT_SEND_REPORT.format(meter_id=meter['meter_id'], timestamp=meter['timestamp'], value=meter['value'])
                message = Message(msg_txt_formatted_send_report)

                client.send_message(message)                   

            except Exception as err:
                logging.exception(msg="Scheduled Report for {meter_id} were not sent, {error}".format(meter_id=meter['meter_id'], error=err))
                if DEBUG : print("EXCEPTION : Scheduled Report for {meter_id} were not sent, {error}".format(meter_id=meter['meter_id'], error=err)) 

            if DEBUG : print("INFO : Scheduled Reports sent successfully")     
            logging.info(msg="Scheduled Reports sent successfully")                 
    
    except Exception as err:
        logging.exception(msg=err)
        if DEBUG : print(F"EXCEPTION : {err}")

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
    logging.info(msg=F"Connected to AZURE IoT server")
    if DEBUG : print("INFO : Connected to AZURE IoT server")
    try:
        ## adding timestamp to logfile
        logging.info(F"Start Script to listen for remote requests")

        if DEBUG : print(F"INFO : Start Script  to listen for remote requests @ {datetime.datetime.now().isoformat()[:23]+'Z'} (ISO)\n")
        client.on_message_received = message_received_handler
        global command
        try:
            msg_txt_formatted = MSG_TXT_GET_ID.format()
            message = Message(msg_txt_formatted)
            
            if DEBUG : print("INFO : Sending message - {}".format(message))
                
            client.send_message(message)

            if DEBUG : print("INFO : Waiting for response")

            logging.info(msg="Requested meter list from server")

            client.on_message_received = message_received_handler

            while (command==""):
                continue

            response_message = command
            command = ""               

            response_json = json.loads(response_message)  

            if DEBUG : print("INFO : Response : {}".format(response_json))

            logging.info(msg="Response : {}".format(response_json))

        except Exception as err:
            logging.exception(msg=F"Requested meter list from server FAILED, {err}")
            if DEBUG : print(F"EXCEPTION : Requested meter list from server FAILED, {err}") 

        finally:
            if DEBUG : print("INFO : System ready for requests")
            logging.info(msg="System ready for requests")

        while True:
            if command:            
                try:  
                    command_message = command
                    command = ""

                    if DEBUG : print("INFO : New command (processing...): {}".format(command_message))
                    logging.info(msg="New command (processing...): {}".format(command_message))   
                                        
                    command_json = json.loads(command_message)  

                    if DEBUG : print("INFO : jsonified response : {}".format(command_json))
                    logging.info(msg="jsonified response : {}".format(command_json))   

                    if command_json["cmd"] == "get_meter_reports":
                        if DEBUG : print("INFO : Need to send meter report immediately")
                        logging.info(msg="Need to send meter report immediately")

                        send_meter_report(command_json["args"]["meter_ids"], client)
                    
                    elif command_json["cmd"] == "set_ntp_servers":
                        if DEBUG : print("INFO : Need to update ntp servers immediately")
                        logging.info(msg="Need to update ntp servers immediately")
                        # timedated = pydbus.SystemBus().get(".timedate1")
                        # dir(timedated)

                    else:
                        if DEBUG : print("WARNING : command is not an allowed instruction")
                        logging.info(msg="Command is not an allowed instruction")                               


                except Exception as err:
                    logging.exception(msg=F"remote request server failed to handle incomming command,\n {err}")
                    if DEBUG : print(F"EXCEPTION : remote request server failed to handle incomming messsage,\n {err}")
            
    
    except KeyboardInterrupt:
        if DEBUG : print(F"WARNING : IoTHubClient stopped by user @ {datetime.datetime.now().isoformat()[:23]+'Z'} (ISO)")
        logging.warning(msg="IoTHubClient stopped by user")

    finally:        
        if DEBUG : print(F"WARNING : Shutting down IoTHubClient @ {datetime.datetime.now().isoformat()[:23]+'Z'} (ISO)")
        logging.warning(msg="Shutting down IoTHubClient")
        client.shutdown()


if __name__ == "__main__":

    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%m-%d-%Y %H:%M:%S')    
    log_handler = handlers.TimedRotatingFileHandler("logfiles/remote_request/logdata.log", when='midnight', encoding='utf-8',backupCount=30, interval=1)
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)

    main()