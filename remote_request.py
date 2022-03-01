import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import os
from WatthourMeter import WatthourMeter
from uuid import getnode as get_mac
import sys
import datetime


TOPIC=None
config_json = None

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    
    print("Connected with result code {0}".format(str(rc)))
    print(F"Listening to topic : {TOPIC}")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.

    print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg
    # print(config_json['meter_list'])
    pi_hub_id = config_json['pi_hub_id']
    client_id = config_json['client_id']
    found_address = False
    for smart_meter in config_json['meter_list']:
        print(smart_meter)
        if str(smart_meter['id']) == msg.payload.decode("utf-8") :
            found_address = True
            smart_meter = smart_meter['serial_number']
    
    if (found_address):
        try:
            smart_meter_address = [smart_meter[i:i + 2] for i in range(0, len(smart_meter), 2)][::-1]
            meter_instance = WatthourMeter(str(os.getenv('COM_PORT')))
            meter_usage = meter_instance.getActivePower(smart_meter_address)

            if (meter_usage is not None):
                publish.single(f"RESPONSE/{client_id}/{pi_hub_id}", payload=F"{meter_usage} kWh @{datetime.datetime.utcnow()}", hostname=broker, port=port)
            
            else:
                publish.single(f"RESPONSE/{client_id}/{pi_hub_id}", payload=F"COULD NOT RETRIVE DATA FROM METER @{datetime.datetime.utcnow()}", hostname=broker, port=port)

        except Exception as err:
            print(f'Other error occurred: {err}')
            publish.single(f"RESPONSE/{client_id}/{pi_hub_id}", payload=F"ERROR - {err} - WHEN RETRIEVING DATA @{datetime.datetime.utcnow()}", hostname=broker, port=port)
    
    else:
        print(f'Could not find Smart Meter')
        publish.single(f"RESPONSE/{client_id}/{pi_hub_id}", payload=F"COULD NOT FIND SMART METER ADDRESS IN CONFIGURATION @{datetime.datetime.utcnow()}", hostname=broker, port=port)



if __name__ == "__main__":

    while True:
        try:
            load_dotenv()   

            access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}{get_mac()}/"
            # access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}202481587158093/"

            print(access_url)
        
            ## make api call to obtain the MQTT broker details and topic for publishing and also the smart meter list 
            response = requests.get(access_url)

            config_json = response.json()

            print(config_json)

        except HTTPError as http_err:
            config_json = None
            print(f'HTTP error occurred: {http_err}')

        except Exception as err:
            config_json = None
            print(f'Other error occurred: {err}')

        else:

            if (config_json is not None):

                broker = config_json['mqtt']['broker']
                port = config_json['mqtt']['port']
                pi_hub_id = config_json['pi_hub_id']
                client_id = config_json['client_id']
                TOPIC = F"COMMAND/{client_id}/{pi_hub_id}"

                try:
                    client = mqtt.Client(F"remote-request-handler-{get_mac()}/")
                    # client = mqtt.Client(F"remote-request-handler-{202481587158093}/") 
                    client.on_connect = on_connect
                    client.on_message = on_message

                    client.connect(broker, port)
                    client.loop_forever()

                except Exception as err:
                    print(f'Error occurred: {err}')
        

                
        

