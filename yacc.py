# Yacc. PLYを用いる

import ply.yacc as yacc
from lex import tokens
import sys
import flow

def p_expr_a0(p):
     's : A0 LPAREN as RPAREN'
     p[0] = flow.A0(p[3])

def p_expr_b0_plus(p):
     's : B0_PLUS LPAREN b_plus COMMA LPAREN cs_plus RPAREN RPAREN'
     p[0] = flow.B0_plus(p[3], p[6])

def p_expr_b0_minus(p):
     's : B0_MINUS LPAREN b_minus COMMA LPAREN cs_minus RPAREN RPAREN'
     p[0] = flow.B0_minus(p[3], p[6])

def p_expr_as_nil(p):
     'as : NIL'#文法ルール
     p[0] = flow.Nil()

def p_expr_as_cons(p):
     'as : CONS LPAREN a COMMA as RPAREN'
     p[0] = flow.Cons(p[3], p[5])

def p_expr_a_plus(p):
     'a : A_PLUS LPAREN b_plus RPAREN'
     p[0] = flow.A_plus(p[3])

def p_expr_a_minus(p):
     'a : A_MINUS LPAREN b_minus RPAREN'
     p[0] = flow.A_minus(p[3])

def p_expr_a2(p):
     'a : A2 LPAREN cs_plus COMMA cs_minus RPAREN'
     p[0] = flow.A2(p[3],p[5])

def p_expr_b_plus_leaf(p):
     'b_plus : LEAF'
     p[0] = flow.Leaf()

def p_expr_b_plus_plus(p):
     'b_plus : B_PLUS_PLUS LPAREN b_plus COMMA b_plus RPAREN'
     p[0] = flow.B_plus_plus(p[3], p[5])

def p_expr_b_plus_minus(p):
     'b_plus : B_PLUS_MINUS LPAREN b_plus COMMA b_minus RPAREN'
     p[0] = flow.B_plus_minus(p[3], p[5])

def p_expr_be_plus(p):
     'b_plus : BETA_PLUS LPAREN cs_plus RPAREN'
     p[0] = flow.Beta_plus(p[3])

def p_expr_b_minus_leaf(p):
     'b_minus : LEAF'
     p[0] = flow.Leaf()

def p_expr_b_minus_minus(p):
     'b_minus : B_MINUS_MINUS LPAREN b_minus COMMA b_minus RPAREN'
     p[0] = flow.B_minus_minus(p[3], p[5])

def p_expr_b_minus_plus(p):
     'b_minus : B_MINUS_PLUS LPAREN b_minus COMMA b_plus RPAREN'
     p[0] = flow.B_minus_plus(p[3], p[5])

def p_expr_be_minus(p):
     'b_minus : BETA_MINUS LPAREN cs_minus RPAREN'
     p[0] = flow.Beta_minus(p[3])

def p_expr_c_plus(p):
     'c_plus : C_PLUS LPAREN b_plus COMMA cs_minus RPAREN'
     p[0] = flow.C_plus(p[3], p[5])

def p_expr_c_minus(p):
     'c_minus : C_MINUS LPAREN b_minus COMMA cs_plus RPAREN'
     p[0] = flow.C_minus(p[3], p[5])

def p_expr_cs_plus_nil(p):
     'cs_plus : NIL'
     p[0] = flow.Nil()

def p_expr_cs_plus_cons(p):
     'cs_plus : CONS LPAREN c_plus COMMA cs_plus RPAREN'
     p[0] = flow.Cons(p[3], p[5])

def p_expr_cs_minus_nil(p):
     'cs_minus : NIL'
     p[0] = flow.Nil()

def p_expr_cs_minus_cons(p):
     'cs_minus : CONS LPAREN c_minus COMMA cs_minus RPAREN'
     p[0] = flow.Cons(p[3], p[5])

def p_error(p):
    print ('Syntax error in input %s' %p)

parser = yacc.yacc()

def parse(data):
    return yacc.parse(data)

if __name__ == '__main__':
    while True:
        try:
            s = input('>>> ')
        except EOFError:
            break
        print(parser.parse(s).show())
        parser.parse(s).draw()
        flow.show_matplotlib()
        break
