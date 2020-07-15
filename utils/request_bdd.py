from configparser import ConfigParser
from sqlalchemy import create_engine, update, Table, Column, MetaData, func
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
import pandas as pd
import numpy as np 
from PIL import Image
from models import my_models
import os
import shutil
from datetime import datetime
from uuid import getnode as get_mac

def create_engine_db() -> str:
    config = ConfigParser()
    cwd = os.getcwd()

    config.read(cwd+"/utils/config.ini")
    #config.read("D:/Skoula/utils/config.ini")
    mac = get_mac()
    if str(mac) == "163519832176392":
        get_connection = 'mysql+pymysql://'\
                            + config.get('Hamza_mysql', 'user')\
                            + ':' + config.get('Hamza_mysql','pwd')\
                            + '@' + config.get('Hamza_mysql', 'host')\
                            + '/' + config.get('Hamza_mysql', 'database') + ''
    else:
        get_connection = 'mysql+pymysql://' \
                         + config.get('other', 'user') \
                         + ':' + config.get('other', 'pwd') \
                         + '@' + config.get('other', 'host') \
                         + '/' + config.get('other', 'database') + ''

    return get_connection

def learn2draw_connect(login:str, pwd:str) -> pd.DataFrame:

    print("DEBUGGIND LEARN2DRAW CONNECT")
    try:
        db_connection = create_engine(create_engine_db())
        user = pd.read_sql("SELECT * FROM USERS WHERE email = %s AND pwd = %s" % ("'" + login + "'", "'" + pwd + "'"),
                         con=db_connection, index_col=None)

    except Exception as e:
        print("Exception : ", str(e))
        return str(e)

    return user

def select_top_5() -> pd.DataFrame:

    db_connection = create_engine(create_engine_db())
    top_5 = pd.read_sql("SELECT u.username, u.id, SUM(d.score) as score_model, SUM(d.score_by_votes) as score_vote, COUNT(d.USERS_id) as nb_dessins FROM drawings d INNER JOIN users u ON u.id = d.USERS_id GROUP BY d.USERS_id",
                       con=db_connection, index_col=None)

    return top_5

def select_top_5_nb_drawings() -> pd.DataFrame:

    db_connection = create_engine(create_engine_db())
    top_5 = pd.read_sql("SELECT u.id, u.username, u.score, count(n.USERS_id) nb_dessins FROM notations n INNER JOIN users u ON n.USERS_id = u.id GROUP BY n.USERS_id ORDER BY nb_dessins desc",
                       con=db_connection, index_col=None)

    return top_5

def select_top_5_nb_notation() -> pd.DataFrame:

    db_connection = create_engine(create_engine_db())
    top_5 = pd.read_sql("SELECT * FROM users ORDER BY count_notation DESC",
                       con=db_connection, index_col=None)

    return top_5


def count_notation_by_user(id_user) -> pd.DataFrame:

    db_connection = create_engine(create_engine_db())
    count = pd.read_sql("SELECT count(USERS_id) as count_notation FROM notations WHERE USERS_id = %s GROUP BY USERS_id" % (id_user),
                       con=db_connection, index_col=None)

    return count

def update_notation_by_user(id_user, notation) -> bool:

    # old method

    # query = "UPDATE users SET count_notation = %s WHERE id = %s" % (notation, id_user)

    # connection = pymysql.connect(host='localhost',
    #                          user='root',
    #                          password='Azertyuiop91&*',
    #                          db='learn2draw_db',
    #                          charset='utf8mb4',
    #                          cursorclass=pymysql.cursors.DictCursor)


    # cursor = connection.cursor()
    # cursor.execute(query)
    # connection.commit()
    # cursor.close()
    # connection.close()

    # return True

    try:
        print("\n update notation by user id_user = ", id_user, " notation = ", notation,"\n")
        db_connection = create_engine(create_engine_db())
        Base = declarative_base()

        class User(Base):
            __tablename__ = 'users'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            username = sqlalchemy.Column(sqlalchemy.String(length=50), unique=True, nullable=False)
            email = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            pwd = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            admin = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            count_notation = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<User(username='{0}', email='{1}', pwd='{2}', admin='{3}',score='{4}', count_notation='{5}')>"\
                .format(self.username, self.email, self.pwd,
                  self.admin, self.score, self.count_notation)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        session.query(User).filter(User.id == int(id_user)).update({User.count_notation: int(notation)})
        #session.query(User).filter(User.username == infos[0], User.email == infos[1]).update({User.username: new_username}, {User.email: new_email})
        #print("error handle ? : ", test)
        session.commit()

        return True

    except Exception as e:
        print("Exception in update notation by user : \n", str(e))
        return False


def learn2draw_sign_up_verif(username:str, email:str, pwd:str, username_email_or_2:"2") -> bool:

    try:
        db_connection = create_engine(create_engine_db())
        if username_email_or_2 == "2":
            user = pd.read_sql("SELECT * FROM USERS WHERE username = %s OR email = %s" % ("'" + username + "'", "'" + email + "'"),
                     con=db_connection, index_col=None)
        elif username_email_or_2 == "email":
            user = pd.read_sql("SELECT * FROM USERS WHERE username = %s" % ("'" + username + "'"),
                     con=db_connection, index_col=None)
        else:
            print("email strat in request bdd")
            user = pd.read_sql("SELECT * FROM USERS WHERE email = %s" % ("'" + email + "'"),
                     con=db_connection, index_col=None)
            
        print("user : ", user)
        if user.empty:
            return True
        return False

    except Exception as e:

        print(e)
        return False

def learn2draw_sign_up(username:str, email:str, pwd:str) -> bool:

    try:
        db_connection = create_engine(create_engine_db())
        user = {"username": username, "email": email, "pwd": pwd, "admin": 0, "score": 0, "count_notation": 0}
        df_user = pd.DataFrame(user, index=[None])
        df_user.to_sql('USERS', db_connection, index=False, if_exists='append')
        return True

    except Exception as e:

        print(e)
        return False

def learn2draw_list_draw_to_score(username:str) -> list:
    try:
        db_connection = create_engine(create_engine_db())
        user_id = pd.read_sql("SELECT id FROM USERS WHERE username = %s" % ("'" + username + "'"),
                           con=db_connection, index_col=None).to_dict()
        print("user id : ", user_id)

        # les 100 dessins les plus anciens avec un status == 1 sont récupérés, 12 seront tirés au hasard
        list_draws = pd.read_sql("SELECT * FROM DRAWINGS WHERE USERS_id != %s AND status=1 ORDER BY id DESC Limit 100;" % ("'" + str(user_id['id'][0]) + "'"),
                           con=db_connection, index_col=None).to_dict('index')
        #print("list draws : ", list_draws)

        list_notation = pd.read_sql(
            "SELECT DRAWINGS_id FROM NOTATIONS WHERE USERS_id = %s" % ("'" + str(user_id['id'][0]) + "'"),
            con=db_connection, index_col=None).to_dict('index')

        print("list notation : ", list_notation)

        liste = []

        for i in list_draws:
            skip = False
            for j in list_notation:
                if list_notation[j]["DRAWINGS_id"] == list_draws[i]['id']:
                    skip = True
                    break
            if skip == True:
                continue
            category_name = pd.read_sql("SELECT name FROM CATEGORIES WHERE id = %s" % ("'" + str(list_draws[i]['CATEGORIES_id']) + "'"),
                           con=db_connection, index_col=None).to_dict()
            list_draws[i]['CATEGORIES_id'] = category_name['name'][0]

            user_name = pd.read_sql(
                "SELECT username FROM USERS WHERE id = %s" % ("'" + str(list_draws[i]['USERS_id']) + "'"),
                con=db_connection, index_col=None).to_dict()
            list_draws[i]['USERS_id'] = user_name['username'][0]

            # line = "{};{};{};{};{};{}".format(list_draws[i]['USERS_id'], list_draws[i]['CATEGORIES_id'], list_draws[i]['location'],
            #  list_draws[i]['score'], list_draws[i]['time'], list_draws[i]['id'])
            line = "{}".format(list_draws[i]["location"])
            # change line to respect format from app.py
            line = line.replace("\\static\\", "")
            line = line.replace("\\", "/")

            liste.append(line)
            print("line ", i, " = ", line)

        return liste

    except Exception as e:
        print(e)

def learn2draw_insert_score(username:str,information:str,score:str) -> bool:
    try:
        db_connection = create_engine(create_engine_db())
        infos=information.split(';')
        user_id = str(pd.read_sql("SELECT id FROM USERS WHERE username = %s" % ("'" + username + "'"),
                              con=db_connection, index_col=None).to_dict()['id'][0])
        user_drawings_id = str(pd.read_sql("SELECT id FROM USERS WHERE username = %s" % ("'" + infos[0] + "'"),
                                  con=db_connection, index_col=None).to_dict()['id'][0])
        category_id = str(pd.read_sql("SELECT id FROM CATEGORIES WHERE name = %s" % ("'" + infos[1] + "'"),
                                      con=db_connection, index_col=None).to_dict()['id'][0])
        notation = {'score':score, "USERS_id":user_id, 'DRAWINGS_id':infos[5], "DRAWINGS_USERS_id":user_drawings_id, "DRAWINGS_CATEGORIES_id":category_id}

        df_notation = pd.DataFrame(notation, index=[None])
        df_notation.to_sql('NOTATIONS', db_connection, index=False, if_exists='append')

        return True

    except Exception as e:

        print(e)
        return False


# Functions for backoffice

# user backoffice

# list all users, maybe need to check if user is admin before querying but not now
def learn2draw_list_all_users() -> list:
    try:
        db_connection = create_engine(create_engine_db())
        users_infos = pd.read_sql("SELECT username, email, score, count_notation FROM USERS",
                           con=db_connection, index_col=None).to_dict()
        #print("users infos : ", users_infos)

        liste = []

        for i in users_infos["username"]:
            #print("i = ", i)
            line = "{};{};{};{}".format(users_infos['username'][i], users_infos['email'][i], users_infos['score'][i], users_infos['count_notation'][i])
            #print("LINE = ", line)
            liste.append(line)

        #print("USER INFOS : \n", liste)
        return liste

    except Exception as e:
        print(e)

def learn2draw_create_user(new_username, new_email, new_password, new_confirm_password) -> str:
    print("Welcome in create user")
    try:
        #if passwords aren't equal, throw error
        if new_password != new_confirm_password:
            return "passwords doesn't match"

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
    
        Base = declarative_base()

        class User(Base):
            __tablename__ = 'users'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            username = sqlalchemy.Column(sqlalchemy.String(length=50), unique=True, nullable=False)
            email = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            pwd = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            admin = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            count_notation = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<User(username='{0}', email='{1}', pwd='{2}', admin='{3}',score='{4}', count_notation='{5}')>"\
                .format(self.username, self.email, self.pwd,
                  self.admin, self.score, self.count_notation)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        my_new_user = User(username=new_username, email=new_email, pwd=new_password, admin=0, score=0, count_notation=0)
        session.add(my_new_user)
        session.commit()

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "Duplicate entry" in str(e):
            if "for key \'users.username\'" in str(e):
                print("send dupplicate username error")
                return "username_already_exist"
            else:
                print("send dupplicate email error")
                return "email_already_exist"

        print(e)
        return "False"

def learn2draw_update_user(informations:str, new_username, new_email, new_score, new_count_notation) -> str:
    try:
        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        infos=informations.split(';')

        print("infos 0 ", infos[0], " infos 1 ", infos[1])
        Base = declarative_base()

        class User(Base):
            __tablename__ = 'users'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            username = sqlalchemy.Column(sqlalchemy.String(length=50), unique=True, nullable=False)
            email = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            pwd = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            admin = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            count_notation = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<User(username='{0}', email='{1}', pwd='{2}', admin='{3}',score='{4}', count_notation='{5}')>"\
                .format(self.username, self.email, self.pwd,
                  self.admin, self.score, self.count_notation)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        session.query(User).filter(User.username == infos[0] and User.email == infos[1]).update({User.username: new_username, User.email: new_email, User.score: new_score, User.count_notation: new_count_notation})
        #session.query(User).filter(User.username == infos[0], User.email == infos[1]).update({User.username: new_username}, {User.email: new_email})
        #print("error handle ? : ", test)
        session.commit()

        # metadata = MetaData()
        # users = Table('users', metadata,
        #     Column('id', Integer, primary_key=True),
        #     Column('username', String(50), nullable=False),
        #     Column('email', String(100), username nullable=False),
        #     Column('pwd', String(40), nullable=False),
        #     Column('admin', Integer, nullable=False),
        #     Column('score', Integer, nullable=False)
        # )



        # jwk_user = User(username="user_test", email="user_test@gmail.com", pwd="aqwzsx",
        # admin=0, score=0)
        # session.add(jwk_user)
        # session.commit()

        print("BILLY C TOI ?")

        # # user = pd.read_sql("SELECT * FROM USERS WHERE username = %s AND email = %s" % ("'" + infos[0] + "'", "'" + infos[1] + "'")
        # #     ,con=db_connection, index_col=None)
        # df_user = pd.read_sql("SELECT * FROM USERS" 
        #     ,db_connection)
        # #df_user = pd.DataFrame(user, index=[None])
        # df_user[df_user['username'] == "arnaudsimon091@gmail.coma", "username"] = new_username
        # print("SUIS JE BEAU ?")
        # df_user.to_sql('USERS', db_connection, if_exists='replace')


        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "Duplicate entry" in str(e):
            if "for key \'users.username\'" in str(e):
                print("send dupplicate username error")
                return "username_already_exist"
            else:
                print("send dupplicate email error")
                return "email_already_exist"

        print(e)
        return "False"

def learn2draw_delete_user(informations) -> str:
    try:

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        infos=informations.split(';')

        my_username = infos[0]
    
        Base = declarative_base()

        class User(Base):
            __tablename__ = 'users'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            username = sqlalchemy.Column(sqlalchemy.String(length=50), unique=True, nullable=False)
            email = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            pwd = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            admin = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            count_notation = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<User(username='{0}', email='{1}', pwd='{2}', admin='{3}',score='{4}', count_notation='{5}')>"\
                .format(self.username, self.email, self.pwd,
                  self.admin, self.score, self.count_notation)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        session.query(User).filter(User.username == my_username).delete()
        session.commit()

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "Duplicate entry" in str(e):
            if "for key \'users.username\'" in str(e):
                print("send dupplicate username error")
                return "username_already_exist"
            else:
                print("send dupplicate email error")
                return "email_already_exist"

        print(e)
        return "False"


# drawing backoffice
# list all drawings, maybe need to check if user is admin before querying but not now
def learn2draw_list_all_drawings() -> list:
    try:
        db_connection = create_engine(create_engine_db())
        drawings_infos = pd.read_sql("SELECT id, USERS_id, CATEGORIES_id, CATEGORIES_PREDICTED_id, status, score, score_by_votes, time FROM DRAWINGS",
                           con=db_connection, index_col=None).to_dict()
        #print("users infos : ", users_infos)

        liste = []

        for i in drawings_infos["USERS_id"]:
            #print("i = ", i)
            line = "{};{};{};{};{};{};{};{}".format(drawings_infos['id'][i], drawings_infos['USERS_id'][i], drawings_infos['CATEGORIES_id'][i], drawings_infos['CATEGORIES_PREDICTED_id'][i], drawings_infos['status'][i], drawings_infos['score'][i], drawings_infos['score_by_votes'][i], drawings_infos['time'][i])
            #print("LINE = ", line)
            liste.append(line)

        #print("USER INFOS : \n", liste)
        return liste

    except Exception as e:
        print(e)

def learn2draw_create_drawing(new_user_id, new_category_id, new_category_predicted_id, new_location, new_status, new_score, new_score_by_votes, new_time) -> str:
    try:
        if int(new_status) < 0 or int(new_score) < 0 or int(new_time) < 0:
            return "status / score / time should be >= 0"

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
    
        Base = declarative_base()

        class Drawing(Base):
            __tablename__ = 'drawings'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            users_id = sqlalchemy.Column(sqlalchemy.Integer)
            categories_id = sqlalchemy.Column(sqlalchemy.Integer)
            categories_predicted_id = sqlalchemy.Column(sqlalchemy.Integer)
            location = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            status = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            score_by_votes = sqlalchemy.Column(sqlalchemy.Integer)
            time = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<Drawing(users_id='{0}', categories_id='{1}', categories_predicted_id='{2}', location='{3}', status='{4}', score='{5}', time='{6}')>"\
                .format(self.users_id, self.categories_id, self.categories_predicted_id, self.location,
                  self.status, self.score, self.score_by_votes, self.time)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
        #print("salut")
        print("score before query = ", new_score)

        my_new_drawing = Drawing(users_id=new_user_id, categories_id=new_category_id, categories_predicted_id= new_category_predicted_id, location=new_location, status=new_status, score=new_score, score_by_votes=new_score_by_votes, time=new_time)
        session.add(my_new_drawing)
        session.commit()

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) dans create drawing \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "foreign key constraint" in str(e):
            if "fk_DRAWINGS_USERS_idx" in str(e):
                print("User doesn't exist")
                return "user_doesnt_exist"
            else:
                print("category doesn't exist")
                return "category_doesnt_exist"

        print(e)
        return "False"

def learn2draw_update_drawing(informations:str, new_user_id, new_category_id, new_category_predicted_id, new_location, new_status, new_score, new_score_by_votes, new_time) -> str:
    try:
        if int(new_status) < 0 or int(new_score) < 0 or int(new_time) < 0:
            return "status / score / time should be >= 0"

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        infos=informations.split(';')

        print("infos 0 ", infos[0])#, " infos 1 ", infos[1])
        Base = declarative_base()

        class Drawing(Base):
            __tablename__ = 'drawings'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            users_id = sqlalchemy.Column(sqlalchemy.Integer)
            categories_id = sqlalchemy.Column(sqlalchemy.Integer)
            categories_predicted_id = sqlalchemy.Column(sqlalchemy.Integer)
            location = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            status = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            score_by_votes = sqlalchemy.Column(sqlalchemy.Integer)
            time = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<Drawing(users_id='{0}', categories_id='{1}', categories_predicted_id='{2}', location='{3}', status='{4}', score='{5}', time='{6}')>"\
                .format(self.users_id, self.categories_id, self.categories_predicted_id, self.location,
                  self.status, self.score, self.score_by_votes, self.time)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        session.query(Drawing).filter(Drawing.id == infos[0]).update({Drawing.users_id: new_user_id, Drawing.categories_id: new_category_id, Drawing.categories_predicted_id: new_category_predicted_id, Drawing.status: new_status, Drawing.score: new_score, Drawing.score_by_votes: new_score_by_votes, Drawing.time: new_time})
        #session.query(User).filter(User.username == infos[0], User.email == infos[1]).update({User.username: new_username}, {User.email: new_email})
        #print("error handle ? : ", test)
        session.commit()

        #print("BILLY C TOI ?")

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "foreign key constraint" in str(e):
            if "fk_DRAWINGS_USERS_idx" in str(e):
                print("User doesn't exist")
                return "user_doesnt_exist"
            else:
                print("category doesn't exist")
                return "category_doesnt_exist"

        print(e)
        return "False"

def learn2draw_delete_drawing(informations) -> str:
    try:

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        infos=informations.split(';')

        my_id = infos[0]
    
        Base = declarative_base()

        class Drawing(Base):
            __tablename__ = 'drawings'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            users_id = sqlalchemy.Column(sqlalchemy.Integer)
            categories_id = sqlalchemy.Column(sqlalchemy.Integer)
            categories_predicted_id = sqlalchemy.Column(sqlalchemy.Integer)
            location = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            status = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            score_by_votes = sqlalchemy.Column(sqlalchemy.Integer)
            time = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<Drawing(users_id='{0}', categories_id='{1}', categories_predicted_id='{2}', location='{3}', status='{4}', score='{5}', time='{6}')>"\
                .format(self.users_id, self.categories_id, self.categories_predicted_id, self.location,
                  self.status, self.score, self.score_by_votes, self.time)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        session.query(Drawing).filter(Drawing.id == my_id).delete()
        session.commit()

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "Duplicate entry" in str(e):
            if "for key \'users.username\'" in str(e):
                print("send dupplicate username error")
                return "username_already_exist"
            else:
                print("send dupplicate email error")
                return "email_already_exist"

        print(e)
        return "False"


# categories backoffice
# list all categories, maybe need to check if user is admin before querying but not now
def learn2draw_list_all_categories() -> list:
    try:
        db_connection = create_engine(create_engine_db())
        categories_infos = pd.read_sql("SELECT id, name, dataset_available FROM CATEGORIES",
                           con=db_connection, index_col=None).to_dict()
        #print("users infos : ", users_infos)

        liste = []

        for i in categories_infos["name"]:
            #print("i = ", i)
            line = "{};{};{}".format(categories_infos['name'][i], categories_infos['id'][i], categories_infos["dataset_available"][i])
            #print("LINE = ", line)
            liste.append(line)

        #print("USER INFOS : \n", liste)
        return liste

    except Exception as e:
        print(e)

def learn2draw_create_category(new_category) -> str:
    try:

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
    
        Base = declarative_base()

        class Category(Base):
            __tablename__ = 'categories'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            name = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            dataset_available = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "< Category(id='{0}', name='{1}', dataset_available='{2}')>"\
                .format(self.id, self.name, self.dataset_available)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        my_new_category = Category(name=new_category, dataset_available=0)
        session.add(my_new_category)
        session.commit()

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) dans create catego \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "Duplicate entry" in str(e):
            print("send dupplicate category error")
            return "category_already_exist"
            

        print(e)
        return "False"

def learn2draw_update_category(informations:str, new_category) -> str:
    try:
        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        infos=informations.split(';')

        if infos[0] == "broom" or infos[0] == "baseball":
            return "cant_delete_or_modify_native_categories"

        print("infos 0 ", infos[0])
        Base = declarative_base()

        class Category(Base):
            __tablename__ = 'categories'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            name = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            dataset_available = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "< Category(id='{0}', name='{1}', dataset_available='{2}')>"\
                .format(self.id, self.name, self.dataset_available)

        class Model(Base):
            __tablename__ = 'models'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            name = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            epochs = sqlalchemy.Column(sqlalchemy.Integer)
            accuracy = sqlalchemy.Column(sqlalchemy.Float)
            loss = sqlalchemy.Column(sqlalchemy.Float)
            val_accuracy = sqlalchemy.Column(sqlalchemy.Float)
            val_loss = sqlalchemy.Column(sqlalchemy.Float)
            params = sqlalchemy.Column(sqlalchemy.String(length=800), nullable=False)
            time = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            categories_handled = sqlalchemy.Column(sqlalchemy.String(length=800), nullable=False)

         
            def __repr__(self):
                return "<Model(name='{0}', epochs='{1}', accuracy='{2}', loss='{3}',val_accuracy='{4}', val_loss='{5}', params='{6}', time='{7}'>"\
                .format(self.name, self.epochs, self.accuracy,
                  self.loss, self.val_accuracy, self.val_loss, self.params, self.time, self.categories_handled)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        session.query(Category).filter(Category.name == infos[0]).update({Category.name: new_category})
        #session.query(User).filter(User.username == infos[0], User.email == infos[1]).update({User.username: new_username}, {User.email: new_email})
        #print("error handle ? : ", test)
        session.commit()

        # now we need to update names in the model table ("categories_handled")
        session.query(Model).update({Model.categories_handled : func.replace(Model.categories_handled, infos[0], new_category)}, synchronize_session='fetch')
        session.commit()
        #print("BILLY C TOI ?")

        # now replace existing folders + files by the new cateogry name (doodle + npy dataset)
        #dirpath, dirnames, filenames = [] 
        data_path = "static/doodle/"
        my_dirnames = []
        my_dir = [x[0] for x in os.walk(data_path)]
        print("my dir = ", my_dir)

        # if folder have the category_name, rename it
        if "static/doodle/"+infos[0] in my_dir:
            os.rename(data_path+infos[0], data_path+new_category)

        data_path = "models/dataset_quickdraw/" 
        for (dirpath, dirnames, filenames) in os.walk(data_path):
             pass # filenames accumulate in list 'filenames'
        print(filenames)

        if infos[0]+".npy" in filenames:
            # rename
            os.rename(data_path+infos[0]+".npy", data_path+new_category+".npy")


        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "Duplicate entry" in str(e):
            print("send dupplicate category error")
            return "category_already_exist"
            

        print(e)
        return "False"

# WARNING : When a category is deleted, the current model cannot predict like before,
# so a new one (basic params) is created and set as current model, if you want
# to change the current model by an old one, a warning message will appear and force
# to update the model before you set it as current model
def learn2draw_delete_category(informations) -> str:
    try:

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        infos=informations.split(';')

        my_id = infos[0]
        print("my_id = ", my_id)

        if my_id == "broom" or my_id == "baseball":
            return "cant_delete_or_modify_native_categories"
    
        Base = declarative_base()

        class Category(Base):
            __tablename__ = 'categories'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            name = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            dataset_available = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "< Category(id='{0}', name='{1}', dataset_available='{2}')>"\
                .format(self.id, self.name, self.dataset_available)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        # before delete, create new model (cnn default) and set it as current model
        time = int(datetime.now().strftime("%Y%m%d%H%M%S"))
        create_model = learn2draw_create_model("cnn", "delete_"+str(time), "40", "1024", "adadelta", "0.001", my_id)
        if "True" not in create_model:
            return "error_" + create_model

        # set as current (extra param to avoid classic denial behaviour)
        query_result = change_current_model("cnn_delete_"+str(time))
        if "True" not in query_result:
            return "problem_when_changing_current_model_"+query_result

        session.query(Category).filter(Category.name == my_id).delete()
        session.commit()

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "Duplicate entry" in str(e):
            print("send dupplicate category error")
            return "category_already_exist"
            

        print(e)
        return "False in delete category"


def get_category_id(category_name):
    try:
        db_connection = create_engine(create_engine_db())
        categories_infos = pd.read_sql("SELECT id FROM CATEGORIES WHERE name = %s" % ("'" + category_name + "'"),
                           con=db_connection, index_col=None).to_dict()

        
        print("categories infos ",categories_infos)
        line = "{}".format(categories_infos['id'][0])
        print("line = ", line)

        return line



    except Exception as e:
        print("on a récup l'exception ; dans get_category_id\n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "foreign key constraint" in str(e):
            if "fk_DRAWINGS_USERS_idx" in str(e):
                print("User doesn't exist")
                return "user_doesnt_exist"
            else:
                print("id doesn't exist")
                return "id_doesnt_exist"

        print(e)
        return "False"



# notations backoffice
# list all notations, maybe need to check if user is admin before querying but not now
def learn2draw_list_all_notations() -> list:
    try:
        db_connection = create_engine(create_engine_db())
        notations_infos = pd.read_sql("SELECT id, score, USERS_id, DRAWINGS_id, DRAWINGS_USERS_id, DRAWINGS_CATEGORIES_id FROM NOTATIONS",
                           con=db_connection, index_col=None).to_dict()
        #print("users infos : ", users_infos)

        liste = []

        for i in notations_infos["id"]:
            #print("i = ", i)
            line = "{};{};{};{};{};{}".format(notations_infos['id'][i], notations_infos['score'][i], notations_infos['USERS_id'][i], notations_infos['DRAWINGS_id'][i], notations_infos['DRAWINGS_USERS_id'][i], notations_infos['DRAWINGS_CATEGORIES_id'][i])
            #print("LINE = ", line)
            liste.append(line)

        #print("USER INFOS : \n", liste)
        return liste

    except Exception as e:
        print(e)

def learn2draw_create_notation(new_score, new_user_id, new_drawing_id, new_drawing_user_id, new_drawing_category_id) -> str:
    try:

        if new_user_id == new_drawing_user_id:
            return "A user cannot note his own drawing"
        if new_score != "yes" and new_score != "no":
            return "Score_should_be_yes_or_no"

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
    
        Base = declarative_base()

        class Notation(Base):
            __tablename__ = 'notations'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            score = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            users_id = sqlalchemy.Column(sqlalchemy.Integer)
            drawings_id = sqlalchemy.Column(sqlalchemy.Integer)
            drawings_users_id = sqlalchemy.Column(sqlalchemy.Integer)
            drawings_categories_id = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<Notation(score='{0}', users_id='{1}', drawings_id='{2}', drawings_users_id='{3}', drawings_categories_id='{4}')>"\
                .format(self.score, self.users_id, self.drawings_id,
                  self.drawings_users_id, self.drawings_categories_id)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")

        my_new_notation = Notation(score=new_score, users_id=new_user_id, drawings_id=new_drawing_id, drawings_users_id=new_drawing_user_id, drawings_categories_id=new_drawing_category_id)
        session.add(my_new_notation)
        session.commit()

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "foreign key constraint" in str(e):
            if "fk_DRAWINGS_USERS_idx" in str(e):
                print("User doesn't exist")
                return "user_doesnt_exist"
            else:
                print("id doesn't exist")
                return "id_doesnt_exist"

        print(e)
        return "False"

def learn2draw_update_notation(informations:str, new_score, new_user_id, new_drawing_id, new_drawing_user_id, new_drawing_category_id) -> str:
    try:
        if new_user_id == new_drawing_user_id:
            return "A user cannot note his own drawing"
        if new_score != "yes" and new_score != "no":
            return "Score_should_be_yes_or_no"

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        infos=informations.split(';')

        print("infos 0 ", infos[0], " infos 1 ", infos[1])
        Base = declarative_base()

        class Notation(Base):
            __tablename__ = 'notations'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            score = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            users_id = sqlalchemy.Column(sqlalchemy.Integer)
            drawings_id = sqlalchemy.Column(sqlalchemy.Integer)
            drawings_users_id = sqlalchemy.Column(sqlalchemy.Integer)
            drawings_categories_id = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<Notation(score='{0}', users_id='{1}', drawings_id='{2}', drawings_users_id='{3}', drawings_categories_id='{4}')>"\
                .format(self.score, self.users_id, self.drawings_id,
                  self.drawings_users_id, self.drawings_categories_id)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        session.query(Notation).filter(Notation.id == infos[0]).update({Notation.score: new_score, Notation.users_id: new_user_id, Notation.drawings_id: new_drawing_id, Notation.drawings_users_id: new_drawing_user_id, Notation.drawings_categories_id: new_drawing_category_id})
        #session.query(User).filter(User.username == infos[0], User.email == infos[1]).update({User.username: new_username}, {User.email: new_email})
        #print("error handle ? : ", test)
        session.commit()

        #print("BILLY C TOI ?")

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "foreign key constraint" in str(e):
            if "fk_DRAWINGS_USERS_idx" in str(e):
                print("User doesn't exist")
                return "user_doesnt_exist"
            else:
                print("id doesn't exist")
                return "id_doesnt_exist"

        print(e)
        return "False"

def learn2draw_delete_notation(informations) -> str:
    try:

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        infos=informations.split(';')

        my_id = infos[0]
    
        Base = declarative_base()

        class Notation(Base):
            __tablename__ = 'notations'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            score = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            users_id = sqlalchemy.Column(sqlalchemy.Integer)
            drawings_id = sqlalchemy.Column(sqlalchemy.Integer)
            drawings_users_id = sqlalchemy.Column(sqlalchemy.Integer)
            drawings_categories_id = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<Notation(score='{0}', users_id='{1}', drawings_id='{2}', drawings_users_id='{3}', drawings_categories_id='{4}')>"\
                .format(self.score, self.users_id, self.drawings_id,
                  self.drawings_users_id, self.drawings_categories_id)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        session.query(Notation).filter(Notation.id == my_id).delete()
        session.commit()

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "foreign key constraint" in str(e):
            if "fk_DRAWINGS_USERS_idx" in str(e):
                print("User doesn't exist")
                return "user_doesnt_exist"
            else:
                print("category doesn't exist")
                return "category_doesnt_exist"

        print(e)
        return "False"



# models backoffice

# get all infos of existing models
def learn2draw_list_all_models() -> list:
    try:
        db_connection = create_engine(create_engine_db())
        models_infos = pd.read_sql("SELECT name, epochs, accuracy, loss, val_accuracy, val_loss, params, time, categories_handled FROM MODELS",
                           con=db_connection, index_col=None).to_dict()
        #print("users infos : ", users_infos)

        liste = []

        
        for i in models_infos["name"]:
            
            # create last information : the model is the current one ? ==> MAYBE TO SLOW METHOD, FASTER WITH BDD ENTRY ???
            current_model = [f for f in os.listdir("models/") if f.endswith('.h5') and "current_"+models_infos['name'][i] in f]
            #print("current_model = ", current_model)
            if current_model == []:
                current_model = "no"
            else:
                current_model = "yes"
            #print("current_model = ", current_model)
            #print("i = ", i)
            line = "{};{};{};{};{};{};{};{};{};{}".format(models_infos['name'][i], models_infos['epochs'][i], models_infos['accuracy'][i], models_infos['loss'][i], models_infos['val_accuracy'][i], models_infos['val_loss'][i], models_infos['params'][i], models_infos['time'][i], models_infos['categories_handled'][i], current_model)
            #print("LINE = ", line)
            liste.append(line)

        #print("USER INFOS : \n", liste)
        return liste

    except Exception as e:
        print(e)

# get all categories handled by one model
def learn2draw_get_categories_handled_for_one_model(model_name) -> str:
    try:
        db_connection = create_engine(create_engine_db())
        model_infos = pd.read_sql("SELECT categories_handled FROM MODELS WHERE name = %s" % ("'" + model_name + "'"),
                           con=db_connection, index_col=None).to_dict()
        

        print("models infos ",model_infos)
        line = "{}".format(model_infos['categories_handled'][0])
        print("line = ", line)

        return line

    except Exception as e:
        print(e)

# create and train model
def learn2draw_create_model(model_type, new_inputName, new_inputEpochs, new_inputBacthSize, new_optimizer, new_learning_rate, delete_catego_or_not) -> str:
    try:
        # basic tests
        if new_inputName == "":
            return "name empty"

        if int(new_inputEpochs) < 1 or int(new_inputBacthSize) < 1 or float(new_learning_rate) < 0.0:
            return "epochs_or_batchsize_or_learning_rate_too_low"

        my_params = "batch_size;"+new_inputBacthSize+";optimizer;"+new_optimizer+";learning_rate;"+new_learning_rate

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
    
        Base = declarative_base()

        class Model(Base):
            __tablename__ = 'models'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            name = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            epochs = sqlalchemy.Column(sqlalchemy.Integer)
            accuracy = sqlalchemy.Column(sqlalchemy.Float)
            loss = sqlalchemy.Column(sqlalchemy.Float)
            val_accuracy = sqlalchemy.Column(sqlalchemy.Float)
            val_loss = sqlalchemy.Column(sqlalchemy.Float)
            params = sqlalchemy.Column(sqlalchemy.String(length=800), nullable=False)
            time = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            categories_handled = sqlalchemy.Column(sqlalchemy.String(length=800), nullable=False)

         
            def __repr__(self):
                return "<Model(name='{0}', epochs='{1}', accuracy='{2}', loss='{3}',val_accuracy='{4}', val_loss='{5}', params='{6}', time='{7}'>"\
                .format(self.name, self.epochs, self.accuracy,
                  self.loss, self.val_accuracy, self.val_loss, self.params, self.time, self.categories_handled)


        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()
            
        my_new_model = Model(name=model_type+"_"+new_inputName, epochs=new_inputEpochs, accuracy=0.0, loss=0.0, val_accuracy=0.0, val_loss=0.0, params=my_params, time="0", categories_handled="nothing")
        session.add(my_new_model)
        session.commit()

        # create and train the model, save in .h5 on specific folder
        if model_type == "cnn" :
            create_model = my_models.create_and_train_cnn_model(model_type+"_"+new_inputName, int(new_inputEpochs), int(new_inputBacthSize), new_optimizer, float(new_learning_rate), "is_not_update", delete_catego_or_not)
        else:
            create_model = my_models.create_and_train_mlp_model(model_type+"_"+new_inputName, int(new_inputEpochs), int(new_inputBacthSize), new_optimizer, float(new_learning_rate), "is_not_update", delete_catego_or_not)
        print("create model ? => ", create_model)
        # if everything is good continue, else send error message
        if "True" not in create_model:
            return "error_" + create_model

        # return all cateogories used to create the model inside the create_model var

        splited_result = create_model.split(";")
        # update current record to put results
        session.query(Model).filter(Model.name == model_type+"_"+new_inputName).update({Model.epochs: new_inputEpochs, Model.accuracy: splited_result[1], Model.loss: splited_result[2], Model.val_accuracy: splited_result[3], Model.val_loss: splited_result[4], Model.params: my_params, Model.time: splited_result[5], Model.categories_handled: splited_result[6]})
        session.commit()

        return create_model
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "Duplicate entry" in str(e):
            if "for key \'models.name\'" in str(e):
                print("send dupplicate username error")
                return "modelname_already_exist"
            else:
                print("send dupplicate email error")
                return "email_already_exist"

        print(e)
        return "False in create model"

# delete model in the database and in the models folders
def learn2draw_delete_model(model_name) -> str:
    try:

        if model_name == "":
            return "empty_model"

        if model_name == "default":
            return "cant_delete_or_modify_native_model"

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        
        my_name = model_name
    
        Base = declarative_base()

        class Model(Base):
            __tablename__ = 'models'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            name = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            epochs = sqlalchemy.Column(sqlalchemy.Integer)
            accuracy = sqlalchemy.Column(sqlalchemy.Float)
            loss = sqlalchemy.Column(sqlalchemy.Float)
            val_accuracy = sqlalchemy.Column(sqlalchemy.Float)
            val_loss = sqlalchemy.Column(sqlalchemy.Float)
            params = sqlalchemy.Column(sqlalchemy.String(length=800), nullable=False)
            time = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            categories_handled = sqlalchemy.Column(sqlalchemy.String(length=800), nullable=False)

         
            def __repr__(self):
                return "<Model(name='{0}', epochs='{1}', accuracy='{2}', loss='{3}',val_accuracy='{4}', val_loss='{5}', params='{6}', time='{7}'>"\
                .format(self.name, self.epochs, self.accuracy,
                  self.loss, self.val_accuracy, self.val_loss, self.params, self.time, self.categories_handled)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        session.query(Model).filter(Model.name == my_name).delete()
        session.commit()

        # now that the model is deleted from the database, delete it in the models folder and in static/models folder
        shutil.rmtree("static/models/"+my_name)
        current_model = [f for f in os.listdir("models/") if f.endswith('.h5') and ("current_"+my_name+".h5") in f]
        print("current_model = ", current_model)
        if current_model != []:
            # destroy model
            os.remove("models/current_"+my_name+".h5")

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "foreign key constraint" in str(e):
            if "fk_DRAWINGS_USERS_idx" in str(e):
                print("User doesn't exist")
                return "user_doesnt_exist"
            else:
                print("category doesn't exist")
                return "category_doesnt_exist"

        print(e)
        return "False"


# update and train model
def learn2draw_update_model(model_type, new_inputName, new_inputEpochs, new_inputBacthSize, new_optimizer, new_learning_rate, delete_catego_or_not) -> str:
    try:
        # basic tests
        if new_inputName == "":
            return "name empty"

        if new_inputName == "default":
            return "cant_delete_or_modify_native_model"

        if int(new_inputEpochs) < 1 or int(new_inputBacthSize) < 1 or float(new_learning_rate) < 0.0:
            return "epochs_or_batchsize_or_learning_rate_too_low"

        my_params = "batch_size;"+new_inputBacthSize+";optimizer;"+new_optimizer+";learning_rate;"+new_learning_rate

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
    
        Base = declarative_base()

        class Model(Base):
            __tablename__ = 'models'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            name = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            epochs = sqlalchemy.Column(sqlalchemy.Integer)
            accuracy = sqlalchemy.Column(sqlalchemy.Float)
            loss = sqlalchemy.Column(sqlalchemy.Float)
            val_accuracy = sqlalchemy.Column(sqlalchemy.Float)
            val_loss = sqlalchemy.Column(sqlalchemy.Float)
            params = sqlalchemy.Column(sqlalchemy.String(length=800), nullable=False)
            time = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            categories_handled = sqlalchemy.Column(sqlalchemy.String(length=800), nullable=False)

         
            def __repr__(self):
                return "<Model(name='{0}', epochs='{1}', accuracy='{2}', loss='{3}',val_accuracy='{4}', val_loss='{5}', params='{6}', time='{7}'>"\
                .format(self.name, self.epochs, self.accuracy,
                  self.loss, self.val_accuracy, self.val_loss, self.params, self.time, self.categories_handled)


        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()
            

        session.query(Model).filter(Model.name == new_inputName).update({Model.epochs: new_inputEpochs, Model.accuracy: 0.0, Model.loss: 0.0, Model.val_accuracy: 0.0, Model.val_loss: 0.0, Model.params: my_params, Model.time: "0"})
        session.commit()

        # create and train the model, save in .h5 on specific folder (delete old one before)
        if model_type == "cnn" :
            create_model = my_models.create_and_train_cnn_model(new_inputName, int(new_inputEpochs), int(new_inputBacthSize), new_optimizer, float(new_learning_rate), "is_update", delete_catego_or_not)
        else:
            create_model = my_models.create_and_train_mlp_model(new_inputName, int(new_inputEpochs), int(new_inputBacthSize), new_optimizer, float(new_learning_rate), "is_update", delete_catego_or_not)
        print("create model ? => ", create_model)
        # if everything is good continue, else send error message
        if "True" not in create_model:
            return "error_" + create_model

        splited_result = create_model.split(";")
        # update current record to put results
        session.query(Model).filter(Model.name == new_inputName).update({Model.epochs: new_inputEpochs, Model.accuracy: splited_result[1], Model.loss: splited_result[2], Model.val_accuracy: splited_result[3], Model.val_loss: splited_result[4], Model.params: my_params, Model.time: splited_result[5], Model.categories_handled: splited_result[6]})
        session.commit()

        # if updated model where the current model, replace it
        current_model = [f for f in os.listdir("models/") if f.endswith('.h5') and ("current_"+new_inputName+".h5") in f]
        print("current_model = ", current_model)
        if current_model != []:
            print("replacing current model ...")
            # destroy model
            os.remove("models/current_"+new_inputName+".h5")
            # copy h5 model in the right folder and rename it to "current_modelName"
            shutil.copy2("static/models/"+new_inputName+"/"+new_inputName+".h5", "models/current_"+new_inputName+".h5")


        return "True"
        #return create_model if you want to send many data
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "Duplicate entry" in str(e):
            if "for key \'models.name\'" in str(e):
                print("send dupplicate username error")
                return "modelname_already_exist"
            else:
                print("send dupplicate email error")
                return "email_already_exist"

        print(e)
        return "False"


def change_current_model(model_name) -> str:
    print("model_name : ", model_name)

    # check if .h5 file exist
    h5_model = os.path.exists("static/models/"+model_name+"/"+model_name+".h5");
    if h5_model == False:
        return "Problem ! The model doesn't exist"

    # check if the model doesn't predict on too much categories (one that is isn't in bdd at least)
    categories_infos = learn2draw_list_all_categories()

    # get categories handled by the model
    categories_handled = learn2draw_get_categories_handled_for_one_model(model_name)
    print("categories_infos ", categories_infos)
    print("categories_handled ", categories_handled)
    categories_handled = categories_handled.split(",")

    bdd_categories = []
    for elt in categories_infos:
        elt = elt.split(";")
        bdd_categories.append(elt[0])
    print("bdd catego ", bdd_categories)

    # transfrom in subset, if all categories handled exist, the model can become current
    set1 = set(categories_handled)
    set2 = set(bdd_categories)

    is_subset = set1.issubset(set2)

    if is_subset == False:
        return "This_model_predict_on_too_many_categories_to_become_current_update_it_please"

    # transfrom current in default model ==> finally keep default model intact
    current_model = [f for f in os.listdir("models/") if f.endswith('.h5') and "current" in f]
    print("current_model = ", current_model)
    if current_model != []:
        # rename old model (will become new default model)
        print("current model was ", current_model[0], " deleting hi, we could also change it to default ? ")
        os.remove("models/"+current_model[0])
        # os.rename("models/"+current_model[0], "models/defaul.h5")

        # copy h5 model in the right folder and rename it to "current_modelName"
        shutil.copy2("static/models/"+model_name+"/"+model_name+".h5", "models/current_"+model_name+".h5")
        
        # delete default file and rename defaul to default (now it"s secure because predictions have a usable model)
        # os.remove("models/default.h5")
        # os.rename("models/defaul.h5", "models/default.h5")
    else:
        # only need to copy the model and rename it
        shutil.copy2("static/models/"+model_name+"/"+model_name+".h5", "models/current_"+model_name+".h5")

    return "True"

# create a npy dataset with all images test (tortue)
def create_npy_dataset(category_id, category) -> str:
    print("\ncreate npy dataset\n")
    try:
        # category is fixed here, next we will have to distinguish different categories
        #category = "tortue"

        db_connection = create_engine(create_engine_db())
        list_draws = pd.read_sql("SELECT location FROM DRAWINGS WHERE status=4 and CATEGORIES_id=%s" % ("'" + category_id + "'"),
                           con=db_connection, index_col=None).to_dict('index')

        if bool(list_draws) == False:
            return "No records found with status 4 and category " + category
        liste = []

        print("for each image a convertion is needed (invert bitwise necessary, be carefull")

        for i in list_draws:
            # # METHOD 0 very low modifications
            # img = Image.open(list_draws[i]['location'][1:]).convert('L')
            # # # load image and handle transparency with cv2
            # # image = cv2.imread(list_draws[i]['location'][1:], cv2.IMREAD_UNCHANGED)
            # # #make mask of where the transparent bits are
            # # trans_mask = image[:,:,3] == 0
            # # #replace areas of transparency with white and not transparent
            # # image[trans_mask] = [255, 255, 255, 255]
            # im = np.array(img)
            # print("\nim before resize shape ", im.shape, "\n")
            # im = np.array(img.resize((28, 28), Image.ANTIALIAS))#.flatten()
            
            # print("\nim shape ", im.shape, "\n") 
            # print("i = ", i, "elt = ", list_draws[i]['location']," type = ", type(i))
            
            # if i == 995:
            #     print("img 995 = \n", im)


            # liste.append(im.flatten())

            # METHOD 1, few modifications
            # img = Image.open(list_draws[i]['location'][1:]).convert('L')
            # # # load image and handle transparency with cv2
            # # image = cv2.imread(list_draws[i]['location'][1:], cv2.IMREAD_UNCHANGED)
            # # #make mask of where the transparent bits are
            # # trans_mask = image[:,:,3] == 0
            # # #replace areas of transparency with white and not transparent
            # # image[trans_mask] = [255, 255, 255, 255]
            # im = np.array(img)
            # print("\nim before resize shape ", im.shape, "\n")
            # im = np.array(img.resize((28, 28), Image.ANTIALIAS)).flatten()
            # # im = im.astype('float32')
            # # im /= 255
            # # #print("im : \n", im)
            # # im = np.where(im==1, 0, im)

            
            # print("\nim shape ", im.shape, "\n") 
            # print("i = ", i, "elt = ", list_draws[i]['location']," type = ", type(i))
            
            # if i == 995:
            #     print("img 995 = \n", im)

            # liste.append(im)


            # METHOD 2 modifications like in predict mode
            img = Image.open(list_draws[i]['location'][1:]).convert('L')
            # # load image and handle transparency with cv2
            # image = cv2.imread(list_draws[i]['location'][1:], cv2.IMREAD_UNCHANGED)
            # #make mask of where the transparent bits are
            # trans_mask = image[:,:,3] == 0
            # #replace areas of transparency with white and not transparent
            # image[trans_mask] = [255, 255, 255, 255]
            im = np.array(img)
            print("\nim before resize shape ", im.shape, "\n")
            im = np.array(img.resize((28, 28), Image.ANTIALIAS))#.flatten()
            im = im.reshape(1,im.shape[0],im.shape[1],1)
            im = im.astype('float32') ##normalize image
            im /= 255
            #print("im : \n", im)
            im = np.where(im==1, 0, im)
            # im = im.astype('float32')
            # im /= 255
            # #print("im : \n", im)
            # im = np.where(im==1, 0, im)

            
            print("\nim shape ", im.shape, "\n") 
            print("i = ", i, "elt = ", list_draws[i]['location']," type = ", type(i))
            
            if i == 995:
                print("img 995 = \n", im)


            liste.append(im.flatten())

            # METHOD 3 many modifications, good looking on jupyter but not working here
            # new_width  = 28
            # new_height = 28
            
            # img = Image.open(list_draws[i]['location'][1:]).convert('L')
        
            # img = img.resize((new_width, new_height), Image.ANTIALIAS)
            # img = image.img_to_array(img)
            # #img = cv2.bitwise_not(img)
            # img = img.astype('float32')

            # img = img.reshape(1,img.shape[0],img.shape[1],1)
            # print("new shape for predict : ", img.shape)
            # img = 255 - img
            # img /= 255
            # print("new shap ", img.shape)

            # #im = cv2.bitwise_not(im)

            # img = np.where(img > 0.05, img+0.75, img)
            # img = np.where(img > 0.999, 0.99000001, img)
            # img = img.reshape(28,28).flatten()

            
            # print("\nimg shape ", img.shape, "\n") 
            # print("i = ", i, "elt = ", list_draws[i]['location']," type = ", type(i))
            
            # if i == 995:
            #     print("img 995 = \n", img)

            # liste.append(img)

            # line = "{}".format(list_draws['location'][i])
            # print("LINE = ", line)
            # liste.append(line)

        #change format and transform to numpy dataset (npy)
        liste = np.asarray(liste)
        print(type(liste), "shape = ", liste.shape)

        #save npy file and return true
        print("save npy file in a dataset file, if it already exist, read it, merge and save")
        
        # collect datasets filenames
        print("cwd = ", os.getcwd())
        data_path = "models/dataset_quickdraw/"
        for (dirpath, dirnames, filenames) in os.walk(data_path):
             pass # filenames accumulate in list 'filenames'
        print(filenames)

        if category+".npy" in filenames:
            print("\nload + merge + save\n")
            # load current npy
            current_npy = np.load("models/dataset_quickdraw/"+category+".npy")
            print("npy shape = ", current_npy.shape)
            print("npy 0 shape = ", current_npy[42].shape)

            print("my new npy shape = ", liste.shape)
            print("my new npy 0 shape = ", liste[0].shape)

            merged_npy = np.concatenate([current_npy, liste], axis=0)
            print("merge npy = ", merged_npy.shape, "\n")
            liste = merged_npy


        print("\nsave to .npy file\n")
        np.save("models/dataset_quickdraw/"+category+".npy", liste)

        return "True"

    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        return str(e)


def get_all_badge() -> pd.DataFrame:

    db_connection = create_engine(create_engine_db())
    badges = pd.read_sql("SELECT * FROM TROPHEE", con=db_connection, index_col=None)

    return badges

# functions to change profile of user (connected page)
def change_user_password(user_username, user_old_password, user_new_password) -> str:
    try:
        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        
        # check if user entered the good password
        old_password = pd.read_sql("SELECT pwd FROM USERS WHERE username = %s" % ("'" + user_username + "'"),
                           con=db_connection, index_col=None).to_dict()

        print("old pass ?? ", old_password["pwd"][0])
        if old_password["pwd"][0] != user_old_password:
            return "this_is_not_your_current_password"

        Base = declarative_base()

        class User(Base):
            __tablename__ = 'users'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            username = sqlalchemy.Column(sqlalchemy.String(length=50), unique=True, nullable=False)
            email = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            pwd = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            admin = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            count_notation = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<User(username='{0}', email='{1}', pwd='{2}', admin='{3}',score='{4}', count_notation='{5}')>"\
                .format(self.username, self.email, self.pwd,
                  self.admin, self.score, self.count_notation)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        session.query(User).filter(User.username == user_username, User.pwd == user_old_password).update({User.pwd: user_new_password})
        #session.query(User).filter(User.username == infos[0], User.email == infos[1]).update({User.username: new_username}, {User.email: new_email})
        #print("error handle ? : ", test)
        session.commit()

        # metadata = MetaData()
        # users = Table('users', metadata,
        #     Column('id', Integer, primary_key=True),
        #     Column('username', String(50), nullable=False),
        #     Column('email', String(100), username nullable=False),
        #     Column('pwd', String(40), nullable=False),
        #     Column('admin', Integer, nullable=False),
        #     Column('score', Integer, nullable=False)
        # )



        # jwk_user = User(username="user_test", email="user_test@gmail.com", pwd="aqwzsx",
        # admin=0, score=0)
        # session.add(jwk_user)
        # session.commit()

        print("BILLY C TOI ?")

        # # user = pd.read_sql("SELECT * FROM USERS WHERE username = %s AND email = %s" % ("'" + infos[0] + "'", "'" + infos[1] + "'")
        # #     ,con=db_connection, index_col=None)
        # df_user = pd.read_sql("SELECT * FROM USERS" 
        #     ,db_connection)
        # #df_user = pd.DataFrame(user, index=[None])
        # df_user[df_user['username'] == "arnaudsimon091@gmail.coma", "username"] = new_username
        # print("SUIS JE BEAU ?")
        # df_user.to_sql('USERS', db_connection, if_exists='replace')


        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "Duplicate entry" in str(e):
            if "for key \'users.username\'" in str(e):
                print("send dupplicate username error")
                return "username_already_exist"
            else:
                print("send dupplicate email error")
                return "email_already_exist"

        print(e)
        return str(e)
        #return "False"

def change_user_infos(user_username, user_new_username, user_new_email) -> str:
    try:
        
        print("request.bdd, change user infos")
        print("types of current var")
        print("new username = ", user_new_username, type(user_new_username), "new_email = ", user_new_email, type(user_new_email))
        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        Base = declarative_base()

        class User(Base):
            __tablename__ = 'users'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            username = sqlalchemy.Column(sqlalchemy.String(length=50), unique=True, nullable=False)
            email = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            pwd = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            admin = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            count_notation = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<User(username='{0}', email='{1}', pwd='{2}', admin='{3}',score='{4}', count_notation='{5}')>"\
                .format(self.username, self.email, self.pwd,
                  self.admin, self.score, self.count_notation)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        session.query(User).filter(User.username == user_username).update({User.username: user_new_username, User.email: user_new_email})
        #print("error handle ? : ", test)
        session.commit()

        print("BILLY C TOI ?")

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "Duplicate entry" in str(e):
            if "for key \'users.username\'" in str(e):
                print("send dupplicate username error")
                return "username_already_exist"
            else:
                print("send dupplicate email error")
                return "email_already_exist"

        print(e)
        return str(e)
        #return "False"

def add_points_to_user(username, points_to_add) -> str:
    try:
        

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        Base = declarative_base()

        class User(Base):
            __tablename__ = 'users'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            username = sqlalchemy.Column(sqlalchemy.String(length=50), unique=True, nullable=False)
            email = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            pwd = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            admin = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            count_notation = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<User(username='{0}', email='{1}', pwd='{2}', admin='{3}',score='{4}', count_notation='{5}')>"\
                .format(self.username, self.email, self.pwd,
                  self.admin, self.score, self.count_notation)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        
        # get current score
        #db_connection = create_engine(create_engine_db())
        current_score = pd.read_sql("SELECT score FROM USERS WHERE username = %s" % ("'" + username + "'"),
                         con=db_connection, index_col=None)
        
        print("types : ", type(current_score["score"][0]), " ", type(points_to_add))
        print("score_final = ",int(current_score["score"][0]) + points_to_add)
        score_final = int(current_score["score"][0]) + points_to_add
        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        session.query(User).filter(User.username == username).update({User.score: score_final})
        #session.query(User).filter(User.username == infos[0], User.email == infos[1]).update({User.username: new_username}, {User.email: new_email})
        #print("error handle ? : ", test)
        session.commit()
        return score_final
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))
        return str(e)

def dataset_exist_for_category(category) -> str:
    try:
        db_connection = create_engine(create_engine_db())
        dataset_exist = pd.read_sql("SELECT dataset_available FROM CATEGORIES WHERE name = %s" % ("'" + category + "'"),
                         con=db_connection, index_col=None)
        print("dataset available ? == ", dataset_exist["dataset_available"][0])
        return str(dataset_exist["dataset_available"][0])
    except Exception as e:
        print("on a récup l'exception ;) dans exist for category \n, type e = ", type(e))
        print("try str ==> ", str(e))
        return str(e)

def get_last_drawing_made(user_id) -> str:
    try:
        db_connection = create_engine(create_engine_db())
        #LIMIT 1 OFFSET 0 DESC;"
        last_drawing = pd.read_sql("SELECT * FROM DRAWINGS WHERE USERS_id = %s ORDER BY id DESC Limit 1;" % ("'" + user_id + "'"),
                           con=db_connection, index_col=None).to_dict()
        print("last drawing : ", last_drawing)
        last_drawing = str(last_drawing["id"][0]) + ";"+ str(last_drawing["CATEGORIES_id"][0]) + ";" + \
        str(last_drawing["CATEGORIES_PREDICTED_id"][0]) + ";" + str(last_drawing["location"][0]) + ";" + \
        str(last_drawing["status"][0]) + ";" + str(last_drawing["score"][0]) + ";" + \
        str(last_drawing["score_by_votes"][0]) + ";" + str(last_drawing["time"][0])
        return last_drawing
    except Exception as e:
        print("on a récup l'exception get last drawing made ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))
        return str(e)

def get_drawing_voted(drawing_location) -> str:
    try:
        print("welcome to get drawing voted, location = ", drawing_location)
        db_connection = create_engine(create_engine_db())
        #LIMIT 1 OFFSET 0 DESC;"
        last_drawing = pd.read_sql("SELECT id, USERS_id, CATEGORIES_id FROM DRAWINGS WHERE location = %s;" % ("'" + drawing_location + "'"),
                           con=db_connection, index_col=None).to_dict()
        
        last_drawing = str(last_drawing["id"][0]) + ";" + str(last_drawing["USERS_id"][0]) + ";" + str(last_drawing["CATEGORIES_id"][0])

        return last_drawing

    except Exception as e:
        print("on a récup l'exception get drawing voted ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))
        print("last draw before end : ", last_drawing)
        return str(e)

def add_one_notation_point_to_user(current_user_id) -> str:
    try:
        print("\nwelcome to add one notation point to user ", current_user_id,"\n")
        db_connection = create_engine(create_engine_db())
        Base = declarative_base()

        count = pd.read_sql("SELECT count_notation FROM USERS WHERE id = %s;" % ("'" + current_user_id + "'"),
                       con=db_connection, index_col=None)

        count = count["count_notation"][0]

        class User(Base):
            __tablename__ = 'users'
         
            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            username = sqlalchemy.Column(sqlalchemy.String(length=50), unique=True, nullable=False)
            email = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
            pwd = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            admin = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            count_notation = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<User(username='{0}', email='{1}', pwd='{2}', admin='{3}',score='{4}', count_notation='{5}')>"\
                .format(self.username, self.email, self.pwd,
                  self.admin, self.score, self.count_notation)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        my_session = sqlalchemy.orm.sessionmaker()
        my_session.configure(bind=db_connection)
        my_session = my_session()

        my_session.query(User).filter(User.id == current_user_id).update({User.count_notation: int(count)+1})
        my_session.commit()
        #my_session.query(Drawing).filter(Drawing.id == drawing_id).update({Drawing.status: update_status, Drawing.score_by_votes: yes_votes})
        return "ok"

    except Exception as e:
        print("on a récup l'exception add one notation point to user ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))
        return str(e)

def one_hundred_votes_update(drawing_id, drawing_user_id, current_user_id) -> str:
    try:
        print("welcome to one hundred votes update, drawing id = ", drawing_id, " drawing user id = ", drawing_user_id)
        db_connection = create_engine(create_engine_db())
        #LIMIT 1 OFFSET 0 DESC;"
        votes = pd.read_sql("SELECT count(id) as nb_votes FROM notations WHERE DRAWINGS_id = %s;" % ("'" + drawing_id + "'"),
                           con=db_connection, index_col=None).to_dict()

        print("votes ", votes)
        if votes["nb_votes"][0] == 100:
            print("Time to update status and score of the drawing + update score of winners in one hundred func")
            # get all yes votes and all users who voted yes
            yes_votes = pd.read_sql("SELECT count(id) as nb_votes_yes FROM notations WHERE DRAWINGS_id = %s and score =%s;" % ("'" + drawing_id + "'", "'" + "yes" + "'"),
                           con=db_connection, index_col=None).to_dict()

            yes_users = pd.read_sql("SELECT USERS_id FROM notations WHERE DRAWINGS_id = %s and score =%s;" % ("'" + drawing_id + "'", "'" + "yes" + "'"),
                           con=db_connection, index_col=None).to_dict()
            no_users = pd.read_sql("SELECT USERS_id FROM notations WHERE DRAWINGS_id = %s and score =%s;" % ("'" + drawing_id + "'", "'" + "no" + "'"),
                           con=db_connection, index_col=None).to_dict()

            # keep all ids of yes voters and no voters (to update their score if they win)
            print("yes user type ", type(yes_users))
            yes_users = yes_users["USERS_id"]
            dictList = []
            for key, value in yes_users.items():
                dictList.append(value)

            yes_users = dictList


            no_users = no_users["USERS_id"]
            dictList = []
            for key, value in no_users.items():
                dictList.append(value)

            no_users = dictList


            yes_votes = yes_votes["nb_votes_yes"][0]
            
            # define class and session to do db transformations
            up_session_score = 0 # if current user have win, update the session variable
            Base = declarative_base()

            class Drawing(Base):
                __tablename__ = 'drawings'
             
                id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
                users_id = sqlalchemy.Column(sqlalchemy.Integer)
                categories_id = sqlalchemy.Column(sqlalchemy.Integer)
                categories_predicted_id = sqlalchemy.Column(sqlalchemy.Integer)
                location = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
                status = sqlalchemy.Column(sqlalchemy.Integer)
                score = sqlalchemy.Column(sqlalchemy.Integer)
                score_by_votes = sqlalchemy.Column(sqlalchemy.Integer)
                time = sqlalchemy.Column(sqlalchemy.Integer)
             
                def __repr__(self):
                    return "<Drawing(users_id='{0}', categories_id='{1}', categories_predicted_id='{2}', location='{3}', status='{4}', score='{5}', time='{6}')>"\
                    .format(self.users_id, self.categories_id, self.categories_predicted_id, self.location,
                      self.status, self.score, self.score_by_votes, self.time)
            
            class User(Base):
                __tablename__ = 'users'
             
                id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
                username = sqlalchemy.Column(sqlalchemy.String(length=50), unique=True, nullable=False)
                email = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
                pwd = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
                admin = sqlalchemy.Column(sqlalchemy.Integer)
                score = sqlalchemy.Column(sqlalchemy.Integer)
                count_notation = sqlalchemy.Column(sqlalchemy.Integer)
             
                def __repr__(self):
                    return "<User(username='{0}', email='{1}', pwd='{2}', admin='{3}',score='{4}', count_notation='{5}')>"\
                    .format(self.username, self.email, self.pwd,
                      self.admin, self.score, self.count_notation)

            # create base
            Base.metadata.create_all(db_connection)

            # create session
            my_session = sqlalchemy.orm.sessionmaker()
            my_session.configure(bind=db_connection)
            my_session = my_session()

            # if yes votes < 50, users who voted no will earn points 
            if yes_votes <= 50:
                print("vote no wins")
                print("all id of winner : ", no_users)
                # request to add points for "no" votes
                my_session.query(User).filter(User.id.in_(no_users)).update({User.score: (User.score + (100-int(yes_votes)))}, synchronize_session='fetch')
                my_session.commit()

                # if current user was in the no_user group, change the score session value
                print("NO USER DATA TYPE ", type(no_users[0]), type(no_users))
                print("current user id ", current_user_id, " type ", type(int(current_user_id)))
                
                if int(current_user_id) in no_users:
                    print("current user in no group")
                    up_session_score = 100 - int(yes_votes)

            # if yes_vote > 50, users who voted yes will earn points
            else:
                print("vote yes wins")
                print("all id of winner : ", yes_users)
                # request to add points for "yes" votes
                my_session.query(User).filter(User.id.in_(yes_users)).update({User.score: (User.score + int(yes_votes))}, synchronize_session='fetch')
                my_session.commit()

                # if current user was in the yes_user group, change the score session value
                print("YES USER DATA TYPE ", type(yes_users[0]), type(yes_users))
                print("current user id ", current_user_id, " type ", type(int(current_user_id)))
                
                if int(current_user_id) in yes_users:
                    print("current user in yes group")
                    up_session_score = int(yes_votes)
                    

            # update score and status of drawing

            # check for update status, by default image will not be keeped to create datasets
            update_status = 2 
            if yes_votes >= 90:
                update_status = 3 # keep image for atasets if many yes

                
            my_session.query(Drawing).filter(Drawing.id == drawing_id).update({Drawing.status: update_status, Drawing.score_by_votes: yes_votes})
            my_session.commit()

            # update points of the user who made the drawing (whatever the score, must be thankfull for the participation)
            current_score = pd.read_sql("SELECT score FROM USERS WHERE id = %s" % ("'" + drawing_user_id + "'"),
                         con=db_connection, index_col=None)
            print("current score = ", current_score["score"][0])
            score_final = int(current_score["score"][0]) + yes_votes
            print("final score = ", score_final)
            my_session.query(User).filter(User.id == drawing_user_id).update({User.score: score_final})
            my_session.commit()

            # delete all notations for this drawing

            return str(up_session_score)+";"+str(update_status)

        return "no_update;1"

    except Exception as e:
        print("on a récup l'exception one hundred votes ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))
        return str(e)


def check_thousand_good_images(drawing_category_id) -> str:
    try:
        print("welcome to check thousand good image, drawing category id = ", drawing_category_id)
        db_connection = create_engine(create_engine_db())
        # first count number of "good images" for this category (eq status == 3)

        nb_good_images = pd.read_sql("SELECT count(id) as nb_good_img FROM drawings WHERE CATEGORIES_id = %s and status = 3;" % ("'" + drawing_category_id + "'"),
                           con=db_connection, index_col=None).to_dict()

        if nb_good_images["nb_good_img"][0] >= 1000:
            print("enough images, create a custom npy dataset, but first update status 3 in status 4")

            Base = declarative_base()

            class Drawing(Base):
                __tablename__ = 'drawings'
             
                id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
                users_id = sqlalchemy.Column(sqlalchemy.Integer)
                categories_id = sqlalchemy.Column(sqlalchemy.Integer)
                categories_predicted_id = sqlalchemy.Column(sqlalchemy.Integer)
                location = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
                status = sqlalchemy.Column(sqlalchemy.Integer)
                score = sqlalchemy.Column(sqlalchemy.Integer)
                score_by_votes = sqlalchemy.Column(sqlalchemy.Integer)
                time = sqlalchemy.Column(sqlalchemy.Integer)
             
                def __repr__(self):
                    return "<Drawing(users_id='{0}', categories_id='{1}', categories_predicted_id='{2}', location='{3}', status='{4}', score='{5}', time='{6}')>"\
                    .format(self.users_id, self.categories_id, self.categories_predicted_id, self.location,
                      self.status, self.score, self.score_by_votes, self.time)

            class Category(Base):
                __tablename__ = 'categories'
             
                id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
                name = sqlalchemy.Column(sqlalchemy.String(length=100), unique=True, nullable=False)
                dataset_available = sqlalchemy.Column(sqlalchemy.Integer)
             
                def __repr__(self):
                    return "< Category(id='{0}', name='{1}', dataset_available='{2}')>"\
                    .format(self.id, self.name, self.dataset_available)

            # create base
            Base.metadata.create_all(db_connection)

            # create session
            my_session = sqlalchemy.orm.sessionmaker()
            my_session.configure(bind=db_connection)
            my_session = my_session()

            print("updating drawing status")
            my_session.query(Drawing).filter(Drawing.status == 3).update({Drawing.status: 4})
            my_session.commit()

            print("now merge all images with status 4 in this category in an npy file")
            # get name of category first 
            current_catego_name = pd.read_sql("SELECT name FROM CATEGORIES WHERE id = %s" % ("'" + drawing_category_id + "'"),
                con=db_connection, index_col=None)

            current_catego_name = current_catego_name["name"][0]
            print("current catego name = ", current_catego_name)

            merge = create_npy_dataset(drawing_category_id, current_catego_name)

            # when dataset created, update dataset_available (category attribute) to one, dataset will be open to predictions
            print("now update dataset_available attribute to 1")
            my_session.query(Category).filter(Category.name == current_catego_name).update({Category.dataset_available: 1})
            my_session.commit()


            # if merge != "True":
            #     return "erreur;"+merge

            return merge

        else:
            print("not enough image (", nb_good_images["nb_good_img"][0],"), return to app.py")
            return "nothing"

        return "ok"

    except Exception as e:
        print("on a récup l'exception dans check thousand images ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))
        return str(e)