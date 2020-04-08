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

@app.route('/explain', methods=['GET'])
def explain(token=None):
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("explain.html", token=token, current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("explain.html", error=e)

@app.route('/score', methods=['GET'])
def score(token=utils.generate_token()):
    try:
        if(token==None):
            current_date = utils.get_ccurent_date(format="fr")
            return render_template("common/error.html")
        else:
            current_year = utils.get_ccurent_date(format="ang", full=False)
            return render_template("score.html", token=token, current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("score.html", error=e)


#routes for backend after this comment
@app.route('/admin-home/', methods=['POST', 'GET'])
def admin_home():
    try:
        if request.method == 'POST':
            current_year = utils.get_ccurent_date(format="ang", full=False)
            return render_template("admin_home.html", current_year=current_year)
            #this is for classic user, we want to be redirected to admin for now
            #return render_template("home.html", current_year=current_year)

        elif request.method == 'GET':
            #get temporaly used to debug
            return render_template("admin_home.html", current_year=current_year)
            #return render_template("common/permission.html")

        else:
            e = "something went wrong"
            return redirect(url_for('url_not_found'))

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        #tempo redirect to admin_home
        return render_template("admin_home.html", error=e)   
        #return render_template("home.html", error=e)


@app.route('/admin-home/tables/users', methods=['GET'])
def users():
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("admin_users.html", current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_users.html", error=e)

@app.route('/admin-home/tables/drawings', methods=['GET'])
def drawings():
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("admin_drawings.html", current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_drawings.html", error=e)

@app.route('/admin-home/tables/categories', methods=['GET'])
def categories():
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("admin_categories.html", current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_categories.html", error=e)


@app.route('/admin-home/tables/notations', methods=['GET'])
def notations():
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("admin_notations.html", current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_notations.html", error=e)

@app.route('/admin-models/', methods=['GET'])
def admin_models(token=None):
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("admin_models.html", token=token, current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_models.html", error=e)

# Handle errors section
@app.errorhandler(404)
def url_not_found(e):

    return render_template("common/error.html")

if __name__ == '__main__':

    hostname = socket.gethostname()
    app.run(debug=True, host=socket.gethostbyname(hostname), port=9893)

