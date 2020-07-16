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
                session['count_notation'] = str(user.count_notation[0])

                # Update notation
                #count_nt_by_user = request_bdd.count_notation_by_user(session['id'])
                #stat = request_bdd.update_notation_by_user(user.id[0], count_nt_by_user['count_notation'][0])
                badges = request_bdd.get_all_badge()
                position = 0
                if int(session['count_notation']) > 50:
                    for i in range(len(badges)):
                        range_ = list(badges.iloc[i])[1].split('-')
                        if int(range_[0]) <= int(session['count_notation']) <= int(range_[1]):
                            position = i+1
                            if position == 3:
                                position = 2
                            break
                    session['next_badge'] = ";".join(str(item) for item in list(badges.iloc[position]))
                else:
                    session['next_badge'] = ";".join(str(item) for item in list(badges.iloc[0]))

                current_year = utils.get_ccurent_date(format="ang", full=False)
                top_5 = request_bdd.select_top_5()
                top_5_nb_drawings = request_bdd.select_top_5_nb_drawings()
                top_5_nb_notation = request_bdd.select_top_5_nb_notation()
                random_stat = ['En ligne', 'Hors ligne']

                if position == 0:
                    session['min'] = 0
                    session['max'] = 50
                else:
                    session['min'] = str(list(badges.iloc[position-1])[1]).split('-')[0]
                    session['max'] = str(list(badges.iloc[position-1])[1]).split('-')[0]
                session['position'] = str(position)
                return render_template("user_app/home_user_app.html", token=token, random_stat=random_stat, current_year=current_year, top_5=top_5, count_notation=session['count_notation'], top_5_nb_drawings=top_5_nb_drawings, top_5_nb_notation=top_5_nb_notation)

        return render_template('common/permission.html')

    except Exception as e:

        print(e, "====================================================")
        current_date = utils.get_ccurent_date(format="fr")
        return render_template("login.html", error=e, token=token)

@app.route('/profile/token/<token>', methods=['GET', 'POST'])
def profile_page(token):
    try:
        #print("query result = ", query_result)
        badges = request_bdd.get_all_badge()
        position = None
        if int(session['count_notation']) > 50:
            for i in range(len(badges)):
                range_ = list(badges.iloc[i])[1].split('-')
                if int(range_[0]) <= int(session['count_notation']) <= int(range_[1]):
                    position = i + 1
                    if position == 3:
                        position = 2
                    print(i)
                    break
            session['next_badge'] = ";".join(str(item) for item in list(badges.iloc[position]))
        else:
            session['next_badge'] = ";".join(str(item) for item in list(badges.iloc[0]))

        current_year = utils.get_ccurent_date(format="ang", full=False)
        top_5 = request_bdd.select_top_5()
        random_stat = ['En ligne', 'Hors ligne']
        return render_template("user_app/profile_user_app.html", token=token, current_year=current_year, badges=badges)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template('common/permission.html', e=e)

@app.route('/notation/token/<token>', methods=['GET', 'POST'])
def notation_page(token):
    try:
        # first tests
        all_drawings = []
        list_folder = os.listdir('static/doodle/')
        for folder in list_folder:
            list_opend_folder = os.listdir('static/doodle/'+folder)
            for drawing in list_opend_folder:
                all_drawings.append('doodle/' + folder + '/' + drawing)


        # get drawings in database
        all_drawings = request_bdd.learn2draw_list_draw_to_score(session['username'])
        shuffle(all_drawings)
        print("len of drawings ==> ", len(all_drawings))
        drawings_to_notate = all_drawings[0:12]
        #print("list drawings for arnaud ? ", list_drawings)

        print("current_drawings == ", drawings_to_notate)

        current_year = utils.get_ccurent_date(format="ang", full=False)
        return render_template("user_app/notation_user_app.html", token=token, current_year=current_year, drawings_to_notate = drawings_to_notate)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template('common/permission.html', e=e)

@app.route('/global/token/<token>', methods=['GET', 'POST'])
def global_page(token):
    try:

        # Update notation
        badges = request_bdd.get_all_badge()
        top_5_nb_drawings = request_bdd.select_top_5_nb_drawings()
        top_5_nb_notation = request_bdd.select_top_5_nb_notation()
        position = None
        if int(session['count_notation']) > 50:
            for i in range(len(badges)):
                range_ = list(badges.iloc[i])[1].split('-')
                if int(range_[0]) <= int(session['count_notation']) <= int(range_[1]):
                    position = i + 1
                    if position == 3:
                        position = 2
                    print(i)
                    break
            session['next_badge'] = ";".join(str(item) for item in list(badges.iloc[position]))
        else:
            session['next_badge'] = ";".join(str(item) for item in list(badges.iloc[0]))

        current_year = utils.get_ccurent_date(format="ang", full=False)
        top_5 = request_bdd.select_top_5()
        random_stat = ['En ligne', 'Hors ligne']

        return render_template("user_app/home_user_app.html", token=token, random_stat=random_stat,
                               current_year=current_year, top_5=top_5, count_notation=session['count_notation'],
                               top_5_nb_drawings=top_5_nb_drawings, top_5_nb_notation=top_5_nb_notation)

    except Exception as e:
        current_date = utils.get_ccurent_date(format="fr")
        return render_template('common/permission.html', e=e)

@app.route('/game/token/<token>', methods=['GET', 'POST'])
def game_page(token):
    try:
        current_prediction = request.args.get('current_prediction')
        print("current prediction = ", current_prediction)

        good_prediction = request.args.get('good_prediction')
        print("good prediction = ", good_prediction)

        dataset_exist = request.args.get('dataset_exist')
        print("dataset_exist = ", dataset_exist)

        submitted = request.args.get('submitted')
        print("submitted = ", submitted)

        badges = request_bdd.get_all_badge()
        position = None
        if int(session['count_notation']) > 50:
            for i in range(len(badges)):
                range_ = list(badges.iloc[i])[1].split('-')
                if int(range_[0]) <= session['count_notation'] <= int(range_[1]):
                    position = i + 1
                    if position == 3:
                        position = 2
                    print(i)
                    break
            session['next_badge'] = ";".join(str(item) for item in list(badges.iloc[position]))
        else:
            session['next_badge'] = ";".join(str(item) for item in list(badges.iloc[0]))

        session['position'] = position
        current_year = utils.get_ccurent_date(format="ang", full=False)
        top_5 = request_bdd.select_top_5()
        random_stat = ['En ligne', 'Hors ligne']

        if submitted:
            print("submitted ok , val = ", submitted, " type = ", type(submitted))
        else:
            print("not submitted, default message")
            submitted = "nothing"

        if current_prediction:
            current_prediction = current_prediction.split(";")
            current_prediction[1] = str(int(round(float(current_prediction[1]),2)*100))
            print("current predict length ", len(current_prediction))
            if  good_prediction == None :
                print("GOOD PRED")
                print("good predction, time to add points")
                add_points = request_bdd.add_points_to_user(session["username"], int(current_prediction[1]))
                session["score"] = add_points
                return render_template("user_app/game_user_app.html", token=token, random_stat=random_stat,
                               current_year=current_year, top_5=top_5, count_notation=session['count_notation'], badges = badges,
                               current_prediction=current_prediction[1], current_prediction_label=current_prediction[0], submitted=submitted)
            else :
                print("\nSend information ==> OK, if good predict points will be added, pre =", current_prediction[0], " good =", good_prediction, "\n")
                # if good_prediction == current_prediction[0]:
                #     print("good predction, time to add points")
                #     add_points = request_bdd.add_points_to_user(session["username"], current_prediction[1])


                return render_template("user_app/game_user_app.html", token=token, random_stat=random_stat,
                               current_year=current_year, top_5=top_5, count_notation=session['count_notation'], badges = badges,
                               current_prediction=current_prediction[1], current_prediction_label=current_prediction[0], good_prediction=good_prediction, dataset_exist=dataset_exist, submitted=submitted)
        
        return render_template("user_app/game_user_app.html", token=token, random_stat=random_stat,
                               current_year=current_year, top_5=top_5, count_notation=session['count_notation'], badges = badges, submitted=submitted)


        # return render_template("user_app/game_user_app.html", token=token, random_stat=random_stat,
        #                        current_year=current_year, top_5=top_5, count_notation=session['count_notation'], badges = badges)

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
            return redirect(url_for('connection_page'), code=307)
            #return render_template("login.html")
        else:
            # should 403 but for now stay with session clear (not risky isn't it ?)
            session.clear()
            print("GET METHOD SUPPORTED FOR NOW")
            return redirect(url_for('connection_page'), code=307)
            #return render_template("login.html")
            #return render_template("common/permission.html")
    except Exception as e:
        print("exception in sign_out")
        print("except == ", str(e))
        return redirect(url_for('connection_page'), code=307)


@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    try:

        if request.method == 'POST':

            username = str(request.form['username'])
            email = str(request.form['email'])
            pwd = str(request.form['pwd'])
            cnf_pwd = str(request.form['cnf_pwd'])

            # check if the username / email is already used
            verif = request_bdd.learn2draw_sign_up_verif(username, email, pwd, "2")
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
    #categories = None
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
        print("users infos : ", users_infos)
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
        
        print("GOOD ROUTE, ",query_result)
        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems, url for better because can hide params
            return redirect(url_for('users'), code=307)
        else:
            return redirect(url_for('users', query_result=query_result), code=307)

    except Exception as e:
        print("ECHEC")
        print("Except : ", str(e))
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
        new_count_notation = request.form['count_notation_input']

        print("infos : ", infos)
        print("\nbtn : ", btn)
        print("\nusername : ", new_username)
        print("\nemail : ", new_email)
        print("\nscore : ", new_score)
        print("\ncount notation : ", new_count_notation)

        query_result = request_bdd.learn2draw_update_user(infos, new_username, new_email, new_score, new_count_notation)

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

        query_result = request_bdd.learn2draw_update_drawing(infos, new_user_id, new_category_id, new_category_predicted_id, new_location, new_status, new_score, 0, new_time)

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
        new_dataset_avail = request.form['dataset_avail_input']
        # new_score = request.form['score_input']
        # print("infos : ", infos)
        # print("\nbtn : ", btn)
        print("\ncategory : ", new_category)
        print("\ndataset avail : ", new_dataset_avail)

        query_result = request_bdd.learn2draw_create_category(new_category, new_dataset_avail)
        
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
        new_dataset_avail = request.form['dataset_avail_input']
        print("infos : ", infos)
        print("\nbtn : ", btn)
        print("\ncategory : ", new_category)
        query_result = request_bdd.learn2draw_update_category(infos, new_category, new_dataset_avail)

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
        print("infos = ", infos)

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
        print("\ncudrrent prediction in app.py : ", current_prediction)
        # get category id of category selected by user and category predicted
        id_category = request_bdd.get_category_id(category)
        #print("\n\ntest id catego\n\n")
        # if id_category == False:
        #     print("need to create new category")
        # else:
        #     print("what is id category ?", id_category, " type ", type(id_category))
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
        try:
            user_time = request.form['input_time']
            image_base_64 = request.form['drawing']
            category = request.form['category_drawing']
            #model_name = request.form["model_name"]

            #find current model
            model_name = [f for f in os.listdir("models/") if f.endswith('.h5') and "current" in f]
            print("current_model = ", model_name)
            if model_name == []:
                model_name = "default.h5"
            else:
                model_name = model_name[0].replace("current_", "")

            print("model used = ", model_name)


            print("\n\ntime input : ", user_time, "\n")
            print("model_name = ", model_name)
            print("category = ", category)

            check_is = utils.decode_uploaded_file(image_base_64, category)
            print("check is ", check_is)
            check_is_for_bdd_insert = "\\"+check_is.replace("/", "\\")
            print("check_is_for_bdd_insert ", check_is_for_bdd_insert)

            prediction = my_models.get_predict_sample_cnn_baseball_broom_dolphin(check_is, category, model_name.replace(".h5", ""))

            current_prediction = str(prediction)
            print("\ncurrent prediction in app.py : ", current_prediction,"\n")


            # get category id of category selected by user and category predicted
            id_category = request_bdd.get_category_id(category)

            if id_category == "False":
                print("need to create new category, name entered by user = ", category)
                new_category = request_bdd.learn2draw_create_category(category)
                id_category = request_bdd.get_category_id(category)

            id_category_predicted = request_bdd.get_category_id(current_prediction.split(";")[0])

            print("id catego = ", id_category, " id catego predicted = ", id_category_predicted)

            # save drawing into database, for the test it's always user 2 
            create_drawing = request_bdd.learn2draw_create_drawing(str(session["id"]), id_category, id_category_predicted, check_is_for_bdd_insert, "0", str(round(float(current_prediction.split(";")[1])*100)), "0", user_time)
            print("create drawing ? ==> ", create_drawing)
            # add little message to add info on the veracity of the prediction
            if current_prediction.split(";")[0] == category:
                #current_prediction += ";yes"
                return redirect(url_for('game_page', token=token, current_prediction=current_prediction, code=307))
            else:
                # the prediction is bad, maybe it's because there isn't a dataset for the category
                # entered, if it's the case send the information
                dataset_exist = request_bdd.dataset_exist_for_category(category)
                if dataset_exist == "0":
                    good_prediction = category
                    print("current predict = ", current_prediction, "and dataset doesn't exist")
                    return redirect(url_for('game_page', token=token, current_prediction=current_prediction, good_prediction=good_prediction, dataset_exist= dataset_exist, code=307))
                else:
                    good_prediction = category
                    print("current predict = ", current_prediction)
                    return redirect(url_for('game_page', token=token, current_prediction=current_prediction, good_prediction=good_prediction, code=307))

            #return redirect(url_for('game_page', token=token))
        except Exception as e:
            print("ECHEC")
            print("exception : ", str(e))
            current_date = utils.get_ccurent_date(format="fr")
            return redirect(url_for('game_page', token=token), code=307)


# route to submit last drawing made to user notation system
@app.route('/play/submit_drawing_session/<token>', methods=['POST', 'GET'])
def submit_drawing_session(token):
    if request.method == 'POST':
        try:
            print("\nwelcome to submit drawing func")

            # get last drawing made, if it has already status == 1, send back error message
            last_drawing = request_bdd.get_last_drawing_made(session["id"])
            print("last drawing in app.py = ", last_drawing)
            last_drawing = last_drawing.split(";")
            # status == 1 ? return with error, already submitted
            if last_drawing[4] == "1":
                print("already submitted ;(")
                return redirect(url_for('game_page', token=token, submitted="already_submitted", code=307))

            # update status of drawing (staus == 1) and send a thankfull message
            query_result = request_bdd.learn2draw_update_drawing(last_drawing[0], session["id"], last_drawing[1], last_drawing[2], \
             last_drawing[3], 1, last_drawing[5], 0, last_drawing[7])

            if query_result == "True" or query_result == "False":
                return redirect(url_for('game_page', token=token, submitted="submission_done", code=307))
            else:
                return redirect(url_for('game_page', token=token, submitted=query_result, code=307))

            return redirect(url_for('game_page', token=token, code=307))

        except Exception as e:
            print("ECHEC")
            print("exception : ", str(e))
            current_date = utils.get_ccurent_date(format="fr")
            return redirect(url_for('game_page', token=token), code=307)


@app.route('/create_dataset_test/', methods=['POST', 'GET'])
def create_dataset_test():
    try:
        print("Welcome in create dataset test")
        
        # first request, get categories and images ids that we need to transform
        # (status = 3 ) in dataset, for example only get all turtle images with status 3
        # + transform them into correct data (numpy tensors) + merge them + save npy file
        
        #query_result =  request_bdd.create_npy_dataset("tortue")
        print("not needed anymore, tested by notation pages")
        query_result = "True"

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
    print("welcome in set note (app.py)")
    if request.method == "POST":
        try:
            idUSer = request.form['idUser']
            drawing = request.form['drawing']
            notation = request.form['notation']


            # Still to link to bdd
            print(idUSer, drawing, notation,"=================================")

             #token = request.args['token']
            # infos = request.args['infos']
            # btn = request.form['button']
            
            #modif location to make it usefull
            drawing = drawing.replace("/", "\\\\")
            drawing = drawing.replace("doodle\\\\", "\\\\static\\\\doodle\\\\")

            print("get info for drawing ", drawing)
            # get infos of drawing
            drawing_infos = request_bdd.get_drawing_voted(drawing)
            print("drawings info in app.py : ", drawing_infos)

            drawing_infos = drawing_infos.split(";")
            new_score = notation
            new_user_id = idUSer
            new_drawing_id = drawing_infos[0]
            new_drawing_user_id = drawing_infos[1]
            new_drawing_category_id = drawing_infos[2] 
            
            # new_score = request.form['score_input']
            # print("infos : ", infos)
            # print("\nbtn : ", btn)
            print("\nscore : ", new_score)
            print("\nuser_id : ", new_user_id)
            print("\ndrawing_id : ", new_drawing_id)
            print("\nnew_drawing_user_id : ", new_drawing_user_id)
            print("\new_drawing_category_id : ", new_drawing_category_id)

            query_result = request_bdd.learn2draw_create_notation(new_score, new_user_id, new_drawing_id, new_drawing_user_id, new_drawing_category_id)
            
            # a notation has been made so update count_notatiion attribute of the user
            one_notation_point = request_bdd.add_one_notation_point_to_user(session["id"])
            session["count_notation"] = str(int(session["count_notation"]) + 1)

            # check number of votes (if 100 status can change, score changed for image and for users
            # who made the right choice
            check_votes = request_bdd.one_hundred_votes_update(new_drawing_id, new_drawing_user_id, session["id"])
            if check_votes.split(";")[0] != "no_update":
                if int(check_votes.split(";")[0]) != 0:
                    print("update session score")
                    session["score"] = str(int(session["score"]) + int(check_votes.split(";")[0]))

            # check if there is 1000 images or more in status = 3 for the category
            # if it's the case, set their status to 4, and trigger the custom dataset creation function on all status=4 of category
            
            # only test this condition if the current image were add to "good images"
            if int(check_votes.split(";")[1]) == 3:
                check_1000_images = request_bdd.check_thousand_good_images(new_drawing_category_id)
                print("check 1000 img res in app.py : ", check_1000_images)


            print("GOOD ROUTE")
            if query_result == "True" or query_result == "False":
                # Nothing if 0 problems
                return "ok"
            else:
                return "error;" + query_result

        except Exception as e:
            print("ECHEC in notation app user")
            print("error : ", str(e))
            return "error;"+str(e)
        #return redirect(url_for('game_page', token=token))
        # return redirect(url_for('profile_page', token=token))
        # return redirect(url_for('notation_page', token=token))

    else:

        return render_template("common/error.html")

# profile changes by user section
@app.route('/update_user_password/', methods=['GET', 'POST'])
def update_user_password():
    try:
        token = request.args['token']
        print("token = ", token)
        username = request.args['username']
        btn = request.form['button']
        new_password = request.form['new_password_input']
        new_password_verif = request.form['new_password_verif_input']
        old_password = request.form['old_password_input']

        print("username : ", username)
        print("\nbtn : ", btn)
        print("\nnew password : ", new_password)
        print("\nold password : ", old_password)

        # return error if passwords aren't the same
        if new_password_verif != new_password:
            query_result = "passwords_are_not_the_same"
            print("BAD ROUTE")
        else:
            query_result = request_bdd.change_user_password(username, old_password, new_password)
            print("GOOD ROUTE")

        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            session['pwd'] = new_password
            return redirect(url_for('profile_page', token=token), code=307)
        else:
            print("error return")
            return redirect(url_for('profile_page', token=token, query_result=query_result), code=307)#query_result=query_result, code=307)

    except Exception as e:
        print("ECHEC")
        print(str(e))
        current_date = utils.get_ccurent_date(format="fr")
        return redirect(url_for('profile_page', token=token), code=307)#, query_result=str(e), code=307)
        #return render_template("admin_users.html", error=e)

@app.route('/update_user_infos/', methods=['GET', 'POST'])
def update_user_infos():
    try:
        print("Update USER INFOS")
        token = request.args['token']
        print("token = ", token)
        username = request.args['username']
        btn = request.form['button']
        print("MY ULES")
        new_username = request.form['username_input']
        new_email = request.form['email_input']
        pwd="empty"

        print("username : ", username)
        print("\nbtn : ", btn)
        print("\nnew username : ", new_username)
        print("\nnew email : ", new_email)

        if new_email == "" and new_username == "":
            return "empty_form"
        elif new_email == "":
            print("new email strategy")
            new_email = session['email']
            print("new_email = ", session["email"])
            # check if username / email arent already taken
            verif = request_bdd.learn2draw_sign_up_verif(new_username, new_email, pwd, "email")
            print("VERIF IN EMAIL STRAT = ", verif)
        elif new_username == "":
            print("not here")
            new_username = session["username"]
            # check if username / email arent already taken
            verif = request_bdd.learn2draw_sign_up_verif(new_username, new_email, pwd, "username")
        else:
            print("not here")
            # check if username / email arent already taken
            verif = request_bdd.learn2draw_sign_up_verif(new_username, new_email, pwd, "2")

        # error if username/ email already taken
        if verif == False:
            query_result = "email_or_username_already_taken"
            print("BAD ROUTE")
        else:
            print("new_email before update = ", new_email)
            query_result = request_bdd.change_user_infos(username, new_username, new_email)
            print("GOOD ROUTE")

        if query_result == "True" or query_result == "False":
            # Nothing if 0 problems
            session['username'] = new_username
            session['email'] = new_email
            return redirect(url_for('profile_page', token=token), code=307)
        else:
            print("error return")
            return redirect(url_for('profile_page', token=token, query_result=query_result), code=307)#query_result=query_result, code=307)

    except Exception as e:
        print("ECHEC in app.py")
        print(str(e))
        current_date = utils.get_ccurent_date(format="fr")
        return redirect(url_for('profile_page', token=token), code=307)#, query_result=str(e), code=307)
        #return render_template("admin_users.html", error=e)


# Handle errors section
@app.errorhandler(404)
@app.route('/url_not_found/', methods=['GET'])
def url_not_found(e):

    return render_template("common/error.html")

if __name__ == '__main__':

    hostname = socket.gethostname()
    app.run(debug=True, host=socket.gethostbyname(hostname), port=9893)