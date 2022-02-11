# Routes pour la video
# Import des libs python
import flask
from flask import Blueprint, render_template, make_response

# Creation du blueprint
video = Blueprint('video', __name__)


# Definition des routes
@video.route('/test')
def test():
    resp = make_response(render_template('video.html'))
    resp.headers.add_header('Access-Control-Allow-Origin', '*')
    return resp


@video.route('/threejs')
def threejs():
    return render_template('threejs.html')
