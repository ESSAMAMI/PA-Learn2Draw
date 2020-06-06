from flask import Flask, render_template, redirect, url_for, request, session
import socket
from utils import utils, request_bdd
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/', methods=['GET','POST'])
def home():
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("landing.html", current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("landing.html", error=e)

@app.route('/connection', methods=['GET'])
def connection_page():
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        token = utils.generate_token()
        return render_template("login.html", token=token, current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("login.html", error=e)

@app.route('/connection/token/<token>', methods=['POST', 'GET'])
def connection(token):
    try:

        if request.method == 'POST':

            username = request.form['username']
            pwd = request.form['pwd']
            user = request_bdd.learn2draw_connect(username, pwd)
            if user.empty:
                error_connection = True
                return render_template('login.html', error_connection=error_connection, token=token)
            else:
                session['username'] = str(user.username[0])
                session['email'] = str(user.email[0])
                session['pwd'] = str(user.pwd[0])
                session['score'] = str(user.score[0])
                return redirect(url_for('home', token=token), code=307)

        return render_template('common/permission.html')

    except Exception as e:
        print(e, "====================================================")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("login.html", error=e, token=token)

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

@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    try:

        if request.method == 'POST':

            username = str(request.form['username'])
            email = str(request.form['email'])
            pwd = str(request.form['pwd'])
            cnf_pwd = str(request.form['cnf_pwd'])

            # check if the username / email is already used
            verif = request_bdd.learn2draw_sign_up_verif(username, email, pwd)
            if verif == False:
                error_user_already_created = True
                return render_template('login.html', error_user_already_created=error_user_already_created)
            if pwd != cnf_pwd:

                error_identical_pwd = True
                return render_template('login.html', error_identical_pwd=error_identical_pwd)

            new_account = request_bdd.learn2draw_sign_up(username, email, pwd)
            return render_template('login.html', new_account=new_account, token=utils.generate_token())

        return render_template("common/permission.html")

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("score.html", error=e)

@app.route('/explain/', methods=['GET', 'POST'])
def explain():
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("explain.html", current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("explain.html", error=e)

@app.route('/score/', methods=['GET', 'POST'])
def score():
    try:
        list_drawings = request_bdd.learn2draw_list_draw_to_score('arnaud_lasticotier')
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("score.html", current_year=current_year, list_drawings=list_drawings)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("score.html", error=e)

@app.route('/scoring/', methods=['GET', 'POST'])
def score_image():
    if request.method == 'POST':
        token = request.args['token']
        infos = request.args['infos']
        btn = request.form['button']
        print("\nbtn : ", btn)
        result = request_bdd.learn2draw_insert_score('user1', infos, btn)
        return redirect(url_for('score', token=token), code=307)


#routes for backend after this comment ==> access to pages
@app.route('/admin-home/', methods=['POST', 'GET'])
def admin_home():
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        if request.method == 'POST':
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

@app.route('/admin-home/tables/users/', methods=['GET', 'POST'])
def users():
    try:
        query_result = request.args.get('query_result')
        users_infos = request_bdd.learn2draw_list_all_users()
        current_year = utils.get_ccurent_date(format="ang", full=False)
        #query_result = ""
        print("query_result :", query_result)
        return render_template("admin_users.html", current_year=current_year, users_infos=users_infos, query_result=query_result)

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


# Routes for CRUD Operations in Backend
@app.route('/adding_user/', methods=['GET', 'POST'])
def create_user():
    try:
        #token = request.args['token']
        # infos = request.args['infos']
        # btn = request.form['button']
        print("WELCOME IN ADD USER FUNC")

        new_username = request.form['username_input']
        new_email = request.form['email_input']
        new_password = request.form['password_input']
        new_confirm_password = request.form['confirm_password_input']
        # new_score = request.form['score_input']
        # print("infos : ", infos)
        # print("\nbtn : ", btn)
        print("\nusername : ", new_username)
        print("\nemail : ", new_email)
        print("\npassword : ", new_password)
        print("\nconfirm password : ", new_confirm_password)

        query_result = request_bdd.learn2draw_create_user(new_username, new_email, new_password, new_confirm_password)
        
        print("GOOD ROUTE")
        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('users'), code=307)
        else:
            return redirect(url_for('users', query_result=query_result), code=307)

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_users.html", error=e)

@app.route('/updating_username/', methods=['GET', 'POST'])
def crud_users():
    try:
        #token = request.args['token']
        infos = request.args['infos']
        btn = request.form['button']
        new_username = request.form['username_input']
        new_email = request.form['email_input']
        new_score = request.form['score_input']
        print("infos : ", infos)
        print("\nbtn : ", btn)
        print("\nusername : ", new_username)
        print("\nemail : ", new_email)
        print("\nscore : ", new_score)
        query_result = request_bdd.learn2draw_update_user(infos, new_username, new_email, new_score)

        print("GOOD ROUTE")
        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('users'), code=307)
        else:
            return redirect(url_for('users', query_result=query_result), code=307)

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_users.html", error=e)

@app.route('/delete_user/', methods=['GET', 'POST'])
def delete_user():
    try:
        #token = request.args['token']
        infos = request.args['infos']
        # btn = request.form['button']
        print("WELCOME IN DELETE USER FUNC")

        query_result = request_bdd.learn2draw_delete_user(infos)

        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('users'), code=307)
        else:
            return redirect(url_for('users', query_result=query_result), code=307)
        

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_users.html", error=e)


# Handle errors section
@app.errorhandler(404)
def url_not_found(e):

    return render_template("common/error.html")

if __name__ == '__main__':

    hostname = socket.gethostname()
    app.run(debug=True, host=socket.gethostbyname(hostname), port=9893)

