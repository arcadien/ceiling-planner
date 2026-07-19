# Technical Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### TECH-API-PLAN-001
**Title:** Expose a /plan HTTP endpoint returning the full material plan
**Status:** validated
**Dependencies:** FUNC-SURFACE-INPUT-001, FUNC-FRAMING-MONTANTS-001, FUNC-FRAMING-RAILS-001, FUNC-PLATE-OPTIM-001
**Description:** The system exposes an HTTP `POST /plan` endpoint. The request body carries the
outline edges (length and interior angle) and optional parameters (closure tolerance, montant
spacing, plate dimensions, minimum offcut). On a valid outline it returns HTTP 200 with the
reconstructed vertices, the montant cut list, the rail cut list, and the plate layout (pieces
plus summary). On an outline that fails validation it returns HTTP 400 with the `SurfaceError`
code. Invalid parameter values also return HTTP 400. Responses are JSON.
