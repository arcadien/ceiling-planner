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

### FUNC-SURFACE-FROMPOINTS-001
**Title:** Derive the outline edge sequence from ordered vertices
**Status:** validated
**Dependencies:** FUNC-SURFACE-INPUT-001
**Description:** Given an ordered list of at least 3 outline vertices `(x, y)` in meters, the
system derives the edge sequence used by the validator: each edge's length is the distance to
the next vertex, and its interior angle is the polygon's interior angle at the vertex that
starts it. Clockwise input is normalized to counter-clockwise so convex corners yield angles
below 180 degrees. The derived sequence round-trips: validating it reconstructs the same shape
up to translation and rotation. Fewer than 3 vertices are rejected. The capability is exposed
at `POST /edges`, returning the derived edges as JSON.

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
An optional joint spacing forces an extra montant at every interior strip boundary (each
multiple of the joint spacing from the near extremity) so a montant always backs a plasterboard
joint; when the joint spacing is unset, no joints are forced. Joint montants may be doubled
back-to-back (each adjoining plate then screws to its own montant); doubling is off by default,
and each montant reports whether it is doubled.

### FUNC-FRAMING-RAILS-001
**Title:** Compute the perimeter rail cut list
**Status:** validated
**Dependencies:** FUNC-SURFACE-INPUT-001, FUNC-FRAMING-MONTANTS-001
**Description:** Given a validated polygon, the system returns the perimeter rails fixed flush
to the walls: every outline edge carries one rail whose length equals the edge length, so the
rails follow the whole outline. The result lists each rail length in outline order.

### FUNC-FRAMING-SECTION-001
**Title:** Select the montant section from the required span
**Dependencies:** FUNC-FRAMING-MONTANTS-001
**Status:** validated
**Description:** Given a required free span in meters and whether the montants are doubled
back-to-back (accolés), the system selects the lightest montant section whose maximum admissible
span covers the required span, from a catalog of PRÉGYMÉTAL sections (DTU 25.41 / Siniat
reference): M48-35 (2.00 m single, 2.35 m doubled), M70-35 (2.55 / 3.15), M90-35 (3.05 / 3.80),
M100-50 (3.60 / 4.40). The catalog is the default and may be overridden, and its entries are
ordered from lightest to strongest. If no section covers the span, the system reports that the
span exceeds the catalog, meaning an intermediate support or a longer-span system is required.
The required span for a plan is the longest montant length.

### FUNC-PLATE-OPTIM-001
**Title:** Produce the plasterboard cutting layout with a selectable joint pattern
**Status:** validated
**Dependencies:** FUNC-SURFACE-INPUT-001
**Description:** Given a validated polygon and plate dimensions (default 2.50 m by 1.20 m), the
system produces a cutting layout, splitting the perpendicular extent into strips one plate-width
wide and laying plates end to end along each strip's interior runs. A `joint_mode` parameter
selects the seam pattern: `reuse` (default) carries the offcut of a cut plate to the next run
when it is at least a minimum usable length (default 0.30 m), minimizing waste but leaving
irregular seams; `aligned` restarts a full plate in each strip so seams line up on a regular
grid; `running_bond` offsets each strip by a fixed stagger (default half a plate length) for
regular staggered seams. `aligned` and `running_bond` do not reuse offcuts and so accept more
waste. Non-positive dimensions and an unknown `joint_mode` are rejected. The layout lists every
placed piece — strip band, bearing-direction extent, and kind (`full`, `cut`, or `reused`) — and
summarizes the plate count, the covered length, and the wasted length.

### BOM-FUNC-LINES-001
**Title:** Maintain a bill of materials as a list of referenced lines
**Status:** validated
**Dependencies:** none
**Description:** The system maintains a bill of materials (BOM) as an ordered set of lines, each
identified by a supplier reference (free-text, unique within the BOM, matched case-insensitively
and trimmed of surrounding whitespace) and carrying a designation, a quantity (strictly
positive), and a unit (default `pcs`). Lines are added, listed, and removed independently of any
price information. A non-positive quantity, an empty reference, or a reference that already
exists in the BOM is rejected, so price captures can be matched to exactly one line.

### BOM-FUNC-PRICES-001
**Title:** Capture a store price quote for a BOM line
**Status:** validated
**Dependencies:** BOM-FUNC-LINES-001
**Description:** The system records a price capture for a BOM line: a store name, a price
(strictly positive, in a currency defaulting to EUR), a source URL, and a capture timestamp. A
capture is matched to a BOM line by reference (case-insensitive, trimmed); if no line carries
that reference, the capture is rejected with an `unknown_reference` error rather than silently
creating one, so the caller can prompt for the missing line first. A line may accumulate
captures from several stores and several captures from the same store over time (e.g. price
changes); all captures are kept, not overwritten.

### BOM-FUNC-SUMMARY-001
**Title:** Summarize the best captured price per line and the estimated total
**Status:** validated
**Dependencies:** BOM-FUNC-LINES-001, BOM-FUNC-PRICES-001
**Description:** Given the current BOM and its price captures, the system reports, for each line,
every captured price sorted ascending and which one is cheapest (store, price, url). It computes
an estimated total by summing, for each line, quantity times its cheapest captured price, and
separately lists the lines that have no captured price yet (excluded from the total, reported as
gaps so the user knows the estimate is partial).
