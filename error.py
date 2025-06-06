import re
from typing import List, Dict, Tuple

class CSyntaxChecker:
    def __init__(self):
        
        self.keywords = {
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
            'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
            'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static',
            'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while'
        }
        
        
        self.operators = {
            '+', '-', '*', '/', '%', '=', '==', '!=', '<', '>', '<=', '>=',
            '&&', '||', '!', '&', '|', '^', '~', '<<', '>>', '+=', '-=', '*=',
            '/=', '%=', '&=', '|=', '^=', '<<=', '>>='
        }

    def check_syntax(self, code: str) -> List[Dict[str, any]]:
        errors = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            
            line_errors = self._check_line(line, line_num)
            errors.extend(line_errors)
            
        return errors

    def _check_line(self, line: str, line_num: int) -> List[Dict[str, any]]:
        errors = []
        
       
        if self._should_have_semicolon(line) and not line.strip().endswith(';'):
            errors.append({
                'line': line_num,
                'message': 'Satır sonunda noktalı virgül (;) eksik',
                'column': len(line.rstrip()) + 1
            })

       
        if not self._check_parentheses_match(line):
            errors.append({
                'line': line_num,
                'message': 'Parantezler eşleşmiyor',
                'column': self._find_mismatched_parenthesis_position(line)
            })

        
        if not self._check_braces_match(line):
            errors.append({
                'line': line_num,
                'message': 'Süslü parantezler eşleşmiyor',
                'column': self._find_mismatched_brace_position(line)
            })

       
        invalid_op = self._check_invalid_operators(line)
        if invalid_op:
            errors.append({
                'line': line_num,
                'message': f'Geçersiz operatör kullanımı: {invalid_op}',
                'column': line.find(invalid_op) + 1
            })

     
        if self._is_variable_declaration(line):
            if not self._check_valid_declaration(line):
                errors.append({
                    'line': line_num,
                    'message': 'Geçersiz değişken tanımlaması',
                    'column': 1
                })

        return errors

    def _should_have_semicolon(self, line: str) -> bool:
        line = line.strip()
        
        if not line or line.endswith('{') or line.endswith('}') or line.strip() == '}':
            return False
        if line.startswith('#'): 
            return False
        if line.strip().startswith('//'):  
            return False
        if 'for' in line and '(' in line and ')' in line:  
            return False
        if any(line.startswith(keyword + ' ') for keyword in ['if', 'while', 'switch']):
            return False
        
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*{?\s*$', line):
            return False
        return True

    def _check_parentheses_match(self, line: str) -> bool:
        stack = []
        for char in line:
            if char == '(':
                stack.append(char)
            elif char == ')':
                if not stack or stack[-1] != '(':
                    return False
                stack.pop()
        return len(stack) == 0

    def _check_braces_match(self, line: str) -> bool:
        line = line.strip()
       
        if line == '{' or line == '}':
            return True
            
       
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*{?\s*$', line):
            return True
            
        stack = []
        for char in line:
            if char == '{':
                stack.append(char)
            elif char == '}':
                if not stack or stack[-1] != '{':
                    return False
                stack.pop()
        return len(stack) == 0

    def _find_mismatched_parenthesis_position(self, line: str) -> int:
        stack = []
        for i, char in enumerate(line):
            if char == '(':
                stack.append(i)
            elif char == ')':
                if not stack:
                    return i + 1
                stack.pop()
        return len(line) if stack else -1

    def _find_mismatched_brace_position(self, line: str) -> int:
        stack = []
        for i, char in enumerate(line):
            if char == '{':
                stack.append(i)
            elif char == '}':
                if not stack:
                    return i + 1
                stack.pop()
        return len(line) if stack else -1

    def _check_invalid_operators(self, line: str) -> str:
        
        invalid_patterns = [
            r'\+\+\+',  
            r'---',     
            r'\*\*',    
            r'===',     
            r'!==',     
            r'&&&&',    
            r'\|\|\|'  
        ]
        
        for pattern in invalid_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group()
        return ''

    def _is_variable_declaration(self, line: str) -> bool:
        line = line.strip()
        return any(line.startswith(type_name + ' ') for type_name in 
                  ['int', 'char', 'float', 'double', 'void', 'long', 'short'])

    def _check_valid_declaration(self, line: str) -> bool:
        
        line = line.strip()
        
        
        if '(' in line and ')' in line:
            return True
            
        if not line.endswith(';'):
            return False
        
        
        line = line.rstrip(';').strip()
        
        
        if '=' in line:
            
            parts = line.split('=', 1)
            declaration = parts[0].strip()
            
            parts = declaration.split()
        else:
            parts = line.split()
            
        if len(parts) < 2:
            return False
            
        type_name = parts[0]
        if type_name not in ['int', 'char', 'float', 'double', 'void', 'long', 'short']:
            return False
            
        
        var_name = parts[1]
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
            return False
            
        return True

def highlight_errors(code_text_widget, errors: List[Dict[str, any]], add_error_callback=None):
    """
    GUI'de hataları kırmızı renkte gösterir ve error listesine ekler
    
    Args:
        code_text_widget: GUI'deki text widget
        errors: Hata listesi (her hata için line, message ve column bilgisi içerir)
        add_error_callback: GUI'nin error listesine hata eklemek için callback fonksiyonu
    """

    code_text_widget.tag_remove("error", "1.0", "end")
    
  
    for error in errors:
        line = error['line']
        
        start_pos = f"{line}.0"
        end_pos = f"{line}.end"
        
        
        code_text_widget.tag_add("error", start_pos, end_pos)
        
        
        if add_error_callback:
            add_error_callback(error['message'], error['line'], error.get('column', 0))
        else:
            
            print(f"Satır {line}: {error['message']}") 