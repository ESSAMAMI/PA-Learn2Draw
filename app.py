from flask import Flask, render_template, redirect, url_for, request, session
import socket
from utils import utils, request_bdd
from models import cnn
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# basic access routes
@app.route('/', methods=['GET', 'POST'])
def home(token=None):
    try:
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("landing.html", token=token, current_year=current_year)

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
            
            # redirect to admin is username == admin, temprary method
            if username == "admin":
                return redirect(url_for('admin_home', token=token), code=307)
            if user.empty:
                error_connection = True
                return render_template('login.html', error_connection=error_connection, token=token)
            else:
                session['username'] = str(user.username[0])
                session['email'] = str(user.email[0])
                session['pwd'] = str(user.pwd[0])
                session['score'] = str(user.score[0])
                return redirect(url_for('home', token=token), code=307)
                #return redirect(url_for('user_profil', token=token), code=307)

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
            # handle permission later if possible
            return render_template("profile.html", current_year=current_year)
            #return render_template("common/permission.html")

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

@app.route('/play/', methods=['GET'])
def play():
    current_prediction = request.args.get('current_prediction')
    print("current prediction = ", current_prediction)
    
    if current_prediction:
        current_prediction = current_prediction.split(";")
        current_prediction[1] = str(int(round(float(current_prediction[1]),2)*100))
        token = None
        play = True
        return render_template("play.html", token=None, play=play, current_prediction=current_prediction[1], current_prediction_label=current_prediction[0])
    token = None
    play = True
    return render_template("play.html", token=None, play=play)


@app.route('/score/', methods=['GET', 'POST'])
def score():
    try:
        list_drawings = request_bdd.learn2draw_list_draw_to_score('arnaud_lasticotier')
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("score.html", current_year=current_year, list_drawings=list_drawings)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("score.html", error=e)

# route to insert new score in bdd
@app.route('/scoring/', methods=['GET', 'POST'])
def score_image():
    if request.method == 'POST':
        token = request.args['token']
        infos = request.args['infos']
        btn = request.form['button']
        print("\nbtn : ", btn)
        result = request_bdd.learn2draw_insert_score('user1', infos, btn)
        return redirect(url_for('score', token=token), code=307)

#routes for backend access
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

@app.route('/admin-home/tables/drawings', methods=['GET', 'POST'])
def drawings():
    try:
        query_result = request.args.get('query_result')
        drawings_infos = request_bdd.learn2draw_list_all_drawings()
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("admin_drawings.html", current_year=current_year, drawings_infos=drawings_infos, query_result=query_result)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_drawings.html", error=e)

@app.route('/admin-home/tables/categories', methods=['GET', 'POST'])
def categories():
    try:
        query_result = request.args.get('query_result')
        categories_infos = request_bdd.learn2draw_list_all_categories()
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("admin_categories.html", current_year=current_year, categories_infos=categories_infos, query_result=query_result)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_categories.html", error=e)

@app.route('/admin-home/tables/notations', methods=['GET', 'POST'])
def notations():
    try:
        query_result = request.args.get('query_result')
        notations_infos = request_bdd.learn2draw_list_all_notations()
        print("notations_infos : ", notations_infos)
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("admin_notations.html", current_year=current_year, notations_infos=notations_infos, query_result=query_result)

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
# user operations
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


# drawing operations
@app.route('/adding_drawing/', methods=['GET', 'POST'])
def create_drawing():
    try:
        #token = request.args['token']
        # infos = request.args['infos']
        # btn = request.form['button']
        print("WELCOME IN ADD DRAWING FUNC")

        new_user_id = request.form['user_id_input']
        new_category_id = request.form['category_id_input']
        new_location = "\\static\\assets\\images\\test\\plot.png"
        new_status = 0
        new_score = request.form['score_input']
        new_time = request.form['time_input']
        # new_score = request.form['score_input']
        # print("infos : ", infos)
        # print("\nbtn : ", btn)
        print("\nuser_id : ", new_user_id)
        print("\ncategory_id : ", new_category_id)
        print("\nlocation : ", new_location)
        print("\nstatus : ", new_status)
        print("\nscore : ", new_score)
        print("\ntime : ", new_time)

        query_result = request_bdd.learn2draw_create_drawing(new_user_id, new_category_id, new_location, new_status, new_score, new_time)
        
        print("GOOD ROUTE")
        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('drawings'), code=307)
        else:
            return redirect(url_for('drawings', query_result=query_result), code=307)

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_users.html", error=e)

@app.route('/updating_drawing/', methods=['GET', 'POST'])
def crud_drawing():
    try:
        #token = request.args['token']
        infos = request.args['infos']
        btn = request.form['button']
        new_user_id = request.form['user_id_input']
        new_category_id = request.form['category_id_input']
        new_location = "\\static\\assets\\images\\test\\plot.png"
        new_status = request.form['status_input'] 
        new_score = request.form['score_input']
        new_time = request.form['time_input']
        print("infos : ", infos)
        print("\nbtn : ", btn)
        print("\nuser_id : ", new_user_id)
        print("\ncategory_id : ", new_category_id)
        print("\nlocation : ", new_location)
        print("\nstatus : ", new_status)
        print("\nscore : ", new_score)
        print("\ntime : ", new_time)

        query_result = request_bdd.learn2draw_update_drawing(infos, new_user_id, new_category_id, new_location, new_status, new_score, new_time)

        print("GOOD ROUTE")
        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('drawings'), code=307)
        else:
            return redirect(url_for('drawings', query_result=query_result), code=307)

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_users.html", error=e)

@app.route('/delete_drawing/', methods=['GET', 'POST'])
def delete_drawing():
    try:
        #token = request.args['token']
        infos = request.args['infos']
        # btn = request.form['button']
        print("WELCOME IN DELETE DRAWING FUNC")

        query_result = request_bdd.learn2draw_delete_drawing(infos)

        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('drawings'), code=307)
        else:
            return redirect(url_for('drawings', query_result=query_result), code=307)
        

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_drawings.html", error=e)

# Operations for categories
@app.route('/adding_category/', methods=['GET', 'POST'])
def create_category():
    try:
        #token = request.args['token']
        # infos = request.args['infos']
        # btn = request.form['button']
        print("WELCOME IN ADD CATEGORY FUNC")

        new_category = request.form['category_input']
        # new_score = request.form['score_input']
        # print("infos : ", infos)
        # print("\nbtn : ", btn)
        print("\ncategory : ", new_category)

        query_result = request_bdd.learn2draw_create_category(new_category)
        
        print("GOOD ROUTE")
        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('categories'), code=307)
        else:
            return redirect(url_for('categories', query_result=query_result), code=307)

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_categories.html", error=e)

@app.route('/updating_category/', methods=['GET', 'POST'])
def crud_categories():
    try:
        #token = request.args['token']
        infos = request.args['infos']
        btn = request.form['button']
        new_category = request.form['category_input']
        print("infos : ", infos)
        print("\nbtn : ", btn)
        print("\ncategory : ", new_category)
        query_result = request_bdd.learn2draw_update_category(infos, new_category)

        print("GOOD ROUTE")
        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('categories'), code=307)
        else:
            return redirect(url_for('categories', query_result=query_result), code=307)

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_categories.html", error=e)

@app.route('/delete_category/', methods=['GET', 'POST'])
def delete_category():
    try:
        #token = request.args['token']
        infos = request.args['infos']
        # btn = request.form['button']
        print("WELCOME IN DELETE CATEGORY FUNC")

        query_result = request_bdd.learn2draw_delete_category(infos)

        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('categories'), code=307)
        else:
            return redirect(url_for('categories', query_result=query_result), code=307)
        

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_categories.html", error=e)


# notation operations
@app.route('/adding_notation/', methods=['GET', 'POST'])
def create_notation():
    try:
        #token = request.args['token']
        # infos = request.args['infos']
        # btn = request.form['button']
        print("WELCOME IN ADD DRAWING FUNC")

        new_score = request.form['score_input']
        new_user_id = request.form['user_id_input']
        new_drawing_id = request.form['drawing_id_input']
        new_drawing_user_id = request.form['drawing_user_id_input']
        new_drawing_category_id = request.form['drawing_category_id_input']
        
        # new_score = request.form['score_input']
        # print("infos : ", infos)
        # print("\nbtn : ", btn)
        print("\nscore : ", new_score)
        print("\nuser_id : ", new_user_id)
        print("\ndrawing_id : ", new_drawing_id)
        print("\new_drawing_user_id : ", new_drawing_user_id)
        print("\new_drawing_category_id : ", new_drawing_category_id)

        query_result = request_bdd.learn2draw_create_notation(new_score, new_user_id, new_drawing_id, new_drawing_user_id, new_drawing_category_id)
        
        print("GOOD ROUTE")
        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('notations'), code=307)
        else:
            return redirect(url_for('notations', query_result=query_result), code=307)

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_notations.html", error=e)

@app.route('/updating_notation/', methods=['GET', 'POST'])
def crud_notation():
    try:
        #token = request.args['token']
        infos = request.args['infos']
        btn = request.form['button']
        new_score = request.form['score_input']
        new_user_id = request.form['user_id_input']
        new_drawing_id = request.form['drawing_id_input']
        new_drawing_user_id = request.form['drawing_user_id_input']
        new_drawing_category_id = request.form['drawing_category_id_input']
        
        print("infos : ", infos)
        print("\nbtn : ", btn)
        print("\nscore : ", new_score)
        print("\nuser_id : ", new_user_id)
        print("\ndrawing_id : ", new_drawing_id)
        print("\new_drawing_user_id : ", new_drawing_user_id)
        print("\new_drawing_category_id : ", new_drawing_category_id)

        query_result = request_bdd.learn2draw_update_notation(infos, new_score, new_user_id, new_drawing_id, new_drawing_user_id, new_drawing_category_id)

        print("GOOD ROUTE")
        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('notations'), code=307)
        else:
            return redirect(url_for('notations', query_result=query_result), code=307)

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_notations.html", error=e)

@app.route('/delete_notation/', methods=['GET', 'POST'])
def delete_notation():
    try:
        #token = request.args['token']
        infos = request.args['infos']
        # btn = request.form['button']
        print("WELCOME IN DELETE NOTATION FUNC")

        query_result = request_bdd.learn2draw_delete_notation(infos)

        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('notations'), code=307)
        else:
            return redirect(url_for('notations', query_result=query_result), code=307)
        

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_notations.html", error=e)



# routes for drawings actions and everything linked to it, here get file + prediction
@app.route('/play/get_drawing/', methods=['POST', 'GET'])
def get_drawing(token=None):
    if request.method == 'POST':
        image_base_64 = request.form['drawing']
        category = request.form['category_drawing']

        check_is = utils.decode_uploaded_file(image_base_64, category)

        prediction = cnn.get_predict_sample_cnn_baseball_broom_dolphin(check_is, category)

        current_prediction = str(prediction)
        return redirect(url_for('play', current_prediction=current_prediction, code=307))
        #return "image name : " + str(check_is) + " | " + prediction

    return redirect(url_for('url_not_found'))

# Handle errors section
@app.errorhandler(404)
@app.route('/url_not_found/', methods=['GET'])
def url_not_found(e):

    return render_template("common/error.html")

if __name__ == '__main__':

    hostname = socket.gethostname()
    app.run(debug=True, host=socket.gethostbyname(hostname), port=9893)

