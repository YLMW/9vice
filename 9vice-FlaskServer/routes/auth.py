# Routes pour l'auth
# Import des libs python
import re
import string


from flask import Blueprint, render_template, request
from markupsafe import escape

# Creation du blueprint
auth = Blueprint('auth', __name__)


# Definition des routes
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        loginUsernameMail = escape(request.form.get('login'))

        if not isValidMail(loginUsernameMail) and not isValidUsername(loginUsernameMail):
            return render_template('login.html', erreur='Nom d\'utilisateur / Addresse mail incorrect')

        loginType = 'mail' if loginUsernameMail.__contains__('@') else 'username'

        if (loginType == 'mail' and not isRegistredMail(loginUsernameMail)) \
                or (loginType == 'username' and isRegistredUsername(loginUsernameMail)):
            return render_template('login.html', erreur='Nom d\'utilisateur / Addresse mail inconnu')

        password = escape(request.form.get('password'))

        # TODO -> probleme remember TRUE mais non coché
        doRemember = True if escape(request.form.get('rememberme')) == 'remember-me' else False

        # TODO -> remove cette feature de dev
        allData = 'login: ' + loginUsernameMail + ' / password: ' + password + ' / remember: ' + str(doRemember)

        return render_template('login.html', erreur=allData)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = escape(request.form.get('email'))
        if not isValidMail(email):
            return render_template('register.html', erreur='Email incorrect')
        if requestDB.isRegistredMail(email):
            return render_template('register.html', erreur='Email déjà enregistré')

        username = escape(request.form.get('username'))
        if not isValidUsername(username):
            return render_template('register.html', erreur='Nom d\'utilisateur incorrect (charactères autorisés = A-Z, a-z, 0-9)')
        if isRegistredUsername(username):
            return render_template('register.html', erreur='Nom d\'utilisateur déjà pris')

        password = escape(request.form.get('password'))
        passwordConfirm = escape(request.form.get('passwordConfirm'))
        if not isSamePassword(password, passwordConfirm):
            return render_template('register.html', erreur='Les mots de passe ne correspondent pas')

        # TODO -> Faire politique password

        # TODO -> remove feature dev
        allData = 'email: ' + email + ' / pass: ' + password + ' / passConfirm: ' + passwordConfirm + ' / username: ' + username

        return render_template('register.html', erreur=allData)


@auth.route('/logout')
def logout():
    return render_template('base.html', logout_active='active')


# Verification funcs
def isValidMail(mail):
    # TODO -> regex de m**** qui ne valide pas marc@ens.uvsq.fr -> changer la regex
    return True if re.search("^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w{2,3}$", mail) else False


def isValidUsername(username):
    return all(c in string.ascii_letters + string.digits for c in username)


def isSamePassword(password, passwordConf):
    return password == passwordConf


