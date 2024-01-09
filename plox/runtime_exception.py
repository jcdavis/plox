from .tokens import Token


class PloxRuntimeException(Exception):
    def __init__(self, token: Token, message: str):
        self.message = message
        super().__init__(message)
        self.token = token
