"""Adaptive occupation areas — elliptical replacement for circular."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class CircularOccupation:
    """Standard circular occupation area."""

    center: tuple[float, float]
    radius: float

    def bounding_box(self) -> tuple[float, float, float, float]:
        """Return (x_min, y_min, x_max, y_max)."""
        cx, cy = self.center
        return (cx - self.radius, cy - self.radius, cx + self.radius, cy + self.radius)

    def area(self) -> float:
        return math.pi * self.radius ** 2


@dataclass
class EllipticalOccupation:
    """Elliptical occupation area for B_Evc nodes.

    Replaces the circular area that causes excess whitespace.
    semi_major = r_up + r_lw + 2*margin  (vertical extent)
    semi_minor = max(r_up, r_lw) + margin  (horizontal extent)
    """

    center: tuple[float, float]
    semi_major: float  # vertical
    semi_minor: float  # horizontal

    def bounding_box(self) -> tuple[float, float, float, float]:
        cx, cy = self.center
        return (
            cx - self.semi_minor,
            cy - self.semi_major,
            cx + self.semi_minor,
            cy + self.semi_major,
        )

    def area(self) -> float:
        return math.pi * self.semi_major * self.semi_minor


OccupationArea = CircularOccupation | EllipticalOccupation


def compute_b_evc_occupation(
    r_up: float,
    r_lw: float,
    margin: float,
    center: tuple[float, float] = (0, 0),
    use_ellipse: bool = True,
) -> OccupationArea:
    """Compute occupation area for B_Evc (b++/b--) nodes.

    Args:
        r_up: Radius of the upper child's occupation area.
        r_lw: Radius of the lower child's occupation area.
        margin: Margin between children and parent boundary.
        center: Center of the occupation area.
        use_ellipse: If True, use elliptical area (reduced whitespace).

    Returns:
        Either EllipticalOccupation or CircularOccupation.
    """
    if use_ellipse:
        semi_major = r_up + r_lw + 2 * margin
        semi_minor = max(r_up, r_lw) + margin
        return EllipticalOccupation(
            center=center, semi_major=semi_major, semi_minor=semi_minor
        )
    r = r_up + r_lw + 2 * margin
    return CircularOccupation(center=center, radius=r)


def depth_adaptive_margin(
    base_margin: float,
    depth: int,
    n_siblings: int,
) -> float:
    """Compute depth-adaptive margin.

    margin = base_margin * (0.8 ** depth) * min(1.0, 3.0 / max(n_siblings, 1))

    Deeper nodes and nodes with more siblings get smaller margins.
    """
    depth_factor = 0.8 ** depth
    sibling_factor = min(1.0, 3.0 / max(n_siblings, 1))
    return base_margin * depth_factor * sibling_factor
