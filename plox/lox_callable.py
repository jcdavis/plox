from abc import abstractmethod

from .runtime_exception import ReturnException
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
    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool = False):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance: object) -> 'LoxFunction':
        env = Environment(self.closure)
        env.define("this", instance)
        return LoxFunction(self.declaration, env, self.is_initializer)

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        env = Environment(self.closure)
        for (i, param) in enumerate(self.declaration.params):
            env.define(param.lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnException as re:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return re.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
