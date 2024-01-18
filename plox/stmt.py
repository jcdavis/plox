from dataclasses import dataclass
from typing import Optional

from .tokens import Token
from .expr import Expr


@dataclass(frozen=True)
class Stmt:
    pass


@dataclass(frozen=True)
class Block(Stmt):
    statements: list[Stmt]


@dataclass(frozen=True)
class Expression(Stmt):
    expression: Expr


@dataclass(frozen=True)
class Print(Stmt):
    expression: Expr


@dataclass(frozen=True)
class Return(Stmt):
    keyword: Token
    value: Optional[Expr]


@dataclass(frozen=True)
class Var(Stmt):
    name: Token
    initializer: Optional[Expr]


@dataclass(frozen=True)
class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]


@dataclass(frozen=True)
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt]


@dataclass(frozen=True)
class While(Stmt):
    condition: Expr
    body: Stmt


@dataclass(frozen=True)
class Class(Stmt):
    name: Token
    functions: list[Function]
