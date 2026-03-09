"""M1: Overlap and crossing detection metric."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..core.canvas import DrawnElement, DrawnSpline
from .sampling import elements_to_polylines


def _bounding_box(poly: np.ndarray) -> tuple[float, float, float, float]:
    """Return (x_min, y_min, x_max, y_max) for a polyline."""
    return (
        float(poly[:, 0].min()),
        float(poly[:, 1].min()),
        float(poly[:, 0].max()),
        float(poly[:, 1].max()),
    )


def _bboxes_overlap(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> bool:
    """Check if two bounding boxes overlap."""
    return a[0] <= b[2] and a[2] >= b[0] and a[1] <= b[3] and a[3] >= b[1]


def _segments_intersect(
    p1: np.ndarray,
    p2: np.ndarray,
    p3: np.ndarray,
    p4: np.ndarray,
) -> bool:
    """Check if line segment p1-p2 intersects p3-p4 using cross products."""
    d1 = p2 - p1
    d2 = p4 - p3

    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) < 1e-12:
        return False

    t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / cross
    u = ((p3[0] - p1[0]) * d1[1] - (p3[1] - p1[1]) * d1[0]) / cross

    return bool(0 < t < 1 and 0 < u < 1)


@dataclass
class OverlapResult:
    """Result of overlap/crossing detection."""

    crossing_count: int
    overlap_ratio: float  # fraction of points within epsilon of another element


def compute_overlap(
    elements: list[DrawnElement],
    epsilon: float = 0.05,
    spline_only: bool = False,
) -> OverlapResult:
    """Compute crossing count and overlap ratio for drawn elements.

    Uses bounding box pruning to skip pairs that cannot intersect.

    Args:
        elements: List of drawn elements to analyze.
        epsilon: Distance threshold for considering points as overlapping.
        spline_only: If True, only analyze spline elements (excludes
            structural crossings between splines and parent circles).

    Returns:
        OverlapResult with crossing_count and overlap_ratio.
    """
    if spline_only:
        target = [e for e in elements if isinstance(e, DrawnSpline)]
        polylines = [e.points for e in target]
    else:
        polylines = elements_to_polylines(elements)

    if len(polylines) < 2:
        return OverlapResult(crossing_count=0, overlap_ratio=0.0)

    # Precompute bounding boxes
    bboxes = [_bounding_box(p) for p in polylines]

    # Crossing detection between different polylines (with bbox pruning)
    crossing_count = 0
    for i in range(len(polylines)):
        for j in range(i + 1, len(polylines)):
            if not _bboxes_overlap(bboxes[i], bboxes[j]):
                continue
            pi = polylines[i]
            pj = polylines[j]
            for si in range(len(pi) - 1):
                for sj in range(len(pj) - 1):
                    if _segments_intersect(pi[si], pi[si + 1], pj[sj], pj[sj + 1]):
                        crossing_count += 1

    # Overlap ratio using epsilon-neighborhood
    total_points = 0
    overlap_points = 0
    for i in range(len(polylines)):
        for pi_idx in range(len(polylines[i])):
            total_points += 1
            pt = polylines[i][pi_idx]
            for j in range(len(polylines)):
                if i == j:
                    continue
                # Bbox check: skip if point is far from polyline j
                bj = bboxes[j]
                if (pt[0] < bj[0] - epsilon or pt[0] > bj[2] + epsilon
                        or pt[1] < bj[1] - epsilon or pt[1] > bj[3] + epsilon):
                    continue
                dists = np.linalg.norm(polylines[j] - pt, axis=1)
                if np.min(dists) < epsilon:
                    overlap_points += 1
                    break

    overlap_ratio = overlap_points / total_points if total_points > 0 else 0.0

    return OverlapResult(
        crossing_count=crossing_count,
        overlap_ratio=overlap_ratio,
    )
