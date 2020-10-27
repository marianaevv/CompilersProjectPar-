# A00513571 Mariana Villegas
# A00820323 Noé Campos

import ply.lex as lex
import ply.yacc as yacc
import sys

from FunctionTable import FunctionTable

# Initialize the helper objects
funcTable = FunctionTable()


# Flags to make certain validations
flgError = False
flgHaveReturn = False

# Tokens definition
tokens = [
    # Arithmetic Operators
    'MINUS',
    'PLUS',
    'MULTIPLY',
    'DIVIDE',
    'MOD',
    'INCREMENT',
    'DECREMENT',
    # Relational Operators
    'COMPARISON',
    'DIFFERENT',
    'GREATERTHAN',
    'LESSTHAN',
    'GREATERHANOREQUAL',
    'LESSTHANOREQUAL',
    # Logical Operators
    'AND',
    'OR',
    # Assignment Operators
    'EQUALS',
    'PLUSEQUALS',
    'SUBSTRACTEQUALS',
    # Others
    'ID',
    'COMMA',
    'LEFTBRACKET',
    'RIGHTBRACKET',
    'LEFTSQRBRACKET',
    'RIGHTSQRBRACKET',
    'LEFTPARENTHESIS',
    'RIGHTPARENTHESIS',
    'SEMICOLON',
    'CTESTRING',
    'CTECHAR',
    'CTEFLOAT',
    'CTEINT'
]

# Reserved words definition
reserved = {
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR',
    'void': 'VOID',
    'var': 'VAR',
    'module': 'MODULE',
    'return': 'RETURN',
    'while': 'WHILE',
    'for': 'FOR',
    'do': 'DO',
    'to': 'TO',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'read': 'READ',
    'write': 'WRITE',
    'program': 'PROGRAM',
    'main': 'MAIN'
}

tokens += list(reserved.values())

# Token expressions
t_MINUS = r'\-'
t_PLUS = r'\+'
t_MULTIPLY = r'\*'
t_DIVIDE = r'\/'
t_MOD = r'\%'
t_INCREMENT = r'\+\+'
t_DECREMENT = r'\-\-'

t_COMPARISON = r'\=\='
t_GREATERHANOREQUAL = r'\>\='
t_LESSTHANOREQUAL = r'\<\='
t_GREATERTHAN = r'\>'
t_LESSTHAN = r'\<'
t_DIFFERENT = r'\!\='

t_AND = r'\&'
t_OR = r'\|'

t_EQUALS = r'\='
t_PLUSEQUALS = r'\+\='
t_SUBSTRACTEQUALS = r'\-\='
t_LEFTBRACKET = r'\{'
t_RIGHTBRACKET = r'\}'
t_LEFTSQRBRACKET = r'\['
t_RIGHTSQRBRACKET = r'\]'
t_LEFTPARENTHESIS = r'\('
t_RIGHTPARENTHESIS = r'\)'
t_COMMA = r'\,'
t_SEMICOLON = r'\;'
t_ignore = ' \t'


def t_CTECHAR(token):
    r'"([^"])"'
    token.value = str(token.value)
    return token


def t_CTESTRING(token):
    r'"([^"]*)"'
    token.value = str(token.value)
    return token


def t_CTEFLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_CTEINT(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_CTEBOOL(t):
    r'(true|false)'
    t.value(t.value == "true")
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(token):
    print('No apropiado')
    token.lexer.skip(1)


lexer = lex.lex()


# ====================== Main ======================
def p_program(p):
    '''
    program : PROGRAM ID SEMICOLON vars MAIN LEFTPARENTHESIS RIGHTPARENTHESIS block
            | PROGRAM ID SEMICOLON functions_list MAIN LEFTPARENTHESIS RIGHTPARENTHESIS block
            | PROGRAM ID SEMICOLON MAIN LEFTPARENTHESIS RIGHTPARENTHESIS block
    '''


# ====================== Variables ======================
def p_data_type(p):
    '''
    data_type : INT
              | FLOAT
              | CHAR
    '''
    p[0] = p[1]


def p_vars(p):
    '''
    vars : VAR vars_lists
    '''
    # Add the variables to the current function
    funcTable.addVariables(p[-2], p[2])


def p_vars_lists(p):
    '''
    vars_lists : data_type decla_ids_list SEMICOLON vars_lists
               | data_type decla_ids_list SEMICOLON functions_list
               | data_type decla_ids_list SEMICOLON
    '''
    # Map the id list to a tupple format (VarType, ID)
    p[0] = list(map(lambda x: (p[1], x), p[2]))

    # Put all the IDs list together
    if(len(p) > 4):
        if(type(p[4]) == list):
            p[0] += p[4]


def p_decla_ids_list(p):
    '''
    decla_ids_list : decla_identifier COMMA decla_ids_list
                   | decla_identifier
    '''
    # Return an array with all the IDs of the current id list
    if(len(p) == 2):
        p[0] = [p[1]]
    elif(len(p) > 2):
        p[0] = [p[1]] + p[3]


def p_decla_identifier(p):
    '''
    decla_identifier : ID LEFTSQRBRACKET CTEINT RIGHTSQRBRACKET LEFTSQRBRACKET CTEINT RIGHTSQRBRACKET
                     | ID LEFTSQRBRACKET CTEINT RIGHTSQRBRACKET
                     | ID
    '''
    p[0] = p[1]


def p_ids_list(p):
    '''
    ids_list : identifier COMMA ids_list
             | identifier
    '''
    pass


def p_identifier(p):
    '''
    identifier : ID LEFTSQRBRACKET expresion RIGHTSQRBRACKET LEFTSQRBRACKET expresion RIGHTSQRBRACKET
               | ID LEFTSQRBRACKET expresion RIGHTSQRBRACKET
               | ID
    '''
    pass


# ====================== Functions ======================
def p_return_type(p):
    '''
    return_type : data_type
                | VOID
    '''
    p[0] = p[1]


def p_function(p):
    '''
    function : return_type MODULE ID parameters_list vars block
             | return_type MODULE ID parameters_list block
    '''
    global flgHaveReturn

    # Makes the validation if the function is not void and does not have a return
    if(p[1] != 'void' and not flgHaveReturn):
        raise Exception(
            'Function "{}" need a return of type {}'.format(p[3], p[1]))

    # or if the function is void and have a return
    elif(p[1] == 'void' and flgHaveReturn):
        raise Exception(
            'Function "{}" is void and does not need a return'.format(p[3]))

    # for i in p:
    #     print(i, end=' ')
    # print()

    flgHaveReturn = False


def p_functions_list(p):
    '''
    functions_list : function functions_list
                   | function
    '''
    pass


def p_parameters_list(p):
    '''
    parameters_list : LEFTPARENTHESIS parameter RIGHTPARENTHESIS
                    | LEFTPARENTHESIS RIGHTPARENTHESIS
    '''
    pass


def p_parameter(p):
    '''
    parameter : data_type decla_identifier COMMA parameter
              | data_type decla_identifier
    '''
    pass


# ====================== Operators ======================
def p_comparators(p):
    '''
    comparators : COMPARISON
                | GREATERHANOREQUAL
                | LESSTHANOREQUAL
                | GREATERTHAN
                | LESSTHAN
                | DIFFERENT
                | OR
                | AND
    '''
    pass


def p_exp_operator(p):
    '''
    exp_operator : PLUS
                 | MINUS
    '''
    pass


def p_term_operator(p):
    '''
    term_operator : MULTIPLY
                  | DIVIDE
                  | MOD
    '''
    pass


# ====================== Statutes ======================
def p_block(p):
    '''
    block : LEFTBRACKET statutes_list RIGHTBRACKET
          | LEFTBRACKET RIGHTBRACKET
    '''
    pass


def p_statutes_list(p):
    '''
    statutes_list : statute statutes_list
                  | statute
    '''
    pass


def p_statute(p):
    '''
    statute : asignation
            | reading
            | writing
            | decision
            | loop
            | function_return
            | function_call SEMICOLON
    '''
    pass


def p_asignation(p):
    '''
    asignation : identifier EQUALS expresion SEMICOLON
               | identifier PLUSEQUALS expresion SEMICOLON
               | identifier SUBSTRACTEQUALS expresion SEMICOLON
               | identifier INCREMENT SEMICOLON
               | identifier DECREMENT SEMICOLON
    '''
    pass


def p_reading(p):
    '''
    reading : READ LEFTPARENTHESIS ids_list RIGHTPARENTHESIS SEMICOLON
    '''
    pass


def p_writing(p):
    '''
    writing : WRITE LEFTPARENTHESIS writing_list RIGHTPARENTHESIS SEMICOLON
    '''
    pass


def p_writing_list(p):
    '''
    writing_list : CTESTRING COMMA writing_list
                 | expresion COMMA writing_list
                 | CTESTRING
                 | expresion
    '''
    pass


def p_decision(p):
    '''
    decision : IF LEFTPARENTHESIS expresion RIGHTPARENTHESIS THEN block ELSE block
             | IF LEFTPARENTHESIS expresion RIGHTPARENTHESIS THEN block
    '''
    pass


def p_loop(p):
    '''
    loop : conditional block
         | non_conditional block
    '''
    pass


def p_conditional(p):
    '''
    conditional : WHILE LEFTPARENTHESIS expresion RIGHTPARENTHESIS DO
    '''
    pass


def p_non_conditional(p):
    '''
    non_conditional : FOR ID EQUALS exp TO exp DO
    '''
    pass


def p_function_return(p):
    '''
    function_return : RETURN LEFTPARENTHESIS exp RIGHTPARENTHESIS SEMICOLON
    '''
    global flgHaveReturn
    flgHaveReturn = True


def p_function_call(p):
    '''
    function_call : ID LEFTPARENTHESIS expresion_list RIGHTPARENTHESIS
    '''
    pass


def p_expresion_list(p):
    '''
    expresion_list : expresion COMMA expresion_list
                   | expresion
    '''
    pass


def p_expresion(p):
    '''
    expresion : exp comparators exp
              | exp
    '''
    pass


def p_exp(p):
    '''
    exp : term exp_operator exp
        | term
    '''
    pass


def p_term(p):
    '''
    term : factor term_operator term
         | factor
    '''
    pass


def p_factor(p):
    '''
    factor : LEFTPARENTHESIS expresion RIGHTPARENTHESIS
           | exp_operator opt_value
           | opt_value
    '''
    pass


def p_opt_value(p):
    '''
    opt_value : CTEINT
              | CTEFLOAT
              | CTECHAR
              | function_call
              | identifier
    '''
    pass


def p_error(p):
    # Error rule for syntax errors
    global flgError
    flgError = True
    print("\n-> No apropiado\n")


# Build the parser
parser = yacc.yacc()

# Needed stacks (list on python)
stackOperand = list()
stackType = list()
stackOperator = list()
stackJumps = list()

try:
    # Read the source file
    fileName = './Tests/Input.txt'
    f = open(fileName, "r")
    srcFile = f.read()

    # Parser the input
    result = parser.parse(srcFile)

    if not flgError:
        print("\n-> Apropiado\n")

except FileNotFoundError:
    print("\n-> No existe el archivo\n")
