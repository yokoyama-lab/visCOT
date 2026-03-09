"""Canvas class — drawing surface with DrawnElement recording."""

from __future__ import annotations

import math
from dataclasses import dataclass

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

from .config import DEFAULT_CONFIG, LayoutConfig

# --- DrawnElement types ---


@dataclass
class DrawnCircle:
    center: tuple[float, float]
    radius: float
    filled: bool = False


@dataclass
class DrawnSpline:
    points: np.ndarray  # (N, 2)


@dataclass
class DrawnLine:
    start: tuple[float, float]
    end: tuple[float, float]


@dataclass
class DrawnArrow:
    center: tuple[float, float]
    theta: float


@dataclass
class DrawnPoint:
    center: tuple[float, float]


DrawnElement = DrawnCircle | DrawnSpline | DrawnLine | DrawnArrow | DrawnPoint


class Canvas:
    """Drawing surface backed by matplotlib, with element recording for metrics."""

    def __init__(self, config: LayoutConfig | None = None) -> None:
        self.config = config or DEFAULT_CONFIG
        self._drawn_elements: list[DrawnElement] = []
        self._init_figure()

    def _init_figure(self) -> None:
        """Create (or reset) the matplotlib figure and axes."""
        self.fig, self.ax = plt.subplots()
        plt.axis("off")
        self.ax.set_aspect("equal")

    @property
    def drawn_elements(self) -> list[DrawnElement]:
        return self._drawn_elements

    def show_canvas(self) -> None:
        self.fig.tight_layout()
        plt.show()

    def save_canvas(self, file_name: str, dpi: int = 150) -> None:
        self.fig.tight_layout()
        self.fig.savefig(file_name, dpi=dpi)

    def close(self) -> None:
        """Close the figure without re-creating. Use for final cleanup."""
        plt.close(self.fig)
        self._drawn_elements.clear()

    def __enter__(self) -> Canvas:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def clear_canvas(self) -> None:
        """Reset the canvas for reuse, clearing all drawn elements."""
        self.ax.clear()
        plt.axis("off")
        self.ax.set_aspect("equal")
        self._drawn_elements.clear()

    def _spline(
        self,
        x: list[float],
        y: list[float],
        num_points: int,
        degree: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        tck, _ = interpolate.splprep([x, y], k=degree, s=0)
        u = np.linspace(0, 1, num=num_points, endpoint=True)
        result = interpolate.splev(u, tck)
        return result[0], result[1]

    def draw_spline(self, xy: list[list[float] | tuple[float, float]]) -> None:
        if len(xy) < 3:
            raise ValueError(f"draw_spline requires at least 3 points, got {len(xy)}")
        num_points = self.config.spline_num_points
        xs, ys = zip(*xy, strict=True)
        a, b = self._spline(
            list(xs),
            list(ys),
            num_points,
            min(len(xy), 4) - 1,
        )
        self.ax.plot(a, b, color="black")
        pts = np.column_stack([a, b])
        self._drawn_elements.append(DrawnSpline(points=pts))

    def draw_circle(
        self,
        r: float,
        center: tuple[float, float] = (0, 0),
        circle_fill: bool = False,
        fc: str = "gray",
    ) -> None:
        common = {"ec": "black", "linewidth": self.config.line_width}
        if circle_fill:
            circ = mpatches.Circle(center, r, fc=fc, **common)
        else:
            circ = mpatches.Circle(center, r, fill=False, **common)
        self.ax.add_patch(circ)
        self._drawn_elements.append(DrawnCircle(center=center, radius=r, filled=circle_fill))

    def draw_arrow(self, center: tuple[float, float], theta: float = 0) -> None:
        tw = self.config.arrow_tail_width
        sf = self.config.arrow_shrink_factor
        arst = f"wedge,tail_width={tw},shrink_factor={sf}"
        self.ax.annotate(
            "",
            xy=(
                center[0] + 0.1 * math.cos(theta),
                center[1] + 0.05 * math.sin(theta),
            ),
            xytext=(
                center[0] + 0.1 * math.cos(math.pi + theta),
                center[1] + 0.1 * math.sin(math.pi + theta),
            ),
            arrowprops=dict(
                arrowstyle=arst,
                connectionstyle="arc3",
                facecolor="k",
                edgecolor="k",
                shrinkA=0,
                shrinkB=0,
            ),
        )
        self._drawn_elements.append(DrawnArrow(center=center, theta=theta))

    def draw_point(self, center: tuple[float, float]) -> None:
        self.ax.plot([center[0]], [center[1]], "k.")
        self._drawn_elements.append(DrawnPoint(center=center))

    def draw_line(
        self,
        xy_1: tuple[float, float],
        xy_2: tuple[float, float],
    ) -> None:
        self.ax.plot([xy_1[0], xy_2[0]], [xy_1[1], xy_2[1]], "k-")
        self._drawn_elements.append(DrawnLine(start=xy_1, end=xy_2))

    def axvspan(self, r: float) -> None:
        ratio = self.config.axvspan_margin_ratio
        self.ax.axvspan(-r * ratio, r * ratio, color="gray", alpha=0.5)
        self.ax.set_xlim(-r * ratio, r * ratio)
        self.ax.set_ylim(-r * ratio, r * ratio)
