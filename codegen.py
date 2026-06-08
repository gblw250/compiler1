from quad import QuadGenerator
from my_ast import *

class CodeGenerator:
    def __init__(self, symtab):
        self.quad_gen = QuadGenerator()
        self.symtab = symtab
        self.label_counter = 0

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def generate(self, ast_node):
        if ast_node is None:
            return None
        if isinstance(ast_node, BlockNode):
            for stmt in ast_node.stmts:
                self.generate(stmt)
        elif isinstance(ast_node, AssignNode):
            expr_temp = self.generate_expr(ast_node.expr)
            self.quad_gen.add_quad(':=', expr_temp, '_', ast_node.var)
        elif isinstance(ast_node, IfNode):
            cond_temp = self.generate_expr(ast_node.cond)
            else_label = self.new_label()
            end_label = self.new_label()
            self.quad_gen.add_quad('ifFalse', cond_temp, '_', else_label)
            self.generate(ast_node.then_stmt)
            self.quad_gen.add_quad('goto', '_', '_', end_label)
            self.quad_gen.add_quad('label', '_', '_', else_label)
            if ast_node.else_stmt:
                self.generate(ast_node.else_stmt)
            self.quad_gen.add_quad('label', '_', '_', end_label)
        elif isinstance(ast_node, WhileNode):
            start_label = self.new_label()
            end_label = self.new_label()
            self.quad_gen.add_quad('label', '_', '_', start_label)
            cond_temp = self.generate_expr(ast_node.cond)
            self.quad_gen.add_quad('ifFalse', cond_temp, '_', end_label)
            self.generate(ast_node.body)
            self.quad_gen.add_quad('goto', '_', '_', start_label)
            self.quad_gen.add_quad('label', '_', '_', end_label)
        else:
            raise Exception(f"Unknown AST node: {type(ast_node)}")

    def generate_expr(self, node):
        if isinstance(node, NumNode):
            temp = self.quad_gen.new_temp()
            self.quad_gen.add_quad('const', node.value, '_', temp)
            return temp
        elif isinstance(node, IdNode):
            return node.name
        elif isinstance(node, BinaryOpNode):
            left = self.generate_expr(node.left)
            right = self.generate_expr(node.right)
            temp = self.quad_gen.new_temp()
            self.quad_gen.add_quad(node.op, left, right, temp)
            return temp
        else:
            raise Exception(f"Unknown expr node: {type(node)}")

    def get_quads(self):
        return self.quad_gen.quads

    def __str__(self):
        return str(self.quad_gen)
