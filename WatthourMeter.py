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
                return {'success': False, 'description': 'Cannot Open port'}

    def dataListProcess(self, addressField, controlCode, dataFieldLength, dateFieldStr=''):
        dateField = re.findall(r'[0-9A-F]{2}', dateFieldStr)
        dateField.reverse()
        dateField = [hex(int('0x{}'.format(data), 16) + int('0x33', 16)).replace('0x', '').upper().zfill(2)[-2:] for data in dateField]

        checkList = ['68'] + addressField + ['68', controlCode, dataFieldLength] + dateField
        checkCode = hex(sum([int('0x{}'.format(check_l), 16) for check_l in checkList])).replace('0x', '').upper().zfill(2)[-2:]

        # print(['FE'] * 4 + checkList + [checkCode, '16'])
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

    def getActivePower(self, addressField):
        # addressField = self.getMeterNumber()
        if addressField:
            # print(F"addressField: {addressField}\t controlcode: 11\t datafieldlength: 04\t datafieldString: 00010000")
            dataList = self.dataListProcess(addressField, '11', '04', "00010000") 
            result = self.serialExchange(dataList)
            if result['success']:
                resultList = self.resultListProcess(result['data'], '04')
                resultList.reverse()
                addressField.reverse()
                meterNo = ''.join(addressField)
                meterRecord = float(resultList[0]) * 10000 + float(resultList[1]) * 100 + float(resultList[2]) + float(resultList[3]) * 0.01
                print('[{0}][{1}] usage: {2} kWh'.format(datetime.datetime.now(), meterNo, meterRecord))
                return meterRecord
            else:
                # print(result['description'])
                return None