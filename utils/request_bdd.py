from configparser import ConfigParser
from sqlalchemy import create_engine, update, Table, Column, MetaData
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
import pandas as pd

def create_engine_db() -> str:
    config = ConfigParser()
    config.read("C:\\Users\\arnau\\git_projects\\projets_annuels\\PA4A\\PA-Learn2Draw\\utils\\config.ini")
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
        drawings_infos = pd.read_sql("SELECT id, USERS_id, CATEGORIES_id, status, score, time FROM DRAWINGS",
                           con=db_connection, index_col=None).to_dict()
        #print("users infos : ", users_infos)

        liste = []

        for i in drawings_infos["USERS_id"]:
            #print("i = ", i)
            line = "{};{};{};{};{};{}".format(drawings_infos['id'][i], drawings_infos['USERS_id'][i], drawings_infos['CATEGORIES_id'][i], drawings_infos['status'][i], drawings_infos['score'][i], drawings_infos['time'][i])
            #print("LINE = ", line)
            liste.append(line)

        #print("USER INFOS : \n", liste)
        return liste

    except Exception as e:
        print(e)

def learn2draw_create_drawing(new_user_id, new_category_id, new_location, new_status, new_score, new_time) -> str:
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
            location = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            status = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            time = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<Drawing(users_id='{0}', categories_id='{1}', location='{2}', status='{3}', score='{4}', time='{5}')>"\
                .format(self.users_id, self.categories_id, self.location,
                  self.status, self.score, self.time)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
        print("salut")
        print("score before query = ", new_score)

        my_new_drawing = Drawing(users_id=new_user_id, categories_id=new_category_id, location=new_location, status=new_status, score=new_score, time=new_time)
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

def learn2draw_update_drawing(informations:str, new_user_id, new_category_id, new_location, new_status, new_score, new_time) -> str:
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
            location = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            status = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            time = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<Drawing(users_id='{0}', categories_id='{1}', location='{2}', status='{3}', score='{4}', time='{5}')>"\
                .format(self.users_id, self.categories_id, self.location,
                  self.status, self.score, self.time)

        # create base
        Base.metadata.create_all(db_connection)

        # create session
        Session = sqlalchemy.orm.sessionmaker()
        Session.configure(bind=db_connection)
        session = Session()

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        session.query(Drawing).filter(Drawing.id == infos[0]).update({Drawing.users_id: new_user_id, Drawing.categories_id: new_category_id, Drawing.status: new_status, Drawing.score: new_score, Drawing.time: new_time})
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
            location = sqlalchemy.Column(sqlalchemy.String(length=40), nullable=False)
            status = sqlalchemy.Column(sqlalchemy.Integer)
            score = sqlalchemy.Column(sqlalchemy.Integer)
            time = sqlalchemy.Column(sqlalchemy.Integer)
         
            def __repr__(self):
                return "<Drawing(users_id='{0}', categories_id='{1}', location='{2}', status='{3}', score='{4}', time='{5}')>"\
                .format(self.users_id, self.categories_id, self.location,
                  self.status, self.score, self.time)

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
        categories_infos = pd.read_sql("SELECT name FROM CATEGORIES",
                           con=db_connection, index_col=None).to_dict()
        #print("users infos : ", users_infos)

        liste = []

        for i in categories_infos["name"]:
            #print("i = ", i)
            line = "{}".format(categories_infos['name'][i])
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

        print("infos 0 ", infos[0])
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

        #update = User.update().where(User.c.username=="arnaud_lasticot").values(username="new_name")
            
        session.query(Category).filter(Category.name == infos[0]).update({Category.name: new_category})
        #session.query(User).filter(User.username == infos[0], User.email == infos[1]).update({User.username: new_username}, {User.email: new_email})
        #print("error handle ? : ", test)
        session.commit()

        #print("BILLY C TOI ?")

        return "True"
        
    except Exception as e:
        print("on a récup l'exception ;) \n, type e = ", type(e))
        print("try str ==> ", str(e))

        if "Duplicate entry" in str(e):
            print("send dupplicate category error")
            return "category_already_exist"
            

        print(e)
        return "False"

def learn2draw_delete_category(informations) -> str:
    try:

        #init session to query database, maybe place it in a function later
        db_connection = create_engine(create_engine_db())
        infos=informations.split(';')

        my_id = infos[0]
        print("my_id = ", my_id)
    
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