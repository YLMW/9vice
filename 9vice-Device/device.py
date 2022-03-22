import socketio
import cv2
import json
import os
import base64
from time import sleep
import time
cap=cv2.VideoCapture(0) # Le 1 c'est pour ma webcam

"""
import hashlib
from Crypto.Cipher import AES
from Crypto import Random
from dotenv import load_dotenv

class AESCipher(object):

    def __init__(self):
        env_path = os.getcwd() + "/.env"
        load_dotenv(dotenv_path=env_path)
        SECRET = os.getenv("SECRET_KEY")
        self.bs = AES.block_size
        self.key = hashlib.sha256(SECRET.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]
"""

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

########################################################################################################################
os.chdir('./shared/')
rootdir = os.getcwd()

@sio.on('start-transfer-device')#判断文件格式和文件名，如果包含可以信息则拒绝，返回False
def start_transfer(uploadDir, filename, size):
    print("analyzing file")
    """Process an upload request from the client."""
    root, ext = os.path.splitext(filename)#pour savoir le type de fichier
    if ext in ['.exe', '.bin', '.js', '.sh', '.py', '.php']:#ne permet pas des fichiers de codes 
        sio.emit('allow-transfer-device')
        return False  # reject the upload
    if root.__contains__('..') or uploadDir.__contains__('..'):
        print('Directory traversal ?')
        sio.emit('allow-transfer-device')
        return False

    print("extensions allowed")
    print(rootdir + uploadDir + root + '.json')
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

    contents= []
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

@sio.on('read_file_asked')
def read_file_asked(dirCurrent, filename):
    fullPath = "." + dirCurrent + os.sep +filename
    if os.path.exists(fullPath):
        root, ext = os.path.splitext(filename)#pour savoir le type de fichier
        if dirCurrent.__contains__('..') or root.__contains__('..'):
            print('Directory traversal ?')
            return False
        if ext in ['.txt']:
            f = open(fullPath, 'r')# r->text， rb->bite
        else:
            f = open(fullPath, 'rb')# r->text， rb->bite

        ### à continuer mais je vais au dodo 


########################################################################################################################

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
sio.emit('Connect Device', ID)  #设备只要一连上就会把自己的ID发送到服务器
