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
closure tolerance is provided externally (see configuration requirements).
