"""Tests for the parser module."""

from __future__ import annotations

import pytest
from conftest import MAKEFILE_EXPRESSIONS

from viscot.core.nodes import (
    A0,
    A2,
    A_minus,
    A_plus,
    B0_minus,
    B0_plus,
    B_minus_minus,
    B_minus_plus,
    B_plus_minus,
    B_plus_plus,
    Beta_minus,
    Beta_plus,
    C_minus,
    C_plus,
    Cons,
    Leaf_minus,
    Leaf_plus,
    Nil,
)
from viscot.core.parser import parse


class TestBasicParsing:
    """Test basic parsing of all node types."""

    def test_a0_empty(self) -> None:
        tree = parse("A0()")
        assert isinstance(tree, A0)
        assert isinstance(tree.head, Nil)

    def test_a0_with_child(self) -> None:
        tree = parse("A0(a+(l+))")
        assert isinstance(tree, A0)
        assert isinstance(tree.head, Cons)
        assert isinstance(tree.head.head, A_plus)

    def test_a_plus(self) -> None:
        tree = parse("A0(a+(l+))")
        a = tree.head.head
        assert isinstance(a, A_plus)
        assert isinstance(a.head, Leaf_plus)

    def test_a_minus(self) -> None:
        tree = parse("A0(a-(l-))")
        a = tree.head.head
        assert isinstance(a, A_minus)
        assert isinstance(a.head, Leaf_minus)

    def test_b0_plus(self) -> None:
        tree = parse("B0+(l+,)")
        assert isinstance(tree, B0_plus)
        assert isinstance(tree.head, Leaf_plus)
        assert isinstance(tree.tail, Nil)

    def test_b0_minus(self) -> None:
        tree = parse("B0-(l-,)")
        assert isinstance(tree, B0_minus)
        assert isinstance(tree.head, Leaf_minus)

    def test_b_plus_plus(self) -> None:
        tree = parse("B0+(b++(l+,l+),)")
        assert isinstance(tree.head, B_plus_plus)

    def test_b_plus_minus(self) -> None:
        tree = parse("B0+(b+-(l+,l-),)")
        assert isinstance(tree.head, B_plus_minus)

    def test_b_minus_plus(self) -> None:
        tree = parse("B0-(b-+(l-,l+),)")
        assert isinstance(tree.head, B_minus_plus)

    def test_b_minus_minus(self) -> None:
        tree = parse("B0-(b--(l-,l-),)")
        assert isinstance(tree.head, B_minus_minus)

    def test_beta_plus(self) -> None:
        tree = parse("B0+(B+{},)")
        assert isinstance(tree.head, Beta_plus)

    def test_beta_minus(self) -> None:
        tree = parse("B0-(B-{},)")
        assert isinstance(tree.head, Beta_minus)

    def test_c_plus(self) -> None:
        tree = parse("B0-(l-,c+(l+,))")
        assert isinstance(tree.tail, Cons)
        assert isinstance(tree.tail.head, C_plus)

    def test_c_minus(self) -> None:
        tree = parse("B0+(l+,c-(l-,))")
        assert isinstance(tree.tail, Cons)
        assert isinstance(tree.tail.head, C_minus)

    def test_cons_chain(self) -> None:
        tree = parse("A0(a+(l+).a+(l+))")
        assert isinstance(tree.head, Cons)
        assert isinstance(tree.head.tail, Cons)

    def test_a2(self) -> None:
        tree = parse("A0(a2(c+(l+,),c-(l-,)))")
        a2 = tree.head.head
        assert isinstance(a2, A2)


class TestBugFixes:
    """Verify that all identified bugs are fixed."""

    def test_bug1_cs_minus1_recursion(self) -> None:
        """Bug #1: cs_minus1 should recurse to cs_minus1, not cs_minus."""
        # This expression has 3 c_minus nodes chained with dots
        tree = parse("B0+(l+,c-(l-,).c-(l-,).c-(l-,))")
        assert isinstance(tree, B0_plus)
        # Walk the tail: Cons -> Cons -> Cons -> Nil
        cons1 = tree.tail
        assert isinstance(cons1, Cons)
        assert isinstance(cons1.head, C_minus)
        cons2 = cons1.tail
        assert isinstance(cons2, Cons)
        assert isinstance(cons2.head, C_minus)
        cons3 = cons2.tail
        assert isinstance(cons3, Cons)
        assert isinstance(cons3.head, C_minus)

    def test_bug4_no_debug_print(self) -> None:
        """Bug #4: B0+ parsing should not produce debug output."""
        import io
        import sys

        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            parse("B0+(l+,)")
        finally:
            sys.stdout = old_stdout
        # No debug print should be present
        assert "B0+" not in captured.getvalue()


class TestRoundTrip:
    """Test parse(tree.show()) == original structure."""

    @pytest.mark.parametrize("expr", MAKEFILE_EXPRESSIONS)
    def test_show_roundtrip(self, expr: str) -> None:
        tree1 = parse(expr)
        shown = tree1.show()
        tree2 = parse(shown)
        assert tree2.show() == shown


class TestEdgeCases:
    """Edge cases and error handling."""

    def test_invalid_syntax_raises(self) -> None:
        with pytest.raises(ValueError):
            parse("invalid_input!!!")

    def test_parenthesized_s(self) -> None:
        tree = parse("(A0())")
        assert isinstance(tree, A0)

    def test_parenthesized_cs(self) -> None:
        tree = parse("B0+(l+,(c-(l-,)))")
        assert isinstance(tree.tail, Cons)

    def test_illegal_character_raises_lex_error(self) -> None:
        from viscot.core.lexer import COTLexError
        with pytest.raises((ValueError, COTLexError)):
            parse("@@@")

    def test_error_message_includes_detail(self) -> None:
        with pytest.raises(ValueError, match="Failed to parse"):
            parse("A0(((")

    def test_empty_input_raises(self) -> None:
        with pytest.raises(ValueError):
            parse("")

    def test_parse_with_config(self) -> None:
        from viscot.core.config import LayoutConfig
        cfg = LayoutConfig(a_flip_margin=3.0)
        tree = parse("A0(a+(l+))", config=cfg)
        a = tree.head.head
        assert a.r == 0 + 3.0  # leaf.r + a_flip_margin
