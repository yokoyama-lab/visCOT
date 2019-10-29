# lexerを生成する．PLYを用いる．

import ply.lex as lex

tokens = (
    'CONS',
    'NIL',
    'A0',
    'LPAREN',
    'RPAREN',
    'COMMA',
    'A_PLUS',
    'A_MINUS',
    'B0_PLUS',
    'B0_MINUS',
    'A2',
    'LEAF',
    'B_PLUS_PLUS',
    'B_PLUS_MINUS',
    'B_MINUS_PLUS',
    'B_MINUS_MINUS',
    'BETA_MINUS',
    'BETA_PLUS',
    'C_PLUS',
    'C_MINUS',
)

t_ignore = ' \t\n'              # 入力を無視する
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COMMA  = r','
t_CONS = r'cons'
t_NIL = r'n'
t_A0 = r'a0'
t_A_PLUS = r'a\+'
# ここにoperationsを足していく
t_B0_PLUS = r'b0\+'
t_B0_MINUS = r'b0\-'
t_A_MINUS = r'a\-'
t_A2 = r'a2'
t_LEAF = r'l'
t_B_PLUS_PLUS = r'b\+\+'
t_B_PLUS_MINUS = r'b\+\-'
t_BETA_PLUS = r'be\+'
t_B_MINUS_MINUS = r'b\-\-'
t_B_MINUS_PLUS = r'b\-\+'
t_BETA_MINUS = r'be\-'
t_C_PLUS = r'c\+'
t_C_MINUS = r'c\-'

# error handling
def t_error(t):
    print("不正な文字 '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()
