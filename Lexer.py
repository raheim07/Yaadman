import ply.lex as lex

class YaadmanLexer:
    reserved = {
        'Start': 'START',
        'Done': 'DONE',
        'Mek': 'MEK',
        'Set': 'SET',
        'To': 'TO',
        'Show': 'SHOW',
        'Tek': 'TEK',
        'if': 'IF',
        'Else': 'ELSE',
        'While': 'WHILE',
        'For': 'FOR',
        'Function': 'FUNCTION',
        'Return': 'RETURN',
        'Try': 'TRY',
        'Ketch': 'KETCH',
        'Number': 'NUMBER_TYPE',
        'Text': 'TEXT_TYPE',
        'True': 'TRUE',
        'False': 'FALSE',
    }

    tokens = [
        'NAME',
        'NUMBER',
        'STRING',
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'EQ',
        'LT',
        'GT',
        'LE',
        'GE',
        'LPAREN',
        'RPAREN',
        'LBRACE',
        'RBRACE',
        'SEMI',
        'COLON',
        'COMMA',
    ] + list(reserved.values())

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_EQ = r'=='
    t_LE = r'<='
    t_GE = r'>='
    t_LT = r'<'
    t_GT = r'>'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_SEMI = r';'
    t_COLON = r':'
    t_COMMA = r','

    t_ignore = ' \t'

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def t_STRING(self, t):
        r'"([^\\\n]|(\\.))*?"'
        t.value = t.value[1:-1]
        return t

    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        t.value = float(t.value) if '.' in t.value else int(t.value)
        return t

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value, 'NAME')
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
        t.lexer.skip(1)

# Initialize the object
yaadman_lexer = YaadmanLexer()