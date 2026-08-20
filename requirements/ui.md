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
legend. It displays indicators for the total montant length, the total rail length, the plate
count, and the required montant section (for the current span), and offers toggles to show or
hide the montant and rail overlays on the schema. A
validation error is shown to the user as a readable message. The page is self-contained (its
script and styles are served by the application, no external CDN).

### UI-DRAW-001
**Title:** Draw the outline zone with the mouse
**Status:** validated
**Dependencies:** UI-SCHEMA-001, FUNC-SURFACE-FROMPOINTS-001
**Description:** The schema page offers a draw mode. In draw mode the user clicks points on the
canvas over a one-meter grid to sketch the outline, with a live preview of the current points
and segments. Finishing the sketch (double-click or a finish button) sends the points to
`POST /edges` and fills the editable edge list with the derived lengths and interior angles,
then computes and renders the plan. The user can refine the exact lengths and angles afterward,
and can clear the sketch to start over.

### BOM-UI-PAGE-001
**Title:** Web page to manage BOM lines and review captured prices
**Status:** validated
**Dependencies:** BOM-TECH-API-001
**Description:** The system serves a single, self-contained web page (no external CDN) at its
root path. The page lets the user add a line (reference, designation, quantity, unit) and remove
one, and lists every line with all of its captured prices, the cheapest one highlighted, and the
estimated total (per BOM-FUNC-SUMMARY-001) with the list of lines still missing a price. The page
refreshes from the API rather than holding stale state, so prices captured from the browser
extension appear after a manual refresh.

### BOM-UI-EXTENSION-001
**Title:** Browser extension to capture a store price into the BOM
**Status:** validated
**Dependencies:** BOM-TECH-API-001
**Description:** A Manifest V3 browser extension adds a toolbar action. Clicking it while on a
store's product page opens a popup that: extracts a candidate price from the active page
(common selectors and a currency-pattern fallback) prefilled but editable, offers the current
BOM lines (fetched from the API) to pick which reference the capture belongs to, and on
confirmation posts the capture (`store` defaulted to the page's hostname, editable) to
`POST /api/prices`. The API base URL is configurable via an options page (default
`http://localhost:8001`) since the API runs locally. Extraction failure does not block capture:
the user can enter the price manually.
