from configparser import ConfigParser
from sqlalchemy import create_engine, update, Table, Column, MetaData, func
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
import pandas as pd
import numpy as np 
from PIL import Image
import cv2
from models import my_models
import os
import shutil
from datetime import datetime
import pymysql

def create_engine_db() -> str:
    config = ConfigParser()
    cwd = os.getcwd()

    config.read(cwd+"/utils/config.ini")
    #config.read("D:/Skoula/utils/config.ini")

    get_connection = 'mysql+pymysql://'\
                        + config.get('mysql', 'user')\
                        + ':' + config.get('mysql','pwd')\
                        + '@' + config.get('mysql', 'host')\
                        + '/' + config.get('mysql', 'database') + ''

    return get_connection

def learn2draw_connect(login:str, pwd:str) -> pd.DataFrame:

    db_connection = create_engine(create_engine_db())
    user = pd.read_sql("SELECT * FROM USERS WHERE email = %s AND pwd = %s" % ("'" + login + "'", "'" + pwd + "'"),
                     con=db_connection, index_col=None)

    return user

def select_top_5() -> pd.DataFrame:

    db_connection = create_engine(create_engine_db())
    top_5 = pd.read_sql("SELECT u.username, u.id, SUM(d.score) as score_model, SUM(d.score_by_votes) as score_vote, COUNT(d.USERS_id) as nb_dessins FROM drawings d INNER JOIN users u ON u.id = d.USERS_id GROUP BY d.USERS_id",
                       con=db_connection, index_col=None)

    return top_5

def count_notation_by_user(id_user) -> pd.DataFrame:

    db_connection = create_engine(create_engine_db())
    count = pd.read_sql("SELECT count(USERS_id) as count_notation FROM notations WHERE USERS_id = %s GROUP BY USERS_id" % (id_user),
                       con=db_connection, index_col=None)

    return count

def update_notation_by_user(id_user, notation) -> bool:

    query = "UPDATE users SET count_notation = %s WHERE id = %s" % (notation, id_user)

    connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='learn2draw_db',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

    return True


def learn2draw_sign_up_verif(username:str, email:str, pwd:str) -> bool:

    try:
        db_connection = create_engine(create_engine_db())
        user = pd.read_sql("SELECT * FROM USERS WHERE username = %s OR email = %s" % ("'" + username + "'", "'" + email + "'"),
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
        user = {"username": username, "email": email, "pwd": pwd, "admin": 0, "score": 0}
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

        list_draws = pd.read_sql("SELECT * FROM DRAWINGS WHERE USERS_id != %s AND status=1" % ("'" + str(user_id['id'][0]) + "'"),
                           con=db_connection, index_col=None).to_dict('index')
        print("list draws : ", list_draws)

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

            line = "{};{};{};{};{};{}".format(list_draws[i]['USERS_id'], list_draws[i]['CATEGORIES_id'], list_draws[i]['location'],
             list_draws[i]['score'], list_draws[i]['time'], list_draws[i]['id'])

            liste.append(line)

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
        users_infos = pd.read_sql("SELECT username, email, score FROM USERS",
                           con=db_connection, index_col=None).to_dict()
        #print("users infos : ", users_infos)

        liste = []

        for i in users_infos["username"]:
            #print("i = ", i)
            line = "{};{};{}".format(users_infos['username'][i], users_infos['email'][i], users_infos['score'][i])
            #print("LINE = ", line)
            liste.append(line)

        #print("USER INFOS : \n", liste)
        return liste

    except Exception as e:
        print(e)

def learn2draw_create_user(new_username, new_email, new_password, new_confirm_password) -> str:
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
         
            def __repr__(self):
                return "<User(username='{0}', email='{1}', pwd='{2}', admin='{3}',score='{4}')>"\
                .format(self.username, self.email, self.pwd,
                  self.admin, self.score)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        my_new_user = User(username=new_username, email=new_email, pwd=new_password, admin=0, score=0)
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

def learn2draw_update_user(informations:str, new_username, new_email, new_score) -> str:
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
         
            def __repr__(self):
                return "<User(username='{0}', email='{1}', pwd='{2}', admin='{3}',score='{4}')>"\
                .format(self.username, self.email, self.pwd,
                  self.admin, self.score)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        session.query(User).filter(User.username == infos[0] and User.email == infos[1]).update({User.username: new_username, User.email: new_email, User.score: new_score})
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
         
            def __repr__(self):
                return "<User(username='{0}', email='{1}', pwd='{2}', admin='{3}',score='{4}')>"\
                .format(self.username, self.email, self.pwd,
                  self.admin, self.score)

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
        print("salut")
        print("score before query = ", new_score)

        my_new_drawing = Drawing(users_id=new_user_id, categories_id=new_category_id, categories_predicted_id= new_category_predicted_id, location=new_location, status=new_status, score=new_score, score_by_votes=new_score_by_votes, time=new_time)
        session.add(my_new_drawing)
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

def learn2draw_update_drawing(informations:str, new_user_id, new_category_id, new_category_predicted_id, new_location, new_status, new_score, new_score_by_votes, new_time) -> str:
    try:
        if int(new_status) < 0 or int(new_score) < 0 or int(new_time) < 0:
            return "status / score / time should be >= 0"

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        infos=informations.split(';')

        print("infos 0 ", infos[0], " infos 1 ", infos[1])
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
        categories_infos = pd.read_sql("SELECT id, name FROM CATEGORIES",
                           con=db_connection, index_col=None).to_dict()
        #print("users infos : ", users_infos)

        liste = []

        for i in categories_infos["name"]:
            #print("i = ", i)
            line = "{};{}".format(categories_infos['name'][i], categories_infos['id'][i])
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
         
            def __repr__(self):
                return "<Category(name='{0}')>"\
                .format(self.name)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        my_new_category = Category(name=new_category)
        session.add(my_new_category)
        session.commit()

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
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
         
            def __repr__(self):
                return "<Category(name='{0}')>"\
                .format(self.name)

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
         
            def __repr__(self):
                return "<Category(name='{0}')>"\
                .format(self.name)

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
def create_npy_dataset() -> str:
    print("create npy dataset")
    try:
        # category is fixed here, next we will have to distinguish different categories
        category = "tortue"

        db_connection = create_engine(create_engine_db())
        list_draws = pd.read_sql("SELECT location FROM DRAWINGS WHERE status=3",
                           con=db_connection, index_col=None).to_dict('index')

        if bool(list_draws) == False:
            return "No records found with status 3"
        liste = []

        #print("list draws = ", list_draws, "\n\n type ", type(list_draws))
        # collect each image in numpy array


        # print("img name = ", list_draws[0]['location'][1:])
        # img = Image.open(list_draws[0]['location'][1:]).convert('L')
        # im = np.array(img)
        # print("np shape = ", im.shape)
        # new_width  = 28
        # new_height = 28
        # im = np.array(img.resize((new_width, new_height), Image.ANTIALIAS))
        # print("new np shape = ", im.shape)


        for i in list_draws:
            img = Image.open(list_draws[i]['location'][1:]).convert('L')
            im = np.array(img)
            im = np.array(img.resize((28, 28), Image.ANTIALIAS)).flatten()
            print("\nim shape ", im.shape, "\n") 
            print("i = ", i, "elt = ", list_draws[i]['location']," type = ", type(i))
            
            liste.append(im)
            # line = "{}".format(list_draws['location'][i])
            # print("LINE = ", line)
            # liste.append(line)

        #change format and transform to numpy dataset (npy)
        liste = np.asarray(liste)
        print(type(liste), "shape = ", liste.shape)

        #save npy file and return true
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