import re

# Define token types
keywords = {"int", "if", "return", "for", "char", "double", "while", "void", "float"}
operators = r"[+\-*/=<>!]+"
punctuation = r"[;,\(\)\{\}]"
identifier = r"[a-zA-Z_]\w*"
numeric_constant = r"\b\d+(\.\d+)?\b"
character_constant = r"'(\\.|[^\\'])'"
whitespace = r"[ \t]+"
newline = r"\n"
single_line_comment = r"//[^\n]*"
multi_line_comment = r"/\*[\s\S]*?\*/"

# Terminal characters (similar to C++ version)
terminals = set('=+-*/%|\\&^!#(){}[]\';:,."~`_')

def scanner(code):
    """
    Scans the input code and returns a list of tokens
    """
    tokens = []
    position = 0
    
    while position < len(code):
        match = None
        
        if match := re.match(single_line_comment, code[position:]):
            tokens.append(('SINGLE_LINE_COMMENT', match.group()))
            
        elif match := re.match(multi_line_comment, code[position:]):
            tokens.append(('MULTI_LINE_COMMENT', match.group()))
            
        elif match := re.match(identifier, code[position:]):
            text = match.group()
            if text in keywords:
                tokens.append(('KEYWORD', text))
            else:
                tokens.append(('IDENTIFIER', text))

        elif match := re.match(numeric_constant, code[position:]):
            tokens.append(('NUMERIC_CONSTANT', match.group()))

        elif match := re.match(character_constant, code[position:]):
            tokens.append(('CHARACTER_CONSTANT', match.group()))

        elif match := re.match(operators, code[position:]):
            tokens.append(('OPERATOR', match.group()))

        elif match := re.match(punctuation, code[position:]):
            tokens.append(('PUNCTUATION', match.group()))

        elif match := re.match(newline, code[position:]):
            tokens.append(('NEWLINE', '\\n'))

        elif match := re.match(whitespace, code[position:]):
            tokens.append(('WHITESPACE', match.group()))

        if match:
            position += len(match.group())
        else:
            position += 1
    
    return tokens

def tokens_to_string(tokens):
    """
    Convert tokens back to a string for parser input
    Filters out whitespace, newlines, and comments
    """
    result = []
    for token_type, token_value in tokens:
        if token_type not in ['WHITESPACE', 'NEWLINE', 'SINGLE_LINE_COMMENT', 'MULTI_LINE_COMMENT']:
            result.append(token_value)
    return ''.join(result)

def is_terminal(char):
    """
    Check if a character is a terminal (lowercase, digit, or special symbol)
    """
    return char.islower() or char.isdigit() or char in terminals

def is_simple_grammar(grammar):
    """
    Check if the grammar is a simple grammar
    """
    print("\nDEBUG: Checking grammar:")
    for i, (non_terminal, production) in enumerate(grammar):
        print(f"  Rule {i+1}: {non_terminal} -> {production}")
        print(f"    Non-terminal '{non_terminal}' is terminal? {is_terminal(non_terminal)}")
        if production:
            print(f"    First symbol '{production[0]}' is terminal? {is_terminal(production[0])}")
    
    # Check each rule
    for non_terminal, production in grammar:
        # Non-terminal must be uppercase
        if is_terminal(non_terminal):
            print(f"  ERROR: Non-terminal '{non_terminal}' is a terminal!")
            return False
        # First symbol of production must be terminal
        if not production or not is_terminal(production[0]):
            print(f"  ERROR: Production '{production}' doesn't start with terminal!")
            return False
    
    # Check that S rules have different first terminals
    if grammar[0][1][0] == grammar[1][1][0]:
        print(f"  ERROR: S rules have same first terminal '{grammar[0][1][0]}'")
        return False
    
    # Check that B rules have different first terminals
    if grammar[2][1][0] == grammar[3][1][0]:
        print(f"  ERROR: B rules have same first terminal '{grammar[2][1][0]}'")
        return False
    
    print("  ✓ Grammar is valid!")
    return True

def parse(input_string, grammar):
    """
    Parse the input string using the given grammar
    Returns (accepted, stack, remaining_index)
    """
    stack = ['S']
    idx = 0
    
    while stack:
        if idx == len(input_string):
            break
        
        top = stack[-1]
        
        if is_terminal(top):
            # Terminal on stack - must match input
            if top == input_string[idx]:
                stack.pop()
                idx += 1
            else:
                return False, stack, idx
        else:
            # Non-terminal on stack - apply production rule
            non_terminal_idx = None
            
            if top == 'S':
                non_terminal_idx = 0
            elif top == 'B':
                non_terminal_idx = 2
            else:
                return False, stack, idx
            
            # Determine which rule to apply
            if idx < len(input_string) and input_string[idx] == grammar[non_terminal_idx][1][0]:
                rule_idx = non_terminal_idx
            elif idx < len(input_string) and input_string[idx] == grammar[non_terminal_idx + 1][1][0]:
                rule_idx = non_terminal_idx + 1
            else:
                return False, stack, idx
            
            # Apply the production rule
            stack.pop()
            production = grammar[rule_idx][1]
            # Push symbols in reverse order
            for symbol in reversed(production):
                stack.append(symbol)
    
    # Accept if stack is empty and all input consumed
    accepted = len(stack) == 0 and idx == len(input_string)
    return accepted, stack, idx

def main():
    print("=" * 60)
    print("INTEGRATED SCANNER AND PARSER")
    print("=" * 60)
    print()
    
    while True:
        # Get C code input
        print("Enter the C code you want to scan (or 'quit' to exit):")
        print("(Press Enter twice when finished)")
        lines = []
        empty_count = 0
        
        while True:
            line = input()
            if line.lower() == 'quit':
                return
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        
        if not lines:
            print("No code entered. Exiting...")
            break
        
        code = '\n'.join(lines)
        
        # SCANNER PHASE
        print("\n" + "=" * 60)
        print("SCANNER OUTPUT")
        print("=" * 60)
        tokens = scanner(code)
        
        for token in tokens:
            print(token)
        
        # Convert tokens to string for parser
        token_string = tokens_to_string(tokens)
        
        print("\n" + "=" * 60)
        print("TOKEN STRING FOR PARSER")
        print("=" * 60)
        print(f"'{token_string}'")
        print()
        
        # PARSER PHASE
        print("=" * 60)
        print("PARSER CONFIGURATION")
        print("=" * 60)
        
        # Get grammar rules
        grammar = []
        grammar.append(('S', ''))
        grammar.append(('S', ''))
        grammar.append(('B', ''))
        grammar.append(('B', ''))
        
        for i in range(4):
            non_terminal = 'S' if i < 2 else 'B'
            rule = input(f"Enter rule number {i+1} for non-terminal '{non_terminal}': ")
            grammar[i] = (non_terminal, rule)
        
        print()
        
        # Check if grammar is simple
        if not is_simple_grammar(grammar):
            print("Not a simple grammar")
            print()
            continue
        
        print("Grammar is valid (simple grammar)")
        print()
        
        # Parse loop
        while True:
            input_str = input("Enter the string to be checked: ")
            
            print(f"The input string: [{', '.join(repr(c) for c in input_str)}]")
            
            # Parse the string
            accepted, final_stack, rest_idx = parse(input_str, grammar)
            
            print(f"Stack after checking: [{', '.join(repr(c) for c in final_stack)}]")
            print(f"The rest of the unchecked string: [{', '.join(repr(c) for c in input_str[rest_idx:])}]")
            
            if accepted:
                print("The input string is Accepted.")
            else:
                print("The input string is Rejected.")
            
            print()
            print("1- Another grammar.")
            print("2- Another string.")
            print("3- Exit.")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                break
            elif choice == '3':
                return
            # Otherwise, continue with choice 2 (another string)
            print()

if __name__ == "__main__":
    main()
