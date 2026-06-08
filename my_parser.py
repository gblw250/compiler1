from tokens import Token
from symbol_table import SymbolTable
from quad import QuadGenerator
from my_ast import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if tokens else None
        self.symtab = SymbolTable()
        self.quad_gen = QuadGenerator()
        self.errors = []
        self.parse_log = []
        self.ast_root = None


    def log(self, msg):
        self.parse_log.append(msg)

    def error(self, msg):
        if self.current_token:
            line = self.current_token.lineno
        else:
            line = "EOF"
        err_msg = f"Syntax error at line {line}: {msg}"
        if err_msg not in self.errors:
            self.errors.append(err_msg)
        self.log(f"[ERROR] {err_msg}")
        if self.current_token and self.current_token.type != 'EOF':
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = Token('EOF', None, 0)

    def consume(self, expected_type):
        if self.current_token and self.current_token.type == expected_type:
            self.log(f"匹配 {expected_type} : {self.current_token.value}")
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = Token('EOF', None, 0)
        else:
            self.error(f"Expected {expected_type}, got {self.current_token.type if self.current_token else 'EOF'}")

    def peek(self):
        return self.current_token.type if self.current_token else 'EOF'

    def parse_program(self):
        self.log("开始解析 program -> block")
        self.ast_root = self.block()
        if self.current_token and self.current_token.type != 'EOF':
            self.error("Extra tokens after program end")
        self.log("解析完成")
        return self.ast_root

    def block(self):
        self.log("进入 block")
        self.consume('LBRACE')
        stmt_nodes = self.stmts()
        self.consume('RBRACE')
        self.log("退出 block")
        return BlockNode(stmt_nodes)

    def stmts(self):
        stmts = []
        self.log("进入 stmts")
        while self.current_token and self.current_token.type not in ('RBRACE', 'EOF'):
            stmt_node = self.stmt()
            if stmt_node:
                stmts.append(stmt_node)
        self.log(f"stmts 解析到 {len(stmts)} 条语句")
        return stmts

    def stmt(self):
        tok_type = self.current_token.type
        self.log(f"开始解析 stmt, 当前token: {tok_type}")
        if tok_type == 'ID':
            var_name = self.current_token.value
            if not self.symtab.lookup(var_name):
                self.symtab.add(var_name, self.current_token.lineno, 'int')
            self.consume('ID')
            self.consume('ASSIGN')
            expr_node = self.expr()
            self.consume('SEMI')
            self.log(f"赋值语句: {var_name} = ...")
            return AssignNode(var_name, expr_node)
        elif tok_type == 'IF':
            self.consume('IF')
            self.consume('LPAREN')
            cond_node = self.bool()
            self.consume('RPAREN')
            then_node = self.stmt()
            else_node = None
            if self.current_token and self.current_token.type == 'ELSE':
                self.consume('ELSE')
                else_node = self.stmt()
            self.log("if语句解析完成")
            return IfNode(cond_node, then_node, else_node)
        elif tok_type == 'WHILE':
            self.consume('WHILE')
            self.consume('LPAREN')
            cond_node = self.bool()
            self.consume('RPAREN')
            body_node = self.stmt()
            self.log("while语句解析完成")
            return WhileNode(cond_node, body_node)
        elif tok_type == 'LBRACE':
            return self.block()
        else:
            self.error(f"Unexpected statement start: {tok_type}")
            return None

    def bool(self):
        left = self.expr()
        op = self.current_token.type
        rel_ops = {'LT', 'LE', 'GT', 'GE', 'EQ', 'NE'}
        if op in rel_ops:
            self.consume(op)
            right = self.expr()
            return BinaryOpNode(op, left, right)
        else:
            return left

    def expr(self):
        node = self.term()
        while self.current_token and self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token.type
            self.consume(op)
            right = self.term()
            node = BinaryOpNode(op, node, right)
        return node

    def term(self):
        node = self.factor()
        while self.current_token and self.current_token.type in ('MUL', 'DIV'):
            op = self.current_token.type
            self.consume(op)
            right = self.factor()
            node = BinaryOpNode(op, node, right)
        return node

    def factor(self):
        tok = self.current_token
        if tok.type == 'LPAREN':
            self.consume('LPAREN')
            node = self.expr()
            self.consume('RPAREN')
            return node
        elif tok.type == 'ID':
            var_name = tok.value
            if not self.symtab.lookup(var_name):
                self.symtab.add(var_name, tok.lineno, 'int')
            self.consume('ID')
            return IdNode(var_name)
        elif tok.type == 'NUM':
            value = tok.value
            self.consume('NUM')
            return NumNode(value)
        else:
            self.error(f"Unexpected factor: {tok.type}")
            return None
