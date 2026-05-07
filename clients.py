

class _Client(type):
    
    @property
    def favicon_url(cls):
        return f'/static/clients/{cls.code}_favicon.png'
    
    
    @property
    def logo_url(cls):
        return f'/static/clients/{cls.code}_logo.png'


class Boole(metaclass=_Client):
    code = "boole"
    name = "Boole Jobs"


class Staging(metaclass=_Client):
    code = 'staging'
    name = 'Xerowork Staging'

    
class Default(metaclass=_Client):
    code = 'default'
    name = 'Xerowork'

    
client_map = {
    'localhost:4071': Default,
    'xwstg.kdqed.com': Default,
}
