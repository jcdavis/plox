import logging
import numbers

from .stmt import Expression, Print, Stmt
from . import plox
from .expr import Binary, Expr, Grouping, Literal, Unary
from .runtime_exception import PloxRuntimeException
from .tokens import Token, TokenType


class Interpreter:
    def __init__(self):
        self.logger = logging.getLogger("interpreter")

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
        raise Exception(f"Unexpected expr {expr}")

    def __execute(self, statement: Stmt) -> None:
        match statement:
            case Expression(expression):
                self.__evaluate(expression)
            case Print(expression):
                value = self.__evaluate(expression)
                print(self.__stringify(value))

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
