"""Node hierarchy for COT tree representation."""

from __future__ import annotations

import abc
import math
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

from .canvas import Canvas
from .config import DEFAULT_CONFIG, LayoutConfig

# --- Active configuration context ---

_active_config: LayoutConfig = DEFAULT_CONFIG


@contextmanager
def use_config(config: LayoutConfig) -> Generator[None, None, None]:
    """Temporarily set the active config for node construction."""
    global _active_config
    prev = _active_config
    _active_config = config
    try:
        yield
    finally:
        _active_config = prev


# --- OccupationInfo ---


@dataclass
class OccupationInfo:
    """Occupation area of a node."""

    height: float
    width: float


# --- DrawContext ---


@dataclass
class DrawContext:
    """Unified context passed to Node.draw()."""

    center: tuple[float, float] = (0.0, 0.0)
    edge: float = 0.0
    # C-type fields
    length: float = 0.0
    parent_r: float = 0.0
    parent_center: tuple[float, float] = (0.0, 0.0)
    parent_type: bool = False


# --- Helper functions ---


def theta_point(
    theta: float, r: float, center: tuple[float, float]
) -> tuple[float, float]:
    return r * math.cos(theta) + center[0], r * math.sin(theta) + center[1]


def c_list_highest(children: list[OccupationInfo]) -> float:
    return max(c.height for c in children)


def c_list_circ_length(children: list[OccupationInfo], margin: float) -> float:
    circ_length = sum(c.width + margin for c in children)
    widest = max(c.width for c in children)
    return max(circ_length, widest * 2)


def make_list_for_c(
    children: list[OccupationInfo],
    parent_r: float,
    parent_center: tuple[float, float],
    parent_type: bool,
    margin: float,
    parent_length: float = 0,
    first_child: bool = False,
    config: LayoutConfig | None = None,
) -> list[DrawContext]:
    if config is None:
        config = DEFAULT_CONFIG
    result: list[DrawContext] = []
    length = parent_length
    if parent_type and first_child:
        # B0 の最初の子は親円周上で少しオフセットして配置開始
        length += config.b0_first_child_offset
        share = margin / len(children)  # circumference / n_children
        for _ in children:
            result.append(
                DrawContext(
                    length=length,
                    parent_r=parent_r,
                    parent_center=parent_center,
                    parent_type=parent_type,
                )
            )
            # Advance by share to distribute children evenly around the circle
            length += share
    else:
        for child in children:
            length += margin
            result.append(
                DrawContext(
                    length=length,
                    parent_r=parent_r,
                    parent_center=parent_center,
                    parent_type=parent_type,
                )
            )
            length += child.width
    return result


# --- Node base ---


_CENTER_ORIGIN: tuple[float, float] = (0.0, 0.0)
_ZERO_OCCUPATION = OccupationInfo(height=0, width=0)

# Type alias for center parameters that accept either DrawContext or raw coordinates
_CenterArg = DrawContext | tuple[float, float]


class Node(abc.ABC):
    """Abstract base for all tree nodes."""

    dir: int  # +1 or -1, defined by subclasses
    _show_prefix: str = ""

    @abc.abstractmethod
    def __init__(
        self,
        head: Node | None = None,
        tail: Node | None = None,
        canvas: Canvas | None = None,
    ) -> None:
        self.canvas: Canvas | None = canvas
        self.head = head
        self.tail = tail
        self.r: float = 0
        self.occupation: list[OccupationInfo] = [_ZERO_OCCUPATION]
        self._config: LayoutConfig = _active_config

    @abc.abstractmethod
    def draw(self, *args: Any, **kwargs: Any) -> None:
        """Perform drawing."""

    def plot_arrow(self, *args: Any, **kwargs: Any) -> None:
        """Draw arrows.  No-op by default."""

    def set_canvas(self, canvas: Canvas) -> None:
        self.canvas = canvas
        if self.head is not None:
            self.head.set_canvas(canvas)
        if self.tail is not None:
            self.tail.set_canvas(canvas)

    @property
    def _cv(self) -> Canvas:
        """Shorthand for accessing canvas with a runtime check."""
        if self.canvas is None:
            raise RuntimeError("Canvas not set. Call set_canvas() before drawing.")
        return self.canvas

    def dir2rad(self) -> float:
        return (self.dir + 1.0) * math.pi / 2.0

    @staticmethod
    def _resolve_center(
        center: _CenterArg,
    ) -> tuple[float, float]:
        """Extract center tuple from a DrawContext or pass through."""
        if isinstance(center, DrawContext):
            return center.center
        return center

    @staticmethod
    def _resolve_center_edge(
        info: DrawContext | None,
    ) -> tuple[tuple[float, float], float]:
        """Extract (center, edge) from a DrawContext or return defaults."""
        if isinstance(info, DrawContext):
            return info.center, info.edge
        return _CENTER_ORIGIN, 0.0

    @abc.abstractmethod
    def show(self) -> str:
        """Return string representation."""

    def _show_two_children(self) -> str:
        """Common show() for nodes with two children: prefix(head,tail)."""
        if self.head is None or self.tail is None:
            raise RuntimeError("_show_two_children requires both head and tail")
        return f"{self._show_prefix}({self.head.show()},{self.tail.show()})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return type(self) is type(other) and self.show() == other.show()

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.show()))

    def __repr__(self) -> str:
        return self.show()


# --- Concrete nodes ---


class A0(Node):
    """A0 node."""

    head: Node

    def __init__(self, head: Node) -> None:
        super().__init__(head)

    def draw(self, *args: Any, **kwargs: Any) -> None:
        margin = self._config.a0_margin
        childrens_info: list[DrawContext] = []
        if isinstance(self.head, Nil):
            self._cv.draw_line((-1, 0), (1, 0))
            self._cv.draw_arrow((0, 0), 0)
        else:
            count_r = 0.0
            long_child = c_list_highest(self.head.occupation)
            for child in self.head.occupation:
                count_r += child.height + margin
                childrens_info.append(
                    DrawContext(center=(0, -count_r), edge=long_child + margin)
                )
                count_r += child.height + margin
        self.head.draw(childrens_info)

    def show(self) -> str:
        return "A0()" if isinstance(self.head, Nil) else f"A0({self.head.show()})"


class B0(Node):
    """Abstract base for B0+, B0-."""

    head: Node
    tail: Node
    _show_prefix: str

    def __init__(self, head: Node, tail: Node) -> None:
        super().__init__(head, tail)
        cfg = self._config
        high_children = c_list_highest(tail.occupation)
        children_length = c_list_circ_length(tail.occupation, cfg.b0_margin)
        self.r = max(
            children_length / (2 * math.pi), head.r + high_children + cfg.b0_margin
        )

    def draw(self, *args: Any, **kwargs: Any) -> None:
        self._cv.axvspan(self.r)
        self._cv.draw_circle(self.r, _CENTER_ORIGIN, circle_fill=True, fc="white")
        self.plot_arrow()
        for_children = make_list_for_c(
            self.tail.occupation,
            self.r,
            _CENTER_ORIGIN,
            True,
            2 * self.r * math.pi,
            first_child=True,
            config=self._config,
        )
        self.head.draw(_CENTER_ORIGIN)
        self.tail.draw(for_children)

    def plot_arrow(self, *args: Any, **kwargs: Any) -> None:
        self._cv.draw_arrow(
            (self.r, 0), math.pi * 1.5 - self.dir2rad()
        )

    def show(self) -> str:
        return self._show_two_children()


class B0_plus(B0):
    """B0+ node."""

    dir = 1
    _show_prefix = "B0+"


class B0_minus(B0):
    """B0- node."""

    dir = -1
    _show_prefix = "B0-"


class A_Flip(Node):
    """Abstract base for a+, a-."""

    head: Node
    _show_prefix: str

    def __init__(self, head: Node) -> None:
        super().__init__(head)
        margin = self._config.a_flip_margin
        self.r: float = head.r + margin
        self.occupation: list[OccupationInfo] = [OccupationInfo(height=self.r, width=0)]

    def draw(self, info: DrawContext | None = None, *args: Any, **kwargs: Any) -> None:
        center, edge = self._resolve_center_edge(info)
        self._cv.draw_circle(self.r, center)
        self.plot_arrow(center, edge)
        self.head.draw(center)

    def plot_arrow(
        self,
        center: tuple[float, float] | None = None,
        edge: float = 0,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if center is None:
            center = _CENTER_ORIGIN
        cx, cy = center
        stag_y = cy + self.r * self.dir
        self._cv.draw_point((cx, stag_y))
        self._cv.draw_arrow(
            (cx - self.r, cy), theta=math.pi * 0.5 - self.dir2rad(),
        )
        self._cv.draw_arrow(
            (cx + self.r, cy), theta=math.pi * 1.5 - self.dir2rad(),
        )
        self._cv.draw_line((-edge, stag_y), (edge, stag_y))
        self._cv.draw_arrow((-edge / 2, stag_y), 0)
        self._cv.draw_arrow((edge / 2, stag_y), 0)

    def show(self) -> str:
        return f"{self._show_prefix}({self.head.show()})"


class A_plus(A_Flip):
    """a+ node."""

    dir = 1
    _show_prefix = "a+"


class A_minus(A_Flip):
    """a- node."""

    dir = -1
    _show_prefix = "a-"


class A2(Node):
    """a2 node."""

    head: Node
    tail: Node

    def __init__(self, head: Node, tail: Node) -> None:
        super().__init__(head, tail)
        cfg = self._config
        margin = cfg.a2_margin
        self.high = max(
            c_list_highest(head.occupation), c_list_highest(tail.occupation)
        )
        len_of_plus_circ = (
            c_list_circ_length(head.occupation, margin) + margin
        )
        len_of_minus_circ = (
            c_list_circ_length(tail.occupation, margin) + margin
        )
        self.len_of_circ = max(len_of_plus_circ, len_of_minus_circ) * 2
        self.center_r: float = self.len_of_circ / (2 * math.pi)
        self.r: float = self.center_r + self.high
        self.occupation: list[OccupationInfo] = [OccupationInfo(height=self.r, width=0)]

    def draw(self, info: DrawContext | None = None, *args: Any, **kwargs: Any) -> None:
        cfg = self._config
        center, edge = self._resolve_center_edge(info)
        cx, cy = center
        self._cv.draw_circle(self.center_r, center, circle_fill=True)
        self._cv.draw_point((cx + self.center_r, cy))
        self._cv.draw_point((cx - self.center_r, cy))
        self._cv.draw_line((cx - self.r, cy), (cx - self.center_r, cy))
        self._cv.draw_line((cx + self.center_r, cy), (cx + self.r, cy))
        self._cv.draw_line((-edge, cy), (-self.r, cy))
        self._cv.draw_line((self.r, cy), (edge, cy))
        self._cv.draw_arrow(((-edge - self.r) / 2, cy), 0)
        self._cv.draw_arrow(((self.r + edge) / 2, cy), 0)
        for_plus_children = make_list_for_c(
            self.head.occupation, self.center_r, center, False, cfg.a2_margin,
            parent_length=self.len_of_circ / 2,
            config=cfg,
        )
        for_minus_children = make_list_for_c(
            self.tail.occupation,
            self.center_r,
            center,
            False,
            cfg.a2_margin,
            config=cfg,
        )
        self.head.draw(for_plus_children)
        self.tail.draw(for_minus_children)

    def show(self) -> str:
        return f"a2({self.head.show()},{self.tail.show()})"


class Cons(Node):
    """Cons node — list constructor."""

    head: Node
    tail: Node
    dir = 0

    def __init__(self, head: Node, tail: Node) -> None:
        super().__init__(head, tail)
        self.occupation: list[OccupationInfo] = [
            s
            for s in head.occupation + tail.occupation
            if s != _ZERO_OCCUPATION
        ]

    def draw(
        self, children_list: list[DrawContext] | None = None, *args: Any, **kwargs: Any,
    ) -> None:
        if not isinstance(children_list, list):
            self.head.draw(children_list)
            return
        self.head.draw(children_list[0])
        if len(children_list) > 1:
            self.tail.draw(children_list[1:])

    def show(self) -> str:
        if isinstance(self.tail, Nil):
            return self.head.show()
        return f"{self.head.show()}.{self.tail.show()}"


class Nil(Node):
    """Nil node — empty list."""

    dir = 0

    def __init__(self) -> None:
        super().__init__()
        self.occupation: list[OccupationInfo] = [_ZERO_OCCUPATION]

    def draw(self, *args: Any, **kwargs: Any) -> None:
        pass

    def show(self) -> str:
        return ""


class Leaf(Node):
    """Abstract base for l+, l-."""

    _show_prefix: str

    def __init__(self) -> None:
        super().__init__()
        self.r: float = 0

    def draw(self, *args: Any, **kwargs: Any) -> None:
        pass

    def show(self) -> str:
        return self._show_prefix


class Leaf_plus(Leaf):
    """l+ node."""

    dir = 1
    _show_prefix = "l+"


class Leaf_minus(Leaf):
    """l- node."""

    dir = -1
    _show_prefix = "l-"


class B_Evc(Node):
    """Abstract base for b++, b--."""

    head: Node
    tail: Node
    _show_prefix: str

    def __init__(self, head: Node, tail: Node) -> None:
        super().__init__(head, tail)
        margin = self._config.b_evc_margin
        self.r_up: float = head.r
        self.r_lw: float = tail.r
        self.r: float = self.r_up + self.r_lw + 2 * margin

    def draw(self, center: _CenterArg = (0, 0), *args: Any, **kwargs: Any) -> None:
        center = self._resolve_center(center)
        margin = self._config.b_evc_margin
        cx, cy = center
        upper = (cx, cy + self.r_lw + margin)
        lower = (cx, cy - self.r_up - margin)
        self._cv.draw_point((cx, cy + self.r_lw - self.r_up))
        self._cv.draw_circle(self.r_up + margin, upper)
        self._cv.draw_circle(self.r_lw + margin, lower)
        self.plot_arrow(center)
        self.head.draw(upper)
        self.tail.draw(lower)

    def plot_arrow(self, center: _CenterArg = (0, 0), *args: Any, **kwargs: Any) -> None:
        margin = self._config.b_evc_margin
        cx, cy = self._resolve_center(center)
        self._cv.draw_arrow(
            (cx, cy + self.r_lw + 2 * margin + self.r_up),
            self.dir2rad(),
        )
        self._cv.draw_arrow(
            (cx, cy - self.r_up - 2 * margin - self.r_lw),
            math.pi - self.dir2rad(),
        )

    def show(self) -> str:
        return self._show_two_children()


class B_plus_plus(B_Evc):
    """b++ node."""

    dir = 1
    _show_prefix = "b++"


class B_minus_minus(B_Evc):
    """b-- node."""

    dir = -1
    _show_prefix = "b--"


class B_Flip(Node):
    """Abstract base for b+-, b-+."""

    head: Node
    tail: Node
    _show_prefix: str

    def __init__(self, head: Node, tail: Node) -> None:
        super().__init__(head, tail)
        margin = self._config.b_flip_margin
        # tail (2nd child) goes inner/upper, head (1st child) goes outer/lower
        self.r_up: float = tail.r
        self.r_lw: float = head.r
        self.r: float = self.r_up + self.r_lw + 2 * margin

    def draw(self, center: _CenterArg = (0, 0), *args: Any, **kwargs: Any) -> None:
        center = self._resolve_center(center)
        margin = self._config.b_flip_margin
        cx, cy = center
        inner_center = (cx, cy + self.r_lw + margin)
        inner_r = self.r_up + margin
        outer_r = self.r_up + self.r_lw + 2 * margin
        self._cv.draw_circle(inner_r, inner_center)
        self._cv.draw_circle(outer_r, center)
        self._cv.draw_point((cx, inner_center[1] + inner_r))
        self.plot_arrow(center)
        # tail (2nd child) → inner/upper circle
        self.tail.draw(inner_center)
        # head (1st child) → outer/lower region
        self.head.draw((cx, cy - self.r_up - margin))

    def plot_arrow(self, center: _CenterArg = (0, 0), *args: Any, **kwargs: Any) -> None:
        cx, cy = self._resolve_center(center)
        inner_bottom_y = cy + self.r_lw - self.r_up
        outer_r = self.r_up + self.r_lw + 2 * self._config.b_flip_margin
        # Arrow at bottom of inner circle: shows tail's (2nd sign) direction
        self._cv.draw_arrow((cx, inner_bottom_y), theta=self.dir2rad())
        # Arrow at bottom of outer circle: shows head's (1st sign) direction
        self._cv.draw_arrow((cx, cy - outer_r), theta=math.pi - self.dir2rad())

    def show(self) -> str:
        return self._show_two_children()


class B_plus_minus(B_Flip):
    """b+- node."""

    dir = 1
    _show_prefix = "b+-"


class B_minus_plus(B_Flip):
    """b-+ node."""

    dir = -1
    _show_prefix = "b-+"


class Beta(Node):
    """Abstract base for B+, B-."""

    head: Node
    _show_prefix: str

    def __init__(self, head: Node) -> None:
        super().__init__(head)
        cfg = self._config
        high_children = c_list_highest(head.occupation)
        children_length = c_list_circ_length(head.occupation, cfg.beta_margin)
        self.center_r: float = children_length / (2 * math.pi)
        if children_length < 1:
            self.center_r = cfg.beta_min_circ / (2 * math.pi)
        self.r: float = self.center_r + high_children

    def draw(self, center: _CenterArg = (0, 0), *args: Any, **kwargs: Any) -> None:
        center = self._resolve_center(center)
        cfg = self._config
        self._cv.draw_circle(self.center_r, center, circle_fill=True)
        for_children = make_list_for_c(
            self.head.occupation, self.center_r, center, False,
            cfg.beta_margin, config=cfg,
        )
        self.plot_arrow(center)
        self.head.draw(for_children)

    def plot_arrow(self, center: _CenterArg = (0, 0), *args: Any, **kwargs: Any) -> None:
        cx, cy = self._resolve_center(center)
        self._cv.draw_arrow(
            (cx + self.center_r, cy),
            math.pi * 1.5 - self.dir2rad(),
        )

    def show(self) -> str:
        return f"{self._show_prefix}{{{self.head.show()}}}"


class Beta_plus(Beta):
    """B+ node."""

    dir = 1
    _show_prefix = "B+"


class Beta_minus(Beta):
    """B- node."""

    dir = -1
    _show_prefix = "B-"


class C(Node):
    """Abstract base for c+, c-."""

    head: Node
    tail: Node
    _show_prefix: str

    def __init__(self, head: Node, tail: Node) -> None:
        super().__init__(head, tail)
        cfg = self._config
        self.high_children: float = c_list_highest(tail.occupation)
        self.children_length: float = c_list_circ_length(tail.occupation, cfg.c_margin)
        self.high: float = 2 * head.r + self.high_children + cfg.c_margin
        if self.head.r == 0 and len(self.tail.occupation) != 1:
            self.high += len(self.tail.occupation)
        # Effective arc-length extent: at least children_length, but wider for
        # tall splines to prevent crossing with adjacent C-node splines.
        self.effective_extent: float = max(
            self.children_length,
            self.high * cfg.c_height_spacing_factor,
        )
        bottom_length = max(head.r * 2, self.effective_extent)
        self.occupation: list[OccupationInfo] = [
            OccupationInfo(height=self.high, width=bottom_length)
        ]

    def draw(self, c_data: DrawContext | None = None, *args: Any, **kwargs: Any) -> None:
        cfg = self._config
        high_children = max(self.high_children, cfg.c_min_child_height)

        if not isinstance(c_data, DrawContext):
            return

        length = c_data.length
        center_r = c_data.parent_r
        center = c_data.parent_center
        bool_b0 = c_data.parent_type

        start_theta = length / center_r
        start_point = theta_point(start_theta, center_r, center)
        end_theta = (length + self.effective_extent) / center_r
        end_point = theta_point(end_theta, center_r, center)
        high_theta = (end_theta - start_theta) / 2 + start_theta
        sign = -1 if bool_b0 else 1
        high_point = theta_point(high_theta, center_r + sign * self.high, center)
        b_center = theta_point(
            high_theta,
            center_r + sign * (high_children + cfg.c_circ_margin + self.head.r),
            center,
        )
        self.plot_arrow(high_point, high_theta)
        if self.head.r != 0:
            b_r_theta = math.pi - (math.pi / 2 + high_theta)
            b_r_center = theta_point(
                -b_r_theta, self.head.r + cfg.c_circ_margin, b_center
            )
            b_l_center = theta_point(
                math.pi - b_r_theta, self.head.r + cfg.c_circ_margin, b_center
            )
            if self.head.r * 2 < self.children_length / 2:
                self._cv.draw_spline(
                    [start_point, high_point, end_point]
                )
            else:
                self._cv.draw_spline(
                    [start_point, b_r_center, high_point, b_l_center, end_point]
                )
        else:
            self._cv.draw_spline([start_point, high_point, end_point])
        self._cv.draw_point(start_point)
        self._cv.draw_point(end_point)
        # Center sub-children within the (possibly wider) effective extent
        padding = (self.effective_extent - self.children_length) / 2
        for_children = make_list_for_c(
            self.tail.occupation,
            center_r,
            center,
            bool_b0,
            cfg.c_margin / 1.5,
            parent_length=length + padding,
            config=cfg,
        )
        self.head.draw(b_center)
        self.tail.draw(for_children)

    def plot_arrow(
        self,
        high_point: tuple[float, float] = (0, 0),
        high_theta: float = 0,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._cv.draw_arrow(
            high_point,
            high_theta + math.pi * 0.5 + self.dir2rad(),
        )

    def show(self) -> str:
        return self._show_two_children()


class C_plus(C):
    """c+ node."""

    dir = -1
    _show_prefix = "c+"


class C_minus(C):
    """c- node."""

    dir = 1
    _show_prefix = "c-"
