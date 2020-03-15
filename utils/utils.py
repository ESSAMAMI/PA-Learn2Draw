from datetime import datetime
from uuid import uuid4

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