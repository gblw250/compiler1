import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog
from lexer import Lexer
from my_parser import Parser
from codegen import CodeGenerator
from my_ast import ast_to_str

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("编译原理课程设计 - 编译器前端")
        self.root.geometry("1200x800")

        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="打开文件", command=self.load_file)
        filemenu.add_command(label="保存文件", command=self.save_file)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=root.quit)
        menubar.add_cascade(label="文件", menu=filemenu)
        root.config(menu=menubar)

        tk.Label(root, text="源代码（简化C语言子集）:", font=('Arial', 12)).pack(anchor='w', padx=5)
        self.source_text = scrolledtext.ScrolledText(root, height=12, font=('Courier', 11))
        self.source_text.pack(fill='both', expand=True, padx=5, pady=5)

        # 确保示例代码完整，末尾有右花括号并换行
        example = """{
    a = 10;
    if (a > 0) {
        a = a + 1;
    } else {
        a = a - 1;
    }
    while (a < 20) {
        a = a + 2;
    }
}"""
        self.source_text.insert('1.0', example)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="词法分析", command=self.lexical_analysis, width=12).pack(side='left', padx=5)
        tk.Button(btn_frame, text="完整编译", command=self.full_compile, width=12).pack(side='left', padx=5)
        tk.Button(btn_frame, text="清除输出", command=self.clear_output, width=10).pack(side='left', padx=5)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        self.token_text = scrolledtext.ScrolledText(self.notebook, font=('Courier', 10))
        self.symtab_text = scrolledtext.ScrolledText(self.notebook, font=('Courier', 10))
        self.ast_text = scrolledtext.ScrolledText(self.notebook, font=('Courier', 10))
        self.quad_text = scrolledtext.ScrolledText(self.notebook, font=('Courier', 10))
        self.log_text = scrolledtext.ScrolledText(self.notebook, font=('Courier', 10))
        self.error_text = scrolledtext.ScrolledText(self.notebook, font=('Courier', 10), fg='red')

        self.notebook.add(self.token_text, text="Token流 (二元式)")
        self.notebook.add(self.symtab_text, text="符号表")
        self.notebook.add(self.ast_text, text="语法树 (AST)")
        self.notebook.add(self.quad_text, text="四元式")
        self.notebook.add(self.log_text, text="语法分析过程")
        self.notebook.add(self.error_text, text="错误信息")

    def clear_output(self):
        for widget in [self.token_text, self.symtab_text, self.ast_text,
                       self.quad_text, self.log_text, self.error_text]:
            widget.delete('1.0', tk.END)

    def load_file(self):
        filename = filedialog.askopenfilename(filetypes=[("源程序文件", "*.c"), ("所有文件", "*.*")])
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            self.source_text.delete('1.0', tk.END)
            self.source_text.insert('1.0', content)

    def save_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".c", filetypes=[("源程序文件", "*.c")])
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.source_text.get('1.0', tk.END))

    def lexical_analysis(self):
        self.clear_output()
        source = self.source_text.get('1.0', tk.END)
        try:
            lexer = Lexer(source)
            binary_tokens = lexer.get_binary_tokens()
            out = []
            for code, val in binary_tokens:
                out.append(f"({code}, {val})")
            self.token_text.insert('1.0', "\n".join(out))
        except Exception as e:
            self.error_text.insert('1.0', str(e))

    def full_compile(self):
        self.clear_output()
        source = self.source_text.get('1.0', tk.END)
        # 预处理：去除首尾空白，但确保最后有换行（避免 EOF 识别问题）
        source = source.strip() + "\n"
        try:
            lexer = Lexer(source)



            binary_tokens = lexer.get_binary_tokens()
            token_out = []
            for code, val in binary_tokens:
                token_out.append(f"({code}, {val})")
            self.token_text.insert('1.0', "\n".join(token_out))

            lexer2 = Lexer(source)
            tokens = lexer2.get_all_tokens()
            parser = Parser(tokens)
            ast_root = parser.parse_program()
            if ast_root:
                self.ast_text.insert('1.0', ast_to_str(ast_root))
            else:
                self.ast_text.insert('1.0', "语法树为空")
            self.symtab_text.insert('1.0', str(parser.symtab))
            self.log_text.insert('1.0', "\n".join(parser.parse_log))
            if parser.errors:
                self.error_text.insert('1.0', "\n".join(parser.errors))
            else:
                self.error_text.insert('1.0', "✅ 编译成功，无错误。")

            if not parser.errors:
                codegen = CodeGenerator(parser.symtab)
                codegen.generate(ast_root)
                self.quad_text.insert('1.0', str(codegen))
            else:
                self.quad_text.insert('1.0', "由于语法错误，无法生成四元式。")
        except Exception as e:
            self.error_text.insert('1.0', f"编译异常: {str(e)}\n")
            import traceback
            traceback.print_exc()

def main():
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
