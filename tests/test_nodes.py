"""Tests for node types — occupation, show(), equality, config propagation."""

from __future__ import annotations

from viscot.core.config import LayoutConfig
from viscot.core.nodes import (
    A0,
    A_minus,
    A_plus,
    B_minus_plus,
    B_plus_minus,
    B_plus_plus,
    Beta_minus,
    Beta_plus,
    C_minus,
    Cons,
    Leaf_minus,
    Leaf_plus,
    Nil,
    OccupationInfo,
    use_config,
)
from viscot.core.parser import parse


class TestOccupation:
    """Test occupation area calculations."""

    def test_leaf_r_is_zero(self) -> None:
        assert Leaf_plus().r == 0
        assert Leaf_minus().r == 0

    def test_a_flip_occupation(self) -> None:
        a = A_plus(Leaf_plus())
        assert len(a.occupation) == 1
        assert a.occupation[0].height == a.r
        assert a.r > 0

    def test_b_evc_r(self) -> None:
        b = B_plus_plus(Leaf_plus(), Leaf_plus())
        # r = (2*0 + 2*0 + 4*0.5) / 2 = 1.0
        assert b.r == 1.0

    def test_b_flip_r(self) -> None:
        b = B_plus_minus(Leaf_plus(), Leaf_minus())
        assert b.r == 1.0

    def test_b_minus_plus_inherits_b_flip(self) -> None:
        """Bug #3: B_minus_plus should use B_Flip.plot_arrow, not hardcoded theta."""
        b = B_minus_plus(Leaf_minus(), Leaf_plus())
        assert b.dir == -1
        # Ensure plot_arrow is inherited from B_Flip, not overridden
        from viscot.core.nodes import B_Flip
        assert type(b).plot_arrow is B_Flip.plot_arrow

    def test_cons_occupation_filters_empty(self) -> None:
        c1 = C_minus(Leaf_minus(), Nil())
        c2 = C_minus(Leaf_minus(), Nil())
        cons = Cons(c1, Cons(c2, Nil()))
        # Should filter out {height: 0, width: 0} entries
        for occ in cons.occupation:
            assert occ != OccupationInfo(0, 0)

    def test_nil_occupation(self) -> None:
        n = Nil()
        assert n.occupation == [OccupationInfo(0, 0)]

    def test_beta_occupation(self) -> None:
        b = Beta_plus(Nil())
        assert b.r > 0
        assert b.center_r > 0


class TestShow:
    """Test show() produces valid output."""

    def test_nil_show(self) -> None:
        assert Nil().show() == ""

    def test_leaf_show(self) -> None:
        assert Leaf_plus().show() == "l+"
        assert Leaf_minus().show() == "l-"

    def test_a_plus_show(self) -> None:
        assert A_plus(Leaf_plus()).show() == "a+(l+)"

    def test_a0_empty_show(self) -> None:
        assert A0(Nil()).show() == "A0()"

    def test_beta_minus_comment(self) -> None:
        """Bug #5: Beta_minus.dir should be -1 (clockwise)."""
        b = Beta_minus(Nil())
        assert b.dir == -1
        assert b.show() == "B-{}"


class TestDir:
    """Test dir attribute correctness."""

    def test_directions(self) -> None:
        assert Leaf_plus.dir == 1
        assert Leaf_minus.dir == -1
        assert A_plus.dir == 1
        assert A_minus.dir == -1


class TestEquality:
    """Test Node.__eq__ and __hash__."""

    def test_equal_nodes(self) -> None:
        a = parse("A0(a+(l+))")
        b = parse("A0(a+(l+))")
        assert a == b

    def test_unequal_nodes(self) -> None:
        a = parse("A0(a+(l+))")
        b = parse("A0(a-(l-))")
        assert a != b

    def test_different_type_not_equal(self) -> None:
        a = parse("A0()")
        assert a != "A0()"
        assert a != 42

    def test_hash_consistent(self) -> None:
        a = parse("B0+(l+,c-(l-,))")
        b = parse("B0+(l+,c-(l-,))")
        assert hash(a) == hash(b)

    def test_usable_in_set(self) -> None:
        trees = {parse("A0()"), parse("A0()"), parse("A0(a+(l+))")}
        assert len(trees) == 2

    def test_repr(self) -> None:
        a = parse("A0(a+(l+))")
        assert repr(a) == "A0(a+(l+))"


class TestConfigPropagation:
    """Test that LayoutConfig is correctly propagated to nodes."""

    def test_different_config_different_radius(self) -> None:
        """Nodes constructed with different configs should have different radii."""
        default_tree = parse("A0(a+(l+))")
        a_default = default_tree.head.head  # A_plus node
        r_default = a_default.r

        big_config = LayoutConfig(a_flip_margin=2.0)
        big_tree = parse("A0(a+(l+))", config=big_config)
        a_big = big_tree.head.head
        r_big = a_big.r

        assert r_big > r_default

    def test_use_config_context_manager(self) -> None:
        """use_config should temporarily change the active config."""
        cfg = LayoutConfig(b_evc_margin=1.5)
        with use_config(cfg):
            b = B_plus_plus(Leaf_plus(), Leaf_plus())
        # r = (2*0 + 2*0 + 4*1.5) / 2 = 3.0
        assert b.r == 3.0

    def test_config_restored_after_context(self) -> None:
        """After use_config exits, default config should be restored."""
        cfg = LayoutConfig(b_evc_margin=5.0)
        with use_config(cfg):
            pass
        b = B_plus_plus(Leaf_plus(), Leaf_plus())
        # Default: r = (2*0 + 2*0 + 4*0.5) / 2 = 1.0
        assert b.r == 1.0

    def test_parse_with_config_affects_b0(self) -> None:
        """B0 radius should change with b0_margin config."""
        expr = "B0+(l+,c-(l-,).c-(l-,))"
        r_default = parse(expr).r
        r_big = parse(expr, config=LayoutConfig(b0_margin=5.0)).r
        assert r_big > r_default

    def test_c_height_spacing_factor_widens_c_node(self) -> None:
        """Higher c_height_spacing_factor should widen C-node occupation."""
        tree0 = parse("B0+(l+,c-(l-,))", config=LayoutConfig(c_height_spacing_factor=0.0))
        tree1 = parse("B0+(l+,c-(l-,))", config=LayoutConfig(c_height_spacing_factor=2.0))
        c0 = tree0.tail.head  # C_minus node
        c1 = tree1.tail.head
        assert c1.effective_extent >= c0.effective_extent

    def test_b0_children_dont_wrap_around(self) -> None:
        """B0 children should not wrap around the parent circle."""
        import math
        cfg = LayoutConfig(c_margin=0.3)
        tree = parse("B0+(l+,c-(l-,).c-(l-,).c-(l-,))", config=cfg)
        from viscot.core.nodes import make_list_for_c
        circumference = 2 * math.pi * tree.r
        ctxs = make_list_for_c(
            tree.tail.occupation, tree.r, (0, 0), True,
            circumference, first_child=True, config=cfg,
        )
        # Last child's end should not exceed first child's start + circumference
        last_end = ctxs[-1].length + tree.tail.occupation[-1].width
        first_start_wrapped = ctxs[0].length + circumference
        assert last_end <= first_start_wrapped
