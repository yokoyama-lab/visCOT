"""M2: Streamline spacing metric."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..core.canvas import DrawnElement
from .sampling import elements_to_polylines


@dataclass
class SpacingResult:
    """Result of spacing analysis."""

    d_min: float
    d_mean: float
    d_std: float
    d_cv: float  # coefficient of variation = std / mean


def compute_spacing(elements: list[DrawnElement]) -> SpacingResult:
    """Compute pairwise minimum distances between drawn elements.

    Lower d_cv means more uniform spacing, corresponding to
    the "appropriate distance" criterion from the thesis.

    Returns:
        SpacingResult with d_min, d_mean, d_std, d_cv.
    """
    polylines = elements_to_polylines(elements)
    if len(polylines) < 2:
        return SpacingResult(d_min=0.0, d_mean=0.0, d_std=0.0, d_cv=0.0)

    # Compute bounding box diagonal for normalization
    all_points = np.vstack(polylines)
    bbox_min = all_points.min(axis=0)
    bbox_max = all_points.max(axis=0)
    diag = np.linalg.norm(bbox_max - bbox_min)
    if diag < 1e-12:
        return SpacingResult(d_min=0.0, d_mean=0.0, d_std=0.0, d_cv=0.0)

    # Pairwise minimum distances
    min_dists: list[float] = []
    for i in range(len(polylines)):
        for j in range(i + 1, len(polylines)):
            # Compute all pairwise distances between points
            diff = polylines[i][:, np.newaxis, :] - polylines[j][np.newaxis, :, :]
            dists = np.linalg.norm(diff, axis=2)
            min_dists.append(float(np.min(dists)))

    dists_arr = np.array(min_dists) / diag  # normalize by bbox diagonal

    d_min = float(np.min(dists_arr))
    d_mean = float(np.mean(dists_arr))
    d_std = float(np.std(dists_arr))
    d_cv = d_std / d_mean if d_mean > 1e-12 else 0.0

    return SpacingResult(d_min=d_min, d_mean=d_mean, d_std=d_std, d_cv=d_cv)
