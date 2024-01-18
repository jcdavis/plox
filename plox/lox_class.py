from typing import Optional
from .runtime_exception import PloxRuntimeException
from .interpreter import Interpreter
from .tokens import Token
from .lox_callable import LoxCallable, LoxFunction


class LoxClass(LoxCallable):
    def __init__(self, name: str, superclass: Optional['LoxClass'], methods: dict[str, LoxFunction]) -> None:
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def __str__(self) -> str:
        return self.name

    def find_method(self, name: str) -> Optional[LoxFunction]:
        if name in self.methods:
            return self.methods[name]
        if self.superclass:
            return self.superclass.find_method(name)
        return None

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self) -> int:
        match self.find_method("init"):
            case LoxFunction() as lf:
                return lf.arity()
            case None:
                return 0
            case _:
                raise RuntimeError("stupid")


class LoxInstance:
    def __init__(self, klass: LoxClass) -> None:
        self.klass = klass
        self.fields: dict[str, object] = {}

    def get(self, name: Token) -> object:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method:
            return method.bind(self)

        raise PloxRuntimeException(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: object) -> None:
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        return self.klass.name + " instance"
