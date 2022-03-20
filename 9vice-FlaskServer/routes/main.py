# Routes principales
# Import des libs python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from markupsafe import escape
from requester.request import Requester
from user.user import get_info, is_logged, is_locked, beutify_list
import markdown
from pygments.formatters.html import HtmlFormatter
import os

# Creation blueprint
main = Blueprint('main', __name__)
dbReq = Requester()


# Definition des routes
@main.route('/')
def index():
    formatter = HtmlFormatter(style="emacs", full=True, cssclass="codehilite")
    css_string = formatter.get_style_defs()
    readmeFile = open(os.getcwd() + "/README.md", 'r')
    mdTemplateString = markdown.markdown(readmeFile.read(), extensions=['markdown.extensions.fenced_code',
                                                                        'markdown.extensions.codehilite'])
    md_css_string = "<style>" + css_string + "</style>"
    md_template = md_css_string + mdTemplateString

    sessionCookie = request.cookies.get('user_session')
    if sessionCookie:
        loggedUserinfo = get_info(sessionCookie)
        if is_logged(loggedUserinfo) and not is_locked(loggedUserinfo):
            dbReq.update_con(loggedUserinfo['id'])
            return render_template('index.html', readmeContent=md_template, userLogged=loggedUserinfo)
    return render_template('index.html', readmeContent=md_template)


@main.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'GET':
        sessionCookie = request.cookies.get('user_session')
        if sessionCookie:
            loggedUserinfo = get_info(sessionCookie)
            if is_logged(loggedUserinfo) and not is_locked(loggedUserinfo):
                dbReq.update_con(loggedUserinfo['id'])
                return render_template('profile.html', userLogged=loggedUserinfo,
                                       deviceCount=dbReq.count_devices(loggedUserinfo.get('id')),
                                       userDevices=dbReq.list_devices(loggedUserinfo.get('id')))
        return redirect(url_for('auth.login'))
    else:
        sessionCookie = request.cookies.get('user_session')
        if sessionCookie:
            loggedUserinfo = get_info(sessionCookie)
            if is_logged(loggedUserinfo) and not is_locked(loggedUserinfo):
                dbReq.update_con(loggedUserinfo['id'])
                idToDel = int(request.form['delDeviceByID'])
                if dbReq.is_user_device(loggedUserinfo["id"], idToDel):
                    if dbReq.del_device(idToDel):
                        return render_template('profile.html', userLogged=loggedUserinfo,
                                               deviceCount=dbReq.count_devices(loggedUserinfo.get('id')),
                                               userDevices=dbReq.list_devices(loggedUserinfo.get('id')),
                                               success="Device supprime")
                    else:
                        return render_template('profile.html', userLogged=loggedUserinfo,
                                               deviceCount=dbReq.count_devices(loggedUserinfo.get('id')),
                                               userDevices=dbReq.list_devices(loggedUserinfo.get('id')),
                                               erreur="Le device n'a pas pu etre supprime")
                else:
                    return render_template('profile.html', userLogged=loggedUserinfo,
                                           deviceCount=dbReq.count_devices(loggedUserinfo.get('id')),
                                           userDevices=dbReq.list_devices(loggedUserinfo.get('id')),
                                           erreur="Le device ne semble pas vous appartenir")
        return redirect(url_for('auth.login'))


@main.route('/list')
def list():
    if request.method == 'GET':
        sessionCookie = request.cookies.get('user_session')
        if sessionCookie:
            loggedUserinfo = get_info(sessionCookie)
            if is_logged(loggedUserinfo) and not is_locked(loggedUserinfo):
                dbReq.update_con(loggedUserinfo['id'])
                return render_template('devicesList.html', userLogged=loggedUserinfo,
                                       userDevices=dbReq.list_devices(loggedUserinfo.get('id')))
        return redirect(url_for('auth.login'))


@main.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        sessionCookie = request.cookies.get('user_session')
        if sessionCookie:
            loggedUserinfo = get_info(sessionCookie)
            if is_logged(loggedUserinfo) and not is_locked(loggedUserinfo):
                dbReq.update_con(loggedUserinfo['id'])
                return render_template('addDevice.html', userLogged=loggedUserinfo)
        return redirect(url_for('auth.login'))
    else:
        sessionCookie = request.cookies.get('user_session')
        if sessionCookie:
            loggedUserinfo = get_info(sessionCookie)
            if is_logged(loggedUserinfo) and not is_locked(loggedUserinfo):
                dbReq.update_con(loggedUserinfo['id'])
                deviceName = escape(request.form.get('deviceName'))
                devicePubKey = escape(request.form.get('pubkey'))
                isFolderDevice = True if escape(request.form.get('isFolderDevice')) == "on" else False
                isAudioDevice = True if escape(request.form.get('isAudioDevice')) == "on" else False
                isVideoDevice = True if escape(request.form.get('isVideoDevice')) == "on" else False

                if not isFolderDevice and not isAudioDevice and not isVideoDevice:
                    return render_template('addDevice.html', erreur='Il faut sélectionner au moins un type de device', userLogged=loggedUserinfo)

                if deviceName == "":
                    return render_template('addDevice.html', erreur='Il faut mettre un nom pour son device', userLogged=loggedUserinfo)

                if devicePubKey == "":
                    return render_template('addDevice.html', erreur='Il faut renseigner une cle publique', userLogged=loggedUserinfo)

                if dbReq.insert_device(loggedUserinfo['id'], deviceName, isVideoDevice, isAudioDevice, isFolderDevice, devicePubKey):
                    return render_template('addDevice.html', success="Device ajoute", userLogged=loggedUserinfo)
                else:
                    return render_template('addDevice.html', erreur='Une erreur est survenue', userLogged=loggedUserinfo)
        return redirect(url_for('auth.login'))


@main.route('/adminPanel', methods=['GET', 'POST'])
def adminPanel():
    if request.method == 'GET':
        sessionCookie = request.cookies.get('user_session')
        if sessionCookie:
            loggedUserinfo = get_info(sessionCookie)
            if is_logged(loggedUserinfo) and loggedUserinfo['isAdmin']:
                dbReq.update_con(loggedUserinfo['id'])
                users = beutify_list(dbReq.list_users())
                if request.args.get('success'):
                    return render_template('adminPanel.html', userList=users, userLogged=loggedUserinfo, success="Mot de passe modifie avec succes")
                else:
                    return render_template('adminPanel.html', userList=users, userLogged=loggedUserinfo)
        return redirect(url_for('auth.login'))
    else:
        sessionCookie = request.cookies.get('user_session')
        if sessionCookie:
            loggedUserinfo = get_info(sessionCookie)

            if is_logged(loggedUserinfo) and loggedUserinfo['isAdmin']:
                dbReq.update_con(loggedUserinfo['id'])
                idToDel = None
                idToUnlock = None
                idToLock = None
                formDict = request.form.to_dict()
                if 'delUserByID' in formDict.keys():
                    idToDel = request.form['delUserByID']

                elif 'unlockUserByID' in formDict.keys():
                    idToUnlock = request.form['unlockUserByID']

                else:
                    idToLock = request.form['lockUserByID']

                if idToUnlock:
                    if dbReq.unlock_user(int(idToUnlock)):
                        users = beutify_list(dbReq.list_users())
                        return render_template('adminPanel.html', userList=users, success="Compte debloque",
                                               userLogged=loggedUserinfo)
                    else:
                        users = beutify_list(dbReq.list_users())
                        return render_template('adminPanel.html', userList=users,
                                               erreur="Le compte n'a pas pu etre debloque", userLogged=loggedUserinfo)
                elif idToLock:
                    if dbReq.lock_user(int(idToLock)):
                        users = beutify_list(dbReq.list_users())
                        return render_template('adminPanel.html', userList=users, success="Compte bloque",
                                               userLogged=loggedUserinfo)
                    else:
                        users = beutify_list(dbReq.list_users())
                        return render_template('adminPanel.html', userList=users,
                                               erreur="Le compte n'a pas pu etre bloque", userLogged=loggedUserinfo)
                elif idToDel:
                    if dbReq.del_user(int(idToDel)):
                        users = beutify_list(dbReq.list_users())
                        return render_template('adminPanel.html', userList=users, success="Utilisateur supprime",
                                               userLogged=loggedUserinfo)
                    else:
                        users = beutify_list(dbReq.list_users())
                        return render_template('adminPanel.html', userList=users,
                                               erreur="L'utilisateur n'a pas pu etre supprime", userLogged=loggedUserinfo)
                else:
                    users = beutify_list(dbReq.list_users())
                    return render_template('adminPanel.html', userList=users,
                                           erreur="500 Internal Server Error", userLogged=loggedUserinfo)
        else:
            return redirect(url_for('auth.login'))


