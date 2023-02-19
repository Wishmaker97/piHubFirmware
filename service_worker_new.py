from dotenv import load_dotenv
import os
import datetime
import logging.handlers as handlers
import logging
import base64
import hmac
import hashlib
import json
import random
from WatthourMeter import WatthourMeter
import threading
import time

from azure.iot.device import IoTHubDeviceClient, Message

DEBUG = True
LOG = False

response_for_service_worker = False

client = None

MSG_TXT_GET_ID = '{{"cmd" : "get_meter_ids"}}'
MSG_TXT_SEND_REPORT = '{{ "data": {{"meter_reports": [{{"meter_id":"{meter_id}","timestamp":"{timestamp}","value":{value} }}]}}}}'

response = ""

error = None

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
            meter_report['timestamp'] = datetime.datetime.now().astimezone().isoformat()[:23]+'Z'
            
            ## try block for communication with Smart meter
            try:              
                
                meter_usage = meter_instance.getActivePower(smart_meter_address)
                
                # dummy for testing
                # meter_usage = 100 + int(random.random() * 20)
                
                meter_report['value'] = int(meter_usage)

                if LOG : logging.info(msg=F"(Primary Thread) - smart meter id [{smart_meter}] returned {meter_usage}kWh @{meter_report['timestamp']}")
                if DEBUG : print(F"INFO : (Primary Thread) - smart meter id [{smart_meter}] returned {meter_usage}kWh @{meter_report['timestamp']}")                   

            except Exception as err:
                meter_report['value'] = -1
                if LOG : logging.exception(msg=F"(Primary Thread) - Data retrieval from {smart_meter} was unsuccessfull")
                if DEBUG : print(F"EXCEPTION : (Primary Thread) - Data retrieval from {smart_meter} was unsuccessfull")
            
            finally:
                meter_reports.append(meter_report)
        
        if LOG : logging.info(msg=F"(Primary Thread) - Got smart meter data from smart meters")
        if DEBUG : print("\nINFO : (Primary Thread) - Got smart meter data from smart meters\n")

        for meter in meter_reports:
            try:                      
                msg_txt_formatted_send_report = MSG_TXT_SEND_REPORT.format(meter_id=meter['meter_id'], timestamp=meter['timestamp'], value=meter['value'])
                message = Message(msg_txt_formatted_send_report)

                client.send_message(message)   

                if DEBUG : print("INFO : (Primary Thread) - Requested Reports sent successfully for {meter_id}".format(meter_id=meter['meter_id']))     
                if LOG : logging.info(msg="(Primary Thread) - Requested Reports sent successfully for {meter_id}".format(meter_id=meter['meter_id']))                    

            except Exception as err:
                if LOG : logging.exception(msg="(Primary Thread) - Requested Report for {meter_id} were not sent, {error}".format(meter_id=meter['meter_id'], error=err))
                if DEBUG : print("EXCEPTION : (Primary Thread) - Requested Report for {meter_id} were not sent, {error}".format(meter_id=meter['meter_id'], error=err)) 
   
    except Exception as err:
        if LOG : logging.exception(msg=err)
        if DEBUG : print(F"EXCEPTION : (Primary Thread) - {err}")

 
def message_received_handler(message):
    try:
        command_message = message.data.decode('utf8')
        command_json = json.loads(command_message)  
        global client
        if not response_for_service_worker:
            if command_json["cmd"] == "get_meter_reports":
                if DEBUG : print("INFO : Need to send meter report immediately")            
                send_meter_report(command_json["args"]["meter_ids"], client)

            elif command_json["cmd"] == "set_ntp_servers":
                if DEBUG : print("INFO : Need to update ntp servers immediately")
            else:
                if DEBUG : print("WARNING : command is not an allowed instruction")
        
        else:
            global response
            response = command_message
    
    except Exception as err:
        if LOG : logging.exception(msg=F"remote request server failed to handle incomming command,\n {err}")
        if DEBUG : print(F"EXCEPTION : remote request server failed to handle incomming messsage,\n {err}")

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

class ServiceWorkerThread(threading.Thread):
    def __init__(self, client_object):
        threading.Thread.__init__(self)
        self.client_object = client_object

    def run(self):
        while True:
            ## adding timestamp to logfile
            if LOG : logging.info(F"(Secondary Thread) - Start Script to send timed report")
            if DEBUG : print(F"INFO : (Secondary Thread) - Start Script to send timed report @ {datetime.datetime.now().isoformat()[:23]+'Z'} (ISO)")

            try:
                if DEBUG : print("INFO : (Secondary Thread) - entering try block")
                
                msg_txt = '{{"cmd" : "get_meter_ids"}}'
                
                if DEBUG : print("INFO : (Secondary Thread) - Packaging message")
                
                message_request_list = Message(msg_txt)
                
                if DEBUG : print("INFO : (Secondary Thread) - Sending message - {msg}".format(msg=message_request_list))

                global response_for_service_worker
                response_for_service_worker = True;
                    
                client.send_message(message_request_list)

                if DEBUG : print("INFO : (Secondary Thread) - Waiting for response")

                if LOG : logging.info(msg="(Secondary Thread) - Requested meter list from server")

                self.client_object.on_message_received = message_received_handler

                global response
                while (response==""):
                    continue

                response_message = response
                response = "" 
  
                response_for_service_worker = False;        

                response_json = json.loads(response_message)  

                if DEBUG : print("INFO : (Secondary Thread) - Response : {}".format(response_json))

                if LOG : logging.info(msg="(Secondary Thread) - Response : {}".format(response_json))

                ## Get list of meter ids from json 

                smart_meter_list = response_json['data']['meter_ids']            

                ## variable for holding all the data
                meter_reports = []
                meter_instance = WatthourMeter(str(os.getenv('COM_PORT')))


                ## iterate through the smart meters in the list ("meter_list")
                for smart_meter in smart_meter_list:
                    
                    ## variable for holding data of specific meter
                    meter_report = {}

                    smart_meter_address = [smart_meter[i:i + 2] for i in range(0, len(smart_meter), 2)][::-1]

                    meter_report['meter_id'] = smart_meter
                    meter_report['timestamp'] = datetime.datetime.now().astimezone().isoformat()[:23]+'Z'
                    
                    ## try block for communication with Smart meter
                    try:              
                       
                        # meter_usage = meter_instance.getActivePower(smart_meter_address)
                        
                        # dummy for testing
                        meter_usage = 100 + int(random.random() * 20)
                        
                        meter_report['value'] = int(meter_usage)

                        if LOG : logging.info(msg=F"(Secondary Thread) - smart meter id [{smart_meter}] returned {meter_usage}kWh @{meter_report['timestamp']}")
                        if DEBUG : print(F"INFO : (Secondary Thread) - smart meter id [{smart_meter}] returned {meter_usage}kWh @{meter_report['timestamp']}")                   

                    except Exception as err:
                        meter_report['value'] = -1

                        logging.exception(msg=F"(Secondary Thread) - Data retrieval from {smart_meter} was unsuccessfull")
                        if DEBUG : print(F"EXCEPTION : (Secondary Thread) - Data retrieval from {smart_meter} was unsuccessfull")
                    
                    finally:
                        meter_reports.append(meter_report)
                
                if LOG : logging.info(msg=F"(Secondary Thread) - Got smart meter data from smart meters")
                if DEBUG : print("\nINFO : (Secondary Thread) - Got smart meter data from smart meters\n")

                for meter in meter_reports:
                    try:                      
                        msg_txt_formatted_send_report = MSG_TXT_SEND_REPORT.format(meter_id=meter['meter_id'], timestamp=meter['timestamp'], value=meter['value'])
                        message = Message(msg_txt_formatted_send_report)

                        self.client_object.send_message(message)     

                        if DEBUG : print("INFO : (Secondary Thread) - Scheduled Reports sent successfully for {meter_id}".format(meter_id=meter['meter_id']))     
                        if LOG : logging.info(msg="(Secondary Thread) - Scheduled Reports sent successfully{meter_id}".format(meter_id=meter['meter_id']))                

                    except Exception as err:
                        if LOG : logging.exception(msg="(Secondary Thread) - Scheduled Report for {meter_id} were not sent, {error}".format(meter_id=meter['meter_id'], error=err))
                        if DEBUG : print("EXCEPTION : (Secondary Thread) - Scheduled Report for {meter_id} were not sent, {error}".format(meter_id=meter['meter_id'], error=err)) 
                    
            
            except Exception as err:
                if LOG : logging.exception(msg=F"(Secondary Thread) - Requested meter list from server FAILED, {err}")
                if DEBUG : print(F"EXCEPTION : (Secondary Thread) - Requested meter list from server FAILED, {err}")  

            finally:
                load_dotenv('.env', override=True)
                period_time_value = int(os.getenv('PeriodValue'))
                if LOG : logging.exception(msg=F"(Secondary Thread) - {period_time_value} seconds waiting time")
                if DEBUG : print(F"INFO : (Secondary Thread) - {period_time_value} seconds waiting time")    
                time.sleep(period_time_value)
        


def main():
    
    load_dotenv('.env', override=True)

    DeviceId = str(os.getenv('DeviceId'))
    GroupSymmetricKey = str(os.getenv('GroupSymmetricKey'))
    HostName = str(os.getenv('HostName'))

    symmetricKey = derive_device_key(DeviceId, GroupSymmetricKey)
    global client
    client = IoTHubDeviceClient.create_from_symmetric_key(
            symmetric_key=symmetricKey,
            hostname=HostName,
            device_id=DeviceId
        )    
    
    client.connect()    
    if LOG : logging.info(msg=F"(Primary Thread) - Connected to AZURE IoT server")
    if DEBUG : print("INFO : (Primary Thread) - Connected to AZURE IoT server")
    try:
        ## adding timestamp to logfile
        client.on_message_received = message_received_handler
        thread_item = ServiceWorkerThread(client)
        thread_item.start()

        message_flag = True
        while True: 
            if (message_flag):
                if LOG : logging.info(F"(Primary Thread) - Start Script to listen for remote requests")

                if DEBUG : print(F"INFO : (Primary Thread) - Start Script  to listen for remote requests @ {datetime.datetime.now().isoformat()[:23]+'Z'} (ISO)\n")
                message_flag = False
                pass
                           
    
    except KeyboardInterrupt:
        if DEBUG : print(F"WARNING : (Primary Thread) - IoTHubClient stopped by user @ {datetime.datetime.now().isoformat()[:23]+'Z'} (ISO)")
        if LOG : logging.warning(msg="(Primary Thread) - IoTHubClient stopped by user")

    finally:        
        if DEBUG : print(F"WARNING : (Primary Thread) - Shutting down IoTHubClient @ {datetime.datetime.now().isoformat()[:23]+'Z'} (ISO)")
        if LOG : logging.warning(msg="(Primary Thread) - Shutting down IoTHubClient")
        client.shutdown()



if __name__ == "__main__":
    if LOG: 
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%m-%d-%Y %H:%M:%S')    
        log_handler = handlers.TimedRotatingFileHandler("logfiles/service_worker/logdata.log", when='midnight', encoding='utf-8',backupCount=5, interval=1)
        log_handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(log_handler)
        logger.setLevel(logging.DEBUG)

    main()