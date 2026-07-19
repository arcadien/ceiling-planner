"""Plasterboard cutting optimization (FUNC-PLATE-OPTIM-001).

The outline is covered with plates laid in strips one plate-width wide along the bearing
direction (the x axis after outline reconstruction). Each strip's interior runs are filled with
plates of the plate length, consumed end to end; the offcut from a cut plate is carried to the
next run when it is long enough to be usable, otherwise it is discarded as waste. The plan
records every placed piece so the layout can be drawn on the schema.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ceiling_planner.geometry.scanline import interior_intervals
from ceiling_planner.geometry.surface import Polygon

_DEFAULT_PLATE_LENGTH_M = 2.50
_DEFAULT_PLATE_WIDTH_M = 1.20
_DEFAULT_MIN_OFFCUT_M = 0.30
_EPSILON_M = 1e-9

FULL = "full"
CUT = "cut"
REUSED = "reused"


@dataclass(frozen=True)
class PlatePiece:
    """One placed plate piece, positioned for drawing on the layout schema.

    ``kind`` is ``"full"`` (a whole plate used end to end), ``"cut"`` (a plate cut to length,
    leaving an offcut), or ``"reused"`` (a previously cut offcut placed at a run start).
    """

    strip_index: int
    y_min_m: float
    y_max_m: float
    x_start_m: float
    x_end_m: float
    kind: str


@dataclass(frozen=True)
class PlatePlan:
    """Cutting layout: the placed pieces plus purchase and waste summary."""

    plate_count: int
    covered_length_m: float
    waste_length_m: float
    pieces: list[PlatePiece]


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

    pieces: list[PlatePiece] = []
    plate_count = 0
    offcut = 0.0

    for strip_index, (y_min, y_max, intervals) in enumerate(_strips(polygon, plate_width_m)):
        for x_start, x_end in intervals:
            cursor = x_start
            while cursor < x_end - _EPSILON_M:
                run_left = x_end - cursor
                if offcut >= min_offcut_m:
                    take = min(offcut, run_left)
                    pieces.append(
                        PlatePiece(strip_index, y_min, y_max, cursor, cursor + take, REUSED)
                    )
                    cursor += take
                    offcut -= take
                    if offcut < min_offcut_m:
                        offcut = 0.0  # remaining stub too short to reuse — scrap
                    continue

                plate_count += 1
                if plate_length_m >= run_left:
                    kind = FULL if plate_length_m - run_left <= _EPSILON_M else CUT
                    pieces.append(PlatePiece(strip_index, y_min, y_max, cursor, x_end, kind))
                    offcut = plate_length_m - run_left
                    cursor = x_end
                else:
                    pieces.append(
                        PlatePiece(
                            strip_index, y_min, y_max, cursor, cursor + plate_length_m, FULL
                        )
                    )
                    cursor += plate_length_m
                    offcut = 0.0

    covered_length_m = math.fsum(p.x_end_m - p.x_start_m for p in pieces)
    waste_length_m = plate_count * plate_length_m - covered_length_m
    return PlatePlan(
        plate_count=plate_count,
        covered_length_m=covered_length_m,
        waste_length_m=waste_length_m,
        pieces=pieces,
    )


def _strips(
    polygon: Polygon, strip_width_m: float
) -> list[tuple[float, float, list[tuple[float, float]]]]:
    """Each strip as ``(y_min, y_max, intervals)`` where intervals are interior (x_start, x_end)."""
    ys = [y for _, y in polygon.vertices]
    y_min, y_max = min(ys), max(ys)
    strip_count = max(1, math.ceil((y_max - y_min) / strip_width_m))

    strips: list[tuple[float, float, list[tuple[float, float]]]] = []
    for i in range(strip_count):
        band_min = y_min + i * strip_width_m
        band_max = min(y_min + (i + 1) * strip_width_m, y_max)
        midline = min(max((band_min + band_max) / 2, y_min + _EPSILON_M), y_max - _EPSILON_M)
        strips.append((band_min, band_max, interior_intervals(polygon, midline)))
    return strips


__all__ = ["CUT", "FULL", "REUSED", "PlatePiece", "PlatePlan", "optimize_plates"]
