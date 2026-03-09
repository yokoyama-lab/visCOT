"""Batch evaluation runner for COT expressions."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import sys
from dataclasses import dataclass

from ..core import render_expression
from ..metrics.composite import CompositeScore, compute_composite_score

# Benchmark expressions categorized by complexity
BENCHMARK_EXPRESSIONS: dict[str, list[str]] = {
    "leaf_only": [
        "a0()",
        "a0(a+(l+))",
        "a0(a-(l-))",
        "a0(a+(l+).a+(l+))",
        "B0+(l+,)",
        "B0-(l-,)",
    ],
    "single_nesting": [
        "B0+(l+,c-(l-,))",
        "B0+(l+,c-(l-,).c-(l-,))",
        "B0-(l-,c+(l+,))",
        "B0+(b+-(l+,l-),)",
        "B0-(b-+(l-,l+),)",
        "B0+(b++(l+,l+),)",
    ],
    "double_nesting": [
        "B0+(b+-(l+,l-),c-(l-,).c-(l-,).c-(l-,))",
        "B0+(b+-(l+,l-),c-(B-{},).c-(l-,).c-(l-,))",
        "B0-(b-+(b-+(l-,l+),B+{}),c+(B+{},).c+(l+,).c+(l+,))",
        "B0+(b+-(b+-(l+,l-),B-{}),c-(B-{},).c-(l-,).c-(l-,))",
    ],
    "max_depth": [
        "B0+(b+-(b+-(l+,l-),b+-(l+,l-)),c-(B-{c+(l+,)},).c-(l-,))",
    ],
}


@dataclass
class BenchmarkResult:
    """Result for a single benchmark expression."""

    expression: str
    category: str
    score: CompositeScore
    tree_depth: int


def _estimate_depth(expression: str) -> int:
    """Rough estimate of tree depth by counting nesting."""
    depth = 0
    max_depth = 0
    for ch in expression:
        if ch in "({":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch in ")}":
            depth -= 1
    return max_depth


def run_benchmark() -> list[BenchmarkResult]:
    """Run all benchmark expressions and collect scores.

    Returns:
        List of BenchmarkResult for each expression.
    """
    results: list[BenchmarkResult] = []
    for category, expressions in BENCHMARK_EXPRESSIONS.items():
        for expr in expressions:
            try:
                with render_expression(expr) as canvas:
                    score = compute_composite_score(canvas.drawn_elements)
                    depth = _estimate_depth(expr)
                    results.append(
                        BenchmarkResult(
                            expression=expr,
                            category=category,
                            score=score,
                            tree_depth=depth,
                        )
                    )
            except (ValueError, RuntimeError) as e:
                print(f"Failed to benchmark {expr!r}: {e}", file=sys.stderr)
    return results
