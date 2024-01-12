from abc import abstractmethod

from .environment import Environment
from .stmt import Function
from .interpreter import Interpreter


class LoxCallable:
    @abstractmethod
    def arity(self) -> int:
        pass

    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        pass

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function):
        self.declaration = declaration

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        env = Environment(interpreter.globals)
        for (i, param) in enumerate(self.declaration.params):
            env.define(param.lexeme, arguments[i])
        interpreter.execute_block(self.declaration.body, env)
        return None

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
