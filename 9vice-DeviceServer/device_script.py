import socketio
import json
from crypto.crypto import AESCipher
import base64
from time import sleep
import cv2

import os
from dotenv import load_dotenv

cap=cv2.VideoCapture(0)

env_path = os.getcwd() + '/.env'
load_dotenv(dotenv_path=env_path)


ID_USER = os.getenv("ACCOUNT_ID")
DEVICE_NAME = os.getenv("DEVICE_NAME")
SERVER_KEY = os.getenv("SERVER_KEY")
CLIENT_KEY = os.getenv("CLIENT_KEY")
SHARED_FOLDER = os.getenv("FILE_PATH")

URL = 'http://127.0.0.1:5000'


ID = -1
CameraON = False
chunk_size = 64 * 1024

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
    global CameraON
    CameraON = True
    while (cap.isOpened() and CameraON):
        ret, img = cap.read()
        if ret:
            img = cv2.resize(img, (0, 0), fx=1, fy=1)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            frame = base64.encodebytes(frame).decode("utf-8")
            sio.emit('to Client', frame)
            sleep(0.016) # 60 fps master race
        else:
            break
    print('Stopping Camera')
    sio.emit('camera Stopped - Device')

@sio.on('ask Stop Webcam - Device')
def stop_data():
    print('asked to stop the webcam')
    global CameraON
    CameraON = False


# Upload
########################################################################################################################
@sio.on('start-transfer-device')
def start_transfer(filename, size):
    print("analyzing file")
    """Process an upload request from the client."""
    root, ext = os.path.splitext(filename)
    if ext in ['.exe', '.bin', '.js', '.sh', '.py', '.php']:
        sio.emit('allow-transfer-device')
        return False  # reject the upload
    if root.__contains__('.'):
        print('Directory traversal ?')
        sio.emit('allow-transfer-device')
        return False

    print("extensions allowed")

    with open(SHARED_FOLDER + root + '.json', 'wt') as f:
        json.dump({'filename': filename, 'size': size}, f)
        print("wt")
    with open(SHARED_FOLDER + root + ext, 'wb') as f:
        print("wb")
        pass
    print("returning " + root + ext)
    sio.emit('allow-transfer-device', root + ext)  # allow the upload


@sio.on('write-chunk-device')
def write_chunk(filename, offset, data):
    """Write a chunk of data sent by the client."""
    if not os.path.exists(SHARED_FOLDER + filename):
        sio.emit('chunk-uploaded-device', (offset, False))
        return False
    try:
        with open(SHARED_FOLDER + filename, 'r+b') as f:
            f.seek(offset)
            f.write(data)
    except IOError:
        sio.emit('chunk-uploaded-device', (offset, False))
        return False
    sio.emit('chunk-uploaded-device', (offset, True))
    return True
########################################################################################################################

# Shared Folder
########################################################################################################################

@sio.on('download File')
def check_download(filename, offset):
    print('downloading ' + filename)
    root, ext = os.path.splitext(filename)
    if not os.path.exists(SHARED_FOLDER + filename):
        print('file does not exist')
        return False
    if root.__contains__('.'):
        print('Directory traversal ?')
        return False

    try:
        with open(SHARED_FOLDER + filename, 'r+b') as f:
            f.seek(offset)
            data = f.read(chunk_size)
            data = base64.b64encode(data).decode('utf-8')
            if offset + (chunk_size) >= os.path.getsize(SHARED_FOLDER + filename):
                stop = True
            else:
                stop = False
    except IOError:
        print('IO error')
        return False
    sio.emit('returning Downloading', (offset, data, stop))

@sio.on('give Listing - Device')
def give_listing():
    print('asking for listing')
    listing = os.listdir(SHARED_FOLDER)
    print(listing)
    sio.emit('returning Listing', listing)

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
