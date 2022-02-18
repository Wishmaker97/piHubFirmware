import json
import paho.mqtt.publish as publish
import socket
import requests
from requests.exceptions import HTTPError
from dotenv import load_dotenv
import os
import sys
import re
import binascii
import serial
import datetime
import time

class WatthourMeter:
    def __init__(self, comPort):
        self.comPort = comPort

    def serialExchange(self, dataList):
        with serial.Serial(self.comPort, 2400, parity=serial.PARITY_EVEN, timeout=2) as serialConn:
            if serialConn.isOpen():
                serialConn.write(b''.join([binascii.a2b_hex(data) for data in dataList]))
                return {'success': True, 'data': re.findall(r'[0-9A-Z]{2}', binascii.b2a_hex(serialConn.readline()).decode().upper())}
            else:
                return {'success': False, 'description': '端口未打开'}

    def dataListProcess(self, addressField, controlCode, dataFieldLength, dateFieldStr=''):
        dateField = re.findall(r'[0-9A-F]{2}', dateFieldStr)
        dateField.reverse()
        dateField = [hex(int('0x{}'.format(data), 16) + int('0x33', 16)).replace('0x', '').upper().zfill(2)[-2:] for data in dateField]

        checkList = ['68'] + addressField + ['68', controlCode, dataFieldLength] + dateField
        checkCode = hex(sum([int('0x{}'.format(check_l), 16) for check_l in checkList])).replace('0x', '').upper().zfill(2)[-2:]
        return ['FE'] * 4 + checkList + [checkCode, '16']

    def resultListProcess(self, resultList, dataFieldLength):
        return [hex(int('0x{}'.format(res), 16) - int('0x33', 16)).replace('0x', '').upper().zfill(2)[-2:] for res in resultList[14 + int(dataFieldLength) : -2]]
 
    def getMeterNumber(self):
        dataList = self.dataListProcess(['AA'] * 6, '13', '00')
        result = self.serialExchange(dataList)
        if result['success']:
            return self.resultListProcess(result['data'], '00')
        else:
            return None

    def getActivePower(self):
        addressField = self.getMeterNumber()
        if addressField:
            dataList = self.dataListProcess(addressField, '11', '04', "00010000")
            print(dataList)
 
            result = self.serialExchange(dataList)
            print(result)
            if result['success']:
                resultList = self.resultListProcess(result['data'], '04')
                print(resultList)
                resultList.reverse()
                addressField.reverse()
                meterNo = ''.join(addressField)
                meterRecord = float(resultList[0]) * 10000 + float(resultList[1]) * 100 + float(resultList[2]) + float(resultList[3]) * 0.01
                print('[{0}][{1}] usage: {2} kWh'.format(datetime.datetime.now(), meterNo, meterRecord))
            else:
                print(result['description'])



if __name__ == "__main__":
    load_dotenv()

   

    # access_url = F"{os.getenv('CONFIG_URL_ENDPOINT')}{str(socket.gethostname())}/"

    WatthourMeter(str(os.getenv('COM_PORT'))).getActivePower()


   
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
        