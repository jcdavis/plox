from .tokens import Token


class PloxRuntimeException(Exception):
    def __init__(self, token: Token, msg: str):
        super(msg)
        self.token = token