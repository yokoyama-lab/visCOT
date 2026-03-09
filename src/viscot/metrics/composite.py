"""Composite readability score combining M1, M2, M3."""

from __future__ import annotations

from dataclasses import dataclass

from ..core.canvas import DrawnElement
from .overlap import OverlapResult, compute_overlap
from .smoothness import SmoothnessResult, compute_smoothness
from .spacing import SpacingResult, compute_spacing


@dataclass
class CompositeScore:
    """Combined readability score (higher is better)."""

    score: float
    overlap: OverlapResult
    spacing: SpacingResult
    smoothness: SmoothnessResult


def compute_composite_score(
    elements: list[DrawnElement],
    w1: float = 100.0,
    w2: float = 1.0,
    w3: float = 1.0,
) -> CompositeScore:
    """Compute composite readability score.

    Score = -w1 * crossing_count - w2 * d_cv - w3 * jerk
    Higher is better (ideally 0 when no crossings, uniform spacing, smooth curves).

    Args:
        elements: List of drawn elements from Canvas.
        w1: Weight for crossing count penalty.
        w2: Weight for spacing coefficient of variation penalty.
        w3: Weight for jerk (curvature variation) penalty.

    Returns:
        CompositeScore with individual and combined results.
    """
    overlap = compute_overlap(elements, spline_only=True)
    spacing = compute_spacing(elements)
    smoothness = compute_smoothness(elements)

    score = -w1 * overlap.crossing_count - w2 * spacing.d_cv - w3 * smoothness.jerk

    return CompositeScore(
        score=score,
        overlap=overlap,
        spacing=spacing,
        smoothness=smoothness,
    )
