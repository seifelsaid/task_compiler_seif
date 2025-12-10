import re

# Define token types for C++ Scanner
keywords = {
    "int", "if", "return", "for", "char", "double", "while", "void", "float",
    "else", "class", "public", "private", "protected", "struct", "namespace",
    "using", "include", "const", "static", "bool", "true", "false", "new",
    "delete", "this", "virtual", "override", "template", "typename"
}

operators = r"[+\-*/=<>!&|%]+"
punctuation = r"[;,\(\)\{\}\[\]:]"
identifier = r"[a-zA-Z_]\w*"
numeric_constant = r"\b\d+(\.\d+)?\b"
character_constant = r"'(\\.|[^\\'])'"
string_literal = r'"(?:[^"\\]|\\.)*"'
preprocessor = r"#\s*\w+"
whitespace = r"[ \t]+"
newline = r"\n"
single_line_comment = r"//[^\n]*"
multi_line_comment = r"/\*[\s\S]*?\*/"

def scanner(code):
    """
    Scans C++ code and returns a list of tokens
    """
    tokens = []
    position = 0
    
    while position < len(code):
        match = None
        
        if match := re.match(single_line_comment, code[position:]):
            tokens.append(('COMMENT', match.group()))
            
        elif match := re.match(multi_line_comment, code[position:]):
            tokens.append(('COMMENT', match.group()))
        
        elif match := re.match(preprocessor, code[position:]):
            tokens.append(('PREPROCESSOR', match.group()))
            
        elif match := re.match(string_literal, code[position:]):
            tokens.append(('STRING', match.group()))
            
        elif match := re.match(identifier, code[position:]):
            text = match.group()
            if text in keywords:
                tokens.append(('KEYWORD', text))
            else:
                tokens.append(('IDENTIFIER', text))

        elif match := re.match(numeric_constant, code[position:]):
            tokens.append(('NUMBER', match.group()))

        elif match := re.match(character_constant, code[position:]):
            tokens.append(('CHAR', match.group()))

        elif match := re.match(operators, code[position:]):
            tokens.append(('OPERATOR', match.group()))

        elif match := re.match(punctuation, code[position:]):
            tokens.append(('PUNCTUATION', match.group()))

        elif match := re.match(newline, code[position:]):
            position += 1
            continue

        elif match := re.match(whitespace, code[position:]):
            position += len(match.group())
            continue

        if match:
            position += len(match.group())
        else:
            position += 1
    
    return tokens

class CppParser:
    """
    Simple recursive descent parser for C++ subset
    Grammar:
    program -> statement_list
    statement_list -> statement statement_list | statement
    statement -> declaration | assignment | if_statement | return_statement | block
    declaration -> type IDENTIFIER ;
    assignment -> IDENTIFIER = expression ;
    if_statement -> if ( condition ) block
    if_statement -> if ( condition ) block else block
    return_statement -> return expression ;
    block -> { statement_list }
    expression -> IDENTIFIER | NUMBER | expression OPERATOR expression
    condition -> expression OPERATOR expression
    type -> int | float | double | char | void | bool
    """
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.errors = []
        
    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def peek_token(self, offset=1):
        if self.position + offset < len(self.tokens):
            return self.tokens[self.position + offset]
        return None
    
    def consume(self, expected_type=None, expected_value=None):
        token = self.current_token()
        if token is None:
            self.errors.append(f"Unexpected end of input")
            return None
        
        token_type, token_value = token
        
        if expected_type and token_type != expected_type:
            self.errors.append(f"Expected {expected_type}, got {token_type} ('{token_value}')")
            return None
        
        if expected_value and token_value != expected_value:
            self.errors.append(f"Expected '{expected_value}', got '{token_value}'")
            return None
        
        self.position += 1
        return token
    
    def parse(self):
        """Main parsing function"""
        try:
            self.program()
            if self.position < len(self.tokens):
                self.errors.append(f"Unexpected tokens after parsing: {self.tokens[self.position:]}")
            
            if not self.errors:
                return True, "✓ Code parsed successfully! No syntax errors found."
            else:
                return False, "✗ Syntax errors found:\n  " + "\n  ".join(self.errors)
        except Exception as e:
            return False, f"✗ Parser error: {str(e)}"
    
    def program(self):
        """program -> statement_list"""
        self.statement_list()
    
    def statement_list(self):
        """statement_list -> statement statement_list | statement"""
        while self.current_token() is not None:
            if not self.statement():
                break
    
    def statement(self):
        """statement -> declaration | assignment | if_statement | return_statement | block | function_declaration"""
        token = self.current_token()
        if token is None:
            return False
        
        token_type, token_value = token
        
        # Block statement
        if token_type == 'PUNCTUATION' and token_value == '{':
            return self.block()
        
        # Return statement
        if token_type == 'KEYWORD' and token_value == 'return':
            return self.return_statement()
        
        # If statement
        if token_type == 'KEYWORD' and token_value == 'if':
            return self.if_statement()
        
        # Function declaration or variable declaration (type identifier ...)
        if token_type == 'KEYWORD' and token_value in ['int', 'float', 'double', 'char', 'void', 'bool']:
            # Look ahead to see if it's a function (has parentheses after identifier)
            next_token = self.peek_token()
            next_next_token = self.peek_token(2)
            
            if next_token and next_token[0] == 'IDENTIFIER' and next_next_token and next_next_token[0] == 'PUNCTUATION' and next_next_token[1] == '(':
                return self.function_declaration()
            else:
                return self.declaration()
        
        # Assignment (identifier = ...)
        if token_type == 'IDENTIFIER':
            next_token = self.peek_token()
            if next_token and next_token[0] == 'OPERATOR' and next_token[1] == '=':
                return self.assignment()
        
        # Skip comments
        if token_type == 'COMMENT':
            self.consume()
            return True
        
        # Skip unrecognized tokens
        self.position += 1
        return True
    
    def declaration(self):
        """declaration -> type IDENTIFIER [, IDENTIFIER]* [= expression] ;"""
        # Consume type
        self.consume('KEYWORD')
        
        # Consume identifier(s) - handle comma-separated declarations
        while True:
            if not self.consume('IDENTIFIER'):
                return False
            
            # Check for initialization
            token = self.current_token()
            if token and token[0] == 'OPERATOR' and token[1] == '=':
                self.consume()
                self.expression()
            
            # Check for comma (more declarations)
            token = self.current_token()
            if token and token[0] == 'PUNCTUATION' and token[1] == ',':
                self.consume('PUNCTUATION', ',')
                continue
            else:
                break
        
        # Consume semicolon
        if not self.consume('PUNCTUATION', ';'):
            return False
        
        return True
    
    def assignment(self):
        """assignment -> IDENTIFIER = expression ;"""
        self.consume('IDENTIFIER')
        self.consume('OPERATOR', '=')
        self.expression()
        
        if not self.consume('PUNCTUATION', ';'):
            return False
        
        return True
    
    def if_statement(self):
        """if_statement -> if ( condition ) block [else block]"""
        self.consume('KEYWORD', 'if')
        
        if not self.consume('PUNCTUATION', '('):
            return False
        
        self.condition()
        
        if not self.consume('PUNCTUATION', ')'):
            return False
        
        self.block()
        
        # Check for else
        token = self.current_token()
        if token and token[0] == 'KEYWORD' and token[1] == 'else':
            self.consume('KEYWORD', 'else')
            self.block()
        
        return True
    
    def return_statement(self):
        """return_statement -> return expression ;"""
        self.consume('KEYWORD', 'return')
        self.expression()
        
        if not self.consume('PUNCTUATION', ';'):
            return False
        
        return True
    
    def block(self):
        """block -> { statement_list }"""
        if not self.consume('PUNCTUATION', '{'):
            return False
        
        while self.current_token() and not (self.current_token()[0] == 'PUNCTUATION' and self.current_token()[1] == '}'):
            self.statement()
        
        if not self.consume('PUNCTUATION', '}'):
            return False
        
        return True
    
    def expression(self):
        """expression -> term [OPERATOR term]*"""
        if not self.term():
            return False
        
        # Handle operators and continuing expressions
        while True:
            token = self.current_token()
            if token and token[0] == 'OPERATOR' and token[1] not in ['=']:
                self.consume('OPERATOR')
                if not self.term():
                    return False
            else:
                break
        
        return True
    
    def term(self):
        """term -> IDENTIFIER | NUMBER | ( expression )"""
        token = self.current_token()
        if token is None:
            self.errors.append("Expected term (identifier, number, or expression)")
            return False
        
        token_type, token_value = token
        
        # Parenthesized expression
        if token_type == 'PUNCTUATION' and token_value == '(':
            self.consume('PUNCTUATION', '(')
            self.expression()
            if not self.consume('PUNCTUATION', ')'):
                return False
            return True
        
        # Identifier or number
        if token_type in ['IDENTIFIER', 'NUMBER']:
            self.consume()
            return True
        
        self.errors.append(f"Expected identifier or number, got {token_type} '{token_value}'")
        return False
    
    def condition(self):
        """condition -> expression OPERATOR expression"""
        self.expression()
    
    def function_declaration(self):
        """function_declaration -> type IDENTIFIER ( [parameters] ) block"""
        # Consume return type
        self.consume('KEYWORD')
        
        # Consume function name
        if not self.consume('IDENTIFIER'):
            return False
        
        # Consume opening parenthesis
        if not self.consume('PUNCTUATION', '('):
            return False
        
        # Handle parameters (simplified - just skip everything until closing paren)
        while self.current_token() and not (self.current_token()[0] == 'PUNCTUATION' and self.current_token()[1] == ')'):
            self.consume()
        
        # Consume closing parenthesis
        if not self.consume('PUNCTUATION', ')'):
            return False
        
        # Consume function body (block)
        return self.block()

def main():
    print("=" * 70)
    print("C++ SCANNER AND PARSER")
    print("=" * 70)
    print("\nBuilt-in Grammar for C++ subset:")
    print("  - Variable declarations: int x;")
    print("  - Assignments: x = 5;")
    print("  - If statements: if (x > 0) { ... }")
    print("  - Return statements: return x;")
    print("  - Blocks: { ... }")
    print("=" * 70)
    print()
    
    while True:
        print("\nEnter your C++ code (press Enter twice when finished):")
        print("Or type 'exit' to quit")
        print("-" * 70)
        
        lines = []
        empty_count = 0
        
        while True:
            line = input()
            if line.lower() == 'exit':
                print("\nExiting...")
                return
            
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        
        if not lines:
            print("No code entered.")
            continue
        
        code = '\n'.join(lines)
        
        # SCANNER PHASE
        print("\n" + "=" * 70)
        print("SCANNER OUTPUT - TOKENS")
        print("=" * 70)
        tokens = scanner(code)
        
        if not tokens:
            print("No tokens found!")
            continue
        
        for i, (token_type, token_value) in enumerate(tokens, 1):
            display_value = token_value.replace('\n', '\\n')
            print(f"{i:3d}. ({token_type:15s}) '{display_value}'")
        
        print(f"\nTotal tokens: {len(tokens)}")
        
        # PARSER PHASE
        print("\n" + "=" * 70)
        print("PARSER OUTPUT - SYNTAX ANALYSIS")
        print("=" * 70)
        
        parser = CppParser(tokens)
        success, message = parser.parse()
        
        print(message)
        
        if success:
            print("\n✓ The code is syntactically correct!")
        else:
            print("\n✗ The code has syntax errors!")
        
        print("\n" + "=" * 70)
        choice = input("\nParse another code? (y/n): ")
        if choice.lower() != 'y':
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
