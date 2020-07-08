from flask import Flask, render_template, redirect, url_for, request, session
import socket
from utils import utils, request_bdd
from models import my_models
import os
from random import shuffle
import shutil

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
                session['id'] = str(user.id[0])
                count_notation = request_bdd.count_notation_bu_user(user.id[0])
                session['count_notation'] = None
                if not count_notation['count_notation'].empty:
                    session['count_notation'] = str(count_notation['count_notation'][0])

                current_year = utils.get_ccurent_date(format="ang", full=False)
                top_5 = request_bdd.select_top_5()
                random_stat = ['En ligne', 'Hors ligne']

                return render_template("user_app/home_user_app.html", token=token, random_stat=random_stat, current_year=current_year, top_5=top_5, count_notation=count_notation)

        return render_template('common/permission.html')

    except Exception as e:
        print(e, "====================================================")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("login.html", error=e, token=token)

@app.route('/profile/token/<token>', methods=['GET', 'POST'])
def profile_page(token):
    try:

        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("user_app/profile_user_app.html", token=token, current_year=current_year)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template('common/permission.html', e=e)

@app.route('/notation/token/<token>', methods=['GET', 'POST'])
def notation_page(token):
    try:
        all_drawings = []
        list_folder = os.listdir('static/doodle/')
        for folder in list_folder:
            list_opend_folder = os.listdir('static/doodle/'+folder)
            for drawing in list_opend_folder:
                all_drawings.append('doodle/' + folder + '/' + drawing)

        shuffle(all_drawings)
        drawings_to_notate = all_drawings[0:12]
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("user_app/notation_user_app.html", token=token, current_year=current_year, drawings_to_notate = drawings_to_notate)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template('common/permission.html', e=e)

@app.route('/global/token/<token>', methods=['GET', 'POST'])
def global_page(token):
    try:

        count_notation = request_bdd.count_notation_bu_user(session['id'])
        session['count_notation'] = None
        if not count_notation['count_notation'].empty:
            session['count_notation'] = str(count_notation['count_notation'][0])

        current_year = utils.get_ccurent_date(format="ang", full=False)
        top_5 = request_bdd.select_top_5()
        random_stat = ['En ligne', 'Hors ligne']

        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("user_app/home_user_app.html", token=token, random_stat=random_stat, current_year=current_year, top_5=top_5, count_notation=count_notation)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template('common/permission.html', e=e)

@app.route('/game/token/<token>', methods=['GET', 'POST'])
def game_page(token):
    try:

        count_notation = request_bdd.count_notation_bu_user(session['id'])
        session['count_notation'] = None
        if not count_notation['count_notation'].empty:
            session['count_notation'] = str(count_notation['count_notation'][0])

        current_year = utils.get_ccurent_date(format="ang", full=False)
        top_5 = request_bdd.select_top_5()
        random_stat = ['En ligne', 'Hors ligne']

        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("user_app/game_user_app.html", token=token, random_stat=random_stat, current_year=current_year, top_5=top_5, count_notation=count_notation)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template('common/permission.html', e=e)

@app.route('/user-profil/', methods=['POST', 'GET'])
def user_profil():
    try:
        if request.method == 'POST':
            current_year = utils.get_ccurent_date(format="ang", full=False)
            return render_template("user_app/home_user_app.html", current_year=current_year)

        elif request.method == 'GET':
            # handle permission later if possible
            #return render_template("home.html", current_year=current_year)
            return render_template("common/permission.html")

        else:
            e = "something went wrong"
            return redirect(url_for('url_not_found'))

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("home.html", error=e)

@app.route('/sign-out', methods=['POST', 'GET'])
def sign_out():

    try:
        if request.method == "POST":
            session.clear()
            return render_template("login.html")
        else:
            return render_template("common/permission.html")
    except Exception as e:
        return render_template("login.html")


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

    good_prediction = request.args.get('good_prediction')
    print("good prediction = ", good_prediction)
    
    # get all predictable categories, first get current model name, then categories
    cwd = os.getcwd()
    current_model = [f for f in os.listdir(cwd+"/models/") if f.endswith('.h5') and "current" in f and "default" not in f]
    print("current_model = ", current_model)
    if current_model == []:
        current_model = "default.h5"
    else:
        current_model = str(current_model).strip("['']")[8:]
    print("current_model = ", current_model)

    categories = request_bdd.learn2draw_get_categories_handled_for_one_model(current_model.replace(".h5", ""))
    print("categories handled : ", categories)
    #learn2draw_get_categories_handled_for_one_model(model_name)


    if current_prediction:
        current_prediction = current_prediction.split(";")
        current_prediction[1] = str(int(round(float(current_prediction[1]),2)*100))
        token = None
        play = True
        #print("current predi 2 ", current_prediction[2])
        print("current predict length ", len(current_prediction))
        if  good_prediction == "" :
            return render_template("play.html", token=None, play=play, current_prediction=current_prediction[1], current_prediction_label=current_prediction[0], categories=categories+","+current_model)
        else :
            print("\nBAD PREDICT GO\n")
            return render_template("play.html", token=None, play=play, current_prediction=current_prediction[1], current_prediction_label=current_prediction[0], good_prediction=good_prediction, categories=categories+","+current_model)
    token = None
    play = True
    categories = None
    if categories == None:
        return render_template("common/permission.html", token=None, error_code=220, error_handled = "No categories selected for current model...")

    return render_template("play.html", token=None, play=play, categories=categories+","+current_model)


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
        result = request_bdd.learn2draw_insert_score('arnaud_lasticotier', infos, btn)
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
        print("cat info : ", categories_infos)
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

@app.route('/admin-models/', methods=['GET', 'POST'])
def admin_models(token=None):
    try:
        query_result = request.args.get('query_result')
        models_infos = request_bdd.learn2draw_list_all_models()
        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("admin_models.html", token=token, current_year=current_year, models_infos=models_infos, query_result=query_result)

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
            return redirect(render_template('users'), code=307)
        else:
            return redirect(render_template('users', query_result=query_result), code=307)

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
        new_category_predicted_id = request.form['category_predicted_id_input']
        new_location = "\\static\\assets\\images\\test\\plot.png"
        new_status = 0
        new_score = request.form['score_input']
        new_time = request.form['time_input']
        # new_score = request.form['score_input']
        # print("infos : ", infos)
        # print("\nbtn : ", btn)
        print("\nuser_id : ", new_user_id)
        print("\ncategory_id : ", new_category_id)
        print("\ncategory_id predicted_: ", new_category_predicted_id)
        print("\nlocation : ", new_location)
        print("\nstatus : ", new_status)
        print("\nscore : ", new_score)
        print("\ntime : ", new_time)

        query_result = request_bdd.learn2draw_create_drawing(new_user_id, new_category_id, new_category_predicted_id, new_location, new_status, new_score, new_time)
        
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
        new_category_predicted_id = request.form['category_predicted_id_input']
        new_location = "\\static\\assets\\images\\test\\plot.png"
        new_status = request.form['status_input'] 
        new_score = request.form['score_input']
        new_time = request.form['time_input']
        print("infos : ", infos)
        print("\nbtn : ", btn)
        print("\nuser_id : ", new_user_id)
        print("\ncategory_id : ", new_category_id)
        print("\ncategory_predicted_id : ", new_category_predicted_id)
        print("\nlocation : ", new_location)
        print("\nstatus : ", new_status)
        print("\nscore : ", new_score)
        print("\ntime : ", new_time)

        query_result = request_bdd.learn2draw_update_drawing(infos, new_user_id, new_category_id, new_category_predicted_id, new_location, new_status, new_score, new_time)

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

# models operations
@app.route('/adding_model/', methods=['POST'])
def create_model():
    try:
        #token = request.args['token']
        # infos = request.args['infos']
        # btn = request.form['button']
        print("WELCOME IN ADD MODEL FUNC")
        model_type = request.form['model_type']
        new_inputName = request.form['inputName']
        new_inputEpochs = request.form['inputEpochs']
        new_inputBatchSize = request.form['inputBatchSize']
        new_optimizer = request.form['inputOptimizer']
        new_learning_rate = request.form['inputLearningRate']
        # new_score = request.form['score_input']
        # print("infos : ", infos)
        # print("\nbtn : ", btn)
        print("\nmodelType = ", model_type)
        print("\ninputName : ", new_inputName)
        print("\ninputEpochs : ", new_inputEpochs)
        print("\ninputBatchSize : ", new_inputBatchSize)
        print("\ninputOptimizer :", new_optimizer)
        print("\ninputLearningRate :", new_learning_rate)

        # create basic model, 1st try = create the whole model and insert in database
        # In the future I think we should use Celery to run this task in background
        query_result = request_bdd.learn2draw_create_model(model_type, new_inputName, new_inputEpochs, new_inputBatchSize, new_optimizer, new_learning_rate, "no")

        print("GOOD ROUTE")
        if "True" in query_result or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('admin_models'), code=307)
        else:
            return redirect(url_for('admin_models', query_result=query_result), code=307)

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("admin_users.html", error=e)

# change current model
@app.route('/change_current_model/', methods=['POST'])
def change_current():
    try:
        #token = request.args['token']
        # infos = request.args['infos']
        # btn = request.form['button']
        print("WELCOME IN CHANGE CURRENT FUNC")

        # get model name
        model_name = request.form['the_model_name']
        query_result = request_bdd.change_current_model(model_name)
        # print("model_name : ", model_name)
        # # check if .h5 file exist
        # h5_model = os.path.exists("static/models/"+model_name+"/"+model_name+".h5");
        # if h5_model == False:
        #     return "Problem ! The model doesn't exist"

        # # transfrom current in default model (if it exists)
        # current_model = [f for f in os.listdir("models/") if f.endswith('.h5') and "current" in f]
        # print("current_model = ", current_model)
        # if current_model != []:
        #     # rename old model (will become new default model)
        #     print("current model 0 ", current_model[0])
        #     os.rename("models/"+current_model[0], "models/defaul_model.h5")
        #     # copy h5 model in the right folder and rename it to "current_modelName"
        #     shutil.copy2("static/models/"+model_name+"/"+model_name+".h5", "models/current_"+model_name+".h5")
        #     # delete default file and rename defaul to default (now it"s secure because predictions have a usable model)
        #     os.remove("models/default_model.h5")
        #     os.rename("models/defaul_model.h5", "models/default_model.h5")
        # else:
        #     # only need to copy the model and rename it
        #     shutil.copy2("static/models/"+model_name+"/"+model_name+".h5", "models/current_"+model_name+".h5")
        

        #query_result = "True"#request_bdd.learn2draw_create_model(model_type, new_inputName, new_inputEpochs, new_inputBatchSize)
        
        print("GOOD ROUTE")
        if "True" in query_result or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('admin_models'), code=307)
        else:
            return redirect(url_for('admin_models', query_result=query_result), code=307)

    except Exception as e:
        print("ECHEC")
        query_result = "Error " + str(e)
        return redirect(url_for('admin_models', query_result=query_result), code=307)

# delete model
@app.route('/delete_model/', methods=['POST'])
def delete_model():
    try:
        #token = request.args['token']
        model_name = request.form['the_model_name2']
        # btn = request.form['button']
        print("WELCOME IN DELETE MODEL FUNC")
        print("model_name = ", model_name)

        query_result = request_bdd.learn2draw_delete_model(model_name)

        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('admin_models'), code=307)
        else:
            return redirect(url_for('admin_models', query_result=query_result), code=307)
        

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return redirect(url_for('admin_models', query_result=str(e)), code=307)


# update model (method delete old + create new)
@app.route('/update_model/', methods=['POST'])
def update_model():
    try:
        #token = request.args['token']
        #model_name = request.form['the_model_name2']
        # btn = request.form['button']
        print("WELCOME IN UPDATE MODEL FUNC")
        model_type = request.form['modelTypeSend']
        new_inputName = request.form['inputName2Send']
        new_inputEpochs = request.form['inputEpochs2']
        new_inputBatchSize = request.form['inputBatchSize2']
        new_optimizer = request.form['inputOptimizer2']
        new_learning_rate = request.form['inputLearningRate2']
        # new_score = request.form['score_input']
        # print("infos : ", infos)
        # print("\nbtn : ", btn)
        print("\nmodelType = ", model_type)
        print("\ninputName : ", new_inputName)
        print("\ninputEpochs : ", new_inputEpochs)
        print("\ninputBatchSize : ", new_inputBatchSize)
        print("\ninputOptimizer :", new_optimizer)
        print("\ninputLearningRate :", new_learning_rate)
        #print("model_name = ", model_name)

        query_result = request_bdd.learn2draw_update_model(model_type, new_inputName, new_inputEpochs, new_inputBatchSize, new_optimizer, new_learning_rate, "no")

        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('admin_models'), code=307)
        else:
            return redirect(url_for('admin_models', query_result=query_result), code=307)
        

    except Exception as e:
        print("ECHEC")
        current_date = utils.get_ccurent_date(format="fr")
        return redirect(url_for('admin_models', query_result=str(e)), code=307)

# routes for drawings actions and everything linked to it, here get file + prediction
@app.route('/play/get_drawing/', methods=['POST', 'GET'])
def get_drawing(token=None):
    if request.method == 'POST':
        user_time = request.form['input_time']
        image_base_64 = request.form['drawing']
        category = request.form['category_drawing']
        model_name = request.form["model_name"]

        print("\n\ntime input : ", user_time, "\n")
        print("model_name = ", model_name)
        print("category = ", category)



        check_is = utils.decode_uploaded_file(image_base_64, category)
        print("check is ", check_is)
        check_is_for_bdd_insert = "\\"+check_is.replace("/", "\\")
        print("check_is_for_bdd_insert ", check_is_for_bdd_insert)

        prediction = my_models.get_predict_sample_cnn_baseball_broom_dolphin(check_is, category, model_name.replace(".h5", ""))

        current_prediction = str(prediction)
        print("current prediction in app.py : ", current_prediction)

        # get category id of category selected by user and category predicted
        id_category = request_bdd.get_category_id(category)
        id_category_predicted = request_bdd.get_category_id(current_prediction.split(";")[0])

        print("id catego = ", id_category, " id catego predicted = ", id_category_predicted)

        # save drawing into database, for the test it's always user 2 
        create_drawing = request_bdd.learn2draw_create_drawing("2", id_category, id_category_predicted, check_is_for_bdd_insert, "0", str(round(float(current_prediction.split(";")[1])*100)), "0", user_time)
        print("create drawing ? ==> ", create_drawing)
        # add little message to add info on the veracity of the prediction
        if current_prediction.split(";")[0] == category:
            #current_prediction += ";yes"
            return redirect(url_for('play', current_prediction=current_prediction, code=307))
        else:
            good_prediction = category
            print("current predict = ", current_prediction)
            return redirect(url_for('play', current_prediction=current_prediction, good_prediction=good_prediction, code=307))

        # print("current predict = ", current_prediction)
        # return redirect(url_for('play', current_prediction=current_prediction, code=307))
        #return "image name : " + str(check_is) + " | " + prediction

    return redirect(url_for('url_not_found'))

@app.route('/play/get_drawing_session/<token>', methods=['POST', 'GET'])
def get_drawing_session(token):

    if request.method == 'POST':
        user_time = request.form['input_time']
        image_base_64 = request.form['drawing']
        category = request.form['category_drawing']
        model_name = request.form["model_name"]

        print("\n\ntime input : ", user_time, "\n")
        print("model_name = ", model_name)
        print("category = ", category)

        check_is = utils.decode_uploaded_file(image_base_64, category)
        print("check is ", check_is)

        return redirect(url_for('game_page', token=token))



@app.route('/create_dataset_test/', methods=['POST', 'GET'])
def create_dataset_test():
    try:
        print("Welcome in create dataset test")
        
        # first request, get categories and images ids that we need to transform 
        # (status = 3 ) in dataset, for example only get all turtle images with status 3
        # + transform them into correct data (numpy tensors) + merge them + save npy file
        query_result =  request_bdd.create_npy_dataset()
        
        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            return redirect(url_for('drawings'), code=307)
        else:
            return redirect(url_for('drawings'), code=307)

    except Exception as e:
        print("ECHEC")
        print("exception : ", str(e))
        current_date = utils.get_ccurent_date(format="fr")
        return redirect(url_for('drawings', query_result=str(e)), code=307)

@app.route('/notation/set_note/<token>', methods=['POST'])
def notation_app_user(token):

    if request.method == "POST":


        idUSer = request.form['idUser']
        drawing = request.form['drawing']
        notation = request.form['notation']
        print(idUSer, drawing, notation,"=================================")
        return redirect(url_for('game_page', token=token))

    else:

        return render_template("common/error.html")

# Handle errors section
@app.errorhandler(404)
@app.route('/url_not_found/', methods=['GET'])
def url_not_found(e):

    return render_template("common/error.html")

if __name__ == '__main__':

    hostname = socket.gethostname()
    app.run(debug=True, host=socket.gethostbyname(hostname), port=9893)