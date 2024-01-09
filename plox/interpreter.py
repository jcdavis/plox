import numbers
from . import plox
from .expr import Binary, Expr, Grouping, Literal, Unary
from .runtime_exception import PloxRuntimeException
from .tokens import Token, TokenType


class Interpreter:
    def interpret(self, expr: Expr) -> None:
        try:
            value = self.__evaluate(expr)
            print(self.__stringify(value))
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

    def __visit_unary(self, op: Token, right: Expr) -> object:
        evaluated_right = self.__evaluate(right)

        match op.token_type:
            case TokenType.BANG:
                return not self.__is_truthy(evaluated_right)
            case TokenType.MINUS:
                self.__check_number_operand(right.operator, evaluated_right)
                return -evaluated_right

    def __visit_binary(self, left: Expr, op: Token, right: Expr) -> object:
        evaluated_left = self.__evaluate(left)
        evaluated_right = self.__evaluate(right)

        match op.token_type:
            case TokenType.GREATER:
                self.__check_number_operands(op, evaluated_left, evaluated_right)
                return evaluated_left > evaluated_right
            case TokenType.GREATER_EQUAL:
                self.__check_number_operands(op, evaluated_left, evaluated_right)
                return evaluated_left >= evaluated_right
            case TokenType.LESS:
                self.__check_number_operands(op, evaluated_left, evaluated_right)
                return evaluated_left < evaluated_right
            case TokenType.LESS_EQUAL:
                self.__check_number_operands(op, evaluated_left, evaluated_right)
                return evaluated_left <= evaluated_right
            case TokenType.BANG_EQUAL:
                return not self.__is_equal(evaluated_left, evaluated_right)
            case TokenType.EQUAL_EQUAL:
                return self.__is_equal(evaluated_left, evaluated_right)
            case TokenType.MINUS:
                self.__check_number_operands(op, evaluated_left, evaluated_right)
                return evaluated_left - evaluated_right
            case TokenType.PLUS:
                if (isinstance(evaluated_left, numbers.Number) and
                    isinstance(evaluated_right, numbers.Number)) or (
                        isinstance(evaluated_left, str) and
                        isinstance(evaluated_right, str)
                    ):
                    return evaluated_left + evaluated_right
                # Handle float vs str differently?
                raise PloxRuntimeException(op, "Can only combine numbers or strings")
            case TokenType.SLASH:
                self.__check_number_operands(op, evaluated_left, evaluated_right)
                return evaluated_left / evaluated_right
            case TokenType.STAR:
                self.__check_number_operands(op, evaluated_left, evaluated_right)
                return evaluated_left * evaluated_right

    def __check_number_operand(self, operator: Token, operand: object) -> None:
        if not isinstance(operand, numbers.Number):
            raise PloxRuntimeException(operator, "Operand must be a number")

    def __check_number_operands(self, operator: Token, left: object, right: object) -> None:
        if not (isinstance(left, numbers.Number) and isinstance(right, numbers.Number)):
            raise PloxRuntimeException(operator, "Operands must be numbers")

    def __is_truthy(self, op: object) -> bool:
        if not op:
            return False
        elif isinstance(op, bool):
            return op
        else:
            return True

    def __is_equal(self, left: object, right: object) -> bool:
        if not left and not right:
            return True
        return left is right

    def __stringify(self, obj: object) -> str:
        if not obj:
            return "nil"

        return str(obj)
