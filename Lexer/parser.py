import ply.yacc as yacc
from Lexer import YaadmanLexer

tokens = YaadmanLexer.tokens


class ASTNode:
    def __init__(self, node_type, children=None, value=None, lineno=0):
        self.node_type = node_type
        self.children = children or []
        self.value = value
        self.lineno = lineno

    def __repr__(self, level=0):
        indent = "    " * level
        label = self.node_type

        if self.value is not None:
            if self.node_type in ('BinOp', 'Condition', 'UnaryMinus'):
                label += f"({self.value})"
            else:
                label += f"({self.value!r})"

        if self.lineno:
            label += f" [line {self.lineno}]"

        lines = [indent + label]

        for child in self.children:
            if isinstance(child, ASTNode):
                lines.append(child.__repr__(level + 1))
            elif isinstance(child, list):
                for item in child:
                    if isinstance(item, ASTNode):
                        lines.append(item.__repr__(level + 1))

        return "\n".join(lines)

    def pretty(self):
        return self.__repr__()


precedence = (
    ('left', 'EQ', 'LT', 'GT', 'GE', 'LE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'),
)


# =========================================================
# PROGRAM
# =========================================================

def p_program(p):
    'program : START LBRACE program_body RBRACE DONE SEMI'
    p[0] = ASTNode('Program', children=p[3], lineno=p.lineno(1))


def p_program_body_single(p):
    'program_body : program_element'
    p[0] = [p[1]]


def p_program_body_multi(p):
    'program_body : program_element program_body'
    p[0] = [p[1]] + p[2]


def p_program_element(p):
    '''program_element : func_def
                       | statement'''
    p[0] = p[1]


# =========================================================
# STATEMENT LIST
# =========================================================

def p_statement_list_single(p):
    'statement_list : statement'
    p[0] = [p[1]]


def p_statement_list_multi(p):
    'statement_list : statement statement_list'
    p[0] = [p[1]] + p[2]


# =========================================================
# STATEMENTS
# =========================================================

def p_statement(p):
    '''statement : declaration
                 | assignment
                 | show_statement
                 | tek_statement
                 | if_statement
                 | while_statement
                 | for_statement
                 | func_call
                 | return_statement
                 | try_catch_statement'''
    p[0] = p[1]


# =========================================================
# TYPES / DECLARATIONS / ASSIGNMENTS
# =========================================================

def p_type_number(p):
    'type : NUMBER_TYPE'
    p[0] = 'number'


def p_type_text(p):
    'type : TEXT_TYPE'
    p[0] = 'text'


def p_declaration(p):
    'declaration : MEK NAME type SEMI'
    p[0] = ASTNode(
        'Declare',
        value={'name': p[2], 'type': p[3]},
        lineno=p.lineno(1)
    )


def p_assignment(p):
    'assignment : SET NAME TO expression SEMI'
    p[0] = ASTNode(
        'Assign',
        children=[
            ASTNode('Identifier', value=p[2], lineno=p.lineno(2)),
            p[4]
        ],
        lineno=p.lineno(1)
    )


# =========================================================
# SHOW / OUTPUT
# =========================================================

def p_show_statement(p):
    'show_statement : SHOW show_list SEMI'
    p[0] = ASTNode('Show', children=p[2], lineno=p.lineno(1))


def p_show_list_single(p):
    'show_list : show_item'
    p[0] = [p[1]]


def p_show_list_multi(p):
    'show_list : show_item COMMA show_list'
    p[0] = [p[1]] + p[3]


def p_show_item_name(p):
    'show_item : NAME'
    p[0] = ASTNode('Identifier', value=p[1], lineno=p.lineno(1))


def p_show_item_string(p):
    'show_item : STRING'
    p[0] = ASTNode('StringLiteral', value=p[1], lineno=p.lineno(1))


def p_show_item_expression(p):
    'show_item : expression'
    p[0] = p[1]


# =========================================================
# TEK / INPUT
# =========================================================

def p_tek_statement(p):
    'tek_statement : TEK NAME type SEMI'
    p[0] = ASTNode(
        'Tek',
        value={'name': p[2], 'type': p[3]},
        lineno=p.lineno(1)
    )


# =========================================================
# IF / ELSE
# =========================================================

def p_if_statement_no_else(p):
    'if_statement : IF LPAREN condition RPAREN LBRACE statement_list RBRACE'
    p[0] = ASTNode(
        'If',
        children=[
            p[3],
            ASTNode('ThenBody', children=p[6], lineno=p.lineno(5))
        ],
        lineno=p.lineno(1)
    )


def p_if_statement_with_else(p):
    'if_statement : IF LPAREN condition RPAREN LBRACE statement_list RBRACE ELSE LBRACE statement_list RBRACE'
    p[0] = ASTNode(
        'IfElse',
        children=[
            p[3],
            ASTNode('ThenBody', children=p[6], lineno=p.lineno(5)),
            ASTNode('ElseBody', children=p[10], lineno=p.lineno(9))
        ],
        lineno=p.lineno(1)
    )


# =========================================================
# WHILE
# =========================================================

def p_while_statement(p):
    'while_statement : WHILE LPAREN condition RPAREN LBRACE statement_list RBRACE'
    p[0] = ASTNode(
        'While',
        children=[
            p[3],
            ASTNode('WhileBody', children=p[6], lineno=p.lineno(5))
        ],
        lineno=p.lineno(1)
    )


# =========================================================
# FOR
# =========================================================

def p_for_statement(p):
    'for_statement : FOR LPAREN declaration_for COLON condition COLON assignment_for RPAREN LBRACE statement_list RBRACE'
    p[0] = ASTNode(
        'For',
        children=[
            p[3],
            p[5],
            p[7],
            ASTNode('ForBody', children=p[10], lineno=p.lineno(9))
        ],
        lineno=p.lineno(1)
    )


def p_declaration_for(p):
    'declaration_for : MEK NAME type'
    p[0] = ASTNode(
        'Declare',
        value={'name': p[2], 'type': p[3]},
        lineno=p.lineno(1)
    )


def p_assignment_for(p):
    'assignment_for : SET NAME TO expression'
    p[0] = ASTNode(
        'Assign',
        children=[
            ASTNode('Identifier', value=p[2], lineno=p.lineno(2)),
            p[4]
        ],
        lineno=p.lineno(1)
    )


# =========================================================
# FUNCTIONS
# =========================================================

def p_func_def(p):
    'func_def : FUNCTION NAME LPAREN param_list RPAREN LBRACE statement_list RBRACE'
    p[0] = ASTNode(
        'FuncDef',
        value=p[2],
        children=[
            ASTNode('Params', children=p[4], lineno=p.lineno(3)),
            ASTNode('FuncBody', children=p[7], lineno=p.lineno(6))
        ],
        lineno=p.lineno(1)
    )


def p_param_list_single(p):
    'param_list : param'
    p[0] = [p[1]]


def p_param_list_multi(p):
    'param_list : param COMMA param_list'
    p[0] = [p[1]] + p[3]


def p_param_list_empty(p):
    'param_list : empty'
    p[0] = []


def p_param(p):
    'param : NAME type'
    p[0] = ASTNode(
        'Param',
        value={'name': p[1], 'type': p[2]},
        lineno=p.lineno(1)
    )


def p_func_call(p):
    'func_call : NAME LPAREN arg_list RPAREN SEMI'
    p[0] = ASTNode(
        'FuncCall',
        value=p[1],
        children=p[3],
        lineno=p.lineno(1)
    )


def p_func_call_expr(p):
    'func_call_expr : NAME LPAREN arg_list RPAREN'
    p[0] = ASTNode(
        'FuncCallExpr',
        value=p[1],
        children=p[3],
        lineno=p.lineno(1)
    )


def p_arg_list_single(p):
    'arg_list : expression'
    p[0] = [p[1]]


def p_arg_list_multi(p):
    'arg_list : expression COMMA arg_list'
    p[0] = [p[1]] + p[3]


def p_arg_list_empty(p):
    'arg_list : empty'
    p[0] = []


def p_return_statement(p):
    'return_statement : RETURN expression SEMI'
    p[0] = ASTNode('Return', children=[p[2]], lineno=p.lineno(1))


# =========================================================
# TRY / KETCH
# =========================================================

def p_try_catch_statement(p):
    'try_catch_statement : TRY LBRACE statement_list RBRACE KETCH LBRACE statement_list RBRACE'
    p[0] = ASTNode(
        'TryCatch',
        children=[
            ASTNode('TryBody', children=p[3], lineno=p.lineno(1)),
            ASTNode('KetchBody', children=p[7], lineno=p.lineno(5))
        ],
        lineno=p.lineno(1)
    )


# =========================================================
# CONDITIONS
# =========================================================

def p_condition_compare(p):
    '''condition : expression GT expression
                 | expression LT expression
                 | expression EQ expression
                 | expression GE expression
                 | expression LE expression'''
    p[0] = ASTNode(
        'Condition',
        value=p[2],
        children=[p[1], p[3]],
        lineno=p.lineno(2)
    )


def p_condition_bool(p):
    '''condition : TRUE
                 | FALSE'''
    p[0] = ASTNode(
        'BoolLiteral',
        value=(p.slice[1].type == 'TRUE'),
        lineno=p.lineno(1)
    )


# =========================================================
# EXPRESSIONS
# =========================================================

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    p[0] = ASTNode(
        'BinOp',
        value=p[2],
        children=[p[1], p[3]],
        lineno=p.lineno(2)
    )


def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS'
    p[0] = ASTNode('UnaryMinus', children=[p[2]], value='-', lineno=p.lineno(1))


def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]


def p_expression_number(p):
    'expression : NUMBER'
    p[0] = ASTNode('Number', value=p[1], lineno=p.lineno(1))


def p_expression_name(p):
    'expression : NAME'
    p[0] = ASTNode('Identifier', value=p[1], lineno=p.lineno(1))


def p_expression_string(p):
    'expression : STRING'
    p[0] = ASTNode('StringLiteral', value=p[1], lineno=p.lineno(1))


def p_expression_true(p):
    'expression : TRUE'
    p[0] = ASTNode('BoolLiteral', value=True, lineno=p.lineno(1))


def p_expression_false(p):
    'expression : FALSE'
    p[0] = ASTNode('BoolLiteral', value=False, lineno=p.lineno(1))


def p_expression_func_call(p):
    'expression : func_call_expr'
    p[0] = p[1]


# =========================================================
# EMPTY
# =========================================================

def p_empty(p):
    'empty :'
    p[0] = []


# =========================================================
# ERROR HANDLER
# =========================================================

class YaadmanSyntaxError(Exception):
    pass


def p_error(p):
    if p:
        msg = (
            f"[Yaadman Syntax Error] Line {p.lineno}: "
            f"Unexpected token '{p.value}' (type: {p.type}).\n"
            f"  Hints:\n"
            f"    • Every statement ends with ';'\n"
            f"    • Declarations -> Mek <name> Number|Text ;\n"
            f"    • Assignments  -> Set <name> To <expr> ;\n"
            f"    • Program must open with Start {{ and close with }} Done ;\n"
            f"    • Check that all {{ }} blocks are balanced."
        )
    else:
        msg = (
            "[Yaadman Syntax Error] Unexpected end of input.\n"
            "  Hint: the program may be missing Done ; or an unclosed block."
        )
    raise YaadmanSyntaxError(msg)


parser = yacc.yacc(debug=False, write_tables=False)


def parse(source_code: str) -> ASTNode:
    lexer_instance = YaadmanLexer()
    lexer_instance.lexer.lineno = 1
    return parser.parse(source_code, lexer=lexer_instance.lexer)


def parse_and_print(source_code: str) -> None:
    try:
        tree = parse(source_code)
        print("═" * 60)
        print("  YaadmanLang — Abstract Syntax Tree")
        print("═" * 60)
        print(tree.pretty())
        print("═" * 60)
    except YaadmanSyntaxError as e:
        print(e)


if __name__ == "__main__":
    sample = """
    Start {
        Function add(a Number, b Number) {
            Mek result Number;
            Set result To a + b;
            Return result;
        }

        Mek x Number;
        Mek name Text;
        Set x To 20;
        Tek name Text;

        Set x To x + 5 * 2;

        if (x > 25) {
            Show "x is large", x;
        } Else {
            Show "x is small";
        }

        While (x > 0) {
            Set x To x - 1;
        }

        For (Mek i Number : i < 10 : Set i To i + 1) {
            Show i;
        }

        Try {
            Mek d Number;
            Set d To x / 0;
        } Ketch {
            Show "Error: division by zero caught";
        }

        add(10, 20);
    } Done;
    """
    parse_and_print(sample)