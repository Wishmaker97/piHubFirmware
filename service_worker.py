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


if __name__ == "__main__":

    formatter = logging.Formatter('%(asctime)s program_name [%(process)d]: %(message)s', '%b %d %H:%M:%S')    
    log_handler = handlers.TimedRotatingFileHandler("logfiles\service_worker\logdata.log", when='midnight', encoding='utf-8',backupCount=30, interval=1)
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)

    ## Read .env file from directory to get config data
    load_dotenv()  
    
    logging.info(F"Start Script to send timed report @ {datetime.datetime.utcnow()} (UTC)")

    access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}{get_mac()}/"
    # access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}202481587158093/"

    ## Main try block
    try: 

        ## make api call to obtain the MQTT broker details and topic for publishing and also the smart meter list 
        response = requests.get(access_url)

        ## parse response as json object to extract configuration
        config_json = response.json()

        ## initilaized variables based on api config
        broker = config_json['mqtt']['broker']
        port = config_json['mqtt']['port']
        pi_hub_id = config_json['pi_hub_id']
        client_id = config_json['client_id']
        smart_meters = config_json['meter_list']

        ## try block for communication with Smart meter
        try:
            ## iterate through the smart meters in the json list object ("meter_list")
            for smart_meter in smart_meters:

                smart_meter_address = [smart_meter['serial_number'][i:i + 2] for i in range(0, len(smart_meter['serial_number']), 2)][::-1]
                meter_instance = WatthourMeter(str(os.getenv('COM_PORT')))
                meter_usage = meter_instance.getActivePower(smart_meter_address)
                logging.info(msg=F"smart meter [{smart_meter['id']}] returned {meter_usage} kWh")

                ## try block for MQTT message
                try:                
                    if (meter_usage is not None):
                        publish.single(F"{client_id}/{pi_hub_id}/{smart_meter['id']}", payload=F"{meter_usage} kWh @{datetime.datetime.utcnow()}", hostname=broker, port=port, qos=2, retain=False)
                        logging.info(msg=F"topic : [{client_id}/{pi_hub_id}/{smart_meter['id']}] \npayload : {meter_usage} kWh @{datetime.datetime.utcnow()} \nbroker : {broker} \nport : {port}")
                    
                    else:
                        publish.single(f"{client_id}/{pi_hub_id}/{smart_meter['id']}", payload=F"COULD NOT RETRIEVE DATA @{datetime.datetime.utcnow()}", hostname=broker, port=port, qos=2, retain=False)
                        logging.warning(msg=F"topic : [{client_id}/{pi_hub_id}/{smart_meter['id']}] \npayload : COULD NOT RETRIEVE DATA @{datetime.datetime.utcnow()} \nbroker : {broker} \nport : {port}")

                except Exception as err:
                    logging.exception(msg=F"ERROR WHEN PUBLISHING MQTT @{datetime.datetime.utcnow()}")

        except Exception as err:
            try: 
                publish.single(F"{client_id}/{pi_hub_id}", payload=F"ERROR WHEN RETRIEVING DATA @{datetime.datetime.utcnow()}", hostname=broker, port=port, qos=2, retain=False)
            except Exception as err:
                logging.exception(msg=F"Failed to Publish error message to mqtt @{datetime.datetime.utcnow()}")
            logging.exception(msg=F"ERROR WHEN RETRIEVING DATA @{datetime.datetime.utcnow()}")

    except HTTPError as http_err:
        logging.exception(msg=F"HTTP error occurred: {http_err} @{datetime.datetime.utcnow()}")
    
    
    except Exception as err:
        logging.exception(msg=F"Other error occurred: {err} @{datetime.datetime.utcnow()}")

    

