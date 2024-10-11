from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        status_code = status.HTTP_401_UNAUTHORIZED
        detail = "Invalid credentials."
        super().__init__(status_code=status_code, detail=detail)


class InvalidTokenException(HTTPException):
    def __init__(self):
        status_code = status.HTTP_401_UNAUTHORIZED
        detail = "Token invalid, expired or revoked."
        super().__init__(status_code=status_code, detail=detail)
