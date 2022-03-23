import socketio
import json
import base64
from time import sleep
import time
import cv2
import hashlib
from crypto.crypto import *

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


SECRET = hashlib.sha256(CLIENT_KEY.replace("\n", "").encode()).hexdigest()[0:32]
print('Secret = ' + SECRET)

print(SECRET)

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
            img = cv2.flip(img, 1)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            frame = base64.encodebytes(frame).decode("utf-8")
            print(frame)
            print('')
            encrypted_frame = aes_cbc_encrypt_text(frame, SECRET)
            sio.emit('to Client', encrypted_frame)
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

########################################################################################################################
os.chdir(SHARED_FOLDER) # Fait qu'à l'init #########################
rootdir = os.getcwd()

@sio.on('start-transfer-device')#判断文件格式和文件名，如果包含可以信息则拒绝，返回False
def start_transfer(uploadDir, filename, size):
    print("analyzing file")
    """Process an upload request from the client."""
    root, ext = os.path.splitext(filename)#pour savoir le type de fichier
    if ext in ['.exe', '.bin', '.js', '.sh', '.py', '.php']:#ne permet pas des fichiers de codes
        sio.emit('allow-transfer-device', '..Denied..')
        return False  # reject the upload
    if root.__contains__('..') or uploadDir.__contains__('..'):
        print('Directory traversal ?')
        sio.emit('allow-transfer-device', '..Denied..')
        return False

    print("extensions allowed")
    print(rootdir + uploadDir + root + '.json')
    if os.path.exists(rootdir + uploadDir + filename):
        print('File exists already')
        sio.emit('allow-transfer-device', '..Denied..')
        return False
    with open(rootdir + uploadDir + root + ext, 'wb') as f:#暂时无用
        print("wb")
        pass
    print("returning " + root + ext)
    sio.emit('allow-transfer-device', root + ext)  # 设备检查通过会给服务器返回 allow the upload，返回文件名到allow-transfer-device事件


@sio.on('write-chunk-device')#收到客户端传来的数据，写进device的指定文件夹中
def write_chunk(uploadDir ,filename, offset, data):#写数据
    """Write a chunk of data sent by the client."""
    if not os.path.exists(rootdir + uploadDir + filename):#如果该文件不存在则返回false
        sio.emit('chunk-uploaded-device', (offset, False))
        return False
    try:
        with open(rootdir + uploadDir + filename, 'r+b') as f:#否则打开文件从sffset开始写入data
            f.seek(offset)
            f.write(data)
    except IOError:
        sio.emit('chunk-uploaded-device', (offset, False))
        return False
    sio.emit('chunk-uploaded-device', (offset, True))#写完后返回true和offset
    return True

##################################################################################
@sio.on('show fichiers')
def show_fichiers(dirCurrent, filename):
    """  """
    root, ext = os.path.splitext(filename)

    if(filename == 'begin' or filename == ".."):
        #切换到根目录
        os.chdir(rootdir)
        dirCurrent=os.sep

    elif(filename == ''):
        os.chdir(rootdir + dirCurrent)

    elif root.__contains__('.'):
        print('Directory traversal ?')
        os.chdir(rootdir)
        dirCurrent = os.sep
    else:
        fullname = os.getcwd()+os.sep+filename #os.sep= '/' ou '\' ca depend le systeme, pour nous linux c'est '/'
        #  fichier，download
        if os.path.isfile(fullname):
            # return redirect(url_for('show', fname=subdir))
        #  dossier，cd
            return
        else:
            os.chdir(fullname) #进入文件夹
            dirCurrent += filename+os.sep #更改现在所处地址

    contents = []
    for i in sorted(os.listdir(os.getcwd())):
        fullPath = os.getcwd()+os.sep+i
        if os.path.isdir(fullPath):
           i = i+os.sep#si dossier+'/'
        content = {}
        content['fname'] = i
        content['mtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.stat(fullPath).st_mtime))
        content['fsize'] = str(round(os.path.getsize(fullPath) / 1024)) + 'k'
        contents.append(content)

    sio.emit('send url root', (rootdir, dirCurrent, contents, os.sep) )

@sio.on('create-directory')
def create_directory(x,dirCurrent):
    pathNewDir = os.getcwd() +os.sep+ x
    print("create new dir" + pathNewDir)
    try:
        os.makedirs(pathNewDir)# Si ça marche
    except Exception as e:
        print(e) # Si ca marche pas
        dirCurrent = False
    sio.emit('ask-update',dirCurrent)

########################################################################################################################
@sio.on('download File')
def check_download(dirCurrent, filename, offset):
    print('downloading : ' + rootdir + dirCurrent + filename)
    root, ext = os.path.splitext(filename)
    if not os.path.exists(rootdir + dirCurrent + filename):
        print('file does not exist')
        return False
    if root.__contains__('.'):
        print('Directory traversal ?')
        return False

    try:
        with open(rootdir + dirCurrent + filename, 'r+b') as f:
            f.seek(offset)
            data = f.read(chunk_size)
            data = base64.b64encode(data).decode('utf-8')
            if offset + (chunk_size) >= os.path.getsize(rootdir + dirCurrent + filename):
                stop = True
            else:
                stop = False
    except IOError:
        print('IO error')
        return False
    sio.emit('returning Downloading', (offset, data, stop))

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
