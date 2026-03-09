"""Parser for COT tree notation — uses PLY yacc."""

from __future__ import annotations

import ply.yacc as yacc

from . import nodes
from .config import LayoutConfig
from .lexer import lexer as _lexer
from .lexer import tokens as _tokens  # noqa: F401 — needed by PLY

# Re-export for PLY
tokens = _tokens

_last_error: str | None = None


def p_s(p):  # type: ignore[no-untyped-def]
    """s : A0 '(' as ')'
         | B0_PLUS '(' b_plus ',' cs_minus ')'
         | B0_MINUS '(' b_minus ',' cs_plus ')'
         | '(' s ')'"""
    if p[1] == "A0":
        p[0] = nodes.A0(p[3])
    elif p[1] == "B0+":
        p[0] = nodes.B0_plus(p[3], p[5])
    elif p[1] == "B0-":
        p[0] = nodes.B0_minus(p[3], p[5])
    elif p[1] == "(":
        p[0] = p[2]


def p_empty(p):  # type: ignore[no-untyped-def]
    """empty :"""
    pass


def p_as(p):  # type: ignore[no-untyped-def]
    """as : empty
          | a
          | a '.' as1"""
    if p[1] is None:
        p[0] = nodes.Nil()
    elif len(p) == 2:
        p[0] = nodes.Cons(p[1], nodes.Nil())
    elif p[2] == ".":
        p[0] = nodes.Cons(p[1], p[3])


def p_as1(p):  # type: ignore[no-untyped-def]
    """as1 : a
           | a '.' as1"""
    if len(p) == 2:
        p[0] = nodes.Cons(p[1], nodes.Nil())
    elif p[2] == ".":
        p[0] = nodes.Cons(p[1], p[3])


def p_a(p):  # type: ignore[no-untyped-def]
    """a : A_PLUS '(' b_plus ')'
         | A_MINUS '(' b_minus ')'
         | A2 '(' cs_plus ',' cs_minus ')'"""
    if p[1] == "a+":
        p[0] = nodes.A_plus(p[3])
    elif p[1] == "a-":
        p[0] = nodes.A_minus(p[3])
    elif p[1] == "a2":
        p[0] = nodes.A2(p[3], p[5])


def p_b_plus(p):  # type: ignore[no-untyped-def]
    """b_plus : LEAF_PLUS
              | B_PLUS_PLUS '(' b_plus ',' b_plus ')'
              | B_PLUS_MINUS '(' b_plus ',' b_minus ')'
              | BETA_PLUS '{' cs_plus '}'"""
    if p[1] == "l+":
        p[0] = nodes.Leaf_plus()
    elif p[1] == "b++":
        p[0] = nodes.B_plus_plus(p[3], p[5])
    elif p[1] == "b+-":
        p[0] = nodes.B_plus_minus(p[3], p[5])
    elif p[1] == "B+":
        p[0] = nodes.Beta_plus(p[3])


def p_b_minus(p):  # type: ignore[no-untyped-def]
    """b_minus : LEAF_MINUS
               | B_MINUS_MINUS '(' b_minus ',' b_minus ')'
               | B_MINUS_PLUS '(' b_minus ',' b_plus ')'
               | BETA_MINUS '{' cs_minus '}'"""
    if p[1] == "l-":
        p[0] = nodes.Leaf_minus()
    elif p[1] == "b--":
        p[0] = nodes.B_minus_minus(p[3], p[5])
    elif p[1] == "b-+":
        p[0] = nodes.B_minus_plus(p[3], p[5])
    elif p[1] == "B-":
        p[0] = nodes.Beta_minus(p[3])


def p_c_plus(p):  # type: ignore[no-untyped-def]
    """c_plus : C_PLUS '(' b_plus ',' cs_minus ')'"""
    p[0] = nodes.C_plus(p[3], p[5])


def p_c_minus(p):  # type: ignore[no-untyped-def]
    """c_minus : C_MINUS '(' b_minus ',' cs_plus ')'"""
    p[0] = nodes.C_minus(p[3], p[5])


def p_cs_plus(p):  # type: ignore[no-untyped-def]
    """cs_plus : empty
              | c_plus
              | c_plus '.' cs_plus1
              | '(' cs_plus ')'"""
    if p[1] is None:
        p[0] = nodes.Nil()
    elif p[1] != "(" and len(p) == 2:
        p[0] = nodes.Cons(p[1], nodes.Nil())
    elif len(p) == 4 and p[2] == ".":
        p[0] = nodes.Cons(p[1], p[3])
    elif p[1] == "(":
        p[0] = p[2]


def p_cs_plus1(p):  # type: ignore[no-untyped-def]
    """cs_plus1 : c_plus
                | c_plus '.' cs_plus1"""
    if len(p) == 2:
        p[0] = nodes.Cons(p[1], nodes.Nil())
    elif p[2] == ".":
        p[0] = nodes.Cons(p[1], p[3])


def p_cs_minus(p):  # type: ignore[no-untyped-def]
    """cs_minus : empty
               | c_minus
               | c_minus '.' cs_minus1
               | '(' cs_minus ')'"""
    if p[1] is None:
        p[0] = nodes.Nil()
    elif p[1] != "(" and len(p) == 2:
        p[0] = nodes.Cons(p[1], nodes.Nil())
    elif len(p) == 4 and p[2] == ".":
        p[0] = nodes.Cons(p[1], p[3])
    elif p[1] == "(":
        p[0] = p[2]


def p_cs_minus1(p):  # type: ignore[no-untyped-def]
    """cs_minus1 : c_minus
                 | c_minus '.' cs_minus1"""
    if len(p) == 2:
        p[0] = nodes.Cons(p[1], nodes.Nil())
    elif p[2] == ".":
        p[0] = nodes.Cons(p[1], p[3])


def p_error(p):  # type: ignore[no-untyped-def]
    global _last_error
    if p is None:
        _last_error = "unexpected end of input"
    else:
        _last_error = f"syntax error at {p.value!r} (position {p.lexpos})"


parser = yacc.yacc(debug=False, write_tables=False)


def parse(data: str, config: LayoutConfig | None = None) -> nodes.Node:
    """Parse a COT tree notation string into a Node tree.

    Args:
        data: COT tree notation string.
        config: LayoutConfig to use for node construction. Defaults to DEFAULT_CONFIG.

    Returns:
        Parsed Node tree.
    """
    global _last_error
    _last_error = None

    if config is not None:
        with nodes.use_config(config):
            result = parser.parse(data, lexer=_lexer.clone())
    else:
        result = parser.parse(data, lexer=_lexer.clone())

    if result is None:
        detail = _last_error or "unknown error"
        raise ValueError(f"Failed to parse {data!r}: {detail}")
    return result  # type: ignore[no-any-return]
