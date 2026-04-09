from Lexer import YaadmanLexer
from Parser import parse

# TOKENIZE FUNCTION
def tokenize(code):
    lexer = YaadmanLexer()
    lexer.lexer.input(code)

    tokens = []
    while True:
        tok = lexer.lexer.token()
        if not tok:
            break
        tokens.append({
            "type": tok.type,
            "value": tok.value,
            "line": tok.lineno
        })

    return tokens


# PRINT TOKENS
def print_tokens(code):
    toks = tokenize(code)

    print("═" * 50)
    print("YAADMAN TOKENS")
    print("═" * 50)

    for t in toks:
        print(f"{t['type']:15} | {str(t['value']):10} | line {t['line']}")

    print("═" * 50)


# AST VIEW
def show_ast(code):
    tree = parse(code)

    print("═" * 50)
    print("YAADMAN AST")
    print("═" * 50)
    print(tree.pretty())
    print("═" * 50)