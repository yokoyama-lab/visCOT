"""Tests for Canvas — DrawnElement recording and spline interpolation."""

from __future__ import annotations

import math

import pytest
from conftest import MAKEFILE_EXPRESSIONS

from viscot.core.canvas import (
    Canvas,
    DrawnArrow,
    DrawnCircle,
    DrawnLine,
    DrawnPoint,
    DrawnSpline,
)


class TestDrawnElementRecording:
    """Test that all drawing operations are recorded."""

    def test_draw_circle_recorded(self, canvas: Canvas) -> None:
        canvas.draw_circle(1.0, (0, 0))
        assert len(canvas.drawn_elements) == 1
        elem = canvas.drawn_elements[0]
        assert isinstance(elem, DrawnCircle)
        assert elem.radius == 1.0
        assert elem.center == (0, 0)

    def test_draw_line_recorded(self, canvas: Canvas) -> None:
        canvas.draw_line((0, 0), (1, 1))
        assert len(canvas.drawn_elements) == 1
        elem = canvas.drawn_elements[0]
        assert isinstance(elem, DrawnLine)
        assert elem.start == (0, 0)
        assert elem.end == (1, 1)

    def test_draw_arrow_recorded(self, canvas: Canvas) -> None:
        canvas.draw_arrow((0, 0), math.pi)
        assert len(canvas.drawn_elements) == 1
        assert isinstance(canvas.drawn_elements[0], DrawnArrow)

    def test_draw_point_recorded(self, canvas: Canvas) -> None:
        canvas.draw_point((1, 2))
        assert len(canvas.drawn_elements) == 1
        assert isinstance(canvas.drawn_elements[0], DrawnPoint)

    def test_draw_spline_recorded(self, canvas: Canvas) -> None:
        xy = [[0, 0], [1, 1], [2, 0]]
        canvas.draw_spline(xy)
        assert len(canvas.drawn_elements) == 1
        elem = canvas.drawn_elements[0]
        assert isinstance(elem, DrawnSpline)
        assert elem.points.shape[1] == 2
        assert len(elem.points) == canvas.config.spline_num_points

    def test_clear_canvas_resets_elements(self, canvas: Canvas) -> None:
        canvas.draw_circle(1.0)
        canvas.draw_line((0, 0), (1, 1))
        assert len(canvas.drawn_elements) == 2
        canvas.clear_canvas()
        assert len(canvas.drawn_elements) == 0

    def test_filled_circle_recorded(self, canvas: Canvas) -> None:
        canvas.draw_circle(1.0, circle_fill=True)
        elem = canvas.drawn_elements[0]
        assert isinstance(elem, DrawnCircle)
        assert elem.filled is True


class TestSplineInterpolation:
    """Test spline computation."""

    def test_spline_returns_correct_shape(self, canvas: Canvas) -> None:
        x = [0, 1, 2, 3]
        y = [0, 1, 0, -1]
        sx, sy = canvas._spline(x, y, 50, 3)
        assert len(sx) == 50
        assert len(sy) == 50

    def test_spline_endpoints(self, canvas: Canvas) -> None:
        x = [0.0, 1.0, 2.0]
        y = [0.0, 1.0, 0.0]
        sx, sy = canvas._spline(x, y, 100, 2)
        assert abs(sx[0] - 0.0) < 1e-6
        assert abs(sx[-1] - 2.0) < 1e-6


class TestClearCanvasBugFix:
    """Bug #2: clear_canvas() should re-create fig/ax after plt.close()."""

    def test_clear_then_draw(self, canvas: Canvas) -> None:
        canvas.draw_circle(1.0)
        canvas.clear_canvas()
        # Should not raise — ax should be valid
        canvas.draw_circle(2.0)
        assert len(canvas.drawn_elements) == 1


class TestClose:
    """Test Canvas.close() for final cleanup."""

    def test_close_clears_elements(self) -> None:
        c = Canvas()
        c.draw_circle(1.0)
        assert len(c.drawn_elements) == 1
        c.close()
        assert len(c.drawn_elements) == 0

    def test_save_uses_fig_specific(self, canvas: Canvas, tmp_path) -> None:
        """save_canvas should use fig-specific savefig, not plt global."""
        canvas.draw_circle(1.0)
        out = tmp_path / "test.png"
        canvas.save_canvas(str(out))
        assert out.exists()


class TestFullRendering:
    """Test that Makefile expressions render without error."""

    @pytest.mark.parametrize("expr", MAKEFILE_EXPRESSIONS)
    def test_render_expression(self, render, expr: str) -> None:
        tree, canvas = render(expr)
        assert len(canvas.drawn_elements) > 0


_conftest = __import__("conftest")
_ALL_EXHAUSTIVE = (
    _conftest.EXHAUSTIVE_1_2_3
    + _conftest.EXHAUSTIVE_4
    + _conftest.EXHAUSTIVE_5
)


class TestExhaustive:
    """All valid COT expressions with 1-5 nodes — zero crossings."""

    @pytest.mark.parametrize("expr", _ALL_EXHAUSTIVE)
    def test_exhaustive_no_crossings(self, render, expr: str) -> None:
        from viscot.metrics.overlap import compute_overlap

        _tree, canvas = render(expr)
        result = compute_overlap(canvas.drawn_elements, spline_only=True)
        assert result.crossing_count == 0, (
            f"{expr!r} produced {result.crossing_count} crossing(s)"
        )

    @pytest.mark.parametrize("expr", _ALL_EXHAUSTIVE)
    def test_exhaustive_roundtrip(self, render, expr: str) -> None:
        from viscot.core.parser import parse as cot_parse

        tree, _canvas = render(expr)
        shown = tree.show()
        assert cot_parse(shown).show() == shown


class TestNoSplineCrossings:
    """Verify that rendered COT expressions have no spurious spline crossings.

    A correct visualization should produce streamlines (splines) that do
    not cross each other.  Structural crossings between circles and lines
    are expected (e.g. a separatrix touching a boundary), so we use
    ``spline_only=True`` to restrict the check to spline-vs-spline
    intersections.
    """

    @pytest.mark.parametrize("expr", MAKEFILE_EXPRESSIONS)
    def test_no_spline_crossings(self, render, expr: str) -> None:
        from viscot.metrics.overlap import compute_overlap

        _tree, canvas = render(expr)
        result = compute_overlap(canvas.drawn_elements, spline_only=True)
        assert result.crossing_count == 0, (
            f"Expression {expr!r} produced {result.crossing_count} "
            f"spline crossing(s)"
        )


class TestSmallCrossings:
    """Track the smallest known expressions that produce spline crossings.

    These are regression baselines: layout improvements should reduce
    the crossing counts, never increase them.
    """

    @pytest.mark.parametrize("label,expr", [
        pytest.param(k, v, id=k) for k, v in __import__("conftest").CROSSING_EXPRS.items()
    ])
    def test_crossing_expr_renders(self, render, label: str, expr: str) -> None:
        """Each crossing expression must parse, draw, and round-trip."""
        from viscot.core.parser import parse as cot_parse

        tree, canvas = render(expr)
        assert len(canvas.drawn_elements) > 0
        shown = tree.show()
        assert cot_parse(shown).show() == shown

    @pytest.mark.parametrize("label,expr,max_crossings", [
        ("20node", __import__("conftest").CROSSING_EXPRS["20node"], 0),
        ("22node", __import__("conftest").CROSSING_EXPRS["22node"], 0),
        ("24node", __import__("conftest").CROSSING_EXPRS["24node"], 0),
    ])
    def test_crossing_baseline(self, render, label: str, expr: str, max_crossings: int) -> None:
        """Crossing count must not regress beyond the recorded baseline."""
        from viscot.metrics.overlap import compute_overlap

        _tree, canvas = render(expr)
        ov = compute_overlap(canvas.drawn_elements, spline_only=True)
        assert ov.crossing_count <= max_crossings, (
            f"{label}: {ov.crossing_count} crossings (max allowed: {max_crossings})"
        )


class TestStress:
    """Stress tests with large COT expressions."""

    def test_102_node_renders(self, render) -> None:
        """102-node expression must parse, draw, and round-trip."""
        from conftest import STRESS_EXPR_102
        from viscot.core.parser import parse as cot_parse

        tree, canvas = render(STRESS_EXPR_102)
        assert len(canvas.drawn_elements) > 100
        # Round-trip
        shown = tree.show()
        tree2 = cot_parse(shown)
        assert tree2.show() == shown

    def test_102_node_metrics(self, render) -> None:
        """102-node expression: record crossing count as regression baseline.

        Current layout produces 34 spline crossings at 102 nodes.
        This test documents the baseline and will detect regressions
        (more crossings) or improvements (fewer crossings).
        """
        from conftest import STRESS_EXPR_102
        from viscot.metrics.overlap import compute_overlap
        from viscot.metrics.composite import compute_composite_score

        _tree, canvas = render(STRESS_EXPR_102)
        overlap = compute_overlap(canvas.drawn_elements, spline_only=True)
        score = compute_composite_score(canvas.drawn_elements)

        # Baseline: 0 crossings at 102 nodes (improved from 34→13→3→0).
        # Fail if any crossings appear (regression).
        assert overlap.crossing_count == 0, (
            f"Regression: 102-node stress test produced {overlap.crossing_count} "
            f"crossings (expected: 0)"
        )
        # Score should be finite
        assert score.score > -1e9
