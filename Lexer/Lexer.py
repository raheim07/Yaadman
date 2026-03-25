import ply.lex as lex

class YaadmanLexer:
    reserved = {
        'mek': 'MEK', 'show': 'SHOW', 'try': 'TRY',
        'ketch': 'KETCH', 'if': 'IF', 'den': 'DEN', 'else': 'ELSE'
    }

    tokens = [
        'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 
        'EQUALS', 'LPAREN', 'RPAREN', 'EQ', 'LT', 'GT', 'NAME',
        'LBRACE', 'RBRACE', 'COLON'
    ] + list(reserved.values())

    t_PLUS, t_MINUS = r'\+', r'-'
    t_TIMES, t_DIVIDE = r'\*', r'/'
    t_EQ, t_LT, t_GT = r'==', r'<', r'>'
    t_EQUALS, t_LPAREN, t_RPAREN, t_COLON = r'=', r'\(', r'\)', r':'
    t_LBRACE, t_RBRACE = r'\{', r'\}'
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



    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}'")
        t.lexer.skip(1)

# Initialize the object
yaadman_lexer = YaadmanLexer()