# Routes pour l'auth
# Import des libs python
import re
import string

from requester.request import Requester
from crypto.crypto import AESCipher
from user.user import get_info, is_logged, is_locked
from flask import Blueprint, render_template, request, make_response, redirect, url_for
from markupsafe import escape
import hashlib
from dotenv import load_dotenv
import os

# Creation du blueprint
auth = Blueprint('auth', __name__)
dbReq = Requester()
aesCipher = AESCipher()
# Récupération du SALT
env_path = os.getcwd() + "/.env"
load_dotenv(dotenv_path=env_path)
SALT = os.getenv("SALT")

# Definition des routes
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if request.args.get('success'):
            return render_template('login.html', success=escape(request.args.get('success')))
        session = request.cookies.get('user_session')
        if session:
            loggedUserinfo = get_info(session)
            if is_logged(loggedUserinfo):
                if not is_locked(loggedUserinfo):
                    dbReq.update_con(loggedUserinfo['id'])
                else:
                    resp = make_response(render_template('login.html', erreur="Votre compte est bloque. Veuillez vous rapprocher d'un administrateur."))
                    resp.delete_cookie('user_session')
                    return resp
        return render_template('login.html')
    else:

        loginUsernameMail = escape(request.form.get('login'))

        if not isValidMail(loginUsernameMail) and not isValidUsername(loginUsernameMail):
            return render_template('login.html', erreur='Nom d\'utilisateur / Addresse mail non valide')

        loginType = 'mail' if loginUsernameMail.__contains__('@') else 'username'



        password = request.form.get('password')
        hash = hashlib.sha256(SALT.encode() + password.encode()).hexdigest()

        userInfos = dbReq.login_user(loginUsernameMail.lower(), loginType, hash)

        if userInfos:
            # Login valid
            if bool(userInfos[5]): # Utilisateur bloqué
                return render_template('login.html', erreur="Votre compte est bloque")
            else:
                dbReq.update_con(userInfos[0])
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
            email = escape(request.form.get('email')).lower()
            username = escape(request.form.get('username')).lower()
            password = escape(request.form.get('password'))
            passwordConfirm = escape(request.form.get('passwordConfirm'))
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
            return render_template('register.html', erreur="Un compte existe deja pour ces informations.")


@auth.route('/logout')
def logout():
    resp = make_response(redirect(url_for('main.index')))
    resp.delete_cookie('user_session')
    return resp


@auth.route('/changePass', methods=['GET', 'POST'])
def changePass():
    if request.method == 'GET':
        session = request.cookies.get('user_session')
        if session:
            loggedUserinfo = get_info(session)
            if is_logged(loggedUserinfo) and not is_locked(loggedUserinfo):
                return render_template('changePassword.html', userLogged=loggedUserinfo)
        return redirect(url_for('auth.login'))

    else:
        try:
            session = request.cookies.get('user_session')
            if session:
                loggedUserinfo = get_info(session)
                if is_logged(loggedUserinfo) and not is_locked(loggedUserinfo):
                    currentPassword = escape(request.form.get('currentPassword'))
                    password = escape(request.form.get('newPassword'))
                    passwordConfirm = escape(request.form.get('newPasswordConfirm'))
                    currentHash = hashlib.sha256(SALT.encode() + currentPassword.encode()).hexdigest()
                    hashed = hashlib.sha256(SALT.encode() + password.encode()).hexdigest()

                    if not isStrongPassword(password):
                        return render_template('changePassword.html', erreur="Votre mot de passe doit faire, au moins 8 characteres, et contenir majuscule, minuscule et chiffre")

                    if not isSamePassword(password, passwordConfirm):
                        return render_template('changePassword.html', erreur='Les mots de passe ne correspondent pas')

                    if dbReq.update_passwd(loggedUserinfo['id'], currentHash, hashed):
                        return redirect(url_for('main.profile')+"?success=ok")
                    else:
                        return render_template('changePassword.html', erreur="Le mot de passe n'a pas pu etre change")
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(e)
            return render_template('register.html', erreur="Un compte existe deja pour ces informations.")


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