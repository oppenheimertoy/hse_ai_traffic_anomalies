class TokenExpiredError(BaseException):
    message: str = "token expired"
    status_code: int = 403

class TokenNotFoundError(BaseException): 
    message: str = "token not found"
    status_code: int = 401