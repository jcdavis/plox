from dataclasses import dataclass
from .tokens import Token


@dataclass(frozen=True)
class Expr:
    pass


@dataclass(frozen=True)
class Assign(Expr):
    name: Token
    value: Expr


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(frozen=True)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]


@dataclass(frozen=True)
class Get(Expr):
    object: Expr
    name: Token


@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr


@dataclass(frozen=True)
class Literal(Expr):
    value: object


@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr


@dataclass(frozen=True)
class Variable(Expr):
    name: Token


@dataclass(frozen=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(frozen=True)
class Set(Expr):
    object: Expr
    name: Token
    value: Expr


@dataclass(frozen=True)
class This(Expr):
    keyword: Token


@dataclass(frozen=True)
class Super(Expr):
    keyword: Token
    method: Token
