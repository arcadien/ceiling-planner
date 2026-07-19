"""Montant (stud) cut-list computation for a self-supporting ceiling (FUNC-FRAMING-MONTANTS-001).

Montants run parallel to the first edge of the outline. After outline reconstruction that edge
lies along the x axis, so montants are horizontal scan lines placed at successive y positions
(the perpendicular, cross-span direction). Each montant's length is the interior extent of the
outline along the bearing direction at its position; a concave outline can split a position into
several pieces, each returned as its own montant. An optional joint spacing forces montants at
the plate strip boundaries so a montant always backs a plasterboard joint; those joint montants
may be doubled back-to-back.
"""

from __future__ import annotations

from dataclasses import dataclass

from ceiling_planner.geometry.scanline import interior_spans
from ceiling_planner.geometry.surface import Polygon

_DEFAULT_SPACING_M = 0.60
_BOUNDARY_INSET_M = 1e-9
_MERGE_EPSILON_M = 1e-6


@dataclass(frozen=True)
class Montant:
    """One stud piece: its offset across the span, its length, and whether it is doubled.

    ``doubled`` marks a joint montant placed back-to-back so each adjoining plate has its own
    fixing member; a doubled montant stands for two physical studs at that offset.
    """

    offset_m: float
    length_m: float
    doubled: bool = False


def compute_montants(
    polygon: Polygon,
    spacing_m: float = _DEFAULT_SPACING_M,
    joint_spacing_m: float | None = None,
    double_joints: bool = False,
) -> list[Montant]:
    """Return the montant cut list for ``polygon`` at the given spacing (entraxe).

    Montants are placed at ``y_min``, then every ``spacing_m``, plus one flush to ``y_max``. When
    ``joint_spacing_m`` is given, an extra montant is forced at every interior strip boundary so a
    montant always backs a plasterboard joint; with ``double_joints`` those joint montants are
    doubled. Each position is evaluated just inside the outline so boundary montants report the
    adjacent interior span. A non-positive spacing raises :class:`ValueError`.
    """
    if spacing_m <= 0:
        raise ValueError("spacing_m must be strictly positive")

    ys = [y for _, y in polygon.vertices]
    y_min, y_max = min(ys), max(ys)

    joint_offsets = _joint_offsets(y_min, y_max, joint_spacing_m)
    offsets = _merge_offsets(_montant_offsets(y_min, y_max, spacing_m), joint_offsets)

    montants: list[Montant] = []
    for offset in offsets:
        probe = min(max(offset, y_min + _BOUNDARY_INSET_M), y_max - _BOUNDARY_INSET_M)
        is_joint = _is_close_to_any(offset, joint_offsets)
        doubled = bool(double_joints and is_joint)
        for length in interior_spans(polygon, probe):
            montants.append(Montant(offset_m=offset, length_m=length, doubled=doubled))
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


def _joint_offsets(y_min: float, y_max: float, joint_spacing_m: float | None) -> list[float]:
    """Interior strip-boundary positions (multiples of ``joint_spacing_m`` from ``y_min``)."""
    if joint_spacing_m is None or joint_spacing_m <= 0:
        return []
    offsets: list[float] = []
    step = 1
    while y_min + step * joint_spacing_m < y_max - _BOUNDARY_INSET_M:
        offsets.append(y_min + step * joint_spacing_m)
        step += 1
    return offsets


def _merge_offsets(base: list[float], extra: list[float]) -> list[float]:
    """Sorted union of two offset lists, collapsing values closer than the merge epsilon."""
    merged: list[float] = []
    for offset in sorted(base + extra):
        if not merged or offset - merged[-1] > _MERGE_EPSILON_M:
            merged.append(offset)
    return merged


def _is_close_to_any(value: float, offsets: list[float]) -> bool:
    """True when ``value`` matches one of ``offsets`` within the merge epsilon."""
    return any(abs(value - offset) <= _MERGE_EPSILON_M for offset in offsets)


__all__ = ["Montant", "compute_montants"]
