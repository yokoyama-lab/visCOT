"""Shared test fixtures."""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")  # non-interactive backend for tests

from viscot.core.canvas import Canvas
from viscot.core.parser import parse


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--save-images",
        action="store",
        default=None,
        metavar="DIR",
        help="Save rendered images to DIR (e.g. --save-images=test_output)",
    )
    parser.addoption(
        "--image-format",
        action="store",
        default="png",
        metavar="FMT",
        help="Image format: png, svg, pdf (default: png)",
    )


@pytest.fixture
def save_image_dir(request: pytest.FixtureRequest) -> Path | None:
    raw = request.config.getoption("--save-images")
    if raw is None:
        return None
    d = Path(raw)
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def image_format(request: pytest.FixtureRequest) -> str:
    return str(request.config.getoption("--image-format"))


@pytest.fixture
def canvas() -> Canvas:
    """Provide a fresh Canvas."""
    c = Canvas()
    yield c
    c.close()


def _sanitize_filename(expr: str) -> str:
    """Turn a COT expression into a safe filename."""
    return re.sub(r"[^a-zA-Z0-9_+-]", "_", expr)[:80]


@pytest.fixture
def render(save_image_dir: Path | None, image_format: str):
    """Factory fixture: parse expression, set canvas, draw, return (tree, canvas).

    If --save-images is given, each rendered expression is saved in the
    format specified by --image-format (default: png).
    """
    canvases: list[Canvas] = []

    def _render(expression: str) -> tuple:
        canvas = Canvas()
        canvases.append(canvas)
        tree = parse(expression)
        tree.set_canvas(canvas)
        tree.draw()
        if save_image_dir is not None:
            fname = _sanitize_filename(expression) + "." + image_format
            canvas.save_canvas(str(save_image_dir / fname))
        return tree, canvas

    yield _render

    for c in canvases:
        c.close()


# Makefile test expressions
MAKEFILE_EXPRESSIONS = [
    "A0()",
    "A0(a+(l+))",
    "A0(a+(l+).a+(l+))",
    "B0+(l+,)",
    "B0+(l+,c-(l-,))",
    "B0+(l+,c-(l-,).c-(l-,))",
    "B0-(l-,)",
    "B0+(b+-(l+,l-),c-(l-,).c-(l-,).c-(l-,))",
    "B0+(b+-(l+,l-),c-(B-{},).c-(l-,).c-(l-,))",
    "B0-(b-+(b-+(l-,l+),B+{}),c+(B+{},).c+(l+,).c+(l+,))",
    "B0+(b+-(b+-(l+,l-),B-{}),c-(B-{},).c-(l-,).c-(l-,))",
]

# Exhaustive: all valid COT expressions with 1, 2, or 3 nodes
EXHAUSTIVE_1_2_3 = [
    "A0()",
    "A0(a2(,))",
    "B0+(B+{},)",
    "B0+(l+,)",
    "B0-(B-{},)",
    "B0-(l-,)",
    "A0(a+(B+{}))",
    "A0(a+(l+))",
    "A0(a-(B-{}))",
    "A0(a-(l-))",
    "A0(a2(,).a2(,))",
]

# Exhaustive: all valid COT expressions with 4 nodes (41 expressions)
EXHAUSTIVE_4 = [
    "A0(a+(B+{}).a2(,))", "A0(a+(l+).a2(,))", "A0(a-(B-{}).a2(,))",
    "A0(a-(l-).a2(,))", "A0(a2(,).a+(B+{}))", "A0(a2(,).a+(l+))",
    "A0(a2(,).a-(B-{}))", "A0(a2(,).a-(l-))", "A0(a2(,).a2(,).a2(,))",
    "A0(a2(,c-(B-{},)))", "A0(a2(,c-(l-,)))", "A0(a2(c+(B+{},),))",
    "A0(a2(c+(l+,),))", "B0+(B+{c+(B+{},)},)", "B0+(B+{c+(l+,)},)",
    "B0+(B+{},c-(B-{},))", "B0+(B+{},c-(l-,))", "B0+(b++(B+{},B+{}),)",
    "B0+(b++(B+{},l+),)", "B0+(b++(l+,B+{}),)", "B0+(b++(l+,l+),)",
    "B0+(b+-(B+{},B-{}),)", "B0+(b+-(B+{},l-),)", "B0+(b+-(l+,B-{}),)",
    "B0+(b+-(l+,l-),)", "B0+(l+,c-(B-{},))", "B0+(l+,c-(l-,))",
    "B0-(B-{c-(B-{},)},)", "B0-(B-{c-(l-,)},)", "B0-(B-{},c+(B+{},))",
    "B0-(B-{},c+(l+,))", "B0-(b-+(B-{},B+{}),)", "B0-(b-+(B-{},l+),)",
    "B0-(b-+(l-,B+{}),)", "B0-(b-+(l-,l+),)", "B0-(b--(B-{},B-{}),)",
    "B0-(b--(B-{},l-),)", "B0-(b--(l-,B-{}),)", "B0-(b--(l-,l-),)",
    "B0-(l-,c+(B+{},))", "B0-(l-,c+(l+,))",
]

# Exhaustive: all valid COT expressions with 5 nodes (57 expressions)
EXHAUSTIVE_5 = [
    "A0(a+(B+{c+(B+{},)}))", "A0(a+(B+{c+(l+,)}))", "A0(a+(B+{}).a+(B+{}))",
    "A0(a+(B+{}).a+(l+))", "A0(a+(B+{}).a-(B-{}))", "A0(a+(B+{}).a-(l-))",
    "A0(a+(B+{}).a2(,).a2(,))", "A0(a+(b++(B+{},B+{})))", "A0(a+(b++(B+{},l+)))",
    "A0(a+(b++(l+,B+{})))", "A0(a+(b++(l+,l+)))", "A0(a+(b+-(B+{},B-{})))",
    "A0(a+(b+-(B+{},l-)))", "A0(a+(b+-(l+,B-{})))", "A0(a+(b+-(l+,l-)))",
    "A0(a+(l+).a+(B+{}))", "A0(a+(l+).a+(l+))", "A0(a+(l+).a-(B-{}))",
    "A0(a+(l+).a-(l-))", "A0(a+(l+).a2(,).a2(,))", "A0(a-(B-{c-(B-{},)}))",
    "A0(a-(B-{c-(l-,)}))", "A0(a-(B-{}).a+(B+{}))", "A0(a-(B-{}).a+(l+))",
    "A0(a-(B-{}).a-(B-{}))", "A0(a-(B-{}).a-(l-))", "A0(a-(B-{}).a2(,).a2(,))",
    "A0(a-(b-+(B-{},B+{})))", "A0(a-(b-+(B-{},l+)))", "A0(a-(b-+(l-,B+{})))",
    "A0(a-(b-+(l-,l+)))", "A0(a-(b--(B-{},B-{})))", "A0(a-(b--(B-{},l-)))",
    "A0(a-(b--(l-,B-{})))", "A0(a-(b--(l-,l-)))", "A0(a-(l-).a+(B+{}))",
    "A0(a-(l-).a+(l+))", "A0(a-(l-).a-(B-{}))", "A0(a-(l-).a-(l-))",
    "A0(a-(l-).a2(,).a2(,))", "A0(a2(,).a+(B+{}).a2(,))",
    "A0(a2(,).a+(l+).a2(,))", "A0(a2(,).a-(B-{}).a2(,))",
    "A0(a2(,).a-(l-).a2(,))", "A0(a2(,).a2(,).a+(B+{}))",
    "A0(a2(,).a2(,).a+(l+))", "A0(a2(,).a2(,).a-(B-{}))",
    "A0(a2(,).a2(,).a-(l-))", "A0(a2(,).a2(,).a2(,).a2(,))",
    "A0(a2(,).a2(,c-(B-{},)))", "A0(a2(,).a2(,c-(l-,)))",
    "A0(a2(,).a2(c+(B+{},),))", "A0(a2(,).a2(c+(l+,),))",
    "A0(a2(,c-(B-{},)).a2(,))", "A0(a2(,c-(l-,)).a2(,))",
    "A0(a2(c+(B+{},),).a2(,))", "A0(a2(c+(l+,),).a2(,))",
]

# Smallest known expressions with spline crossings (for regression tracking)
CROSSING_EXPRS = {
    # 20 nodes, 2 crossings — c nested inside c with deep b-tree
    "20node": "B0+(l+,c-(b-+(l-,l+),c+(b+-(b+-(b++(l+,l+),b--(l-,l-)),B-{}),c-(B-{},c+(B+{},)))))",
    # 22 nodes, 4-5 crossings — Beta nesting with multiple c children
    "22node": "B0+(l+,c-(l-,c+(B+{c+(B+{},)},c-(B-{},c+(l+,)).c-(b--(l-,b-+(l-,l+)),c+(l+,).c+(l+,)))))",
    # 24 nodes, 8-12 crossings — triple c chain with mixed Beta/b nodes
    "24node": "B0+(l+,c-(l-,c+(l+,c-(b-+(l-,B+{}),c+(B+{},).c+(l+,)).c-(B-{},c+(B+{},)).c-(b-+(l-,l+),c+(b+-(l+,l-),)))))",
}

# 102-node stress test expression (generated with seed=7)
STRESS_EXPR_102 = (
    "B0+(b++(b++(l+,b+-(B+{},l-)),l+),"
    "c-(l-,c+(b++(b++(B+{},b++(l+,l+)),b+-(l+,l-)),"
    "c-(b-+(B-{},l+),c+(B+{},).c+(l+,))"
    ".c-(B-{},c+(B+{},))"
    ".c-(B-{},c+(b+-(l+,l-),))))"
    ".c-(b-+(b-+(b-+(b--(l-,l-),B+{}),b++(B+{},b+-(l+,l-))),b+-(b++(l+,b+-(l+,l-)),l-)),"
    "c+(B+{c+(B+{},)},"
    "c-(b-+(B-{},b++(l+,l+)),c+(b+-(l+,l-),))"
    ".c-(b--(l-,B-{}),c+(b+-(l+,l-),).c+(b+-(l+,l-),)))"
    ".c+(l+,c-(B-{},c+(b++(l+,l+),))"
    ".c-(b--(b-+(l-,l+),b-+(l-,l+)),c+(l+,)))))"
)
