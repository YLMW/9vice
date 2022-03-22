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
socketio = SocketIO(app)

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


@socketio.on('start-transfer-client')
def start_transfer(filename, size):
    print('asking permission to write ' + filename + ' of size ' + str(size))
    target = clientDevice[request.sid]
    emit('start-transfer-device', (filename, size), room=target)


@socketio.on('write-chunk-client')
def write_chunk(filename, offset, data):
    print('Writing data to ' + filename + ' offset: ' + str(offset))
    target = clientDevice[request.sid]
    emit('write-chunk-device', (filename, offset, data), room=target)
########################################################################################################################

# Shared Folder
########################################################################################################################
@socketio.on('give Listing')
def give_listing():
    print('Giving listing')
    target = clientDevice[request.sid]
    emit('give Listing - Device', room=target)


@socketio.on('returning Listing')
def give_listing(listing):
    target = get_key(request.sid, clientDevice)
    emit('give Listing - Client', listing, room=target)

@socketio.on('ask Download')
def ask_download(filename, offset):
    target = clientDevice[request.sid]
    emit('download File', (filename, offset), room=target)

@socketio.on('returning Downloading')
def send_download(offset, data, stop):
    target = get_key(request.sid, clientDevice)
    print('Downing Client ' + str(offset))
    emit('downloaded Data - to Client', (offset, data, stop), room=target)

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
    app.run()
