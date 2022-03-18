# Routes pour l'auth
# Import des libs python
import re
import string

from ..requester.request import Requester
from ..crypto.crypto import AESCipher
from ..user.user import get_info, is_logged
from flask import Blueprint, render_template, request, make_response, redirect, url_for
from markupsafe import escape
import hashlib
from dotenv import load_dotenv
import os

# Creation du blueprint
auth = Blueprint('auth', __name__)
dbReq = Requester()
aesCipher = AESCipher()
load_dotenv(os.getcwd() + "/9vice-FlaskServer/routes/.env")


# Definition des routes
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        session = request.cookies.get('user_session')
        if session:
            return redirect(url_for('main.index'))
        if request.args.get('success'):
            return render_template('login.html', success=escape(request.args.get('success')))
        else:
            return render_template('login.html')
    else:

        loginUsernameMail = escape(request.form.get('login'))

        if not isValidMail(loginUsernameMail) and not isValidUsername(loginUsernameMail):
            return render_template('login.html', erreur='Nom d\'utilisateur / Addresse mail non valide')

        loginType = 'mail' if loginUsernameMail.__contains__('@') else 'username'

        env_path = os.getcwd() + "/9vice-FlaskServer/routes/.env"
        load_dotenv(dotenv_path=env_path)
        SALT = os.getenv("SALT")

        password = escape(request.form.get('password'))
        hash = hashlib.sha256(SALT.encode() + password.encode()).hexdigest()

        userInfos = dbReq.login_user(loginUsernameMail, loginType, hash)

        if userInfos:
            # Login valid
            resp = make_response(redirect(url_for('main.index')))
            resp.set_cookie('user_session', aesCipher.encrypt(str(userInfos[0])),
                            max_age=18000)  # expire au bout de 5 heures
            return resp
        else:
            # Login invalid
            return render_template('login.html', erreur='Identifiant / mot de passe incorrect')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        session = request.cookies.get('user_session')
        if session:
            return redirect(url_for('main.index'))
        return render_template('register.html')

    else:
        try:
            email = escape(request.form.get('email'))
            username = escape(request.form.get('username'))
            password = escape(request.form.get('password'))
            passwordConfirm = escape(request.form.get('passwordConfirm'))
            SALT = os.getenv("SALT")
            hashed = hashlib.sha256(SALT.encode() + password.encode()).hexdigest()

            if not isValidMail(email):
                return render_template('register.html', erreur='Email incorrect', username=username, mail=email)

            if not isValidUsername(username):
                return render_template('register.html', erreur='Nom d\'utilisateur incorrect (charactères autorisés = A-Z, a-z, 0-9)', username=username, mail=email)

            if not isStrongPassword(password):
                return render_template('register.html', erreur="Votre mot de passe doit faire, au moins 8 characteres, et contenir majuscule, minuscule et chiffre", username=username, mail=email)

            if not isSamePassword(password, passwordConfirm):
                return render_template('register.html', erreur='Les mots de passe ne correspondent pas', username=username, mail=email)

            if dbReq.insert_user(username, email, hashed):
                return redirect(url_for('auth.login') + "?success=Compte cree avec succes")
            else:
                return render_template('register.html', erreur='Informations incorrectes')
        except Exception as e:
            print(e)
            return render_template('register.html', erreur="Methode d'acces incorrect")


@auth.route('/logout')
def logout():
    resp = make_response(redirect(url_for('main.index')))
    resp.delete_cookie('user_session')
    return resp


# Verification funcs
def isValidMail(mail):
    return True if re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", mail) else False


def isValidUsername(username):
    return all(c in string.ascii_letters + string.digits for c in username)


def isSamePassword(password, passwordConf):
    return password == passwordConf


def isStrongPassword(password):
    majuscule = re.compile(r"[A-Z]")
    minuscule = re.compile(r"[a-z]")
    chiffre = re.compile(r"[0-9]")

    return majuscule.search(password) and minuscule.search(password) and chiffre.search(password) and (len(password) > 7)