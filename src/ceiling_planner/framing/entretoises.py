"""Entretoise (cross-brace) computation for interior plate butt joints.

Requirement: FUNC-FRAMING-ENTRETOISE-001.

Montants run parallel to the bearing direction, so they carry the plate edges parallel to them
but not the butt joints (seams perpendicular to the montants). An interior butt joint — a
boundary shared by two contiguous plate pieces within a strip — is therefore unsupported unless
it lies against a wall. This module places one entretoise along every such joint, spanning the
strip band, so both plate edges are carried.
"""

from __future__ import annotations

from dataclasses import dataclass

from ceiling_planner.plates.optimizer import PlatePiece

_EPSILON_M = 1e-9


@dataclass(frozen=True)
class Entretoise:
    """A cross-brace along a plate butt joint: its bearing-direction position, band and length."""

    x_m: float
    y_min_m: float
    y_max_m: float
    length_m: float


def compute_entretoises(pieces: list[PlatePiece]) -> list[Entretoise]:
    """Return one entretoise per interior butt joint in ``pieces``.

    A butt joint is a boundary shared by two contiguous pieces within the same strip. Boundaries
    at the outline (walls) and gaps between disjoint pieces yield no entretoise.
    """
    by_strip: dict[int, list[PlatePiece]] = {}
    for piece in pieces:
        by_strip.setdefault(piece.strip_index, []).append(piece)

    entretoises: list[Entretoise] = []
    for strip_pieces in by_strip.values():
        ordered = sorted(strip_pieces, key=lambda p: p.x_start_m)
        for left, right in zip(ordered, ordered[1:], strict=False):
            if abs(left.x_end_m - right.x_start_m) <= _EPSILON_M:  # contiguous → interior joint
                entretoises.append(
                    Entretoise(
                        x_m=left.x_end_m,
                        y_min_m=left.y_min_m,
                        y_max_m=left.y_max_m,
                        length_m=left.y_max_m - left.y_min_m,
                    )
                )
    return entretoises


__all__ = ["Entretoise", "compute_entretoises"]
