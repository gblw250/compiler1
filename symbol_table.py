class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def add(self, name, lineno, type_='int'):
        if name in self.symbols:
            raise Exception(f"Semantic error at line {lineno}: variable '{name}' already defined")
        self.symbols[name] = {'type': type_, 'line': lineno}

    def lookup(self, name):
        return self.symbols.get(name)

    def __str__(self):
        lines = ["Symbol Table:"]
        for name, info in self.symbols.items():
            lines.append(f"  {name} : {info['type']} (line {info['line']})")
        return "\n".join(lines)
