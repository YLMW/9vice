# Main app
# Import des libs python
import hashlib
import os
import emoji

from dotenv import load_dotenv
from flask import Flask, render_template, request

from flask_socketio import SocketIO
from flask_socketio import send, emit  # Pour utiliser send et emit => réponse du serveur
from flask_socketio import join_room, leave_room  # Les rooms

# Import des blueprints de routage
from routes.main import main
from routes.auth import auth
from user.device import get_device_id, get_device_hash, set_active, set_inactive

import logging

# Creation de l'appli
app = Flask(__name__, template_folder='templates/')

# Ajout des routages blueprint
app.register_blueprint(main)
app.register_blueprint(auth)

env_path = os.getcwd() + "/.env"
load_dotenv(dotenv_path=env_path)
SECRET = os.getenv("APP_SECRET_KEY")
SALT = os.getenv("SALT")

# Setup SocketIO
app.config['SECRET_KEY'] = SECRET
socketio = SocketIO(app, ping_interval=10)

log=logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

@app.template_filter('emojify')
def emoji_filter(s):
    return emoji.emojize(s)

# Interception de l'erreur 404
@app.errorhandler(404)
def not_found(error):
    return render_template('pageNotFound.html'), 404


# Client/Device link setup
clientDevice = {}  # Correspondence ClientSID et DeviceSID
DeviceID = {}  # Correspondence DeviceSID et ID, on devrait pas utiliser un dictionnaire
CurrentDeviceList = {} # Tous les devices actuellement up SID : ID

# Pour récupérer une clé depuis une valeur en O(n)
def get_key(val, dict):
    for key, value in dict.items():
        if val == value:
            return key


# SocketIO Events

@socketio.on('Connect Client')
def handle_my_custom_namespace_event(json):
    print('New client detected, sid: ' + request.sid)


@socketio.on('Connect Device')
def handle_device_connection(data):
    print('New device detected, sid: ' + request.sid)
    id_user = data['id_user']
    name = data['name']
    mdp = data['mdp']
    ID = get_device_id(id_user, name)
    hashed = hashlib.sha256(SALT.encode() + mdp.encode()).hexdigest()
    dbhash = get_device_hash(ID)
    if hashed == dbhash:
        if set_active(id_user, ID):
            DeviceID[request.sid] = ID
            CurrentDeviceList[request.sid] = ID
            emit('Device advertised', {"ID": ID}, broadcast=True)
            return
    raise ConnectionRefusedError('unauthorized!')


@socketio.on('Device disconnected')
def test_disco(data):
    print('request.sid ' + request.sid)
    # Code de vérif que request.sid € CurrentDeviceList
    id_to_inactive = CurrentDeviceList.get(request.sid)
    set_inactive(id_to_inactive)
    CurrentDeviceList.pop(request.sid)


@socketio.on('Link Device')
def link_device_client(ID):
    device_sid = get_key(ID, DeviceID)
    if device_sid == None:
        print('No device available')
        emit('No Device')
    else:
        print('Linking client and device, C_sid: ' + request.sid + ', D_sid: ' + device_sid)
        clientDevice[request.sid] = device_sid

        emit('Linked', clientDevice[request.sid], room=request.sid)
        print('Client Knows - ' + device_sid)

        emit('Linked', request.sid, room=device_sid)
        print('Device Knows - ' + request.sid)

        DeviceID.pop(
            device_sid)  # Pour ne pas réattribuer la même websocket de Device à un autre client on la retire de la liste

@socketio.on('disconnect')
def test_disconnect():
    print('registering Disconnection ' + request.sid)
    # Code de vérif que request.sid € CurrentDeviceList
    id_to_inactive = CurrentDeviceList.get(request.sid)
    if id_to_inactive is None:
        print('It was a client')
        linked_device = clientDevice.get(request.sid)
        if linked_device is not None:
            print('It was linked to a device')
            print('Client: ' + request.sid + ' / Device: ' + linked_device)
            clientDevice.pop(request.sid)
            linked_device_id = CurrentDeviceList[linked_device]
            DeviceID[linked_device] = linked_device_id
        else:
            print('He was alone')
    else:
        print('It was a device')
        linked_client = get_key(request.sid, clientDevice)
        my_id = CurrentDeviceList[request.sid]
        set_inactive(my_id)
        if linked_client is not None:
            print('It was linked to a client')
            print('Client: ' + linked_client + ' / Device: ' + request.sid)
            emit('No Device', room=linked_client)
            clientDevice.pop(linked_client)
            CurrentDeviceList.pop(request.sid)
        else:
            print('He was alone')
            DeviceID.pop(request.sid)
            CurrentDeviceList.pop(request.sid)

# Camera
########################################################################################################################
@socketio.on('to Device')
def to_device(data):
    target = clientDevice[request.sid]
    #print('Sending: "' + data + '" to device')
    emit('from Client', data, room=target)
    emit('stream Webcam', room=target)  # Just to get things started


@socketio.on('to Client')
def to_client(data):
    target = get_key(request.sid, clientDevice)
    #print('Sending: "' + data + '" to client')
    emit('from Device', data, room=target)


@socketio.on('camera Stopped - Device')
def to_client():
    target = get_key(request.sid, clientDevice)
    print('Stopping Camera')
    emit('camera Stopped - Client', room=target)\


@socketio.on('ask Stop Webcam')
def to_device():
    target = clientDevice[request.sid]
    print('asking to stop Webcam')
    emit('ask Stop Webcam - Device', room=target)
########################################################################################################################

# Upload
########################################################################################################################
@socketio.on('allow-transfer-device')
def allow_transfer(answer):
    target = get_key(request.sid, clientDevice)
    print('in callback ' + answer + ' target ' + target)
    emit('allow-transfer', answer, room=target)


@socketio.on('chunk-uploaded-device')
def allow_transfer(offset, ack):
    target = get_key(request.sid, clientDevice)
    print('in callback ' + str(offset) + ' ack: ' + str(ack))
    emit('chunk-uploaded', (offset, ack), room=target)


@socketio.on('start-transfer-client')#服务器监控start-transfer-client事件，如果有数据（name，size）传来
def start_transfer(uploadDir, filename, size):
    print('asking permission to write ' + filename + ' of size ' + str(size))
    target = clientDevice[request.sid]
    emit('start-transfer-device', (uploadDir, filename, size), room=target) #把收到的数据传通过sid发送到设备端的start-transfer-device事件


@socketio.on('write-chunk-client')#接受客户端读取的数据 传送给device
def write_chunk(uploadDir, filename, offset, data):
    print('Writing data to ' + filename + ' offset: ' + str(offset))
    target = clientDevice[request.sid]
    return emit('write-chunk-device', (uploadDir, filename, offset, data), room=target)

########################################################################################################################

# Shared Folder
########################################################################################################################
"""
@socketio.on('give Listing')
def give_listing():
    print('Giving listing')
    target = clientDevice[request.sid]
    emit('give Listing - Device', room=target)


@socketio.on('returning Listing')
def give_listing(listing):
    target = get_key(request.sid, clientDevice)
    emit('give Listing - Client', listing, room=target)
"""

@socketio.on('ask Download')
def ask_download(dirCurrent, filename, offset):
    print('Download asked ' + filename)
    target = clientDevice[request.sid]
    emit('download File', (dirCurrent, filename, offset), room=target)

@socketio.on('returning Downloading')
def send_download(offset, data, stop):
    target = get_key(request.sid, clientDevice)
    print('Downing Client ' + str(offset))
    emit('downloaded Data - to Client', (offset, data, stop), room=target)


@socketio.on('ask show')
def ask_show(dirCurrent, filename, offset):
    print('Show asked ' + filename)
    target = clientDevice[request.sid]
    emit('show File', (dirCurrent, filename, offset), room=target)

@socketio.on('returning Reading')
def send_read(offset, data, stop):
    target = get_key(request.sid, clientDevice)
    print('Reading Client ' + str(offset))
    emit('show Data - to Client', (offset, data, stop), room=target)

@socketio.on('ask-update')
def Update(dirCurrent):
    target = get_key(request.sid, clientDevice)
    if not dirCurrent:
        emit('alert', "Directory already exist", room=target)
    else:
        print('Sending: "' + dirCurrent + '" to client')
        emit('update', dirCurrent, room=target)

@socketio.on('send url root')#to client
def send_url_root(rootdir, dirCurrent, contents, ossep):
    """  """
    print('send root@  to client' + rootdir)
    target = get_key(request.sid, clientDevice)

    emit('Shared Directory', (rootdir, dirCurrent, contents, ossep), room=target)

@socketio.on('send urlCurrent')#to device
def send_url_current(dirCurrent, filename):
    """  """
    try:
        print('send urlCurrent to device')
        target = clientDevice[request.sid]
        emit('show fichiers', (dirCurrent, filename), room=target)
    except Exception as e:
        print(e)

@socketio.on('create-new-directory')#to device
def send_dirname(dirname, dirCurrent):
    print('send new dirname to device' )
    target = clientDevice[request.sid]
    emit('create-directory', (dirname, dirCurrent), room=target)

########################################################################################################################


######################################
# Temporary events to test and debug #
######################################
@socketio.on('request device list')
def handle_my_custom_namespace_event(json):
    print('Devices requested')
    emit('Device Listing', DeviceID)


@socketio.on('my event')
def handle_my_custom_namespace_event(json):
    print('received json: ' + str(json))
    print('Request.sid: ' + request.sid)
    emit('my answer', request.sid)
    emit('my device', 'Hello sid:' + request.sid, broadcast=True)


# Main
if __name__ == '__main__':
    app.run(debug=True)
