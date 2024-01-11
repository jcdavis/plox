from .tokens import Token, TokenType
from . import plox

KEYWORDS: dict[str, TokenType] = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE
}


class Scanner:
    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> list[Token]:
        while not self.__is_at_end():
            self.start = self.current
            self.__scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def __is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def __scan_token(self) -> None:
        match self.__advance():
            case '(':
                self.__add_token(TokenType.LEFT_PAREN)
            case ')':
                self.__add_token(TokenType.RIGHT_PAREN)
            case '{':
                self.__add_token(TokenType.LEFT_BRACE)
            case '}':
                self.__add_token(TokenType.RIGHT_BRACE)
            case ',':
                self.__add_token(TokenType.COMMA)
            case '.':
                self.__add_token(TokenType.DOT)
            case '-':
                self.__add_token(TokenType.MINUS)
            case '+':
                self.__add_token(TokenType.PLUS)
            case ';':
                self.__add_token(TokenType.SEMICOLON)
            case '*':
                self.__add_token(TokenType.STAR)
            case '!':
                self.__add_token(TokenType.BANG_EQUAL if self.__match('=') else TokenType.BANG)
            case '=':
                self.__add_token(TokenType.EQUAL_EQUAL if self.__match('=') else TokenType.EQUAL)
            case '<':
                self.__add_token(TokenType.LESS_EQUAL if self.__match('=') else TokenType.LESS)
            case '>':
                self.__add_token(TokenType.GREATER_EQUAL if self.__match('=') else TokenType.GREATER)
            case '/':
                if self.__match('/'):
                    while self.__peek() != '\n' and not self.__is_at_end():
                        self.__advance()
                else:
                    self.__add_token(TokenType.SLASH)
            case ' ' | '\r' | '\t':
                pass
            case '\n':
                self.line += 1
            case '"':
                self.__string()
            case num if self.__is_digit(num):
                self.__number()
            case alpha if self.__is_alpha(alpha):
                self.__identifier()
            case rest:
                plox.error(self.line, f"Unexpected character {rest}")

    def __is_alpha(self, c: str) -> bool:
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'

    def __is_digit(self, c: str) -> bool:
        return c >= '0' and c <= '9'

    def __is_alphanumeric(self, c: str) -> bool:
        return self.__is_alpha(c) or self.__is_digit(c)

    def __identifier(self) -> None:
        while self.__is_alphanumeric(self.__peek()):
            self.__advance()

        text = self.source[self.start:self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.__add_token(token_type)

    def __number(self) -> None:
        while self.__is_digit(self.__peek()):
            self.__advance()

        if self.__peek() == '.' and self.__is_digit(self.__peek_next()):
            # Consume .
            self.__advance()
            while self.__is_digit(self.__peek()):
                self.__advance()
        self.__add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def __string(self) -> None:
        while self.__peek() != '"' and not self.__is_at_end():
            if self.__peek() == '\n':
                self.line += 1
            self.__advance()

        if self.__is_at_end():
            plox.error(self.line, "unterminated string")
            return

        # Closing "
        self.__advance()

        value = self.source[self.start + 1:self.current - 1]
        self.__add_token(TokenType.STRING, value)

    def __peek(self) -> str:
        if self.__is_at_end():
            return '\0'
        return self.source[self.current]

    def __peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def __match(self, expected: str) -> bool:
        if self.__is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def __advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def __add_token(self, token_type: TokenType, literal: object = None) -> None:
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))
