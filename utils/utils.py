from datetime import datetime
from uuid import uuid4
import base64
import os


'''
    GET CURRENT DATE //
    THIS FUNCTION TAKE ON PARAMS TO DESCRIBE FORMAT OF DATE ENG OR FR...
'''
def get_ccurent_date(format="ANG", full=True) -> str:

    assert isinstance(format, str)
    today = datetime.today()

    if full :
        today = str(today.year)+'-'+str(today.month)+'-'+str(today.day)
        return today

    return str(today.year)

def generate_token() -> str:

    rand_token = uuid4()
    return rand_token.hex

def decode_uploaded_file(image_base_64:str, category:str)-> str:

    img_data = image_base_64.split(",")[1]
    img_data = base64.b64decode(img_data)
    if os.path.exists('doodle/' + category.lower()):
        open_dir = os.listdir('doodle/' + category.lower() + '/')
        file_name = 'doodle/' + category.lower() + '/' + category.lower() + '_' + str(len(open_dir) + 1) + '.jpg'
        with open(file_name, 'wb') as f:
            f.write(img_data)
        return "True"

    else:
        os.mkdir('doodle/' + category.lower())
        open_dir = os.listdir('doodle/' + category.lower() + '/')
        file_name = 'doodle/' + category.lower() + '/' + category.lower() + '_' + str(len(open_dir) + 1) + '.jpg'
        with open(file_name, 'wb') as f:
            f.write(img_data)

        return "True"


