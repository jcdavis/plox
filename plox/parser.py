import logging
from tokens import Token, TokenType
from expr import Expr, Binary, Grouping, Literal, Unary
from plox import error

class ParseException(Exception):
    pass

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0
        self.logger = logging.getLogger("parser")

    def parse(self) -> Expr:
        try:
            return self._expression()
        except ParseException:
            return None
    def _expression(self) -> Expr:
        return self._equality()

    def _equality(self) -> Expr:
        expr = self._comparison()
        self.logger.debug("Entering equality with base of %s", expr)

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr = self._term()
        self.logger.debug("Entering comparison with base of %s", expr)
        while self._match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL):
            operator = self._previous()
            right = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self) -> Expr:
        expr = self._factor()
        self.logger.debug("Entering term with base of %s", expr)

        while self._match(TokenType.MINUS, TokenType.PLUS):
            self.logger.debug('advancing term match')
            operator = self._previous()
            right = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr = self._unary()
        self.logger.debug("Entering factor with base of %s", expr)

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._previous()
            right = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        self.logger.debug("Entering unary, looking at %s", self._peek())
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)
        return self._primary()

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return Literal(False)
        if self._match(TokenType.TRUE):
            return Literal(True)
        if self._match(TokenType.NIL):
            return Literal(TokenType.NIL)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._previous().literal)

        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        self._error(self._peek(), "Expected expression")

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()

        self._error(self._peek(), message)

    def _error(self, token: Token, message: str) -> Token:
        error(token.line, message)
        raise ParseException()

    def _synchronize(self) -> None:
        self._advance()

        while not self._is_at_end():
            if self._previous().token_type is TokenType.SEMICOLON:
                return
            match self._peek().token_type:
                case TokenType.CLASS | TokenType.FUN | TokenType.VAR | TokenType.FOR | TokenType.IF | TokenType.WHILE | TokenType.RETURN:
                    return
            self._advance()

    def _match(self, *types) -> bool:
        for t in types:
            if self._check(t):
                self.logger.debug("Match, %s is a %s. Advancing", self._peek(), t)
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().token_type is token_type

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().token_type is TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]
