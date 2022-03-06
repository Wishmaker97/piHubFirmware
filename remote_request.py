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



TOPIC=None
config_json = None

if __name__ == "__main__":

    formatter = logging.Formatter('%(asctime)s program_name [%(process)d]: %(message)s', '%b %d %H:%M:%S')    
    log_handler = handlers.TimedRotatingFileHandler(r"logfiles/remote_request/logdata.log", when='midnight', encoding='utf-8',backupCount=30, interval=1)
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)    

    while True:
        try:
            load_dotenv()   

            access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}{get_mac()}/"
            # access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}202481587158093/"

            ## make api call to obtain the MQTT broker details and topic for publishing and also the smart meter list 
            response = requests.get(access_url)

            ## parse response as json object to extract configuration
            config_json = response.json()

        except HTTPError as http_err:
            config_json = None
            logging.exception(msg=F"HTTP error occurred: {http_err} @{datetime.datetime.utcnow()}")

        except Exception as err:
            config_json = None
            logging.exception(msg=F"Other error occurred: {err} @{datetime.datetime.utcnow()}")

        if (config_json is not None):
            
            ## initilaized variables based on api config
            broker = config_json['mqtt']['broker']
            port = config_json['mqtt']['port']
            pi_hub_id = config_json['pi_hub_id']
            client_id = config_json['client_id']
            TOPIC = F"COMMAND/{client_id}/{pi_hub_id}"

            try:
                msg = subscribe.simple(TOPIC, qos=2, hostname=broker)

                print(F"\nMessage received-> {msg.topic} {msg.payload.decode('utf-8')} ")  # Print a received msg
                # print(config_json['meter_list'])
                pi_hub_id = config_json['pi_hub_id']
                client_id = config_json['client_id']
                broker = config_json['mqtt']['broker']
                port = config_json['mqtt']['port']
                found_address = False
                smart_meter_address_str = None


                for smart_meter in config_json['meter_list']:

                    logging.info(msg=F"smart meter [{smart_meter['id']}] comapring with {msg.payload.decode('utf-8')}")

                    if str(smart_meter['id']) == msg.payload.decode("utf-8"):
                        found_address = True
                        smart_meter_address_str = smart_meter['serial_number']
                        print(F"Address fround : {smart_meter_address_str}")
                        logging.info(msg=F"Address Found : {smart_meter_address_str}")
                
                if(found_address):
                    try:
                        smart_meter_address = [smart_meter_address_str[i:i + 2] for i in range(0, len(smart_meter_address_str), 2)][::-1]
                        meter_instance = WatthourMeter(str(os.getenv('COM_PORT')))
                        meter_usage = meter_instance.getActivePower(smart_meter_address)

                        logging.info(msg=F"smart meter [{smart_meter['id']}] returned {meter_usage} kWh")

                        if (meter_usage is not None):
                            publish.single(f"RESPONSE/{client_id}/{pi_hub_id}", payload=F"{meter_usage} kWh @{datetime.datetime.utcnow()}", hostname=broker, port=port, qos=2, retain=False)
                            logging.info(msg=F"topic : [{client_id}/{pi_hub_id}/{smart_meter['id']}] \npayload : {meter_usage} kWh @{datetime.datetime.utcnow()} \nbroker : {broker} \nport : {port}")
                        
                        else:
                            publish.single(f"RESPONSE/{client_id}/{pi_hub_id}", payload=F"COULD NOT RETRIVE DATA FROM METER @{datetime.datetime.utcnow()}", hostname=broker, port=port, qos=2, retain=False)
                            logging.warning(msg=F"topic : [{client_id}/{pi_hub_id}/{smart_meter['id']}] \npayload : COULD NOT RETRIEVE DATA @{datetime.datetime.utcnow()} \nbroker : {broker} \nport : {port}")

                    except Exception as err:
                        try: 
                            publish.single(F"{client_id}/{pi_hub_id}", payload=F"ERROR WHEN RETRIEVING DATA @{datetime.datetime.utcnow()}", hostname=broker, port=port, qos=2, retain=False)
                        
                        except Exception as err:
                            logging.exception(msg=F"Failed to Publish error message to mqtt @{datetime.datetime.utcnow()}")

                        logging.exception(msg=F"ERROR WHEN RETRIEVING DATA @{datetime.datetime.utcnow()}")
                        
                else:
                    try: 
                        publish.single(f"RESPONSE/{client_id}/{pi_hub_id}", payload=F"COULD NOT FIND SMART METER ADDRESS IN CONFIGURATION @{datetime.datetime.utcnow()}", hostname=broker, port=port, qos=2, retain=False)
                    
                    except Exception as err:
                        logging.exception(msg=F"Failed to Publish error message to mqtt (COULD NOT FIND SMART METER ADDRESS IN CONFIGURATION) @{datetime.datetime.utcnow()}")                    

            except Exception as err:
                logging.exception(msg=F"MQTT connection failed : {err} @{datetime.datetime.utcnow()} (wait 600 seconds and try again)")
                time.sleep(600)
        
        else:
            logging.warning(msg=F"No API data and script sleep for 600 seconds and try again @{datetime.datetime.utcnow()}")
            time.sleep(600)
        

                
        

