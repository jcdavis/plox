

from typing import Optional
from .runtime_exception import PloxRuntimeException
from .tokens import Token


class Environment:
    def __init__(self, enclosing: Optional['Environment'] = None):
        self.values: dict[str, object] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def get(self, name: Token) -> object:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing:
            return self.enclosing.get(name)

        raise PloxRuntimeException(name, f"Undefined variable {name.lexeme}.")

    def get_at(self, distance: int, name: str) -> object:
        return self.__ancestor(distance).values[name]

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        raise PloxRuntimeException(name, f"Undefined variable '{name.lexeme}'")

    def assign_at(self, distance: int, name: Token, value: object) -> None:
        self.__ancestor(distance).values[name.lexeme] = value

    def __ancestor(self, distance: int) -> 'Environment':
        env = self
        for _ in range(distance):
            if not env.enclosing:
                raise RuntimeError("Why isn't encloding defined")
            env = env.enclosing
        return env
