from .expr import Expr, Binary, Grouping, Literal, Unary


class AstPrinter:
    def print(self, expr: Expr) -> str:
        match expr:
            case Binary(left, op, right):
                return self.__parenthesize(op.lexeme, left, right)
            case Grouping(expression):
                return self.__parenthesize("grouping", expression)
            case Literal(value):
                return str(value)
            case Unary(op, right):
                return self.__parenthesize(op.lexeme, right)
        raise Exception("Missing expr type")

    def __parenthesize(self, name: str, *args: Expr) -> str:
        result = '(' + str(name)

        for op in args:
            result += ' '
            result += self.print(op)
        return result + ')'
