"""Before/after statistical comparison of layout improvements."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import sys
from dataclasses import dataclass

import numpy as np
from scipy import stats

from ..core import render_expression
from ..core.config import LayoutConfig
from ..metrics.composite import CompositeScore, compute_composite_score


@dataclass
class ComparisonResult:
    """Statistical comparison between two configurations."""

    expressions: list[str]
    scores_before: list[float]
    scores_after: list[float]
    d_cv_before: list[float]
    d_cv_after: list[float]
    wilcoxon_statistic: float
    wilcoxon_pvalue: float
    cohens_d: float
    mean_improvement: float


def _render_and_score(expression: str, config: LayoutConfig | None = None) -> CompositeScore:
    """Render expression with config and return composite score."""
    with render_expression(expression, config) as canvas:
        return compute_composite_score(canvas.drawn_elements)


def _cohens_d(before: np.ndarray, after: np.ndarray) -> float:
    """Compute Cohen's d effect size for paired samples."""
    diff = after - before
    d_mean = np.mean(diff)
    d_std = np.std(diff, ddof=1)
    if d_std < 1e-15:
        return 0.0
    return float(d_mean / d_std)


def compare_before_after(
    expressions: list[str],
    config_before: LayoutConfig | None = None,
    config_after: LayoutConfig | None = None,
) -> ComparisonResult:
    """Compare visualization quality before and after layout changes.

    Uses paired Wilcoxon signed-rank test and Cohen's d effect size.

    Args:
        expressions: COT expressions to evaluate.
        config_before: Configuration for "before" (default layout).
        config_after: Configuration for "after" (improved layout).

    Returns:
        ComparisonResult with statistical measures.
    """
    scores_before: list[float] = []
    scores_after: list[float] = []
    d_cv_before: list[float] = []
    d_cv_after: list[float] = []

    for expr in expressions:
        try:
            sb = _render_and_score(expr, config_before)
            sa = _render_and_score(expr, config_after)
            scores_before.append(sb.score)
            scores_after.append(sa.score)
            d_cv_before.append(sb.spacing.d_cv)
            d_cv_after.append(sa.spacing.d_cv)
        except (ValueError, RuntimeError) as e:
            print(f"Skipping {expr!r}: {e}", file=sys.stderr)

    before_arr = np.array(scores_before)
    after_arr = np.array(scores_after)

    # Wilcoxon signed-rank test
    if len(before_arr) >= 6:
        try:
            stat_result = stats.wilcoxon(after_arr - before_arr, alternative="greater")
            w_stat = float(stat_result.statistic)
            w_pval = float(stat_result.pvalue)
        except ValueError:
            w_stat = 0.0
            w_pval = 1.0
    else:
        w_stat = 0.0
        w_pval = 1.0

    cd = _cohens_d(before_arr, after_arr)
    mean_imp = float(np.mean(after_arr - before_arr)) if len(before_arr) > 0 else 0.0

    return ComparisonResult(
        expressions=expressions,
        scores_before=scores_before,
        scores_after=scores_after,
        d_cv_before=d_cv_before,
        d_cv_after=d_cv_after,
        wilcoxon_statistic=w_stat,
        wilcoxon_pvalue=w_pval,
        cohens_d=cd,
        mean_improvement=mean_imp,
    )
