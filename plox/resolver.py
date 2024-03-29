from enum import Enum

from .tokens import Token
from .expr import Assign, Binary, Call, Expr, Get, Grouping, Literal, Logical, Set, Super, This, Unary, Variable
from .stmt import Block, Class, Expression, Function, If, Print, Return, Stmt, Var, While
from .interpreter import Interpreter
from . import plox


class Resolver:
    class FunctionType(Enum):
        NONE = 1
        FUNCTION = 2
        METHOD = 3
        INITIALIZER = 4

    class ClassType(Enum):
        NONE = 1
        CLASS = 2
        SUBClASS = 3

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.current_function = self.FunctionType.NONE
        self.current_class = self.ClassType.NONE

    def resolve(self, statements: list[Stmt]) -> None:
        for statement in statements:
            self.visit_statement(statement)

    def visit_statement(self, statement: Stmt) -> None:
        match statement:
            case Block(statements):
                self.__begin_scope()
                self.resolve(statements)
                self.__end_scope()
            case Expression(expression) | Print(expression):
                self.visit_expr(expression)
            case Return(keyword, return_value):
                if self.current_function == self.FunctionType.NONE:
                    plox.error(keyword.line, "Can't return from top-level code.")
                if return_value:
                    if self.current_function == self.FunctionType.INITIALIZER:
                        plox.error(keyword.line, "Can't return a value from an initializer.")
                    self.visit_expr(return_value)
            case Var(name, initializer):
                self.__declare(name)
                if initializer:
                    self.visit_expr(initializer)
                self.__define(name)
            case Function(name, _, _) as fn:
                self.__declare(name)
                self.__define(name)
                self.__resolve_function(fn, self.FunctionType.FUNCTION)
            case If(condition, then_branch, else_branch):
                self.visit_expr(condition)
                self.visit_statement(then_branch)
                if else_branch:
                    self.visit_statement(else_branch)
            case While(condition, while_body):
                self.visit_expr(condition)
                self.visit_statement(while_body)
            case Class(name, superclass, methods):
                enclosing_class = self.current_class
                self.current_class = self.ClassType.CLASS
                self.__declare(name)
                self.__define(name)

                if superclass:
                    if name.lexeme == superclass.name.lexeme:
                        plox.error(superclass.name.line, "A class can't inherit from itself.")
                    self.current_class = self.ClassType.SUBClASS
                    self.visit_expr(superclass)
                    self.__begin_scope()
                    self.scopes[-1]["super"] = True

                self.__begin_scope()
                self.scopes[-1]["this"] = True

                for method in methods:
                    declaration = self.FunctionType.METHOD
                    if method.name.lexeme == "init":
                        declaration = self.FunctionType.INITIALIZER
                    self.__resolve_function(method, declaration)

                self.__end_scope()
                if superclass:
                    self.__end_scope()
                self.current_class = enclosing_class

    def visit_expr(self, expr: Expr) -> None:
        match expr:
            case Assign(name, value) as assign:
                self.visit_expr(value)
                self.__resolve_local(assign, name)
            case Binary(left, _, right) | Logical(left, _, right):
                self.visit_expr(left)
                self.visit_expr(right)
            case Call(callee, _, arguments):
                self.visit_expr(callee)
                for argument in arguments:
                    self.visit_expr(argument)
            case Grouping(value) | Unary(_, value) | Get(value, _):
                self.visit_expr(value)
            case Literal():
                pass
            case Variable(name) as var:
                if len(self.scopes) > 0 and self.scopes[-1].get(name.lexeme, None) is False:
                    plox.error(name.line, "Can't read local variable in its own initializer.")
                self.__resolve_local(var, name)
            case Set(obj, _, value):
                self.visit_expr(value)
                self.visit_expr(obj)
            case This(keyword) as this:
                if self.current_class == self.ClassType.NONE:
                    plox.error(keyword.line, "Can't use 'this' outside of a class.")
                    return
                self.__resolve_local(this, keyword)
            case Super(keyword, _) as superclass:
                if self.current_class == self.ClassType.NONE:
                    plox.error(keyword.line, "Can't use 'super' outside of a class.")
                if self.current_class == self.ClassType.CLASS:
                    plox.error(keyword.line, "Can't use 'super' in a class with no superclass.")
                self.__resolve_local(superclass, keyword)

    def __resolve_function(self, function: Function, function_type: FunctionType) -> None:
        enclosing_function = self.current_function
        self.current_function = function_type
        self.__begin_scope()
        for param in function.params:
            self.__declare(param)
            self.__define(param)
        self.resolve(function.body)
        self.__end_scope()
        self.current_function = enclosing_function

    def __begin_scope(self) -> None:
        self.scopes.append({})

    def __end_scope(self) -> None:
        self.scopes.pop()

    def __declare(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return
        if name.lexeme in self.scopes[-1]:
            plox.error(name.line, "Already a variable with this name in this scope.")
        self.scopes[-1][name.lexeme] = False

    def __define(self, name: Token) -> None:
        if len(self.scopes) == 0:
            return
        self.scopes[-1][name.lexeme] = True

    def __resolve_local(self, expr: Expr, name: Token) -> None:
        for i in reversed(range(len(self.scopes))):
            scope = self.scopes[i]
            if name.lexeme in scope:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return
