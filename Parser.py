from typing import List, Dict, Any
from Lexer import CLexer

class SyntaxError(Exception):
    def __init__(self, message, line, column, token_value=None):
        self.message = message
        self.line = line
        self.column = column
        self.token_value = token_value
        super().__init__(f"Syntax Error at line {line}, column {column}: {message}" + 
                        (f" near '{token_value}'" if token_value else ""))

class Parser:
    def __init__(self, tokens: List[Dict[str, Any]]):
        self.tokens = tokens
        self.current = 0
        self.tree_items = []
        self.errors = []    
        self.max_iterations = 10000  
        self.iteration_count = 0

    def check_iteration_limit(self):
        
        self.iteration_count += 1
        if self.iteration_count > self.max_iterations:
            raise Exception("Maximum parser iterations exceeded - possible infinite loop")

    def add_error(self, message: str, line: int, column: int, token_value: str = None):
        
        error = SyntaxError(message, line, column, token_value)
        self.errors.append(error)
        return error

    def peek(self) -> Dict:
        
        self.check_iteration_limit()
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None

    def peek_next(self) -> Dict:
        
        self.check_iteration_limit()
        if self.current + 1 < len(self.tokens):
            return self.tokens[self.current + 1]
        return None

    def consume(self, expected_type: str = None) -> Dict:
        
        self.check_iteration_limit()
        
        if self.current >= len(self.tokens):
            last_token = self.tokens[-1] if self.tokens else {'line': 1, 'column': 1}
            raise SyntaxError("Unexpected end of file", 
                            last_token.get('line', 1), 
                            last_token.get('column', 1))
        
        current_token = self.tokens[self.current]
        if expected_type and current_token.get('type') != expected_type:
            raise SyntaxError(
                f"Expected {expected_type}, found {current_token.get('type')}", 
                current_token.get('line', 1), 
                current_token.get('column', 1),
                current_token.get('value')
            )
        
        self.current += 1
        return current_token

    def expect(self, value: str):
        
        token = self.peek()
        if not token or token.get('value') != value:
            raise SyntaxError(
                f"Expected '{value}'",
                token.get('line', 1) if token else 1,
                token.get('column', 1) if token else 1,
                token.get('value') if token else None
            )
        self.consume()

    def parse(self) -> Dict:
        """Main parse method"""
        try:
            self.iteration_count = 0  # Reset iteration counter
            
            # Ana program node'unu oluştur
            program_node = {
                'type': 'program',
                'children': []
            }
            
            # Preprocessor bölümü
            preprocessor_items = []
            while self.peek() and self.peek()['type'] == "PREPROCESSOR":
                self.check_iteration_limit()
                directive = self.parse_preprocessor()
                if directive:
                    preprocessor_items.append(directive)
            
            if preprocessor_items:
                program_node['children'].append({
                    'type': 'preprocessor',
                    'children': preprocessor_items
                })
            
            
            function_items = []
            while self.peek() is not None:
                self.check_iteration_limit()
                
                if (self.peek()['type'] == "KEYWORD" and 
                    self.peek()['value'] in ["int", "void", "double", "float"] and
                    self.peek_next() and 
                    self.peek_next()['type'] == "IDENTIFIER"):
                    
                    
                    if (self.current + 2 < len(self.tokens) and 
                        self.tokens[self.current + 2]['value'] == '('):
                        func_decl = self.parse_function_declaration()
                        if func_decl:
                            function_items.append(func_decl)
                    else:
                        
                        self.current += 1
                else:
                    self.current += 1
            
            if function_items:
                program_node['children'].append({
                    'type': 'function_declarations',
                    'children': function_items
                })
            
            return program_node
            
        except Exception as e:
            
            token = self.peek() or {'line': 1, 'column': 1}
            self.add_error(f"Unexpected parsing error: {str(e)}", 
                         token.get('line', 1), 
                         token.get('column', 1))
            return {'type': 'program', 'children': []}

    def parse_preprocessor(self):
       
        token = self.consume("PREPROCESSOR")
        return {
            'type': 'preprocessor',
            'value': token['value']
        }

    def parse_statement(self):
       
        token = self.peek()
        if not token:
            return None

        
        if token['type'] == "KEYWORD" and token['value'] in ["int", "char", "float", "double", "void"]:
            next_token = self.peek_next()
            if next_token and next_token['type'] == "IDENTIFIER":
              
                if self.current + 2 < len(self.tokens) and self.tokens[self.current + 2]['value'] == '(':
                    return self.parse_function_declaration()
                else:
                    return self.parse_variable_declaration()
            return None
        
        
        elif token['type'] == "KEYWORD" and token['value'] == "if":
            return self.parse_if_statement()
        
        
        elif token['type'] == "KEYWORD" and token['value'] == "while":
            return self.parse_while_statement()
        
        
        elif token['type'] == "KEYWORD" and token['value'] == "for":
            return self.parse_for_statement()
        
        
        elif token['type'] == "IDENTIFIER":
            return self.parse_expression_statement()
        
        self.current += 1
        return None

    def parse_function_declaration(self):
        
        return_type = self.consume("KEYWORD")
        if not return_type:
            return None

        function_name = self.consume("IDENTIFIER")
        if not function_name:
            return None

        
        if not self.peek() or self.peek()['value'] != '(':
            return None
        self.consume()

        
        parameters = []
        while self.peek() and self.peek()['value'] != ')':
            param_type = self.consume("KEYWORD")
            param_name = self.consume("IDENTIFIER")
            if param_type and param_name:
                parameters.append({
                    'type': 'parameter',
                    'children': [
                        {'type': 'type', 'value': param_type['value']},
                        {'type': 'identifier', 'value': param_name['value']}
                    ]
                })
            
            
            if self.peek() and self.peek()['value'] == ',':
                self.consume()


        if not self.peek() or self.peek()['value'] != ')':
            return None
        self.consume()  

        
        body_statements = []
        if self.peek() and self.peek()['value'] == '{':
            self.consume()  
            
            while self.peek() and self.peek()['value'] != '}':
                stmt = self.parse_statement()
                if stmt:
                    body_statements.append(stmt)
            
            if self.peek():
                self.consume()  

        return {
            'type': 'function_declaration',
            'children': [
                {'type': 'return_type', 'value': return_type['value']},
                {'type': 'function_name', 'value': function_name['value']},
                {'type': 'parameters', 'children': parameters},
                {'type': 'block', 'children': body_statements}
            ]
        }

    def parse_variable_declaration(self):
        
        type_token = self.consume("KEYWORD")
        if not type_token:
            return None

        id_token = self.consume("IDENTIFIER")
        if not id_token:
            return None

        node = {
            'type': 'variable_declaration',
            'children': [
                {'type': 'type', 'value': type_token['value']},
                {'type': 'identifier', 'value': id_token['value']}
            ]
        }

        
        if self.peek() and self.peek()['value'] == '=':
            self.consume()  
            expression = self.parse_expression()
            if expression:
                node['children'].append({
                    'type': 'initialization',
                    'children': [expression]
                })

        
        if self.peek() and self.peek()['value'] == ';':
            self.consume()

        return node

    def parse_expression(self):
        
        token = self.peek()
        if not token:
            return None

        
        left = self.parse_term()
        if not left:
            return None

        
        while self.peek() and self.peek()['type'] == 'OPERATOR':
            operator = self.consume()
            right = self.parse_term()
            if not right:
                break

            
            left = {
                'type': 'arithmetic_operation',
                'operator': operator['value'],
                'children': [left, right]
            }

        return left

    def parse_term(self):

        token = self.peek()
        if not token:
            return None

        if token['type'] == 'IDENTIFIER':
            self.consume()
            return {
                'type': 'identifier',
                'value': token['value']
            }
        elif token['type'] == 'NUMBER':
            self.consume()
            return {
                'type': 'number',
                'value': token['value']
            }
        elif token['value'] == '(':
            self.consume()  
            expr = self.parse_expression()
            if self.peek() and self.peek()['value'] == ')':
                self.consume()  
                return expr
        return None

    def parse_if_statement(self):

        if not self.consume("KEYWORD") or self.peek()['value'] != '(':
            return None

        self.consume()  
        condition = self.parse_expression()
        
        if not condition or not self.peek() or self.peek()['value'] != ')':
            return None

        self.consume()  

        node = {
            'type': 'if_statement',
            'children': [
                {'type': 'condition', 'children': [condition]}
            ]
        }

       
        if self.peek() and self.peek()['value'] == '{':
            self.consume()  
            body = []
            while self.peek() and self.peek()['value'] != '}':
                stmt = self.parse_statement()
                if stmt:
                    body.append(stmt)
            self.consume()  
            
            node['children'].append({'type': 'body', 'children': body})

        return node

    def parse_expression_statement(self):
        
        expr = self.parse_expression()
        if not expr:
            return None

        
        if self.peek() and self.peek()['value'] == ';':
            self.consume()

        
        if isinstance(expr, dict) and expr['type'] == 'function_call' and expr.get('function_name') == 'printf':
            return {
                'type': 'expression_statement',
                'children': [expr]
            }

        return {
            'type': 'expression_statement',
            'children': [expr]
        }

    def parse_while_statement(self):
        
        statement = {
            'type': 'while_statement',
            'children': []
        }
        
        self.current += 1  
        
        
        if self.current < len(self.tokens) and self.tokens[self.current]['value'] == "(":
            self.current += 1
            condition = []
            while self.current < len(self.tokens) and self.tokens[self.current]['value'] != ")":
                condition.append(self.tokens[self.current]['value'])
                self.current += 1
            
            statement['children'].append({
                'type': 'condition',
                'value': ' '.join(condition)
            })
            
            self.current += 1  

        self.tree_items.append(statement)

    def parse_for_statement(self):

        statement = {
            'type': 'for_statement',
            'children': []
        }
        
        self.current += 1  
        
        
        if self.current < len(self.tokens) and self.tokens[self.current]['value'] == "(":
            self.current += 1
            
            
            init = []
            while self.current < len(self.tokens) and self.tokens[self.current]['value'] != ";":
                init.append(self.tokens[self.current]['value'])
                self.current += 1
            statement['children'].append({
                'type': 'initialization',
                'value': ' '.join(init)
            })
            self.current += 1  
            
            
            condition = []
            while self.current < len(self.tokens) and self.tokens[self.current]['value'] != ";":
                condition.append(self.tokens[self.current]['value'])
                self.current += 1
            statement['children'].append({
                'type': 'condition',
                'value': ' '.join(condition)
            })
            self.current += 1  
            
            
            increment = []
            while self.current < len(self.tokens) and self.tokens[self.current]['value'] != ")":
                increment.append(self.tokens[self.current]['value'])
                self.current += 1
            statement['children'].append({
                'type': 'increment',
                'value': ' '.join(increment)
            })
            
            self.current += 1  

        self.tree_items.append(statement)

    def parse_function_call(self):
        
        function_name = self.consume('IDENTIFIER')
        if not function_name:
            return None

        
        if not self.peek() or self.peek()['value'] != '(':
            return None
        self.consume()  

        
        parameters = []
        while self.peek() and self.peek()['value'] != ')':
            
            if self.peek()['type'] == 'STRING':
                param = self.consume()
                parameters.append({
                    'type': 'string_literal',
                    'value': param['value']
                })
            
            else:
                expr = self.parse_expression()
                if expr:
                    parameters.append(expr)

          
            if self.peek() and self.peek()['value'] == ',':
                self.consume()

 
        if not self.peek() or self.peek()['value'] != ')':
            return None
        self.consume() 

        return {
            'type': 'function_call',
            'function_name': function_name['value'],
            'children': parameters
        } 