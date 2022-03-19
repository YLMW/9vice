import socketio

# standard Python
sio = socketio.Client()

@sio.on('my device')
def on_message(data):
    print('I received a message!')
    print('data:' + data)

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
