from src.domain.dto import BaseDTO


    

class AccessToken(BaseDTO):
    token: str

class RefreshToken(BaseDTO):
    token: str
    
class Token(BaseDTO):
    access: AccessToken
    token: RefreshToken