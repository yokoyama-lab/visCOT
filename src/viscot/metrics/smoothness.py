"""M3: Curvature-based smoothness metric."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..core.canvas import DrawnElement, DrawnSpline
from .sampling import elements_to_polylines


def _menger_curvature(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """Compute Menger curvature for three consecutive points.

    Returns the discrete curvature: 2 * |triangle_area| / (|p1p2| * |p2p3| * |p1p3|).
    A circle has constant curvature; a straight line has zero curvature.
    """
    d12 = np.linalg.norm(p2 - p1)
    d23 = np.linalg.norm(p3 - p2)
    d13 = np.linalg.norm(p3 - p1)
    denom = d12 * d23 * d13
    if denom < 1e-15:
        return 0.0
    # Twice the signed area of the triangle
    area = abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1]))
    return float(2.0 * area / denom)


@dataclass
class SmoothnessResult:
    """Result of smoothness analysis."""

    kappa_max: float
    kappa_mean: float
    kappa_var: float
    jerk: float  # integral of curvature change rate


def compute_smoothness(elements: list[DrawnElement]) -> SmoothnessResult:
    """Compute curvature-based smoothness metrics.

    For circles, curvature is constant so jerk ≈ 0.
    For splines, jerk measures how much the curvature varies — lower is smoother.

    Returns:
        SmoothnessResult with kappa_max, kappa_mean, kappa_var, jerk.
    """
    # Only analyze splines (curves), not circles or lines
    spline_polylines = [
        elem.points for elem in elements
        if isinstance(elem, DrawnSpline) and len(elem.points) >= 3
    ]

    if not spline_polylines:
        # Fall back to all polylines
        spline_polylines = [p for p in elements_to_polylines(elements) if len(p) >= 3]

    if not spline_polylines:
        return SmoothnessResult(kappa_max=0.0, kappa_mean=0.0, kappa_var=0.0, jerk=0.0)

    all_curvatures: list[float] = []
    total_jerk = 0.0

    for poly in spline_polylines:
        curvatures = []
        for i in range(1, len(poly) - 1):
            k = _menger_curvature(poly[i - 1], poly[i], poly[i + 1])
            curvatures.append(k)
        if curvatures:
            all_curvatures.extend(curvatures)
            # Jerk = sum of |dk/ds| (discrete derivative of curvature)
            for i in range(1, len(curvatures)):
                total_jerk += abs(curvatures[i] - curvatures[i - 1])

    if not all_curvatures:
        return SmoothnessResult(kappa_max=0.0, kappa_mean=0.0, kappa_var=0.0, jerk=0.0)

    arr = np.array(all_curvatures)
    return SmoothnessResult(
        kappa_max=float(np.max(arr)),
        kappa_mean=float(np.mean(arr)),
        kappa_var=float(np.var(arr)),
        jerk=total_jerk,
    )
