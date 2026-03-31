"""Layout configuration — centralizes magic numbers from flow.py."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LayoutConfig:
    """All tunable layout parameters in one place."""

    # A0
    a0_margin: float = 0.5

    # A_Flip (a+, a-)
    a_flip_margin: float = 0.5

    # A2
    a2_margin: float = 0.5

    # B0 (B0+, B0-)
    b0_margin: float = 0.5

    # B_Evc (b++, b--)
    b_evc_margin: float = 0.5

    # B_Flip (b+-, b-+)
    b_flip_margin: float = 0.5

    # Beta (B+, B-)
    beta_margin: float = 0.5
    beta_min_circ: float = 7.0

    # C (c+, c-)
    c_margin: float = 1.0
    c_circ_margin: float = 0.5
    c_height_spacing_factor: float = 3.0  # extra arc-length per unit height
    c_min_child_height: float = 0.3  # fallback height when C has no children
    c_spline_clearance_factor: float = 1.0  # additional width per unit height to prevent crossings
    c_child_start_offset: float = 1.5  # min padding (× height) to separate child C from parent C start

    # B0 first-child offset
    b0_first_child_offset: float = 0.3
    b0_min_inner_radius: float = 2.0  # minimum radius after subtracting child height

    # Spline interpolation points
    spline_num_points: int = 100

    # Arrow style
    arrow_tail_width: float = 0.6
    arrow_shrink_factor: float = 0.5

    # Line width
    line_width: float = 1.5

    # axvspan margin ratio
    axvspan_margin_ratio: float = 1.1


# Global default config instance
DEFAULT_CONFIG = LayoutConfig()
