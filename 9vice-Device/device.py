import socketio
import cv2
import json
import base64
from time import sleep
cap=cv2.VideoCapture(0)

# Probablement un truc qui finira dans un .env, moi j'y connais rien
ID = '9'

# standard Python
sio = socketio.Client()

@sio.on('my device')
def on_message(data):
    print('I received a message!')
    print('data:' + data)

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
    while(cap.isOpened()):
        ret,img=cap.read()
        if ret:
            img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            frame= base64.encodebytes(frame).decode("utf-8")
            sio.emit('to Client', frame)
            sleep(0)
        else:
            break

@sio.event
def connect():
    print("ID: " + ID)
    print("Connected to Server")
    print('SID: ' + sio.sid)

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

@sio.on('*')
def catch_all(event, data):
    print('I don\'t know what to do for' + event)



# main
sio.connect('http://localhost:5000')
sio.sleep(1)
sio.emit('Connect Device', ID)
