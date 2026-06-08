class ASTNode:
    pass

class BlockNode(ASTNode):
    def __init__(self, stmts):
        self.stmts = stmts

class AssignNode(ASTNode):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

class IfNode(ASTNode):
    def __init__(self, cond, then_stmt, else_stmt=None):
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

class WhileNode(ASTNode):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

class BinaryOpNode(ASTNode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class NumNode(ASTNode):
    def __init__(self, value):
        self.value = value

class IdNode(ASTNode):
    def __init__(self, name):
        self.name = name

def ast_to_str(node, indent=0):
    prefix = "  " * indent
    if isinstance(node, BlockNode):
        lines = [prefix + "Block"]
        for stmt in node.stmts:
            lines.append(ast_to_str(stmt, indent + 1))
        return "\n".join(lines)
    elif isinstance(node, AssignNode):
        return f"{prefix}Assign\n{prefix}  var: {node.var}\n{prefix}  expr:\n{ast_to_str(node.expr, indent + 2)}"
    elif isinstance(node, IfNode):
        lines = [prefix + "If", prefix + "  cond:"]
        lines.append(ast_to_str(node.cond, indent + 2))
        lines.append(prefix + "  then:")
        lines.append(ast_to_str(node.then_stmt, indent + 2))
        if node.else_stmt:
            lines.append(prefix + "  else:")
            lines.append(ast_to_str(node.else_stmt, indent + 2))
        return "\n".join(lines)
    elif isinstance(node, WhileNode):
        lines = [prefix + "While", prefix + "  cond:"]
        lines.append(ast_to_str(node.cond, indent + 2))
        lines.append(prefix + "  body:")
        lines.append(ast_to_str(node.body, indent + 2))
        return "\n".join(lines)
    elif isinstance(node, BinaryOpNode):
        op_map = {'PLUS':'+', 'MINUS':'-', 'MUL':'*', 'DIV':'/',
                  'LT':'<', 'LE':'<=', 'GT':'>', 'GE':'>=', 'EQ':'==', 'NE':'!='}
        op_str = op_map.get(node.op, node.op)
        return f"{prefix}{op_str}\n{ast_to_str(node.left, indent+1)}\n{ast_to_str(node.right, indent+1)}"
    elif isinstance(node, NumNode):
        return f"{prefix}Num({node.value})"
    elif isinstance(node, IdNode):
        return f"{prefix}Id({node.name})"
    else:
        return f"{prefix}Unknown"
