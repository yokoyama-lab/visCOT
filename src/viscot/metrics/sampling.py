"""Utilities for discretizing drawn elements into polylines."""

from __future__ import annotations

import math

import numpy as np

from ..core.canvas import DrawnCircle, DrawnElement, DrawnLine, DrawnSpline


def circle_to_polyline(circle: DrawnCircle, num_points: int = 64) -> np.ndarray:
    """Discretize a circle into a polyline of (num_points, 2)."""
    angles = np.linspace(0, 2 * math.pi, num_points, endpoint=False)
    cx, cy = circle.center
    xs = cx + circle.radius * np.cos(angles)
    ys = cy + circle.radius * np.sin(angles)
    return np.column_stack([xs, ys])


def line_to_polyline(line: DrawnLine) -> np.ndarray:
    """Convert a line segment to a polyline of (2, 2)."""
    return np.array([line.start, line.end])


def element_to_polyline(elem: DrawnElement) -> np.ndarray | None:
    """Convert a DrawnElement to a polyline, or None if not applicable."""
    if isinstance(elem, DrawnSpline):
        return elem.points
    if isinstance(elem, DrawnCircle):
        return circle_to_polyline(elem)
    if isinstance(elem, DrawnLine):
        return line_to_polyline(elem)
    return None


def elements_to_polylines(elements: list[DrawnElement]) -> list[np.ndarray]:
    """Convert all applicable drawn elements to polylines."""
    return [p for p in (element_to_polyline(e) for e in elements) if p is not None]
