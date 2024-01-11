import logging
import numbers

from .environment import Environment
from .stmt import Block, Expression, If, Print, Stmt, Var, While
from . import plox
from .expr import Assign, Binary, Expr, Grouping, Literal, Logical, Unary, Variable
from .runtime_exception import PloxRuntimeException
from .tokens import Token, TokenType


class Interpreter:
    def __init__(self, capture_output = False):
        self.logger = logging.getLogger("interpreter")
        self.environment = Environment()
        self.capture_output = capture_output
        self.output: list[str] = []

    def interpret(self, statements: list[Stmt]) -> None:
        try:
            for statement in statements:
                self.__execute(statement)
        except PloxRuntimeException as pre:
            plox.error(pre.token.line, pre.message)

    def __evaluate(self, expr: Expr) -> object:
        match expr:
            case Grouping(expression):
                return self.__evaluate(expression)
            case Literal(value):
                return value
            case Unary(op, right):
                return self.__visit_unary(op, right)
            case Binary(left, op, right):
                return self.__visit_binary(left, op, right)
            case Variable(name):
                return self.environment.get(name)
            case Assign(name, value):
                return self.environment.assign(name, self.__evaluate(value))
            case Logical(left, op, right):
                return self.__visit__logical(left, op, right)
        raise Exception(f"Unexpected expr {expr}")

    def __execute(self, statement: Stmt) -> None:
        match statement:
            case Block(statements):
                self.__execute_block(statements, Environment(self.environment))
            case Expression(expression):
                self.__evaluate(expression)
            case Print(expression):
                string = self.__stringify(self.__evaluate(expression))
                if self.capture_output:
                    self.output.append(string)
                else:
                    print(string)
            case Var(name, intializer):
                value = None
                if intializer:
                    value = self.__evaluate(intializer)
                self.environment.define(name.lexeme, value)
            case If(condition, then_branch, else_branch):
                if self.__is_truthy(self.__evaluate(condition)):
                    self.__execute(then_branch)
                elif else_branch:
                    self.__execute(else_branch)
            case While(condition, body):
                while self.__is_truthy(self.__evaluate(condition)):
                    self.__execute(body)

    def __execute_block(self, statements: list[Stmt], environment: Environment) -> None:
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
