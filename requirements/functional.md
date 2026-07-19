# Functional Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### FUNC-SURFACE-INPUT-001
**Title:** Define and validate the ceiling surface as an ordered sequence of edges
**Status:** validated
**Dependencies:** none
**Description:** The system validates a ceiling outline described as an ordered sequence of
edges. Each edge has a length in meters (2-decimal precision, strictly positive) and an
interior angle in degrees at the corner joining it to the previous edge. The first edge sets
the reference direction; absolute position is not required. A valid outline has at least 3
edges and forms a simple (non-self-intersecting) polygon that closes within a configurable
tolerance. Invalid input returns a specific error identifying the violated rule:
`too_few_edges`, `non_positive_length`, `angle_out_of_range`, `self_intersecting`, or
`not_closed`. Interior angles are expressed in degrees within the open range `(0, 360)`. The
closure tolerance is a caller-supplied parameter in meters (default 0.02).

### FUNC-FRAMING-MONTANTS-001
**Title:** Compute the montant (stud) cut list for a validated outline
**Status:** validated
**Dependencies:** FUNC-SURFACE-INPUT-001
**Description:** Given a validated polygon and a montant spacing (entraxe) in meters, the
system places montants parallel to the first edge (the bearing direction) at the given spacing
across the perpendicular extent of the outline, plus one montant flush to each extremity. For
each montant position it returns the interior spans of the outline measured along the bearing
direction: a convex outline yields one length per position, while a concave outline may yield
several separate pieces at the same position. A non-positive spacing is rejected. Boundary
positions are evaluated just inside the outline so they report the adjacent interior span. The
default spacing is a provisional 0.60 m parameter, to be confirmed against the applicable DTU.

### FUNC-FRAMING-RAILS-001
**Title:** Compute the rail cut list along the bearing walls
**Status:** validated
**Dependencies:** FUNC-SURFACE-INPUT-001, FUNC-FRAMING-MONTANTS-001
**Description:** Given a validated polygon, the system returns the perimeter rails fixed to the
walls that carry the montant ends, that is every outline edge that is not parallel to the
bearing direction (the first edge). Each such edge yields one rail whose length equals the
edge length. Edges parallel to the bearing direction carry no structural rail, since montants
run alongside those walls rather than bearing on them. An edge is treated as parallel when its
extent perpendicular to the bearing direction is below a small epsilon. The result lists each
rail length in outline order.
