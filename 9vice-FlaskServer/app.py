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

@socketio.on('my event')
def handle_my_custom_namespace_event(json):
    print('received json: ' + str(json))
    print('Request.sid: ' + request.sid)
    emit('my answer', request.sid)

# Main
if __name__ == '__main__':
    socketio.run(app)
