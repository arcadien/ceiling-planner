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

from ceiling_planner.geometry.scanline import interior_intervals
from ceiling_planner.geometry.surface import Polygon

_DEFAULT_SPACING_M = 0.60
_DEFAULT_MIN_CLEARANCE_M = 0.10
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
    x_start_m: float = 0.0
    x_end_m: float = 0.0


def compute_montants(
    polygon: Polygon,
    spacing_m: float = _DEFAULT_SPACING_M,
    forced_offsets: list[float] | None = None,
    double_joints: bool = False,
    min_clearance_m: float = _DEFAULT_MIN_CLEARANCE_M,
) -> list[Montant]:
    """Return the montant cut list for ``polygon`` at the given spacing (entraxe).

    Montants are placed at ``y_min``, then every ``spacing_m``, plus one flush to ``y_max``. Each
    offset in ``forced_offsets`` (the plate butt-joint positions) adds a montant so a montant
    always backs a plasterboard joint; with ``double_joints`` those joint montants are doubled.
    Each position is evaluated just inside the outline so boundary montants report the adjacent
    interior span. A non-positive spacing raises :class:`ValueError`.
    """
    if spacing_m <= 0:
        raise ValueError("spacing_m must be strictly positive")

    ys = [y for _, y in polygon.vertices]
    y_min, y_max = min(ys), max(ys)

    joint_offsets = [o for o in (forced_offsets or []) if y_min < o < y_max]
    # An entraxe montant within half the spacing of a wall or joint is dropped, so montants
    # never pair up right next to a forced joint montant.
    clearance = max(min_clearance_m, spacing_m / 2)
    offsets = _place_with_clearance(
        _montant_offsets(y_min, y_max, spacing_m), joint_offsets, y_min, y_max, clearance
    )

    montants: list[Montant] = []
    for offset in offsets:
        probe = min(max(offset, y_min + _BOUNDARY_INSET_M), y_max - _BOUNDARY_INSET_M)
        is_joint = _is_close_to_any(offset, joint_offsets)
        doubled = bool(double_joints and is_joint)
        for x_start, x_end in interior_intervals(polygon, probe):
            montants.append(
                Montant(
                    offset_m=offset,
                    length_m=x_end - x_start,
                    doubled=doubled,
                    x_start_m=x_start,
                    x_end_m=x_end,
                )
            )
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


def _place_with_clearance(
    entraxe: list[float],
    joints: list[float],
    y_min: float,
    y_max: float,
    clearance: float,
) -> list[float]:
    """Combine entraxe and joint offsets so no two montants sit closer than ``clearance``.

    The extremities and the forced joints take priority (placed first); an entraxe montant is
    kept only when it clears every already-kept montant.
    """
    # Walls and forced joints are mandatory (a joint must be backed by its own montant); only
    # near-coincident duplicates are collapsed.
    kept: list[float] = []
    for offset in sorted([y_min, y_max, *joints]):
        if not kept or offset - kept[-1] > _MERGE_EPSILON_M:
            kept.append(offset)

    for offset in entraxe:  # entraxe fillers, dropped when too close to a wall or joint montant
        if all(abs(offset - k) >= clearance for k in kept):
            kept.append(offset)
    return sorted(kept)


def _is_close_to_any(value: float, offsets: list[float]) -> bool:
    """True when ``value`` matches one of ``offsets`` within the merge epsilon."""
    return any(abs(value - offset) <= _MERGE_EPSILON_M for offset in offsets)


__all__ = ["Montant", "compute_montants"]
