"""Rail cut-list computation for a self-supporting ceiling (FUNC-FRAMING-RAILS-001).

Rails are fixed to the walls that carry the montant ends. Montants run parallel to the first
edge (the bearing direction, along the x axis after outline reconstruction), so any outline
edge with a non-zero extent along y is a bearing wall and receives a rail equal to its length.
Edges parallel to the bearing direction carry no structural rail.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ceiling_planner.geometry.surface import Polygon

_PARALLEL_EPSILON_M = 1e-9


@dataclass(frozen=True)
class Rail:
    """One rail piece fixed to a bearing wall, with its length along that wall."""

    length_m: float


def compute_rails(polygon: Polygon) -> list[Rail]:
    """Return the rails for every outline edge not parallel to the bearing direction.

    Edges are visited in outline order; each edge whose perpendicular extent exceeds a small
    epsilon yields one :class:`Rail` equal to the edge length.
    """
    vertices = polygon.vertices
    n = len(vertices)
    rails: list[Rail] = []

    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        if abs(y2 - y1) <= _PARALLEL_EPSILON_M:
            continue  # parallel to the bearing direction — montants run alongside, no rail
        rails.append(Rail(length_m=math.hypot(x2 - x1, y2 - y1)))

    return rails


__all__ = ["Rail", "compute_rails"]
