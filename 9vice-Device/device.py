import socketio

# Probablement un truc qui finira dans un .env, moi j'y connais rien
ID = '9'
client = '' # essentiellement inutile

# standard Python
sio = socketio.Client()

@sio.on('my device')
def on_message(data):
    print('I received a message!')
    print('data:' + data)

@sio.on('Linked')
def on_message(data):
    client = data
    print('I am linked to ' + client)

@sio.on('from Client')
def on_message(data):
    print('I received: ' + data)
    print('I\'ll answer "ACK"')
    sio.emit('to Client', 'ACK')



@sio.event
def connect():
    print("I'm connected!")

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
print('my sid is', sio.sid)
sio.sleep(1)
sio.emit('Connect Device', ID)
