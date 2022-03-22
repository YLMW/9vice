import socketio
import json
import base64
from time import sleep

import os
from dotenv import load_dotenv

env_path = os.getcwd() + '/.env'
load_dotenv(dotenv_path=env_path)


ID_USER = os.getenv("ACCOUNT_ID")
DEVICE_NAME = os.getenv("DEVICE_NAME")
SERVER_KEY = os.getenv("SERVER_KEY")
CLIENT_KEY = os.getenv("CLIENT_KEY")


URL = 'http://127.0.0.1:5000'


ID = -1


# standard Python
sio = socketio.Client()


@sio.on('my device')
def on_message(data):
    print('I received a message!')
    print('data:' + data)


@sio.on('Device advertised')
def on_message(data):
    print('My device ID is : ' + str(data['ID']))
    ID = data['ID']
    if ID == -1:
        sio.disconnect()


@sio.on('Linked')
def on_message(data):
    print('I am linked to ' + data)


@sio.on('from Client')
def on_message(data):
    print('I received: ' + data)
    print('I\'ll answer "ACK"')
    sio.emit('to Client', 'ACK')


@sio.on('stream Webcam')
def send_data():
    print('Sending webcam data')
    while (cap.isOpened()):
        ret, img = cap.read()
        if ret:
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            frame = base64.encodebytes(frame).decode("utf-8")
            sio.emit('to Client', frame)
            sleep(0)
        else:
            break


@sio.event
def connect():
    sio.sleep(1)
    sio.emit('Connect Device', {"id_user": ID_USER, "name": DEVICE_NAME, "mdp": SERVER_KEY})
    print("Connected to Server")
    print('SID: ' + sio.sid)


@sio.event
def connect_error(data):
    print("The connection failed!")


@sio.event
def disconnect():
    print('Disconnecting ...')
    sio.emit('Device disconnected', {"id_user": ID_USER, "name": DEVICE_NAME})
    print("I'm disconnected!")


@sio.on('*')
def catch_all(event, data):
    print('I don\'t know what to do for' + event)


# main
sio.connect(URL)
