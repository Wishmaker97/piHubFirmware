import random
import time
import json
import paho.mqtt.publish as publish
import socket
import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import os
import serial
import sys
import time

def getCurrentMeterReading(meter_serial_number):
    print(meter_serial_number)
    return "10.7 kWh"



if __name__ == "__main__":
    load_dotenv()

    # access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}{str(socket.gethostname())}/"

    ser = serial.Serial(
        port='COM4',  # Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate=2400,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )

    bytesend = b" FE FE FE FE 68 16 76 10 82 88 88 68 14 0E 33 33 35 3D 35 33 33 33 33 33 33 33 33 33 CS 16"
    
    # macaddress = "888882107616"
    # macaddress_array_for_command = []
    # mac_len = len(macaddress)
    # mac_len_half = int(mac_len /2)
    # print("mac_len",mac_len)

    # mac_half_range = range(mac_len_half)
    # for i in mac_half_range:
    #     value = str(macaddress[mac_len - (i+1)*2]) + str(macaddress[mac_len - ((i+1)*2 -1)])
    #     print("self.macaddress[mac_len - i*2]", value)
    #     macaddress_array_for_command.append(value)

    # macaddress_string_for_command = ""
    # for val in macaddress_array_for_command:
    #     macaddress_string_for_command = macaddress_string_for_command + val + " "

    # send_bytearray = bytearray.fromhex("fe fe fe fe 68 " + macaddress_string_for_command + "68 11 04 33 33 33 33 3c 16")

    # reply = ser.write(bytearray(send_bytearray))
    # print("reply",reply)

    time.sleep(0.5)

    print(ser.read(30))


    # try:
    #     response = requests.get(access_url)

    #     config_json = response.json()

    #     broker = config_json['mqtt']['broker']
    #     port = config_json['mqtt']['port']
    #     pi_hub_id = config_json['pi_hub_id']
    #     client_id = config_json["client_id"]
    #     smart_meters = config_json["meter_list"]

    #     for smart_meter in smart_meters:
    #         print(smart_meter['id'], smart_meter['serial_number']) 
    #         print(sys.argv[1])

    #         if (str(sys.argv[1]) == smart_meter['id']):           
                   
    #             response_from_meter = getCurrentMeterReading(smart_meter['serial_number'])        

    #             publish.single(F"{client_id}/{pi_hub_id}/{smart_meter['id']}", payload=response_from_meter, hostname=broker, port=port)



    # except HTTPError as http_err:
    #     print(f'HTTP error occurred: {http_err}')  # Python 3.6
    # except Exception as err:
    #     print(f'Other error occurred: {err}')  # Python 3.6
    # else:
    #     print('Success!')
        