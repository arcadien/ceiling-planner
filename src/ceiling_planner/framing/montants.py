"""Montant (stud) cut-list computation for a self-supporting ceiling (FUNC-FRAMING-MONTANTS-001).

Montants run parallel to the first edge of the outline. After outline reconstruction that edge
lies along the x axis, so montants are horizontal scan lines placed at successive y positions
(the perpendicular, cross-span direction). Each montant's length is the interior extent of the
outline along the bearing direction at its position; a concave outline can split a position into
several pieces, each returned as its own montant.
"""

from __future__ import annotations

from dataclasses import dataclass

from ceiling_planner.geometry.scanline import interior_spans
from ceiling_planner.geometry.surface import Polygon

_DEFAULT_SPACING_M = 0.60
_BOUNDARY_INSET_M = 1e-9


@dataclass(frozen=True)
class Montant:
    """One stud piece: its offset across the span and its length along the bearing direction."""

    offset_m: float
    length_m: float


def compute_montants(polygon: Polygon, spacing_m: float = _DEFAULT_SPACING_M) -> list[Montant]:
    """Return the montant cut list for ``polygon`` at the given spacing (entraxe).

    Montants are placed at ``y_min``, then every ``spacing_m``, plus one flush to ``y_max``.
    Each position is evaluated just inside the outline so boundary montants report the
    adjacent interior span. A non-positive spacing raises :class:`ValueError`.
    """
    if spacing_m <= 0:
        raise ValueError("spacing_m must be strictly positive")

    ys = [y for _, y in polygon.vertices]
    y_min, y_max = min(ys), max(ys)

    offsets = _montant_offsets(y_min, y_max, spacing_m)

    montants: list[Montant] = []
    for offset in offsets:
        probe = min(max(offset, y_min + _BOUNDARY_INSET_M), y_max - _BOUNDARY_INSET_M)
        for length in interior_spans(polygon, probe):
            montants.append(Montant(offset_m=offset, length_m=length))
    return montants


def _montant_offsets(y_min: float, y_max: float, spacing_m: float) -> list[float]:
    """Positions from ``y_min`` every ``spacing_m`` up to (and including) ``y_max``.

    The stepped positions stop short of ``y_max`` by a small epsilon so floating-point noise in
    a reconstructed extent cannot add a montant that duplicates the flush far-wall one.
    """
    offsets: list[float] = []
    step = 0
    while y_min + step * spacing_m < y_max - _BOUNDARY_INSET_M:
        offsets.append(y_min + step * spacing_m)
        step += 1
    offsets.append(y_max)
    return offsets


__all__ = ["Montant", "compute_montants"]
