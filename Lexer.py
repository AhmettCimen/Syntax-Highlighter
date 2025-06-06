class CLexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
        self.line = 1
        self.column = 1
        self.start_line = 1
        self.start_column = 1

    def error(self):
        raise Exception(f'Invalid character at line {self.line}, column {self.column}')

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        self.pos += 1
        self.column += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def mark_token_start(self):
        self.start_line = self.line
        self.start_column = self.column

    def create_token(self, type, value):
        return {
            'type': type,
            'value': value,
            'line': self.start_line,
            'column': self.start_column
        }

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        
        start_line = self.line
        start_column = self.column
        
        result = '//'  
        self.advance()  
        self.advance()  
        
        while self.current_char and self.current_char != '\n':
            result += self.current_char
            self.advance()
        if self.current_char:
            self.advance()
            
        return {
            'type': 'COMMENT',
            'value': result,
            'line': start_line,
            'column': start_column
        }

    def get_preprocessor(self):
        self.mark_token_start()
        result = ''
        while self.current_char and self.current_char != '\n':
            result += self.current_char
            self.advance()
        return self.create_token('PREPROCESSOR', result.strip())

    def get_number(self):
        self.mark_token_start()
        result = ''
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        return self.create_token('NUMBER', result)

    def get_identifier(self):
        self.mark_token_start()
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        keywords = {
            'int', 'char', 'float', 'double', 'void',
            'if', 'else', 'while', 'for', 'return',
            'break', 'continue', 'struct', 'typedef'
        }

        token_type = 'KEYWORD' if result in keywords else 'IDENTIFIER'
        return self.create_token(token_type, result)

    def get_string(self):
        self.mark_token_start()
        result = ''
        self.advance()  
        while self.current_char and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char:
                    result += '\\' + self.current_char
            else:
                result += self.current_char
            self.advance()
        if self.current_char:
            self.advance()  
        return self.create_token('STRING', result)

    def tokenize(self):
        tokens = []
        
        while self.pos < len(self.text):
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
                
            if self.current_char == '#':
                tokens.append(self.get_preprocessor())
                continue
                
            if self.current_char == '/' and self.pos + 1 < len(self.text):
                if self.text[self.pos + 1] == '/':
                    tokens.append(self.skip_comment())
                    continue
                    
            if self.current_char.isdigit():
                tokens.append(self.get_number())
                continue
                
            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.get_identifier())
                continue
                
            if self.current_char == '"':
                tokens.append(self.get_string())
                continue
                
            
            self.mark_token_start()
            if self.current_char in '+-*/%=<>!&|^~':
                tokens.append(self.create_token('OPERATOR', self.current_char))
                self.advance()
                continue
                
            
            if self.current_char in '(){}[]':
                tokens.append(self.create_token('DELIMITER', self.current_char))
                self.advance()
                continue
                
            
            if self.current_char in ';,':
                tokens.append(self.create_token('SEPARATOR', self.current_char))
                self.advance()
                continue
                
            if self.current_char == '<' or self.current_char == '>':
                tokens.append(self.create_token('OPERATOR', self.current_char))
                self.advance()
                continue
                
            self.error()
            
        return tokens
