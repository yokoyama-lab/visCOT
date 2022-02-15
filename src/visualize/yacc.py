# Yacc. PLYを用いる

import ply.yacc as yacc
from .lex import tokens
import sys
from . import flow

"""
入力されるCOTの文法

S ::= "a0" | "b++" | "b--" | "b+-" | "b-+" | "B+" | "B-" | "s+" | "s-"
    | "a0" "(" A As ")"
    | "b++" "{" Bp "," Bp "}"
    | "b--" "{" Bm "," Bm "}"
    | "b+-" "(" Bp "," Bm ")"
    | "b-+" "(" Bm "," Bp ")"
    | "B+" "{" Cp Cps "}"        // 中心になくて良い？
    | "B-" "{" Cm Cms "}"        // 中心になくて良い？

A ::= "a+" | "a-" | "a2"
    | "a+" "(" Bp ")"
    | "a-" "(" Bm ")"
    | "a2" "(" "," ")"
    | "a2" "(" "," Cm Cms ")"
    | "a2" "(" Cp Cps "," ")"
    | "a2" "(" Cp Cps "," Cm Cms ")"

As ::= "" | "." A | "." A As

Bp ::= "s+" | "b++" | "b+-" | "B+"
     | "b++" "{" Bp "," Bp "}"
     | "b+-" "(" Bp "," Bm ")"
     | "B+" "{" "L+" "}"
     | "B+" "{" Cp Cps "}"

Bm ::= "s-" | "b--" | "b-+" | "B-"
     | "b--" "{" Bm "," Bm "}"
     | "b-+" "(" Bm "," Bp ")"
     | "B-" "{" "L-" "}"
     | "B-" "{" Cm Cms "}"

Cp ::= "c+"
     | "c+" "(" Bp "," "L-" ")"
     | "c+" "(" Bp "," Cm Cms ")"

Cm ::= "c-"
     | "c-" "(" Bm "," "L+" ")"
     | "c-" "(" Bm "," Cp Cps ")"

Cps ::= "" | "." Cp | "." Cp Cps

Cms ::= "" | "." Cm | "." Cm Cms
"""

def p_s(p):
     '''s : A0
          | A0 '(' as ')'
          | B_PLUS_PLUS
          | B_MINUS_MINUS
          | B_PLUS_MINUS
          | B_MINUS_PLUS
          | BETA_PLUS
          | BETA_MINUS
          | S_PLUS
          | S_MINUS
          | B_PLUS_PLUS '{' b_plus ',' b_plus '}'
          | B_MINUS_MINUS '{' b_minus ',' b_minus '}'
          | B_PLUS_MINUS '(' b_plus ',' b_minus ')'
          | B_MINUS_PLUS '(' b_minus ',' b_plus ')'
          | BETA_PLUS '{' cs_plus '}'
          | BETA_MINUS '{' cs_minus '}' '''
     if p[1] == 'a0' and len(p) == 2: p[0] = flow.A0()
     elif p[1] == 'a0': p[0] = flow.A0(p[3])
     elif p[1] == 'b++' and len(p)==2: p[0] = flow.B_plus_plus()
     elif p[1] == 'b++': p[0] = flow.B_plus_plus(p[3],p[5])
     elif p[1] == 'b--' and len(p)==2: p[0] = flow.B_minus_minus()
     elif p[1] == 'b--': p[0] = flow.B_minus_minus(p[3],p[5])
     elif p[1] == 'b+-' and len(p)==2: p[0] = flow.B_plus_minus()
     elif p[1] == 'b+-': p[0] = flow.B_plus_minus(p[3],p[5])
     elif p[1] == 'b-+' and len(p)==2: p[0] = flow.B_minus_plus()
     elif p[1] == 'b-+': p[0] = flow.B_minus_plus(p[3],p[5])
     elif p[1] == 's+': p[0] = flow.S_plus()
     elif p[1] == 's-': p[0] = flow.S_minus()
     elif p[1] == 'B+' and len(p)==5: p[0] = flow.Beta_plus(p[3])
     elif p[1] == 'B+': p[0] = flow.Beta_plus(flow.Nil())
     elif p[1] == 'B-' and len(p)==5: p[0] = flow.Beta_minus(p[3])
     elif p[1] == 'B-': p[0] = flow.Beta_minus(flow.Nil())

def p_empty(p):
     'empty :'
     pass

def p_as(p):
     '''as : empty
           | a
           | a '.' as1 '''
     if p[1] == None: p[0] = flow.Nil()
     elif p[1] != None and len(p) == 2: p[0] = flow.Cons(p[1], flow.Nil())
     elif p[2] == '.': p[0] = flow.Cons(p[1], p[3])

def p_as1(p):
     '''as1 : a
            | a '.' as1 '''
     if len(p) == 2: p[0] = flow.Cons(p[1], flow.Nil())
     elif p[2] == '.': p[0] = flow.Cons(p[1], p[3])

def p_a(p):
     '''a : A_PLUS
          | A_MINUS
          | A2
          | A_PLUS '(' b_plus ')'
          | A_MINUS '(' b_minus ')'
          | A2 '(' cs_plus ',' cs_minus ')' '''
     if p[1] == 'a+' and len(p) == 2: p[0] = flow.A_plus()
     elif p[1] == 'a+': p[0] = flow.A_plus(p[3])
     elif p[1] == 'a-' and len(p) == 2: p[0] = flow.A_minus()
     elif p[1] == 'a-': p[0] = flow.A_minus(p[3])
     elif p[1] == 'a2' and len(p) == 2: p[0] = flow.A2()
     elif p[1] == 'a2': p[0] = flow.A2(p[3],p[5])

def p_b_plus(p):
     '''b_plus : S_PLUS
               | B_PLUS_PLUS
               | B_PLUS_MINUS
               | BETA_PLUS
               | B_PLUS_PLUS '(' b_plus ',' b_plus ')'
               | B_PLUS_MINUS '(' b_plus ',' b_minus ')'
               | BETA_PLUS '{' cs_plus '}' '''
     if p[1] == 's+': p[0] = flow.S_plus()
     elif p[1] == 'b++' and len(p)==2: p[0] = flow.B_plus_plus()
     elif p[1] == 'b++': p[0] = flow.B_plus_plus(p[3],p[5])
     elif p[1] == 'b+-' and len(p)==2: p[0] = flow.B_plus_minus()
     elif p[1] == 'b+-': p[0] = flow.B_plus_minus(p[3],p[5])
     elif p[1] == 'B+' and len(p)==5: p[0] = flow.Beta_plus(p[3])
     elif p[1] == 'B+': p[0] = flow.Beta_plus(flow.Nil())

def p_b_minus(p):
     '''b_minus : S_MINUS
                | B_MINUS_MINUS
                | B_MINUS_PLUS
                | BETA_MINUS
                | B_MINUS_MINUS '(' b_minus ',' b_minus ')'
                | B_MINUS_PLUS '(' b_minus ',' b_plus ')'
                | BETA_MINUS '{' cs_minus '}' '''
     if p[1] == 's-': p[0] = flow.S_minus()
     elif p[1] == 'b--' and len(p)==2: p[0] = flow.B_minus_minus()
     elif p[1] == 'b--': p[0] = flow.B_minus_minus(p[3],p[5])
     elif p[1] == 'b-+' and len(p)==2: p[0] = flow.B_minus_plus()
     elif p[1] == 'b-+': p[0] = flow.B_minus_plus(p[3],p[5]) 
     elif p[1] == 'B-' and len(p)==5: p[0] = flow.Beta_minus(p[3])
     elif p[1] == 'B-': p[0] = flow.Beta_minus(flow.Nil())

def p_c_plus(p):
     '''c_plus : C_PLUS
               | C_PLUS '(' b_plus ',' cs_minus ')' '''
     if p[1] == 'c+' and len(p) == 2: p[0] = flow.C_plus()
     elif p[1] == 'c+' and len(p) == 7: p[0] = flow.C_plus(p[3], p[5])

def p_c_minus(p):
     '''c_minus : C_MINUS
                | C_MINUS '(' b_minus ',' cs_plus ')' '''
     if p[1] == 'L-': p[0] = flow.Leaf_plus()
     elif p[1] == 'c-' and len(p) == 2: p[0] = flow.C_minus()
     elif p[1] == 'c-' and len(p) == 7: p[0] = flow.C_minus(p[3], p[5])

def p_cs_plus(p):
     '''cs_plus : empty
                | LEAF_PLUS
                | c_plus
                | c_plus '.' cs_plus1 
                | '(' cs_plus ')' '''
     if p[1] == None: p[0] = flow.Leaf_plus()
     elif p[1] == 'L+': p[0] = flow.Leaf_plus()
     elif p[1] != None and len(p) == 2: p[0] = flow.Cons(p[1], flow.Nil())
     elif p[2] == '.': p[0] = flow.Cons(p[1], p[3])
     elif p[1] == '(' and p[3] == ')' and len(p)==4: p[0] = p[2]

def p_cs_plus1(p):
     '''cs_plus1 : c_plus
                 | c_plus '.' cs_plus1 '''
     if len(p) == 2: p[0] = flow.Cons(p[1], flow.Nil())
     elif p[2] == '.': p[0] = flow.Cons(p[1], p[3])

def p_cs_minus(p):
     '''cs_minus : empty
                 | LEAF_MINUS
                 | c_minus
                 | c_minus '.' cs_minus1
                 | '(' cs_minus ')' '''
     if p[1] == None: p[0] = flow.Leaf_minus()
     elif p[1] == 'L-': p[0] = flow.Leaf_minus()
     elif p[1] != None and len(p) == 2: p[0] = flow.Cons(p[1], flow.Nil())
     elif p[2] == '.': p[0] = flow.Cons(p[1], p[3])
     elif p[1] == '(' and p[3] == ')' and len(p)==4: p[0] = p[2]

def p_cs_minus1(p):
     '''cs_minus1 : c_minus
                  | c_minus '.' cs_minus '''
     if len(p) == 2: p[0] = flow.Cons(p[1], flow.Nil())
     elif p[2] == '.': p[0] = flow.Cons(p[1], p[3])

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
