# UI Requirements

<!-- Requirements are added here during Phase 2 of the RBD workflow. -->
<!-- Format: req(ID): title -->

### UI-SCHEMA-001
**Title:** Web page to enter the outline and display the plan schema
**Status:** validated
**Dependencies:** TECH-API-PLAN-001
**Description:** The system serves a single web page at the root path. The page lets the user
add and remove outline edges (length and interior angle), set the parameters, and request a
plan. On a successful response it draws a schema on a canvas: the outline, the montants, the
bearing-wall rails, and the plasterboard pieces colored by kind (full, cut, reused), with a
legend and the plate count. A validation error is shown to the user as a readable message. The
page is self-contained (its script and styles are served by the application, no external CDN).
