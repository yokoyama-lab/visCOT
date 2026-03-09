"""Shared test fixtures."""

from __future__ import annotations

import matplotlib
import pytest

matplotlib.use("Agg")  # non-interactive backend for tests

from viscot.core.canvas import Canvas
from viscot.core.parser import parse


@pytest.fixture
def canvas() -> Canvas:
    """Provide a fresh Canvas."""
    c = Canvas()
    yield c
    c.close()


@pytest.fixture
def render():
    """Factory fixture: parse expression, set canvas, draw, return (tree, canvas).

    Automatically closes all created canvases to prevent figure leaks.
    """
    canvases: list[Canvas] = []

    def _render(expression: str) -> tuple:
        canvas = Canvas()
        canvases.append(canvas)
        tree = parse(expression)
        tree.set_canvas(canvas)
        tree.draw()
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
