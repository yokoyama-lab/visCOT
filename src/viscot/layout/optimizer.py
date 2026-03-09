"""Metrics-driven layout optimization using scipy.optimize."""

from __future__ import annotations

import numpy as np

from ..core import render_expression
from ..core.config import LayoutConfig
from ..metrics.composite import compute_composite_score


def _objective(params: np.ndarray, expression: str) -> float:
    """Objective function: negative composite score (to minimize)."""
    config = LayoutConfig(
        a0_margin=float(params[0]),
        a_flip_margin=float(params[1]),
        a2_margin=float(params[2]),
        b0_margin=float(params[3]),
        b_evc_margin=float(params[4]),
        b_flip_margin=float(params[5]),
        beta_margin=float(params[6]),
        c_margin=float(params[7]),
        c_circ_margin=float(params[8]),
        c_height_spacing_factor=float(params[9]),
    )
    try:
        with render_expression(expression, config) as canvas:
            score = compute_composite_score(canvas.drawn_elements)
            return -score.score  # minimize negative score
    except (ValueError, RuntimeError):
        return 1e6  # penalty for invalid configs


def optimize_layout(
    expression: str,
    initial_config: LayoutConfig | None = None,
    max_iter: int = 100,
) -> LayoutConfig:
    """Optimize layout margins using Nelder-Mead.

    Args:
        expression: COT tree notation string.
        initial_config: Starting configuration. Defaults to DEFAULT_CONFIG.
        max_iter: Maximum optimization iterations.

    Returns:
        Optimized LayoutConfig.
    """
    from scipy.optimize import minimize

    if initial_config is None:
        initial_config = LayoutConfig()

    x0 = np.array([
        initial_config.a0_margin,
        initial_config.a_flip_margin,
        initial_config.a2_margin,
        initial_config.b0_margin,
        initial_config.b_evc_margin,
        initial_config.b_flip_margin,
        initial_config.beta_margin,
        initial_config.c_margin,
        initial_config.c_circ_margin,
        initial_config.c_height_spacing_factor,
    ])

    result = minimize(
        _objective,
        x0,
        args=(expression,),
        method="Nelder-Mead",
        options={"maxiter": max_iter, "xatol": 0.01, "fatol": 0.1},
    )

    opt = result.x
    return LayoutConfig(
        a0_margin=float(opt[0]),
        a_flip_margin=float(opt[1]),
        a2_margin=float(opt[2]),
        b0_margin=float(opt[3]),
        b_evc_margin=float(opt[4]),
        b_flip_margin=float(opt[5]),
        beta_margin=float(opt[6]),
        c_margin=float(opt[7]),
        c_circ_margin=float(opt[8]),
        c_height_spacing_factor=float(opt[9]),
    )
