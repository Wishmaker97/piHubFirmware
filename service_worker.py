import paho.mqtt.publish as publish
import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import os
from WatthourMeter import WatthourMeter
from uuid import getnode as get_mac
import sys
import datetime


if __name__ == "__main__":
    load_dotenv()   

    # access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}{get_mac()}/"
    access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}202481587158093/"
    print(access_url)
   
    try:
        ## make api call to obtain the MQTT broker details and topic for publishing and also the smart meter list 
        response = requests.get(access_url)

        config_json = response.json()

        broker = config_json['mqtt']['broker']
        port = config_json['mqtt']['port']
        pi_hub_id = config_json['pi_hub_id']
        client_id = config_json['client_id']
        smart_meters = config_json['meter_list']    

        print(config_json)

        if len(sys.argv)>1:

            smart_meter = sys.argv[1]

            smart_meter_address = [smart_meter[i:i + 2] for i in range(0, len(smart_meter), 2)][::-1]
            meter_instance = WatthourMeter(str(os.getenv('COM_PORT')))
            meter_usage = meter_instance.getActivePower(smart_meter_address)

            if (meter_usage is not None):
                publish.single(f"{client_id}/{pi_hub_id}/{smart_meter}", payload=f"{meter_usage} kWh @{datetime.datetime.now()}", hostname=broker, port=port)
            
            else:
                publish.single(f"{client_id}/{pi_hub_id}/{smart_meter}", payload=f"COULD NOT RETRIEVE DATA @{datetime.datetime.now()}", hostname=broker, port=port)

        else:
            for smart_meter in smart_meters:

                smart_meter_address = [smart_meter['serial_number'][i:i + 2] for i in range(0, len(smart_meter['serial_number']), 2)][::-1]
                meter_instance = WatthourMeter(str(os.getenv('COM_PORT')))
                meter_usage = meter_instance.getActivePower(smart_meter_address)
                
                if (meter_usage is not None):
                    publish.single(f"{client_id}/{pi_hub_id}/{smart_meter['id']}", payload=f"{meter_usage} kWh", hostname=broker, port=port)
                
                else:
                    publish.single(f"{client_id}/{pi_hub_id}/{smart_meter['id']}", payload=f"COULD NOT RETRIEVE DATA @{datetime.datetime.now()}", hostname=broker, port=port)

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        publish.single(f"{client_id}/{pi_hub_id}", payload=f"HTTP ERROR WHEN RETRIEVING DATA @{datetime.datetime.now()}", hostname=broker, port=port)

    except Exception as err:
        print(f'Other error occurred: {err}')
        publish.single(f"{client_id}/{pi_hub_id}", payload=f"NON-HTTP ERROR WHEN RETRIEVING DATA @{datetime.datetime.now()}", hostname=broker, port=port)
        