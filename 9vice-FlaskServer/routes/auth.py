# Routes pour l'auth
# Import des libs python
import re
import string

from ..requester.request import Requester
from flask import Blueprint, render_template, request
from markupsafe import escape

# Creation du blueprint
auth = Blueprint('auth', __name__)
dbReq = Requester()

loggedUsersInfos = {}


# Definition des routes
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        loginUsernameMail = escape(request.form.get('login'))

        if not isValidMail(loginUsernameMail) and not isValidUsername(loginUsernameMail):
            return render_template('login.html', erreur='Nom d\'utilisateur / Addresse mail non valide')

        loginType = 'mail' if loginUsernameMail.__contains__('@') else 'username'

        password = escape(request.form.get('password'))

        userInfos = dbReq.login_user(loginUsernameMail, loginType, password)

        if userInfos:
            # Login valid
            # TODO -> session cookie + hash de mot de passe
            loggedUsersInfos[userInfos[0]] = userInfos
            print(loggedUsersInfos)
            return render_template('index.html')
        else:
            # Login invalid
            return render_template('login.html', erreur='Identifiant / mot de passe incorrect')



@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = escape(request.form.get('email'))
        if not isValidMail(email):
            return render_template('register.html', erreur='Email incorrect')

        username = escape(request.form.get('username'))
        if not isValidUsername(username):
            return render_template('register.html',
                                   erreur='Nom d\'utilisateur incorrect (charactères autorisés = A-Z, a-z, 0-9)')

        password = escape(request.form.get('password'))
        passwordConfirm = escape(request.form.get('passwordConfirm'))

        if not isSamePassword(password, passwordConfirm):
            return render_template('register.html', erreur='Les mots de passe ne correspondent pas')

        # TODO -> Faire et verif politique password

        # TODO -> Hash the pass
        hashed = password

        if dbReq.insert_user(username, email, hashed):
            return render_template('index.html')
        else:
            return render_template('register.html', erreur='Informations incorrectes')


@auth.route('/logout')
def logout():
    return render_template('base.html', logout_active='active')


# Verification funcs
def isValidMail(mail):
    return True if re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", mail) else False


def isValidUsername(username):
    return all(c in string.ascii_letters + string.digits for c in username)


def isSamePassword(password, passwordConf):
    return password == passwordConf
