from dataclasses import dataclass
from typing import Optional

from .tokens import Token
from .expr import Expr


class Stmt:
    pass


@dataclass
class Block(Stmt):
    statements: list[Stmt]


@dataclass
class Expression(Stmt):
    expression: Expr


@dataclass
class Print(Stmt):
    expression: Expr


@dataclass
class Return(Stmt):
    keyword: Token
    value: Optional[Expr]


@dataclass
class Var(Stmt):
    name: Token
    initializer: Optional[Expr]


@dataclass
class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]


@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt]


@dataclass
class While(Stmt):
    condition: Expr
    body: Stmt
