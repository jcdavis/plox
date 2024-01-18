import logging
from typing import Optional

from .stmt import Block, Class, Expression, Function, If, Print, Return, Stmt, Var, While
from .tokens import Token, TokenType
from .expr import Assign, Call, Expr, Binary, Grouping, Literal, Logical, Set, This, Unary, Variable, Get, Super
from . import plox


class ParseException(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
        self.logger = logging.getLogger("parser")

    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.__is_at_end():
            declaration = self.__declaration()
            if declaration:
                statements.append(declaration)
            else:
                self.logger.warning("Empty declaration, how to handle???")
        return statements

    def __expression(self) -> Expr:
        return self.__assignment()

    def __declaration(self) -> Optional[Stmt]:
        try:
            if self.__match(TokenType.CLASS):
                return self.__class_declaration()
            if self.__match(TokenType.FUN):
                return self.__function("function")
            if self.__match(TokenType.VAR):
                return self.__var_declaration()
            return self.__statement()
        except ParseException:
            self.__synchronize()
            return None

    def __class_declaration(self) -> Stmt:
        name = self.__consume(TokenType.IDENTIFIER, "Expect class name.")
        superclass = None
        if self.__match(TokenType.LESS):
            self.__consume(TokenType.IDENTIFIER, "Expect superclass name")
            superclass = Variable(self.__previous())
        self.__consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods = []
        while not self.__check(TokenType.RIGHT_BRACE) and not self.__is_at_end():
            methods.append(self.__function("method"))

        self.__consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return Class(name, superclass, methods)

    def __assignment(self) -> Expr:
        expr = self.__or()

        if self.__match(TokenType.EQUAL):
            equals = self.__previous()
            value = self.__assignment()

            match expr:
                case Variable(name):
                    return Assign(name, value)
                case Get(obj, name):
                    return Set(obj, name, value)
                case _:
                    self.__error(equals, "Invalid assignment target")
        return expr

    def __or(self) -> Expr:
        expr = self.__and()

        while self.__match(TokenType.OR):
            operator = self.__previous()
            right = self.__and()
            expr = Logical(expr, operator, right)

        return expr

    def __and(self) -> Expr:
        expr = self.__equality()

        while self.__match(TokenType.AND):
            operator = self.__previous()
            right = self.__equality()
            expr = Logical(expr, operator, right)

        return expr

    def __statement(self) -> Stmt:
        if self.__match(TokenType.FOR):
            return self.__for_statement()
        if self.__match(TokenType.IF):
            return self.__if_statement()
        if self.__match(TokenType.PRINT):
            return self.__print_statement()
        if self.__match(TokenType.RETURN):
            return self.__return_statement()
        if self.__match(TokenType.WHILE):
            return self.__while_statement()
        if self.__match(TokenType.LEFT_BRACE):
            return self.__block_statement()
        return self.__expression_statement()

    def __for_statement(self) -> Stmt:
        self.__consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer = None
        if self.__match(TokenType.SEMICOLON):
            pass
        elif self.__match(TokenType.VAR):
            initializer = self.__var_declaration()
        else:
            initializer = self.__expression_statement()

        condition = None
        if not self.__check(TokenType.SEMICOLON):
            condition = self.__expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.__check(TokenType.RIGHT_PAREN):
            increment = self.__expression()
        self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        body = self.__statement()

        if increment:
            body = Block([body, Expression(increment)])
        if not condition:
            condition = Literal(True)
        body = While(condition, body)
        if initializer:
            body = Block([initializer, body])

        return body

    def __function(self, kind: str) -> Function:
        name = self.__consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.__consume(TokenType.LEFT_PAREN, f"Exepect '(' after {kind} name")
        parameters = []
        if not self.__check(TokenType.RIGHT_PAREN):
            parameters.append(self.__consume(TokenType.IDENTIFIER, "Expect parameter name"))
            while self.__match(TokenType.COMMA):
                if len(parameters) > 255:
                    self.__error(self.__peek(), "Can't have more than 255 parameters.")
                parameters.append(self.__consume(TokenType.IDENTIFIER, "Expect parameter name"))
        self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters")

        self.__consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body")
        body = self.__block_statement()
        return Function(name, parameters, body.statements)

    def __if_statement(self) -> Stmt:
        self.__consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.__expression()
        self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition")

        then_branch = self.__statement()
        else_branch = None
        if self.__match(TokenType.ELSE):
            else_branch = self.__statement()

        return If(condition, then_branch, else_branch)

    def __print_statement(self) -> Stmt:
        value = self.__expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def __return_statement(self) -> Stmt:
        keyword = self.__previous()
        value = None
        if not self.__check(TokenType.SEMICOLON):
            value = self.__expression()

        self.__consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

    def __var_declaration(self) -> Stmt:
        name = self.__consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.__match(TokenType.EQUAL):
            initializer = self.__expression()

        self.__consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")
        return Var(name, initializer)

    def __while_statement(self) -> Stmt:
        self.__consume(TokenType.LEFT_PAREN, "Expected '(' after while")
        condition = self.__expression()
        self.__consume(TokenType.RIGHT_PAREN, "Expected '' after while condition")

        return While(condition, self.__statement())

    def __expression_statement(self):
        value = self.__expression()
        self.__consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(value)

    def __block_statement(self) -> Block:
        statements = []

        while not self.__check(TokenType.RIGHT_BRACE) and not self.__is_at_end():
            declaration = self.__declaration()
            if declaration:
                statements.append(declaration)
            else:
                self.logger.warning("Empty declaration, how to handle???")

        self.__consume(TokenType.RIGHT_BRACE, "Expect '}' after block")
        return Block(statements)

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
        return self.__call()

    def __call(self) -> Expr:
        expr = self.__primary()

        while True:
            if self.__match(TokenType.LEFT_PAREN):
                expr = self.__finish_call(expr)
            elif self.__match(TokenType.DOT):
                name = self.__consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Get(expr, name)
            else:
                break
        return expr

    def __finish_call(self, callee: Expr) -> Expr:
        arguments = []

        if not self.__check(TokenType.RIGHT_PAREN):
            arguments.append(self.__expression())
            while self.__match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.__error(self.__peek(), "Can't have more than 255 arguments.")
                arguments.append(self.__expression())

        paren = self.__consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def __primary(self) -> Expr:
        if self.__match(TokenType.FALSE):
            return Literal(False)
        if self.__match(TokenType.TRUE):
            return Literal(True)
        if self.__match(TokenType.NIL):
            return Literal(TokenType.NIL)

        if self.__match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.__previous().literal)

        if self.__match(TokenType.SUPER):
            keyword = self.__previous()
            self.__consume(TokenType.DOT, "Expect '.' after 'super'.")
            method = self.__consume(TokenType.IDENTIFIER, "Expect superclass method name.")
            return Super(keyword, method)
        if self.__match(TokenType.THIS):
            return This(self.__previous())

        if self.__match(TokenType.IDENTIFIER):
            return Variable(self.__previous())

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
