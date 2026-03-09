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
