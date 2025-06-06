import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import re
from Lexer import CLexer
from Parser import Parser
import math
from typing import List, Dict, Any
from error import CSyntaxChecker, highlight_errors

class Node:
    def __init__(self, value: str, children: List['Node'] = None):
        self.value = value
        self.children = children if children else []
        self.x = 0
        self.y = 0
        self.width = 0

class TopDownParser:
    def __init__(self, tokens: List[Dict[str, Any]]):
        self.tokens = tokens
        self.current = 0
        
    def match(self, expected_type: str) -> bool:
        if self.current < len(self.tokens):
            current_token = self.tokens[self.current]
            if current_token['type'] == expected_type:
                self.current += 1
                return True
        return False
    
    def parse_expression(self) -> Node:
        
        node = Node("expression")
        
        if self.current < len(self.tokens):
            token = self.tokens[self.current]
            
            if token['type'] == "IDENTIFIER":
                node.children.append(Node(f"ID({token['value']})"))
                self.current += 1
                
                if self.current < len(self.tokens) and self.tokens[self.current]['type'] == "OPERATOR":
                    op_token = self.tokens[self.current]
                    node.children.append(Node(f"OP({op_token['value']})"))
                    self.current += 1
                    
                    if self.current < len(self.tokens):
                        right_token = self.tokens[self.current]
                        if right_token['type'] in ["IDENTIFIER", "NUMBER"]:
                            node.children.append(Node(f"{right_token['type']}({right_token['value']})"))
                            self.current += 1
                
            elif token['type'] == "NUMBER":
                node.children.append(Node(f"NUM({token['value']})"))
                self.current += 1
                
        return node

class ParseTreeVisualizer:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.node_height = 40
        self.node_spacing = 50
        self.level_spacing = 80
        
    def calculate_positions(self, node: Node, x: float, y: float, available_width: float):
        node.y = y
        
        if not node.children:
            node.width = 100
            node.x = x + available_width / 2
            return
        
        total_width = 0
        for child in node.children:
            self.calculate_positions(child, x + total_width, y + self.level_spacing, 
                                  available_width / len(node.children))
            total_width += child.width
        
        node.width = max(total_width, 100)
        node.x = x + available_width / 2

    def draw_tree(self, root: Node):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        self.calculate_positions(root, 0, 50, canvas_width)
        self._draw_node(root)
        
    def _draw_node(self, node: Node):
       
        x, y = node.x, node.y
        
       
        oval_width = 80
        oval_height = 30
        self.canvas.create_oval(x - oval_width/2, y - oval_height/2,
                              x + oval_width/2, y + oval_height/2,
                              fill="lightblue")
        
        # Metni yaz
        self.canvas.create_text(x, y, text=node.value)
        
        
        for child in node.children:
            self.canvas.create_line(x, y + oval_height/2,
                                  child.x, child.y - oval_height/2)
            self._draw_node(child)

class CCodeText(tk.Text):
    def __init__(self, master, gui_instance, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        
        self.gui_instance = gui_instance
        
       
        self.scrollbar = ttk.Scrollbar(self.master, orient='vertical', command=self.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.configure(yscrollcommand=self.scrollbar.set)
        
     
        self.configure(font=('Consolas', 11))
        
       
        self.tag_configure("KEYWORD", foreground="#0000FF")  # Mavi
        self.tag_configure("IDENTIFIER", foreground="#000000")  # Siyah
        self.tag_configure("NUMBER", foreground="#FF0000")  # Kırmızı
        self.tag_configure("STRING", foreground="#008000")  # Yeşil
        self.tag_configure("COMMENT", foreground="#008080")  # Turkuaz
        self.tag_configure("PREPROCESSOR", foreground="#A020F0")  # Mor
        self.tag_configure("OPERATOR", foreground="#FF00FF")  # Magenta
        self.tag_configure("error", foreground="red", background="pink")  # Hata vurgulaması
        
        
        self.syntax_checker = CSyntaxChecker()

    def highlight_text(self, event=None):
      
        for tag in self.tag_names():
            self.tag_remove(tag, "1.0", "end")
        
       
        content = self.get("1.0", "end-1c")
        
        try:
           
            lexer = CLexer(content)
            tokens = lexer.tokenize()
                
                
            in_function_params = False
            last_token_type = None
            
            
            for i, token in enumerate(tokens):
                if 'line' in token and 'column' in token and 'value' in token:
                    
                    start_pos = f"{token['line']}.{token['column'] - 1}"
                    end_pos = f"{token['line']}.{token['column'] - 1 + len(token['value'])}"
                    
                    
                    if token['value'] == '(':
                        
                        if (i > 0 and tokens[i-1]['type'] == 'IDENTIFIER' and 
                            i > 1 and tokens[i-2]['type'] == 'KEYWORD'):
                            in_function_params = True
                    elif token['value'] == ')':
                        in_function_params = False
                    
                    
                    if token['type'] == 'STRING':
                        
                        self.tag_add('STRING', start_pos, end_pos)
                        continue
                    
                    
                    if in_function_params and token['type'] == 'IDENTIFIER':
                        self.tag_add('PARAMETER', start_pos, end_pos)
                        continue
                    
                    
                    if token['type'] == 'PREPROCESSOR':
                        self.tag_add('PREPROCESSOR', start_pos, end_pos)
                    elif token['type'] == 'COMMENT':
                        self.tag_add('COMMENT', start_pos, end_pos)
                    elif token['type'] == 'NUMBER':
                        self.tag_add('NUMBER', start_pos, end_pos)
                    elif token['type'] == 'KEYWORD':
                        self.tag_add('KEYWORD', start_pos, end_pos)
                    elif token['type'] == 'OPERATOR':
                        self.tag_add('OPERATOR', start_pos, end_pos)
                    elif token['type'] == 'IDENTIFIER':
                        self.tag_add('IDENTIFIER', start_pos, end_pos)
                    
                    last_token_type = token['type']
            
            
            errors = self.syntax_checker.check_syntax(content)
            if errors:
                highlight_errors(self, errors, self.gui_instance.add_error)
                
        except Exception as e:
            print(f"Highlighting error: {e}")

    def _is_function_declaration(self, tokens, current_index):
        
        if current_index < 2:
            return False
            
        current_token = tokens[current_index]
        prev_token = tokens[current_index - 1]
        prev_prev_token = tokens[current_index - 2]
        
        return (current_token['value'] == '(' and
                prev_token['type'] == 'IDENTIFIER' and
                prev_prev_token['type'] == 'KEYWORD')

def get_node_text(node):
    
    if 'value' in node:
        if node['type'] == 'type' or node['type'] == 'return_type':
            return f"Type: {node['value']}"
        elif node['type'] == 'identifier':
            return f"Identifier: {node['value']}"
        elif node['type'] == 'function_name':
            return f"Function Name: {node['value']}"
        elif node['type'] == 'number':
            return f"Number: {node['value']}"
        else:
            return f"{node['type']}: {node['value']}"
    elif 'operator' in node:
        return f"Operator: {node['operator']}"
    else:
        if node['type'] == 'variable_declaration':
            return "Variable Declaration"
        elif node['type'] == 'function_declaration':
            return "Function Declaration"
        elif node['type'] == 'expression':
            return "Expression"
        elif node['type'] == 'initialization':
            return "Initialization"
        elif node['type'] == 'condition':
            return "Condition"
        elif node['type'] == 'body':
            return "Body"
        elif node['type'] == 'parameters':
            return "Parameters"
        elif node['type'] == 'parameter':
            return "Parameter"
        elif node['type'] == 'if_statement':
            return "If Statement"
        elif node['type'] == 'while_statement':
            return "While Statement"
        elif node['type'] == 'for_statement':
            return "For Statement"
        elif node['type'] == 'program':
            return "Program"
        else:
            return node['type']

def add_node_to_tree(tree, parent, node):
    
    
    node_text = get_node_text(node)
    

    if 'children' in node:
        for child in node['children']:
            add_node_to_tree(tree, node_id, child)
    
    return node_id

def update_tokens_tab():
    lexer = CLexer()
    code = text_area.get("1.0", tk.END)
    tokens = lexer.tokenize(code)

    
    tokens_tree.delete(*tokens_tree.get_children())

    for token in tokens:
        tokens_tree.insert('', 'end', values=(
            token['type'],
            token['value'],
            token['line'],
            token['column']
        ))

def update_parse_tree(self):
    
    self.parse_tree.delete(*self.parse_tree.get_children())
    
    try:
        
        code = self.text_editor.get("1.0", "end-1c")
        if not code.strip():  
            return
            
        lexer = CLexer(code)
        tokens = lexer.tokenize()
        
        
        if tokens:
            parser = Parser(tokens)
            try:
                
                import threading
                import _thread
                
                def timeout_handler():
                    _thread.interrupt_main()
                
                
                timer = threading.Timer(3.0, timeout_handler)
                timer.start()
                
                try:
                    tree_items = parser.parse()
                    
                    if tree_items:
                        self._build_parse_tree(tree_items)
                finally:
                    
                    timer.cancel()
                    
            except KeyboardInterrupt:
                self.add_error("Parser timeout - Code too complex or invalid", 1, 1, "")
            except Exception as e:
                self.add_error(f"Parser error: {str(e)}", 1, 1, "")
        else:
            self.add_error("No valid tokens to parse", 1, 1, "")
            
    except Exception as e:
        self.add_error(f"Lexer error: {str(e)}", 1, 1, "")
        
    finally:
        
        if len(self.error_tree.get_children()) > 0:
            self.right_panel.select(3)  

def on_text_change(event):
    if text_area.edit_modified():
        update_tokens_tab()
        update_parse_tree()
        text_area.edit_modified(False)

class CParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("C Parser")
        
        
        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        
        self.left_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_panel)
        

        self.text_editor = CCodeText(self.left_panel, self, wrap=tk.WORD, width=50, height=30)
        self.text_editor.pack(fill=tk.BOTH, expand=True)
        
        
        self.text_editor.bind('<<Modified>>', self.on_text_change)
        
        
        self.right_panel = ttk.Notebook(self.paned_window)
        self.paned_window.add(self.right_panel)
        
        
        self.token_frame = ttk.Frame(self.right_panel)
        self.right_panel.add(self.token_frame, text='Tokens')
        
       
        self.token_tree = ttk.Treeview(self.token_frame, columns=('Type', 'Value'), show='headings')
        self.token_tree.heading('Type', text='Type')
        self.token_tree.heading('Value', text='Value')
        self.token_tree.pack(fill=tk.BOTH, expand=True)
        
        
        self.grammar_frame = ttk.Frame(self.right_panel)
        self.right_panel.add(self.grammar_frame, text='Grammar')
        
        
        self.grammar_text = scrolledtext.ScrolledText(self.grammar_frame, wrap=tk.WORD, font=('Consolas', 11))
        self.grammar_text.pack(fill=tk.BOTH, expand=True)
        self.load_grammar()
        
        
        self.parse_tree_frame = ttk.Frame(self.right_panel)
        self.right_panel.add(self.parse_tree_frame, text='Parse Tree')
        
        
        self.parse_tree = ttk.Treeview(self.parse_tree_frame, show='tree')
        self.parse_tree.pack(fill=tk.BOTH, expand=True)
        
        
        self.error_frame = ttk.Frame(self.right_panel)
        self.right_panel.add(self.error_frame, text='Errors')
        
        
        self.error_tree = ttk.Treeview(self.error_frame, 
                                     columns=('Message', 'Line', 'Column', 'Token'),
                                     show='headings')
        self.error_tree.heading('Message', text='Message')
        self.error_tree.heading('Line', text='Line')
        self.error_tree.heading('Column', text='Column')
        self.error_tree.heading('Token', text='Token')
        self.error_tree.pack(fill=tk.BOTH, expand=True)
        
        
        self.setup_tags()
        
        
        self.on_text_change(None)

        
        initial_code = """#include <stdio.h>
// Bu bir yorum satırıdır

int main() {
    int sayi1;
    int sayi2;

    sayi1 = 10;
    sayi2 = 5;

    double toplam;
    toplam = sayi1 + sayi2;
    printf("Toplam: %f\\n", toplam);

    double sayi3;
    double sayi4;

    sayi3 = 20;
    sayi4 = 10;

    double fark;
    fark = sayi3 - sayi4;
    printf("Fark: %f\\n", fark);

    double sayi5;
    double sayi6;

    sayi5 = 7;
    sayi6 = 3;

    double carpim;
    carpim = sayi5 * sayi6;
    printf("Çarpım: %f\\n", carpim);

    return 0;
}"""
        self.text_editor.insert("1.0", initial_code)
        self.text_editor.edit_modified(False)

    def setup_tags(self):
        self.text_editor.tag_configure('keyword', foreground='blue')
        self.text_editor.tag_configure('string', foreground='green')
        self.text_editor.tag_configure('comment', foreground='gray')
        self.text_editor.tag_configure('preprocessor', foreground='purple')
        self.text_editor.tag_configure('number', foreground='orange')
        self.text_editor.tag_configure('operator', foreground='red')
        self.text_editor.tag_configure('identifier', foreground='black')
        self.text_editor.tag_configure('error', background='pink')

    def load_grammar(self):
        grammar_rules = """
program → preprocessor* declaration*

preprocessor → '#include' '<' HEADER '>'

declaration → variable_declaration | function_declaration

function_declaration → type IDENTIFIER '(' parameter_list? ')' block

parameter_list → parameter (',' parameter)*
parameter → type IDENTIFIER

block → '{' statement* '}'

statement → variable_declaration
          | expression_statement
          | if_statement
          | while_statement
          | for_statement
          | return_statement
          | block

variable_declaration → type init_declarator (',' init_declarator)* ';'
init_declarator → IDENTIFIER ('=' expression)?

expression_statement → expression ';'

expression → assignment

assignment → IDENTIFIER '=' expression
           | arithmetic_expression

arithmetic_expression → term (('+' | '-' | '*' | '/' | '%') term)*

term → IDENTIFIER
     | NUMBER
     | STRING
     | '(' expression ')'
     | function_call

function_call → IDENTIFIER '(' argument_list? ')'
argument_list → expression (',' expression)*

if_statement → 'if' '(' expression ')' statement ('else' statement)?
while_statement → 'while' '(' expression ')' statement
for_statement → 'for' '(' expression? ';' expression? ';' expression? ')' statement
return_statement → 'return' expression? ';'

type → 'int' | 'char' | 'float' | 'double' | 'void'


Lexer Token Tipleri:
--------------------
KEYWORD       → 'int' | 'char' | 'float' | 'double' | 'void' | 'if' | 'else' | 'while' | 'for' | 'return'
IDENTIFIER    → [a-zA-Z_][a-zA-Z0-9_]*
NUMBER        → [0-9]+(\.[0-9]+)?
STRING        → '"' [^"\\n]* '"'
OPERATOR      → '+' | '-' | '*' | '/' | '%' | '=' | '<' | '>' | '!' | '&' | '|' | '^' | '~'
DELIMITER     → '(' | ')' | '{' | '}' | '[' | ']'
SEPARATOR     → ';' | ','
PREPROCESSOR  → '#' [^\\n]*
HEADER        → [a-zA-Z0-9_/\.]+
"""
        
        self.grammar_text.delete('1.0', tk.END)
        self.grammar_text.insert('1.0', grammar_rules)
        self.grammar_text.configure(state='disabled')

    def highlight_syntax(self):
        content = self.text_editor.get("1.0", tk.END)
        self.text_editor.tag_remove("keyword", "1.0", tk.END)
        self.text_editor.tag_remove("string", "1.0", tk.END)
        self.text_editor.tag_remove("comment", "1.0", tk.END)
        self.text_editor.tag_remove("preprocessor", "1.0", tk.END)
        self.text_editor.tag_remove("number", "1.0", tk.END)
        self.text_editor.tag_remove("operator", "1.0", tk.END)
        
        
        keywords = r'\b(int|char|float|double|void|if|else|while|for|return)\b'
        self.highlight_pattern(keywords, 'keyword')
        
        
        strings = r'"[^"]*"'
        self.highlight_pattern(strings, 'string')
        
        
        comments = r'//[^\n]*'
        self.highlight_pattern(comments, 'comment')
        
        
        preprocessor = r'#[^\n]*'
        self.highlight_pattern(preprocessor, 'preprocessor')
        
       
        numbers = r'\b\d+\b'
        self.highlight_pattern(numbers, 'number')
        
        
        operators = r'[+\-*/%=<>!&|^~]'
        self.highlight_pattern(operators, 'operator')

    def highlight_pattern(self, pattern, tag):
        content = self.text_editor.get("1.0", tk.END)
        for match in re.finditer(pattern, content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.text_editor.tag_add(tag, start, end)

    def update_tokens(self):
        
        self.token_tree.delete(*self.token_tree.get_children())
        
        try:
            
            content = self.text_editor.get("1.0", "end-1c")
            lexer = CLexer(content)
            tokens = lexer.tokenize()
            
       
            for token in tokens:
                if 'type' in token and 'value' in token and 'line' in token and 'column' in token:
                    self.token_tree.insert('', 'end', values=(
                        token['type'],
                        token['value'],
                        token['line'],
                        token['column']
                    ))
        except Exception as e:
            self.add_error("Lexer error", 1, 1, str(e))

    def update_parse_tree(self):
        # Clear existing tree
        self.parse_tree.delete(*self.parse_tree.get_children())
        
        try:
            # Get code and create lexer
            code = self.text_editor.get("1.0", "end-1c")
            if not code.strip():  # If code is empty or only whitespace
                return
                
            lexer = CLexer(code)
            tokens = lexer.tokenize()
            
            # Only try to parse if we have valid tokens
            if tokens:
                parser = Parser(tokens)
                try:
                    # Set a timeout for parsing (3 seconds)
                    import threading
                    import _thread
                    
                    def timeout_handler():
                        _thread.interrupt_main()
                    
                    # Start timeout timer
                    timer = threading.Timer(3.0, timeout_handler)
                    timer.start()
                    
                    try:
                        tree_items = parser.parse()
                        # Build tree only if parsing was successful
                        if tree_items:
                            self._build_parse_tree(tree_items)
                    finally:
                        # Cancel timer
                        timer.cancel()
                        
                except KeyboardInterrupt:
                    self.add_error("Parser timeout - Code too complex or invalid", 1, 1, "")
                except Exception as e:
                    self.add_error(f"Parser error: {str(e)}", 1, 1, "")
            else:
                self.add_error("No valid tokens to parse", 1, 1, "")
                
        except Exception as e:
            self.add_error(f"Lexer error: {str(e)}", 1, 1, "")
            
        finally:
            # Always ensure the error tab is visible if there are errors
            if len(self.error_tree.get_children()) > 0:
                self.right_panel.select(3)  # Switch to errors tab

    def _build_parse_tree(self, items, parent=''):
        """Build the parse tree in the treeview widget"""
        if isinstance(items, dict):
            # Create node text based on the type and value
            node_text = items.get('type', 'unknown')
            
            
            if items['type'] == 'arithmetic_operation':
                
                node_id = self.parse_tree.insert(parent, 'end', text=items['operator'])
                
                if 'children' in items:
                    for child in items['children']:
                        self._build_parse_tree(child, node_id)
                return
            
            if 'value' in items:
                if items['type'] == 'function_name':
                    node_text = items['value']  
                elif items['type'] == 'return_type':
                    node_text = f"({items['value']})"  
                elif items['type'] in ['identifier', 'number']:
                    node_text = items['value']  
                else:
                    node_text += f": {items['value']}"
            
            
            node_id = self.parse_tree.insert(parent, 'end', text=node_text)
            
            
            if 'children' in items and items['children']:
                if items['type'] == 'program':
                    
                    self.parse_tree.item(node_id, open=True)
                    for child in items['children']:
                        self._build_parse_tree(child, node_id)
                
                elif items['type'] == 'preprocessor':
                    
                    self.parse_tree.item(node_id, open=True)
                    for child in items['children']:
                        self._build_parse_tree(child, node_id)
                
                elif items['type'] == 'function_declarations':
                    
                    self.parse_tree.item(node_id, open=True)
                    for child in items['children']:
                        self._build_parse_tree(child, node_id)
                
                elif items['type'] == 'function_declaration':
                    
                    function_info = {}
                    block_items = []
                    
                    for child in items['children']:
                        if child['type'] in ['return_type', 'function_name', 'parameters']:
                            function_info[child['type']] = child
                        elif child['type'] == 'block':
                            block_items = child.get('children', [])
                    
                    
                    header_parts = []
                    if 'return_type' in function_info:
                        header_parts.append(function_info['return_type']['value'])
                    if 'function_name' in function_info:
                        header_parts.append(function_info['function_name']['value'])
                    
                    
                    self.parse_tree.item(node_id, text=' '.join(header_parts))
                    
                    
                    if 'parameters' in function_info:
                        params = function_info['parameters']
                        if params.get('children'):
                            params_node = self.parse_tree.insert(node_id, 'end', text='params')
                            for param in params['children']:
                                self._build_parse_tree(param, params_node)
                    
                    
                    if block_items:
                        block_node = self.parse_tree.insert(node_id, 'end', text='block')
                        for block_item in block_items:
                            self._build_parse_tree(block_item, block_node)
                
                else:
                    
                    for child in items['children']:
                        self._build_parse_tree(child, node_id)
            
        elif isinstance(items, list):
            
            for item in items:
                self._build_parse_tree(item, parent)

    def on_text_change(self, event):
        
        if self.text_editor.edit_modified():
            
            self.error_tree.delete(*self.error_tree.get_children())
            self.text_editor.tag_remove('error', '1.0', 'end')
            
           
            self.text_editor.highlight_text()
            
            
            self.update_tokens()
            
            
            self.update_parse_tree()
            
            
            self.text_editor.edit_modified(False)

    def add_error(self, message, line, column, token_value=None):
        """Hata listesine yeni bir hata ekler"""
        self.error_tree.insert('', 'end', values=(message, line, column, token_value))
        self.highlight_error(line, column)
        self.right_panel.select(3)  # 3 = Errors tab

    def highlight_error(self, line, column):
        """Belirtilen konumdaki hatayı vurgular"""
       
        self.text_editor.tag_remove('error', '1.0', 'end')
        

        start = f"{line}.{column}"
        end = f"{line}.{column + 1}"
        self.text_editor.tag_add('error', start, end)

if __name__ == "__main__":
    root = tk.Tk()
    app = CParserGUI(root)
    app.text_editor.highlight_text()
    app.update_tokens()
    app.update_parse_tree()
    app.text_editor.edit_modified(False)
    root.mainloop()
