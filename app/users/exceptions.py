from app.exceptions import AlreadyExistsException


class UsernameAlreadyExistsException(AlreadyExistsException):
    def __init__(self):
        super().__init__(key="username")
