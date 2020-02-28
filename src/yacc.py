# Yacc. PLYを用いる

import ply.yacc as yacc
from .lex import tokens
import sys
from . import flow

def p_s(p):
     '''s : A0 '(' as ')'
          | B0_PLUS '(' b_plus ',' '(' cs_minus ')' ')'
          | B0_MINUS '(' b_minus ',' '(' cs_plus ')' ')' '''
     if p[1] == 'a0': p[0] = flow.A0(p[3])
     elif p[1] == 'b0+': p[0] = flow.B0_plus(p[3], p[6])
     elif p[1] == 'b0-': p[0] = flow.B0_minus(p[3], p[6])

def p_as(p):
     '''as : NIL
           | CONS '(' a ',' as ')' '''
     if p[1] == 'n': p[0] = flow.Nil()
     elif p[1] == 'cons': p[0] = flow.Cons(p[3], p[5])

def p_a(p):
     '''a : A_PLUS '(' b_plus ')'
          | A_MINUS '(' b_minus ')'
          | A2 '(' cs_plus ',' cs_minus ')' '''
     if p[1] == 'a+': p[0] = flow.A_plus(p[3])
     elif p[1] == 'a-': p[0] = flow.A_minus(p[3])
     elif p[1] == 'a2': p[0] = flow.A2(p[3],p[5])

def p_b_plus(p):
     '''b_plus : LEAF
               | B_PLUS_PLUS '(' b_plus ',' b_plus ')'
               | B_PLUS_MINUS '(' b_plus ',' b_minus ')'
               | BETA_PLUS '(' cs_plus ')' '''
     if p[1] == 'l': p[0] = flow.Leaf()
     elif p[1] == 'b++': p[0] = flow.B_plus_plus(p[3], p[5])
     elif p[1] == 'b+-': p[0] = flow.B_plus_minus(p[3], p[5])
     elif p[1] == 'be+': p[0] = flow.Beta_plus(p[3])

def p_b_minus(p):
     '''b_minus : LEAF
                | B_MINUS_MINUS '(' b_minus ',' b_minus ')'
                | B_MINUS_PLUS '(' b_minus ',' b_plus ')'
                | BETA_MINUS '(' cs_minus ')' '''
     if p[1] == 'l': p[0] = flow.Leaf()
     elif p[1] == 'b--': p[0] = flow.B_minus_minus(p[3], p[5])
     elif p[1] == 'b-+': p[0] = flow.B_minus_plus(p[3], p[5])
     elif p[1] == 'be-': p[0] = flow.Beta_minus(p[3])

def p_c_plus(p):
     '''c_plus : C_PLUS '(' b_plus ',' cs_minus ')' '''
     p[0] = flow.C_plus(p[3], p[5])

def p_c_minus(p):
     '''c_minus : C_MINUS '(' b_minus ',' cs_plus ')' '''
     p[0] = flow.C_minus(p[3], p[5])

def p_cs_plus(p):
     '''cs_plus : NIL
                | CONS '(' c_plus ',' cs_plus ')' '''
     if p[1] == 'n': p[0] = flow.Nil()
     elif p[1] == 'cons': p[0] = flow.Cons(p[3], p[5])

def p_cs_minus(p):
     '''cs_minus : NIL
                 | CONS '(' c_minus ',' cs_minus ')' '''
     if p[1] == 'n': p[0] = flow.Nil()
     elif p[1] == 'cons': p[0] = flow.Cons(p[3], p[5])

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
        parser.parse(s).draw()
        break
