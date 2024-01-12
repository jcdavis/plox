from .tokens import Token


class PloxRuntimeException(Exception):
    def __init__(self, token: Token, message: str):
        self.message = message
        super().__init__(message)
        self.token = token


class ReturnException(Exception):
    def __init__(self, value: object):
        super().__init__("placeholder")
        self.value = value
