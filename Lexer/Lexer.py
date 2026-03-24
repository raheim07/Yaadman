import ply.lex as lex

reserved = {
   'let'    : 'LET',
   'print'  : 'PRINT',
   'try'    : 'TRY',
   'except' : 'EXCEPT'
}

tokens = [
    'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 
    'EQUALS', 'LPAREN', 'RPAREN', 'NAME', 'LBRACE', 'RBRACE'
] + list(reserved.values())

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'

# The NEW Decimal-aware NUMBER rule
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'NAME')
    return t

t_ignore = ' \t'

def t_error(t):
    print(f"Lexical error: '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()