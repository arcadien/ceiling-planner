"""Rail cut-list computation for a self-supporting ceiling (FUNC-FRAMING-RAILS-001).

Rails are fixed flush to the walls around the whole perimeter: every outline edge yields one
rail equal to its length, so the rails follow the entire outline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ceiling_planner.geometry.surface import Polygon


@dataclass(frozen=True)
class Rail:
    """One rail piece fixed flush to a wall, with its length along that wall."""

    length_m: float


def compute_rails(polygon: Polygon) -> list[Rail]:
    """Return one :class:`Rail` per outline edge, in outline order, equal to the edge length."""
    vertices = polygon.vertices
    n = len(vertices)
    rails: list[Rail] = []

    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        rails.append(Rail(length_m=math.hypot(x2 - x1, y2 - y1)))

    return rails


__all__ = ["Rail", "compute_rails"]
