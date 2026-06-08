class Quad:
    def __init__(self, op, arg1, arg2, result):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __repr__(self):
        return f"({self.op}, {self.arg1}, {self.arg2}, {self.result})"

class QuadGenerator:
    def __init__(self):
        self.quads = []
        self.temp_counter = 0

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def add_quad(self, op, arg1, arg2, result):
        self.quads.append(Quad(op, arg1, arg2, result))

    def gen_label(self):
        return f"L{len(self.quads)}"

    def __str__(self):
        lines = ["Quads (four-address code):"]
        for i, q in enumerate(self.quads):
            lines.append(f"{i}: {q}")
        return "\n".join(lines)
