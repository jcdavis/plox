from tokens import Token, TokenType
import plox

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
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _scan_token(self) -> None:
        match self._advance():
            case '(':
                self._add_token(TokenType.LEFT_PAREN)
            case ')':
                self._add_token(TokenType.RIGHT_PAREN)
            case '{':
                self._add_token(TokenType.LEFT_BRACE)
            case '}':
                self._add_token(TokenType.RIGHT_BRACE)
            case ',':
                self._add_token(TokenType.COMMA)
            case '.':
                self._add_token(TokenType.DOT)
            case '-':
                self._add_token(TokenType.MINUS)
            case '+':
                self._add_token(TokenType.PLUS)
            case ';':
                self._add_token(TokenType.SEMICOLON)
            case '*':
                self._add_token(TokenType.STAR)
            case '!':
                self._add_token(TokenType.BANG_EQUAL if self._match('=') else TokenType.BANG)
            case '=':
                self._add_token(TokenType.EQUAL_EQUAL if self._match('=') else TokenType.EQUAL)
            case '<':
                self._add_token(TokenType.LESS_EQUAL if self._match('=') else TokenType.LESS)
            case '>':
                self._add_token(TokenType.GREATER_EQUAL if self._match('=') else TokenType.GREATER)
            case '/':
                if self._match('/'):
                    while self._peek() != '\n' and not self._is_at_end():
                        self.advance()
                else:
                    self._add_token(TokenType.SLASH)
            case ' ' | '\r' | '\t':
                pass
            case '\n':
                self.line += 1
            case '"':
                self._string()
            case num if self._is_digit(num):
                self._number()
            case alpha if self._is_alpha(alpha):
                self._identifier()
            case rest:
                plox.error(self.line, "Unexpected character {}".format(rest))

    def _is_alpha(self, c: str) -> bool:
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'

    def _is_digit(self, c: str) -> bool:
        return c >= '0' and c <= '9'

    def _is_alphanumeric(self, c: str) -> bool:
        return self._is_alpha(c) or self._is_digit(c)

    def _identifier(self) -> None:
        while self._is_alphanumeric(self._peek()):
            self._advance()
  
        text = self.source[self.start : self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self._add_token(token_type)

    def _number(self) -> None:
        while self._is_digit(self._peek()):
            self._advance()

        if self._peek() == '.' and self._is_digit(self._peek_next()):
            # Consume .
            self._advance()
            while self._is_digit(self._peek()):
                self._advance()
        self._add_token(TokenType.NUMBER,float(self.source[self.start : self.current]))

    def _string(self) -> None:
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            self._advance()

        if self._is_at_end():
            plox.error(self.line, "unterminated string")
            return

        # Closing "
        self._advance()

        value = self.source[self.start + 1 : self.current - 1]
        self._add_token(TokenType.STRING, value)

    def _peek(self) -> str:
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char

    def _add_token(self, token_type: TokenType, literal: object = None) -> None:
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))
