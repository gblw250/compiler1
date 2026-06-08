class Token:
    def __init__(self, type_, value, lineno):
        self.type = type_
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, {self.lineno})"
