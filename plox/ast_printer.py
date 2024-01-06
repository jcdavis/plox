from tokens import Token, TokenType
from expr import Expr, Binary, Grouping, Literal, Unary

class AstPrinter:
    def print(self, expr: Expr) -> str:
        match expr:
            case Binary(left, op, right):
                print("visiting Binary {} {} {}".format(left, op, right))
                return self.__parenthesize(op.lexeme, left, right)
            case Grouping(expression):
                print("visiting Grouping {}".format(expression))
                return self.__parenthesize("grouping", expression)
            case Literal(value):
                print("visiting Literal {}".format(value))
                return str(value)
            case Unary(op, right):
                print("visiting Unary {} {}".format(right, op))
                return self.__parenthesize(op.lexeme, right)
        raise Exception("Missing expr type")

    def __parenthesize(self, name: str, *args: Expr) -> str:
        result = '(' + str(name)

        for op in args:
            result += ' '
            result += self.print(op)
        return result + ')'
