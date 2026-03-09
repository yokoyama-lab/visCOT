"""Lexer for COT tree notation — uses PLY."""

from __future__ import annotations

import ply.lex as lex

tokens = (
    "A0",
    "B0_PLUS",
    "B0_MINUS",
    "A_PLUS",
    "A_MINUS",
    "A2",
    "B_PLUS_PLUS",
    "B_PLUS_MINUS",
    "B_MINUS_PLUS",
    "B_MINUS_MINUS",
    "BETA_PLUS",
    "BETA_MINUS",
    "C_PLUS",
    "C_MINUS",
    "CONS",
    "NIL",
    "LEAF_PLUS",
    "LEAF_MINUS",
)

literals = "(),{}."

t_A0 = r"A0"
t_B0_PLUS = r"B0\+"
t_B0_MINUS = r"B0\-"

t_A_PLUS = r"a\+"
t_A_MINUS = r"a\-"
t_A2 = r"a2"

t_B_PLUS_PLUS = r"b\+\+"
t_B_PLUS_MINUS = r"b\+\-"
t_B_MINUS_PLUS = r"b\-\+"
t_B_MINUS_MINUS = r"b\-\-"

t_BETA_PLUS = r"B\+"
t_BETA_MINUS = r"B\-"

t_C_PLUS = r"c\+"
t_C_MINUS = r"c\-"

t_CONS = r"cons"
t_NIL = r"n"
t_LEAF_PLUS = r"l\+"
t_LEAF_MINUS = r"l\-"

t_ignore = " \t\n"
t_ignore_COMMENT = r"\#.*"


class COTLexError(ValueError):
    """Raised when the lexer encounters an illegal character."""


def t_error(t: lex.LexToken) -> None:
    raise COTLexError(
        f"Illegal character {t.value[0]!r} at position {t.lexpos}"
    )


lexer = lex.lex()
