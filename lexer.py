import re
from tokens import Token

class Lexer:
    keywords = {
        'if': 'IF', 'int': 'INT', 'while': 'WHILE', 'do': 'DO',
        'else': 'ELSE', 'return': 'RETURN', 'continue': 'CONTINUE'
    }
    tokens_spec = [
        ('NUM',     r'\b(0|[1-9][0-9]*)\b'),
        ('ID',      r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('ASSIGN',  r'='),
        ('EQ',      r'=='),
        ('NE',      r'!='),
        ('LE',      r'<='),
        ('GE',      r'>='),
        ('LT',      r'<'),
        ('GT',      r'>'),
        ('PLUS',    r'\+'),
        ('MINUS',   r'-'),
        ('MUL',     r'\*'),
        ('DIV',     r'/'),
        ('LPAREN',  r'\('),
        ('RPAREN',  r'\)'),
        ('LBRACE',  r'\{'),
        ('RBRACE',  r'\}'),
        ('SEMI',    r';'),
        ('COMMA',   r','),
        ('WS',      r'[ \t\n\r]+'),
        ('COMMENT', r'//[^\n]*'),
    ]
    tokens_re = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in tokens_spec)

    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.lineno = 1

    def error(self, msg):
        raise SyntaxError(f"Lexer error at line {self.lineno}: {msg}")

    def next_token(self):
        if self.pos >= len(self.source):
            return Token('EOF', None, self.lineno)
        m = re.match(self.tokens_re, self.source[self.pos:])
        if not m:
            self.error(f'Unexpected character: {self.source[self.pos]}')
        self.pos += m.end()
        kind = m.lastgroup
        value = m.group(kind)
        if kind == 'WS' or kind == 'COMMENT':
            self.lineno += value.count('\n')
            return self.next_token()
        if kind == 'NUM':
            value = int(value)
            kind = 'NUM'
        elif kind == 'ID' and value in self.keywords:
            kind = self.keywords[value]
        return Token(kind, value, self.lineno)

    def get_all_tokens(self):
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == 'EOF':
                break
        return tokens

    def get_binary_tokens(self):
        token_codes = {
            'IF':1, 'INT':1, 'WHILE':1, 'DO':1, 'ELSE':1, 'RETURN':1, 'CONTINUE':1,
            'ID':2, 'NUM':3,
            'PLUS':4, 'MINUS':4, 'MUL':4, 'DIV':4, 'ASSIGN':4,
            'LT':4, 'LE':4, 'GT':4, 'GE':4, 'EQ':4, 'NE':4,
            'LPAREN':5, 'RPAREN':5, 'LBRACE':5, 'RBRACE':5, 'SEMI':5, 'COMMA':5,
            'EOF':0
        }
        tokens = self.get_all_tokens()
        binary = []
        for tok in tokens:
            code = token_codes.get(tok.type, 0)
            binary.append((code, tok.value if tok.value is not None else ''))
        return binary
