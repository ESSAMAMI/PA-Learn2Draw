from flask import Flask, render_template, redirect, url_for, request
import socket
from utils import utils
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home(token=None):
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("index.html", token=token, current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("index.html", error=e)

@app.route('/connection', methods=['GET'])
def connection_page():
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        token = utils.generate_token()
        return render_template("login.html", token=token, current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("login.html", error=e)


@app.route('/connection/token/<token>', methods=['POST'])
def connection(token):
    try:
        return redirect(url_for('user_profil', token=token), code=307)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("login.html", error=e)


@app.route('/user-profil/', methods=['POST', 'GET'])
def user_profil():
    try:
        if request.method == 'POST':
            current_year = utils.get_ccurent_date(format="ang", full=False)
            return render_template("home.html", current_year=current_year)

        elif request.method == 'GET':
            return render_template("common/permission.html")

        else:
            e = "something went wrong"
            return redirect(url_for('url_not_found'))

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("home.html", error=e)


@app.errorhandler(404)
def url_not_found(e):

    return render_template("common/error.html")

if __name__ == '__main__':

    hostname = socket.gethostname()
    app.run(debug=True, host=socket.gethostbyname(hostname), port=9893)
