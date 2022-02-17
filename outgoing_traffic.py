import random
import time
import json
import paho.mqtt.publish as publish
import socket
import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import os




if __name__ == "__main__":
    load_dotenv()

    access_url = os.getenv("CONFIG_URL_ENDPOINT")+str(socket.gethostname())+"/"
    try:
        response = requests.get(access_url)

        config_json = response.json()

        broker = config_json['mqtt']['broker']
        port = config_json['mqtt']['port']
        pi_hub_id = config_json['pi_hub_id']
        client_id = config_json["client_id"]
        smart_meters = config_json["meter_list"]

        for smart_meter in smart_meters:
            publish.single(F"{client_id}/{pi_hub_id}/{smart_meter['id']}", "payload", hostname=broker, port=port)


    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')
        