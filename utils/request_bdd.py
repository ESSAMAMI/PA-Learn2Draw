from configparser import ConfigParser
from sqlalchemy import create_engine
import pandas as pd

def create_engine_db() -> str:
    config = ConfigParser()
    config.read("D:\\Projets\\PA_4e_annee\\code\\utils\\config.ini")

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

        list_draws = pd.read_sql("SELECT * FROM DRAWINGS WHERE USERS_id != %s AND status=0" % ("'" + str(user_id['id'][0]) + "'"),
                           con=db_connection, index_col=None).to_dict('index')

        list_notation = pd.read_sql(
            "SELECT DRAWINGS_id FROM NOTATIONS WHERE USERS_id = %s" % ("'" + str(user_id['id'][0]) + "'"),
            con=db_connection, index_col=None).to_dict('index')

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

            line = "{};{};{};{};{};{}".format(list_draws[i]['USERS_id'], list_draws[i]['CATEGORYS_id'], list_draws[i]['location'], list_draws[i]['score'], list_draws[i]['time'], list_draws[i]['id'])

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