from datetime import datetime

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