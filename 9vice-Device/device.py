import socketio
import cv2
import json
import os
import base64
from time import sleep
cap=cv2.VideoCapture(0) # Le 1 c'est pour ma webcam

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

    with open('./shared/' + root + '.json', 'wt') as f:
        json.dump({'filename': filename, 'size': size}, f)
        print("wt")
    with open('./shared/' + root + ext, 'wb') as f:
        print("wb")
        pass
    print("returning " + root + ext)
    sio.emit('allow-transfer-device', root + ext)  # allow the upload


@sio.on('write-chunk-device')
def write_chunk(filename, offset, data):
    """Write a chunk of data sent by the client."""
    if not os.path.exists('./shared/' + filename):
        sio.emit('chunk-uploaded-device', (offset, False))
        return False
    try:
        with open('./shared/' + filename, 'r+b') as f:
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
    if not os.path.exists('./shared/' + filename):
        print('file does not exist')
        return False
    if root.__contains__('.'):
        print('Directory traversal ?')
        return False

    try:
        with open('./shared/' + filename, 'r+b') as f:
            f.seek(offset)
            data = f.read(64 * 1024)
            data = base64.b64encode(data).decode('utf-8')
            if offset + (64 * 1024) >= os.path.getsize('./shared/' + filename):
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
    listing = os.listdir("./shared/")
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



# main
sio.connect('http://localhost:5000')
sio.sleep(1)
sio.emit('Connect Device', ID)
