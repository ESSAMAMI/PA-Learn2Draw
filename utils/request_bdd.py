from configparser import ConfigParser
from sqlalchemy import create_engine, update, Table, Column, MetaData
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
import pandas as pd

def create_engine_db() -> str:
    config = ConfigParser()
    config.read("D:\\Projets_annuels\\PA4A\\PA-Learn2Draw\\utils\\config.ini")

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

        list_draws = pd.read_sql("SELECT * FROM DRAWINGS WHERE USERS_id != %s AND status=0" % ("'" + str(user_id['id'][0]) + "'"),
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
            category_name = pd.read_sql("SELECT name FROM CATEGORYS WHERE id = %s" % ("'" + str(list_draws[i]['CATEGORYS_id']) + "'"),
                           con=db_connection, index_col=None).to_dict()
            list_draws[i]['CATEGORYS_id'] = category_name['name'][0]

            user_name = pd.read_sql(
                "SELECT username FROM USERS WHERE id = %s" % ("'" + str(list_draws[i]['USERS_id']) + "'"),
                con=db_connection, index_col=None).to_dict()
            list_draws[i]['USERS_id'] = user_name['username'][0]

            line = "{};{};{};{};{};{}".format(list_draws[i]['USERS_id'], list_draws[i]['CATEGORYS_id'], list_draws[i]['location'],
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
        category_id = str(pd.read_sql("SELECT id FROM CATEGORYS WHERE name = %s" % ("'" + infos[1] + "'"),
                                      con=db_connection, index_col=None).to_dict()['id'][0])
        notation = {'score':score, "USERS_id":user_id, 'DRAWINGS_id':infos[5], "DRAWINGS_USERS_id":user_drawings_id, "DRAWINGS_CATEGORYS_id":category_id}

        df_notation = pd.DataFrame(notation, index=[None])
        df_notation.to_sql('NOTATIONS', db_connection, index=False, if_exists='append')

        return True

    except Exception as e:

        print(e)
        return False


# Functions for backoffice

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