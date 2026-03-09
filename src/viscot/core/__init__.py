"""Core modules for visCOT."""

from .canvas import (
    Canvas,
    DrawnArrow,
    DrawnCircle,
    DrawnElement,
    DrawnLine,
    DrawnPoint,
    DrawnSpline,
)
from .config import DEFAULT_CONFIG, LayoutConfig
from .nodes import (
    A0,
    A2,
    B0,
    A_Flip,
    A_minus,
    A_plus,
    B0_minus,
    B0_plus,
    B_Evc,
    B_Flip,
    B_minus_minus,
    B_minus_plus,
    B_plus_minus,
    B_plus_plus,
    Beta,
    Beta_minus,
    Beta_plus,
    C,
    C_minus,
    C_plus,
    Cons,
    DrawContext,
    Leaf,
    Leaf_minus,
    Leaf_plus,
    Nil,
    Node,
    OccupationInfo,
    use_config,
)
from .parser import parse


def render_expression(expression: str, config: LayoutConfig | None = None) -> Canvas:
    """Parse and render a COT expression, returning the Canvas."""
    canvas = Canvas(config=config)
    tree = parse(expression, config=config)
    tree.set_canvas(canvas)
    tree.draw()
    return canvas


__all__ = [
    "Canvas", "DrawnCircle", "DrawnElement", "DrawnLine", "DrawnSpline", "DrawnArrow", "DrawnPoint",
    "DEFAULT_CONFIG", "LayoutConfig",
    "A0", "A2", "A_Flip", "A_minus", "A_plus",
    "B0", "B0_minus", "B0_plus",
    "B_Evc", "B_Flip",
    "B_minus_minus", "B_minus_plus", "B_plus_minus", "B_plus_plus",
    "Beta", "Beta_minus", "Beta_plus",
    "C", "C_minus", "C_plus",
    "Cons", "DrawContext", "Leaf", "Leaf_minus", "Leaf_plus", "Nil", "Node",
    "OccupationInfo", "use_config",
    "parse",
    "render_expression",
]
