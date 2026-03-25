import ply.lex as lex

class YaadmanLexer:
    reserved = {
        'mek': 'MEK', 'show': 'SHOW', 'try': 'TRY',
        'ketch': 'KETCH', 'if': 'IF', 'den': 'DEN', 'else': 'ELSE'
    }

    tokens = [
        'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 
        'EQUALS', 'LPAREN', 'RPAREN', 'EQ', 'LT', 'GT', 'NAME',
        'NEWLINE', 'INDENT', 'DEDENT', 'COLON'
    ] + list(reserved.values())

    t_PLUS, t_MINUS = r'\+', r'-'
    t_TIMES, t_DIVIDE = r'\*', r'/'
    t_EQ, t_LT, t_GT = r'==', r'<', r'>'
    t_EQUALS, t_LPAREN, t_RPAREN, t_COLON = r'=', r'\(', r'\)', r':'
    t_ignore = ' \t'

    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.indent_stack = [0]
        self.token_queue = []

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value, 'NAME')
        return t

    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t

    def t_newline(self, t):
        r'\n[ ]*'
        spaces = len(t.value) - 1
        last_indent = self.indent_stack[-1]

        if spaces > last_indent:
            self.indent_stack.append(spaces)
            t.type = 'INDENT'
            return t
        
        elif spaces < last_indent:
            # Handle multiple dedents
            while spaces < self.indent_stack[-1]:
                self.indent_stack.pop()
                # Create a manual token object
                dedent_tok = lex.LexToken()
                dedent_tok.type = 'DEDENT'
                dedent_tok.value = None
                dedent_tok.lineno = t.lineno
                dedent_tok.lexpos = t.lexpos
                self.token_queue.append(dedent_tok)
            
            # Return a NEWLINE as the current token, 
            # DEDENTs stay in the queue for later
            t.type = 'NEWLINE'
            return t

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}'")
        t.lexer.skip(1)

    # CRITICAL: This method intercepts the parser's request for a token
    def token(self):
        if self.token_queue:
            return self.token_queue.pop(0)
        return self.lexer.token()

# Initialize the object
yaadman_lexer = YaadmanLexer()