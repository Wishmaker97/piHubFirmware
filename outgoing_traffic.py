from socket import socket
import random
import socket
from paho.mqtt import client as mqtt_client




CLIENT_ID = f'pihub01-{random.randint(0, 1000)}'
BROKER = 'mqtt.egstide.com'
PORT = 1883

