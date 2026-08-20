# Technical Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### TECH-API-PLAN-001
**Title:** Expose a /plan HTTP endpoint returning the full material plan
**Status:** validated
**Dependencies:** FUNC-SURFACE-INPUT-001, FUNC-FRAMING-MONTANTS-001, FUNC-FRAMING-RAILS-001, FUNC-PLATE-OPTIM-001
**Description:** The system exposes an HTTP `POST /plan` endpoint. The request body carries the
outline edges (length and interior angle) and optional parameters (closure tolerance, montant
spacing, plate dimensions, minimum offcut, joint mode, joint doubling). Montants are always
forced at the plate joints (plate width). On a valid outline it returns HTTP 200 with the
reconstructed vertices, the montant cut list (each montant flagged if doubled), the rail cut
list, the plate layout (pieces plus summary), a `totals` block giving the total montant length
(counting doubled montants twice), the total rail length, and the plate count, and a `section`
block giving the required span and the selected montant section for single and doubled montants
(null when the span exceeds the catalog). On an outline that fails validation it returns HTTP 400 with the
`SurfaceError` code. Invalid parameter values also return HTTP 400. Responses are JSON.

### BOM-TECH-API-001
**Title:** Expose HTTP endpoints for BOM lines, price capture, and summary
**Status:** validated
**Dependencies:** BOM-FUNC-LINES-001, BOM-FUNC-PRICES-001, BOM-FUNC-SUMMARY-001
**Description:** The system exposes a standalone HTTP API, independent of `ceiling-planner`'s
`/plan` API: `GET /api/lines` (list lines with their captures), `POST /api/lines` (create a
line), `DELETE /api/lines/{line_id}` (remove a line and its captures), `POST /api/prices`
(record a price capture, HTTP 404 with code `unknown_reference` when the reference matches no
line), and `GET /api/summary` (best price per line, estimated total, gaps). Cross-origin requests
are allowed from any origin so the companion browser extension (running under a
`chrome-extension://` origin) can call the API directly; this is an accepted tradeoff for a
tool that is run locally for a single user, not exposed beyond `localhost`. Responses are JSON.
