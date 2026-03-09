"""Tests for layout improvement modules."""

from __future__ import annotations

import math

from viscot.layout.occupation import (
    CircularOccupation,
    EllipticalOccupation,
    compute_b_evc_occupation,
    depth_adaptive_margin,
)


class TestOccupationArea:
    """Test occupation area calculations."""

    def test_circular_bounding_box(self) -> None:
        c = CircularOccupation(center=(0, 0), radius=1.0)
        bbox = c.bounding_box()
        assert bbox == (-1.0, -1.0, 1.0, 1.0)

    def test_circular_area(self) -> None:
        c = CircularOccupation(center=(0, 0), radius=1.0)
        assert abs(c.area() - math.pi) < 1e-10

    def test_elliptical_bounding_box(self) -> None:
        e = EllipticalOccupation(center=(0, 0), semi_major=2.0, semi_minor=1.0)
        bbox = e.bounding_box()
        assert bbox == (-1.0, -2.0, 1.0, 2.0)

    def test_elliptical_smaller_than_circular(self) -> None:
        """Elliptical area should be smaller than circular for b++/b-- nodes."""
        r_up, r_lw, margin = 1.0, 0.5, 0.5
        circ = compute_b_evc_occupation(r_up, r_lw, margin, use_ellipse=False)
        elli = compute_b_evc_occupation(r_up, r_lw, margin, use_ellipse=True)
        assert elli.area() < circ.area()

    def test_elliptical_bbox_smaller(self) -> None:
        """Elliptical bounding box should be tighter."""
        r_up, r_lw, margin = 1.0, 0.5, 0.5
        circ = compute_b_evc_occupation(r_up, r_lw, margin, use_ellipse=False)
        elli = compute_b_evc_occupation(r_up, r_lw, margin, use_ellipse=True)
        c_bbox = circ.bounding_box()
        e_bbox = elli.bounding_box()
        c_w = c_bbox[2] - c_bbox[0]
        e_w = e_bbox[2] - e_bbox[0]
        assert e_w <= c_w

    def test_symmetric_radii_ellipse_vs_circle(self) -> None:
        """When r_up == r_lw, ellipse semi_minor < circular radius."""
        r_up, r_lw, margin = 1.0, 1.0, 0.5
        circ = compute_b_evc_occupation(r_up, r_lw, margin, use_ellipse=False)
        elli = compute_b_evc_occupation(r_up, r_lw, margin, use_ellipse=True)
        assert isinstance(circ, CircularOccupation)
        assert isinstance(elli, EllipticalOccupation)
        # Ellipse semi_minor = max(r_up, r_lw) + margin = 1.5
        # Circle radius = (2*1 + 2*1 + 4*0.5) / 2 = 3.0
        assert elli.semi_minor < circ.radius


class TestDepthAdaptiveMargin:
    """Test depth-adaptive margin calculation."""

    def test_depth_zero(self) -> None:
        m = depth_adaptive_margin(1.0, 0, 1)
        assert m == 1.0

    def test_deeper_means_smaller(self) -> None:
        m0 = depth_adaptive_margin(1.0, 0, 1)
        m1 = depth_adaptive_margin(1.0, 1, 1)
        m2 = depth_adaptive_margin(1.0, 2, 1)
        assert m0 > m1 > m2

    def test_more_siblings_means_smaller(self) -> None:
        m1 = depth_adaptive_margin(1.0, 0, 1)
        m5 = depth_adaptive_margin(1.0, 0, 5)
        assert m1 > m5

    def test_zero_siblings_safe(self) -> None:
        m = depth_adaptive_margin(1.0, 0, 0)
        assert m > 0
