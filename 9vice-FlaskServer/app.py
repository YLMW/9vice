# Main app
# Import des libs python
from flask import Flask, render_template

# Import des blueprints de routage
from routes.main import main
from routes.auth import auth


# Creation de l'appli
app = Flask(__name__, template_folder='templates/')

# Ajout des routages blueprint
app.register_blueprint(main)
app.register_blueprint(auth)


# Interception de l'erreur 404
@app.errorhandler(404)
def not_found(error):
    return render_template('pageNotFound.html'), 404


# Main
if __name__ == '__main__':
    app.run(ssl_context='adhoc')
