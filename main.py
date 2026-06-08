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

        # 创建只读输出组件
        self.token_text = self._create_readonly_text(self.notebook)
        self.symtab_text = self._create_readonly_text(self.notebook)
        self.ast_text = self._create_readonly_text(self.notebook)
        self.quad_text = self._create_readonly_text(self.notebook)
        self.log_text = self._create_readonly_text(self.notebook)
        self.error_text = self._create_readonly_text(self.notebook, fg='red')

        self.notebook.add(self.token_text, text="Token流 (二元式)")
        self.notebook.add(self.symtab_text, text="符号表")
        self.notebook.add(self.ast_text, text="语法树 (AST)")
        self.notebook.add(self.quad_text, text="四元式")
        self.notebook.add(self.log_text, text="语法分析过程")
        self.notebook.add(self.error_text, text="错误信息")

    def _create_readonly_text(self, parent, fg=None):
        """创建一个只读的 ScrolledText 组件"""
        text = scrolledtext.ScrolledText(parent, font=('Courier', 10), fg=fg if fg else 'black')
        text.config(state='disabled')  # 初始设为只读
        return text

    def _set_readonly_text(self, widget, content):
        """安全地设置只读文本组件的内容"""
        widget.config(state='normal')
        widget.delete('1.0', tk.END)
        widget.insert('1.0', content)
        widget.config(state='disabled')

    def _append_readonly_text(self, widget, content):
        """向只读文本组件追加内容"""
        widget.config(state='normal')
        widget.insert(tk.END, content)
        widget.config(state='disabled')

    def clear_output(self):
        """清空所有输出组件的内容（保持只读）"""
        for widget in [self.token_text, self.symtab_text, self.ast_text,
                       self.quad_text, self.log_text, self.error_text]:
            self._set_readonly_text(widget, '')

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
            out = "\n".join([f"({code}, {val})" for code, val in binary_tokens])
            self._set_readonly_text(self.token_text, out)
        except Exception as e:
            self._set_readonly_text(self.error_text, str(e))

    def full_compile(self):
        self.clear_output()
        source = self.source_text.get('1.0', tk.END)
        source = source.strip() + "\n"
        try:
            lexer = Lexer(source)
            # 获取二元式并显示
            binary_tokens = lexer.get_binary_tokens()
            token_out = "\n".join([f"({code}, {val})" for code, val in binary_tokens])
            self._set_readonly_text(self.token_text, token_out)

            # 重新获取 tokens（或复用上面的 tokens，但这里简单重新创建）
            lexer2 = Lexer(source)
            tokens = lexer2.get_all_tokens()
            parser = Parser(tokens)
            ast_root = parser.parse_program()
            if ast_root:
                self._set_readonly_text(self.ast_text, ast_to_str(ast_root))
            else:
                self._set_readonly_text(self.ast_text, "语法树为空")
            self._set_readonly_text(self.symtab_text, str(parser.symtab))
            self._set_readonly_text(self.log_text, "\n".join(parser.parse_log))
            if parser.errors:
                self._set_readonly_text(self.error_text, "\n".join(parser.errors))
            else:
                self._set_readonly_text(self.error_text, "✅ 编译成功，无错误。")

            if not parser.errors:
                codegen = CodeGenerator(parser.symtab)
                codegen.generate(ast_root)
                self._set_readonly_text(self.quad_text, str(codegen))
            else:
                self._set_readonly_text(self.quad_text, "由于语法错误，无法生成四元式。")
        except Exception as e:
            self._set_readonly_text(self.error_text, f"编译异常: {str(e)}\n")
            import traceback
            traceback.print_exc()

def main():
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()