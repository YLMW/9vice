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
    print('New client detected, sid: ' + request.sid)#给予新接入的客户一个请求Sid

@socketio.on('Connect Device')
def handle_my_custom_namespace_event(ID):
    print('New device detected, sid: ' + request.sid + ', id: ' + ID)
    DeviceID[request.sid] = ID#给予接入的设备一个SocketId并将其与设备的ID号一起加入字典
    emit('Device advertised', ID, broadcast=True)#收到新连接的设备的ID，广播给所有客户

@socketio.on('Link Device')
def link_device_client(ID):
    device_sid = get_key(ID, DeviceID)#服务器收到客户端发来的设备ID通过设备的ID得到设备的SocketID
    print('Linking client and device, C_sid: ' + request.sid + ', D_sid: ' + device_sid)
    clientDevice[request.sid] = device_sid#将客户这个请求一个Sid并与设备的sid联结一并存入字典

    emit('Linked', clientDevice[request.sid], room=request.sid)#将设备sid返回给客户
    print('Client Knows - ' + device_sid)

    emit('Linked', request.sid, room=device_sid)#将客户此次请求sid返回给设备
    print('Device Knows - ' + request.sid)

    DeviceID.pop(device_sid)  # Pour ne pas réattribuer la même websocket de Device à un autre client on la retire de la liste
    #一个设备id只对应一个客户sid，所以连接在客户有了设备sid之后便把该sid抛出，如有新的对设备的访问请求则产生新的sid重新加入


@socketio.on('to Device')
def to_device(data):
    target = clientDevice[request.sid]
    print('Sending: "' + data + '" to device')
    emit('from Client', data, room=target)
    # emit('stream Webcam', room=target) # Just to get things started
    emit('show fichiers', ('',''),room=target) # Just to get things started, si on veux fusionner les codes,
                    #ici c'est l'Event: client a choisi un device pour acceder dans le dossier partager


@socketio.on('to Client')
def to_client(data):
    target = get_key(request.sid, clientDevice)
    print('Sending: "' + data + '" to client')
    emit('from Device', data, room=target)

########################################################################################################################


@socketio.on('allow-transfer-device')
def allow_transfer(answer):# 设备将是否允许上传的答复传到服务器上的allow-transfer-device函数
    target = get_key(request.sid, clientDevice)#服务器找到对应请求的sid
    print('in callback ' + answer + ' target ' + target)
    emit('allow-transfer', answer, room=target)#并将答复传送到客户端的allow-transfer事件，这里的答复soit False soit Filename


@socketio.on('chunk-uploaded-device')
def allow_transfer(offset, ack):
    target = get_key(request.sid, clientDevice)
    print('in callback ' + str(offset) + ' ack: ' + str(ack))
    emit('chunk-uploaded', (offset, ack), room=target)#将device写数据的结果传给客户


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

@socketio.on('send url root')#to client
def send_url_root(rootdir, dirCurrent, contents, ossep):
    """  """
    print('send root@  to client' + rootdir)
    target = get_key(request.sid, clientDevice)

    emit('Shared Directory', (rootdir, dirCurrent, contents, ossep), room=target )

@socketio.on('send urlCurrent')#to device
def send_url_current(dirCurrent, filename):
    """  """
    print('send urlCurrent to device' )
    target = clientDevice[request.sid]
    emit('show fichiers', (dirCurrent, filename), room=target )

@socketio.on('read file')
def send_filename(dirCurrent, filename):
    print('send filename to device' )
    target = clientDevice[request.sid]
    emit('read_file_asked', (dirCurrent, filename), room=target )






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
