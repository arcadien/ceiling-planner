"""Plasterboard cutting optimization (FUNC-PLATE-OPTIM-001).

The outline is covered with plates laid in strips one plate-width wide along the bearing
direction (the x axis after outline reconstruction). Each strip's run length is filled with
plates of the plate length, consumed end to end; the offcut from a cut plate is carried to the
next run when it is long enough to be usable, otherwise it is discarded as waste.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ceiling_planner.geometry.scanline import interior_spans
from ceiling_planner.geometry.surface import Polygon

_DEFAULT_PLATE_LENGTH_M = 2.50
_DEFAULT_PLATE_WIDTH_M = 1.20
_DEFAULT_MIN_OFFCUT_M = 0.30
_EPSILON_M = 1e-9


@dataclass(frozen=True)
class PlatePlan:
    """Outcome of the optimization: plates to buy, length covered, and length wasted."""

    plate_count: int
    covered_length_m: float
    waste_length_m: float


def optimize_plates(
    polygon: Polygon,
    plate_length_m: float = _DEFAULT_PLATE_LENGTH_M,
    plate_width_m: float = _DEFAULT_PLATE_WIDTH_M,
    min_offcut_m: float = _DEFAULT_MIN_OFFCUT_M,
) -> PlatePlan:
    """Return the :class:`PlatePlan` covering ``polygon`` with offcut reuse across strips.

    ``plate_length_m`` and ``plate_width_m`` must be strictly positive and ``min_offcut_m`` must
    be non-negative, otherwise :class:`ValueError` is raised.
    """
    if plate_length_m <= 0 or plate_width_m <= 0:
        raise ValueError("plate dimensions must be strictly positive")
    if min_offcut_m < 0:
        raise ValueError("min_offcut_m must be non-negative")

    runs = _strip_runs(polygon, plate_width_m)

    plate_count = 0
    offcut = 0.0
    for run in runs:
        remaining = run
        if offcut >= min_offcut_m:
            take = min(offcut, remaining)
            remaining -= take
            offcut -= take
        if offcut < min_offcut_m:
            offcut = 0.0  # too short to reuse — scrap
        while remaining > _EPSILON_M:
            plate_count += 1
            if plate_length_m >= remaining:
                offcut = plate_length_m - remaining
                remaining = 0.0
            else:
                remaining -= plate_length_m
                offcut = 0.0

    covered_length_m = math.fsum(runs)
    waste_length_m = plate_count * plate_length_m - covered_length_m
    return PlatePlan(
        plate_count=plate_count,
        covered_length_m=covered_length_m,
        waste_length_m=waste_length_m,
    )


def _strip_runs(polygon: Polygon, strip_width_m: float) -> list[float]:
    """Run length to cover in each plate-width strip, measured along the bearing direction."""
    ys = [y for _, y in polygon.vertices]
    y_min, y_max = min(ys), max(ys)
    strip_count = max(1, math.ceil((y_max - y_min) / strip_width_m))

    runs: list[float] = []
    for i in range(strip_count):
        midline = y_min + (i + 0.5) * strip_width_m
        midline = min(max(midline, y_min + _EPSILON_M), y_max - _EPSILON_M)
        runs.append(math.fsum(interior_spans(polygon, midline)))
    return runs


__all__ = ["PlatePlan", "optimize_plates"]
