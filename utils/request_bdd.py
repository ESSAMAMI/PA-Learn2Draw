from configparser import ConfigParser
from sqlalchemy import create_engine
import pandas as pd

def create_engine_db() -> str:
    config = ConfigParser()
    config.read("D:/Skoula/utils/config.ini")

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
