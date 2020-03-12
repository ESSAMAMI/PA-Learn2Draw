from flask import Flask, render_template
import socket
from utils import utils

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("login.html", current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("login.html", error=e)

@app.route('/user-profil', methods=['POST'])
def user_profil():
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("home.html", current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("home.html", error=e)
if __name__ == '__main__':

    hostname = socket.gethostname()
    app.run(debug=True, host=socket.gethostbyname(hostname), port=9893)
