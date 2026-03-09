"""Tests for readability metrics modules."""

from __future__ import annotations

import math

import numpy as np

from viscot.core.canvas import DrawnCircle, DrawnLine, DrawnSpline
from viscot.metrics.composite import compute_composite_score
from viscot.metrics.overlap import compute_overlap
from viscot.metrics.sampling import circle_to_polyline, element_to_polyline, line_to_polyline
from viscot.metrics.smoothness import compute_smoothness
from viscot.metrics.spacing import compute_spacing


class TestSampling:
    """Test element-to-polyline conversion."""

    def test_circle_to_polyline(self) -> None:
        c = DrawnCircle(center=(0, 0), radius=1.0)
        poly = circle_to_polyline(c, num_points=32)
        assert poly.shape == (32, 2)
        # All points should be at distance 1 from center
        dists = np.linalg.norm(poly, axis=1)
        np.testing.assert_allclose(dists, 1.0, atol=1e-10)

    def test_line_to_polyline(self) -> None:
        line = DrawnLine(start=(0, 0), end=(1, 1))
        poly = line_to_polyline(line)
        assert poly.shape == (2, 2)
        np.testing.assert_array_equal(poly[0], [0, 0])
        np.testing.assert_array_equal(poly[1], [1, 1])

    def test_element_to_polyline_spline(self) -> None:
        pts = np.array([[0, 0], [1, 1], [2, 0]])
        s = DrawnSpline(points=pts)
        result = element_to_polyline(s)
        assert result is not None
        np.testing.assert_array_equal(result, pts)


class TestOverlap:
    """Test M1: overlap and crossing detection."""

    def test_no_crossing_parallel_lines(self) -> None:
        elements = [
            DrawnLine(start=(0, 0), end=(1, 0)),
            DrawnLine(start=(0, 1), end=(1, 1)),
        ]
        result = compute_overlap(elements, epsilon=0.01)
        assert result.crossing_count == 0

    def test_crossing_perpendicular_lines(self) -> None:
        elements = [
            DrawnLine(start=(0, -1), end=(0, 1)),
            DrawnLine(start=(-1, 0), end=(1, 0)),
        ]
        result = compute_overlap(elements, epsilon=0.01)
        assert result.crossing_count == 1

    def test_single_element_no_overlap(self) -> None:
        elements = [DrawnLine(start=(0, 0), end=(1, 1))]
        result = compute_overlap(elements)
        assert result.crossing_count == 0
        assert result.overlap_ratio == 0.0

    def test_empty_elements(self) -> None:
        result = compute_overlap([])
        assert result.crossing_count == 0

    def test_spline_only_excludes_circles(self) -> None:
        """spline_only=True should ignore circle-line crossings."""
        elements = [
            DrawnCircle(center=(0, 0), radius=1.0),
            DrawnLine(start=(-2, 0), end=(2, 0)),
        ]
        # Without spline_only: circle and line cross at (-1,0) and (1,0)
        all_result = compute_overlap(elements)
        assert all_result.crossing_count >= 1
        # With spline_only: no splines → no crossings
        spline_result = compute_overlap(elements, spline_only=True)
        assert spline_result.crossing_count == 0

    def test_spline_only_detects_spline_crossings(self) -> None:
        """spline_only=True should still detect spline-spline crossings."""
        elements = [
            DrawnSpline(points=np.array([[-2, -2], [-1, -1], [1, 1], [2, 2.0]])),
            DrawnSpline(points=np.array([[-2, 2], [-1, 1], [1, -1], [2, -2.0]])),
        ]
        result = compute_overlap(elements, spline_only=True)
        assert result.crossing_count >= 1


class TestSpacing:
    """Test M2: streamline spacing."""

    def test_uniform_parallel_lines(self) -> None:
        elements = [
            DrawnLine(start=(0, 0), end=(10, 0)),
            DrawnLine(start=(0, 1), end=(10, 1)),
            DrawnLine(start=(0, 2), end=(10, 2)),
        ]
        result = compute_spacing(elements)
        assert result.d_min > 0
        assert result.d_cv < 0.5  # reasonably uniform

    def test_non_uniform_spacing(self) -> None:
        elements = [
            DrawnLine(start=(0, 0), end=(10, 0)),
            DrawnLine(start=(0, 0.1), end=(10, 0.1)),
            DrawnLine(start=(0, 5), end=(10, 5)),
        ]
        result = compute_spacing(elements)
        assert result.d_cv > 0.5  # non-uniform

    def test_single_element(self) -> None:
        result = compute_spacing([DrawnLine(start=(0, 0), end=(1, 1))])
        assert result.d_min == 0.0


class TestSmoothness:
    """Test M3: curvature-based smoothness."""

    def test_straight_line_zero_curvature(self) -> None:
        pts = np.column_stack([np.linspace(0, 10, 50), np.zeros(50)])
        elements = [DrawnSpline(points=pts)]
        result = compute_smoothness(elements)
        assert result.kappa_max < 1e-10
        assert result.jerk < 1e-10

    def test_circle_constant_curvature(self) -> None:
        t = np.linspace(0, 2 * math.pi, 100, endpoint=False)
        pts = np.column_stack([np.cos(t), np.sin(t)])
        elements = [DrawnSpline(points=pts)]
        result = compute_smoothness(elements)
        # Curvature should be approximately 1.0 for unit circle
        assert abs(result.kappa_mean - 1.0) < 0.1
        # Jerk should be small (nearly constant curvature)
        assert result.kappa_var < 0.01

    def test_empty_elements(self) -> None:
        result = compute_smoothness([])
        assert result.kappa_max == 0.0


class TestComposite:
    """Test composite score."""

    def test_perfect_score_no_crossings(self) -> None:
        elements = [
            DrawnSpline(points=np.array([[0, 0], [5, 0], [10, 0.0]])),
            DrawnSpline(points=np.array([[0, 1], [5, 1], [10, 1.0]])),
        ]
        score = compute_composite_score(elements)
        assert score.overlap.crossing_count == 0
        assert score.score <= 0  # score is non-positive

    def test_crossing_reduces_score(self) -> None:
        # Use DrawnSpline elements since composite score uses spline_only mode.
        # Splines need enough interior points for segment-level crossing.
        no_cross = [
            DrawnSpline(points=np.array([[0, 0], [5, 0], [10, 0.0]])),
            DrawnSpline(points=np.array([[0, 2], [5, 2], [10, 2.0]])),
        ]
        with_cross = [
            DrawnSpline(points=np.array([[-2, -2], [-1, -1], [1, 1], [2, 2.0]])),
            DrawnSpline(points=np.array([[-2, 2], [-1, 1], [1, -1], [2, -2.0]])),
        ]
        score_good = compute_composite_score(no_cross)
        score_bad = compute_composite_score(with_cross)
        assert score_good.score > score_bad.score
