# Main app
# Import des libs python
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import send, emit # Pour utiliser send et emit => réponse du serveur
from flask_socketio import join_room, leave_room    # Les rooms
from flask import request   # request.sid

# Import des blueprints de routage
from routes.main import main
from routes.auth import auth

# Creation de l'appli
app = Flask(__name__, template_folder='templates/')

# Setup SocketIO
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Ajout des routages blueprint
app.register_blueprint(main)
app.register_blueprint(auth)


# Interception de l'erreur 404
@app.errorhandler(404)
def not_found(error):
    return render_template('pageNotFound.html'), 404

# Client/Device link setup
clientDevice = {} # Correspondence ClientSID et DeviceSID
DeviceID = {}     # Correspondence DeviceSID et ID, on devrait pas utiliser un dictionnaire

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
def handle_my_custom_namespace_event(ID):
    print('New device detected, sid: ' + request.sid + ', id: ' + ID)
    DeviceID[request.sid] = ID
    emit('Device advertised', ID, broadcast=True)

@socketio.on('Link Device')
def link_device_client(ID):
    device_sid = get_key(ID, DeviceID)
    print('Linking client and device, C_sid: ' + request.sid + ', D_sid: ' + device_sid)
    clientDevice[request.sid] = device_sid

    emit('Linked', clientDevice[request.sid], room=request.sid)
    print('Client Knows - ' + device_sid)

    emit('Linked', request.sid, room=device_sid)
    print('Device Knows - ' + request.sid)

    DeviceID.pop(device_sid)  # Pour ne pas réattribuer la même websocket de Device à un autre client on la retire de la liste

@socketio.on('to Device')
def to_device(data):
    target = clientDevice[request.sid]
    print('Sending: "' + data + '" to device')
    emit('from Client', data, room=target)

@socketio.on('to Client')
def to_client(data):
    target = get_key(request.sid, clientDevice)
    print('Sending: "' + data + '" to client')
    emit('from Device', data, room=target)

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
    socketio.run(app)
