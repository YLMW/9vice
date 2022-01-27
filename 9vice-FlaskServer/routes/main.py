# Routes principales
# Import des libs python
from flask import Blueprint, render_template, request
from markupsafe import escape
import markdown
from pygments.formatters import HtmlFormatter

# Creation blueprint
main = Blueprint('main', __name__)


# Definition des routes
@main.route('/')
def index():
    formatter = HtmlFormatter(style="emacs", full=True, cssclass="codehilite")
    css_string = formatter.get_style_defs()
    readmeFile = open("README.md", 'r')
    mdTemplateString = markdown.markdown(readmeFile.read(), extensions=['markdown.extensions.fenced_code',
                                                                        'markdown.extensions.codehilite'])
    md_css_string = "<style>" + css_string + "</style>"
    md_template = md_css_string + mdTemplateString
    return render_template('index.html', readmeContent=md_template)


@main.route('/profile')
def profile():
    return render_template('profile.html')


@main.route('/list')
def list():
    device = {
        'title': '',
        'subtitle': '',
        'content': '',
        'status': ''
    }
    return render_template('devicesList.html', device=device)


@main.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('addDevice.html')
    else:
        deviceName = escape(request.form.get('deviceName'))
        deviceIp = escape(request.form.get('deviceIp'))
        isFolderDevice = True if escape(request.form.get('isFolderDevice')) == "on" else False
        isAudioDevice = True if escape(request.form.get('isAudioDevice')) == "on" else False
        isVideoDevice = True if escape(request.form.get('isVideoDevice')) == "on" else False

        if not isFolderDevice and not isAudioDevice and not isVideoDevice:
            return render_template('addDevice.html', erreur='Il faut sélectionner au moins un type de device')

        # TODO -> remove cette feature de dev
        allData = 'Name: ' + deviceName + ' / Ip: ' + deviceIp + ' / Folder: ' + str(isFolderDevice) + \
                  ' / Audio: ' + str(isAudioDevice) + ' / Video: ' + str(isVideoDevice)

        return render_template('addDevice.html', erreur=allData)
