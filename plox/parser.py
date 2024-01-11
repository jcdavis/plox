import logging

from .stmt import Expression, Print, Stmt
from .tokens import Token, TokenType
from .expr import Expr, Binary, Grouping, Literal, Unary
from . import plox


class ParseException(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
        self.logger = logging.getLogger("parser")

    def parse(self) -> list[Stmt]:
        statements = []
        while not self.__is_at_end():
            statements.append(self.__statement())
        return statements

    def __expression(self) -> Expr:
        return self.__equality()

    def __statement(self) -> Stmt:
        if self.__match(TokenType.PRINT):
            return self.__print_statement()
        return self.__expression_statement()

    def __print_statement(self) -> Stmt:
        value = self.__expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def __expression_statement(self):
        value = self.__expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(value)

    def __equality(self) -> Expr:
        expr = self.__comparison()
        self.logger.debug("Entering equality with base of %s", expr)

        while self.__match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.__previous()
            right = self.__comparison()
            expr = Binary(expr, operator, right)

        return expr

    def __comparison(self) -> Expr:
        expr = self.__term()
        self.logger.debug("Entering comparison with base of %s", expr)
        while self.__match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.__previous()
            right = self.__term()
            expr = Binary(expr, operator, right)

        return expr

    def __term(self) -> Expr:
        expr = self.__factor()
        self.logger.debug("Entering term with base of %s", expr)

        while self.__match(TokenType.MINUS, TokenType.PLUS):
            self.logger.debug('advancing term match')
            operator = self.__previous()
            right = self.__factor()
            expr = Binary(expr, operator, right)

        return expr

    def __factor(self) -> Expr:
        expr = self.__unary()
        self.logger.debug("Entering factor with base of %s", expr)

        while self.__match(TokenType.SLASH, TokenType.STAR):
            operator = self.__previous()
            right = self.__unary()
            expr = Binary(expr, operator, right)

        return expr

    def __unary(self) -> Expr:
        self.logger.debug("Entering unary, looking at %s", self.__peek())
        if self.__match(TokenType.BANG, TokenType.MINUS):
            operator = self.__previous()
            right = self.__unary()
            return Unary(operator, right)
        return self.__primary()

    def __primary(self) -> Expr:
        if self.__match(TokenType.FALSE):
            return Literal(False)
        if self.__match(TokenType.TRUE):
            return Literal(True)
        if self.__match(TokenType.NIL):
            return Literal(TokenType.NIL)

        if self.__match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.__previous().literal)

        if self.__match(TokenType.LEFT_PAREN):
            expr = self.__expression()
            self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        # Make lint happy
        return Unary(self.__error(self.__peek(), "Expected expression"), Literal("failed"))

    def __consume(self, token_type: TokenType, message: str) -> Token:
        if self.__check(token_type):
            return self.__advance()

        # Make lint happy
        return self.__error(self.__peek(), message)

    def __error(self, token: Token, message: str) -> Token:
        plox.error(token.line, message)
        raise ParseException()

    def __synchronize(self) -> None:
        self.__advance()

        while not self.__is_at_end():
            if self.__previous().token_type is TokenType.SEMICOLON:
                return
            match self.__peek().token_type:
                case TokenType.CLASS | TokenType.FUN | TokenType.VAR | TokenType.FOR | TokenType.IF | TokenType.WHILE | TokenType.RETURN:
                    return
            self.__advance()

    def __match(self, *types) -> bool:
        for t in types:
            if self.__check(t):
                self.logger.debug("Match, %s is a %s. Advancing", self.__peek(), t)
                self.__advance()
                return True
        return False

    def __check(self, token_type: TokenType) -> bool:
        if self.__is_at_end():
            return False
        return self.__peek().token_type is token_type

    def __advance(self) -> Token:
        if not self.__is_at_end():
            self.current += 1
        return self.__previous()

    def __is_at_end(self) -> bool:
        return self.__peek().token_type is TokenType.EOF

    def __peek(self) -> Token:
        return self.tokens[self.current]

    def __previous(self) -> Token:
        return self.tokens[self.current - 1]
