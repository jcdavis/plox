import logging
import numbers
import time

from .environment import Environment
from .stmt import Block, Class, Expression, Function, If, Print, Return, Stmt, Var, While
from .expr import Assign, Binary, Call, Expr, Get, Grouping, Literal, Logical, Set, This, Unary, Variable
from .runtime_exception import PloxRuntimeException, ReturnException
from .tokens import Token, TokenType


class Interpreter:
    def __init__(self, capture_output=False):
        from . import lox_callable
        self.logger = logging.getLogger("interpreter")
        self.globals = Environment()
        self.locals: dict[Expr, int] = {}
        self.environment = self.globals
        self.capture_output = capture_output
        self.output: list[str] = []

        self.globals.define("clock", type('ClockFunction', (lox_callable.LoxCallable,), {
            'arity': lambda self: 0,
            'call': lambda self, interpreter, arguments: int(time.time())
        })())

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self.__execute(statement)
        except PloxRuntimeException as pre:
            from .plox import error
            error(pre.token.line, pre.message)

    def resolve(self, expr: Expr, depth: int) -> None:
        self.locals[expr] = depth

    def __evaluate(self, expr: Expr) -> object:
        from . import lox_callable
        from . import lox_class
        match expr:
            case Binary(left, op, right):
                return self.__visit_binary(left, op, right)
            case Call(callee, paren, arguments):
                evaluated_callee = self.__evaluate(callee)
                evaluated_arugments = [self.__evaluate(arg) for arg in arguments]
                if isinstance(evaluated_callee, lox_callable.LoxCallable):
                    if len(arguments) != evaluated_callee.arity():
                        raise PloxRuntimeException(paren, f"Expected {evaluated_callee.arity()} arguments but got {len(arguments)}.")
                    return evaluated_callee.call(self, evaluated_arugments)
                raise PloxRuntimeException(paren, f"Can't call {evaluated_callee}. Can only call functions and classes.")
            case Get(object, name):
                match self.__evaluate(object):
                    case lox_class.LoxInstance() as li:
                        return li.get(name)
                    case _:
                        raise PloxRuntimeException(name, "Only instances have properties")

            case Grouping(expression):
                return self.__evaluate(expression)
            case Literal(value):
                return value
            case Unary(op, right):
                return self.__visit_unary(op, right)
            case Variable(name) as var:
                return self.__lookup_variable(name, var)
            case Assign(name, value) as assign:
                evaluated_value = self.__evaluate(value)
                if assign in self.locals:
                    depth = self.locals[assign]
                    self.environment.assign_at(depth, name, evaluated_value)
                else:
                    self.globals.assign(name, evaluated_value)
                return evaluated_value
            case Logical(left, op, right):
                return self.__visit__logical(left, op, right)
            case Set(obj, name, value):
                match self.__evaluate(obj):
                    case lox_class.LoxInstance() as li:
                        evaluated_value = self.__evaluate(value)
                        li.set(name, evaluated_value)
                        return None
                    case _:
                        raise PloxRuntimeException(name, "Only instances have fields.")
            case This(keyword) as this:
                return self.__lookup_variable(keyword, this)

        raise Exception(f"Unexpected expr {expr}")

    def __execute(self, statement: Stmt) -> None:
        from . import lox_class
        from .lox_callable import LoxFunction
        match statement:
            case Block(statements):
                self.execute_block(statements, Environment(self.environment))
            case Expression(expression):
                self.__evaluate(expression)
            case Print(expression):
                string = self.__stringify(self.__evaluate(expression))
                if self.capture_output:
                    self.output.append(string)
                else:
                    print(string)
            case Return(_, return_value):
                evaluated_value = None
                if return_value:
                    evaluated_value = self.__evaluate(return_value)
                raise ReturnException(evaluated_value)
            case Var(name, intializer):
                value = None
                if intializer:
                    value = self.__evaluate(intializer)
                self.environment.define(name.lexeme, value)
            case Function(name, _, _) as fn:
                lox_function = LoxFunction(fn, self.environment, False)
                self.environment.define(name.lexeme, lox_function)
            case If(condition, then_branch, else_branch):
                if self.__is_truthy(self.__evaluate(condition)):
                    self.__execute(then_branch)
                elif else_branch:
                    self.__execute(else_branch)
            case While(condition, body):
                while self.__is_truthy(self.__evaluate(condition)):
                    self.__execute(body)
            case Class(name, methods):
                self.environment.define(name.lexeme, None)
                method_map = {}
                for method in methods:
                    function = LoxFunction(method, self.environment, method.name.lexeme == "init")
                    method_map[method.name.lexeme] = function
                klass = lox_class.LoxClass(name.lexeme, method_map)
                self.environment.assign(name, klass)

    def execute_block(self, statements: list[Stmt], environment: Environment) -> None:
        prev = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.__execute(statement)
        finally:
            self.environment = prev

    def __visit_unary(self, op: Token, right: Expr) -> object:
        self.logger.debug("Evaluating unary: %s (%s)", op, right)
        evaluated_right = self.__evaluate(right)

        match op.token_type:
            case TokenType.BANG:
                return not self.__is_truthy(evaluated_right)
            case TokenType.MINUS:
                if not isinstance(evaluated_right, numbers.Real):
                    raise PloxRuntimeException(op, "Operand must be a number")
                return -evaluated_right
            case _:
                raise PloxRuntimeException(op, f"Unexpected token type {op}")

    def __visit_binary(self, left: Expr, op: Token, right: Expr) -> object:
        self.logger.debug("Evaluating binary: %s (%s %s)", op, left, right)
        evaluated_left = self.__evaluate(left)
        evaluated_right = self.__evaluate(right)

        match op.token_type:
            case TokenType.GREATER:
                if not (isinstance(evaluated_left, numbers.Real) and
                        isinstance(evaluated_right, numbers.Real)):
                    raise PloxRuntimeException(op, "Operands must be numbers")
                return evaluated_left > evaluated_right
            case TokenType.GREATER_EQUAL:
                if not (isinstance(evaluated_left, numbers.Real) and
                        isinstance(evaluated_right, numbers.Real)):
                    raise PloxRuntimeException(op, "Operands must be numbers")
                return evaluated_left >= evaluated_right
            case TokenType.LESS:
                if not (isinstance(evaluated_left, numbers.Real) and
                        isinstance(evaluated_right, numbers.Real)):
                    raise PloxRuntimeException(op, "Operands must be numbers")
                return evaluated_left < evaluated_right
            case TokenType.LESS_EQUAL:
                if not (isinstance(evaluated_left, numbers.Real) and
                        isinstance(evaluated_right, numbers.Real)):
                    raise PloxRuntimeException(op, "Operands must be numbers")
                return evaluated_left <= evaluated_right
            case TokenType.BANG_EQUAL:
                return not self.__is_equal(evaluated_left, evaluated_right)
            case TokenType.EQUAL_EQUAL:
                return self.__is_equal(evaluated_left, evaluated_right)
            case TokenType.MINUS:
                if not (isinstance(evaluated_left, numbers.Real) and
                        isinstance(evaluated_right, numbers.Real)):
                    raise PloxRuntimeException(op, "Operands must be numbers")
                return evaluated_left - evaluated_right
            case TokenType.PLUS:
                if (isinstance(evaluated_left, numbers.Real) and
                        isinstance(evaluated_right, numbers.Real)) or (
                        isinstance(evaluated_left, str) and
                        isinstance(evaluated_right, str)):
                    return evaluated_left + evaluated_right
                # Handle float vs str differently?
                raise PloxRuntimeException(op, "Can only combine numbers or strings")
            case TokenType.SLASH:
                if not (isinstance(evaluated_left, numbers.Real) and
                        isinstance(evaluated_right, numbers.Real)):
                    raise PloxRuntimeException(op, "Operands must be numbers")
                return evaluated_left / evaluated_right
            case TokenType.STAR:
                if not (isinstance(evaluated_left, numbers.Real) and
                        isinstance(evaluated_right, numbers.Real)):
                    raise PloxRuntimeException(op, "Operands must be numbers")
                return evaluated_left * evaluated_right
            case _:
                raise PloxRuntimeException(op, f"Unexpected token type {op}")

    def __visit__logical(self, left: Expr, op: Token, right: Expr) -> object:
        evaluated_left = self.__evaluate(left)

        if op.token_type == TokenType.OR:
            if self.__is_truthy(evaluated_left):
                return left
        else:
            # And case
            if not self.__is_truthy(evaluated_left):
                return evaluated_left
        return self.__evaluate(right)

    def __lookup_variable(self, name: Token, expr: Expr) -> object:
        if expr in self.locals:
            depth = self.locals[expr]
            res = self.environment.get_at(depth, name.lexeme)
            return res
        return self.globals.get(name)

    def __is_truthy(self, op: object) -> bool:
        if not op:
            return False
        if isinstance(op, bool):
            return op
        return True

    def __is_equal(self, left: object, right: object) -> bool:
        if not left and not right:
            return True
        return left is right

    def __stringify(self, obj: object) -> str:
        if obj is None:
            return "nil"

        return str(obj)
