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
bearing-wall rails, the entretoises under interior plate butt joints, and the plasterboard
pieces colored by kind (full, cut, reused), with a legend. Each outline edge is labelled with
its length in meters, placed just outside the outline. It displays indicators for the total montant length, the total rail length, the plate
count, and the required montant section (for the current span), and offers toggles to show or
hide the montant and rail overlays on the schema. A reset control returns the page to its
initial empty state (no edges, default parameters, blank schema). A
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
then computes and renders the plan. While a segment is being drawn, the length from the last
placed point to the cursor is shown in real time as the mouse moves. Holding Ctrl snaps the
segment being drawn to the nearest 45-degree direction (keeping its length). The cursor is also
magnetic to existing vertices: it snaps onto a nearby vertex, and onto the first vertex to help
close the outline — clicking while snapped to the first vertex closes the sketch. The user can
refine the exact lengths and angles afterward, and can clear the sketch to start over.

### UI-NAV-001
**Title:** Zoom, pan and recenter the schema canvas
**Status:** validated
**Dependencies:** UI-SCHEMA-001
**Description:** The schema canvas can be navigated: the mouse wheel zooms in and out around the
cursor, and dragging pans the view (when not in draw mode). A recenter (fit) control resets the
view so the whole outline fits and is centered. On each new plan the view starts fit and
centered.

### UI-EXPORT-001
**Title:** Export the schema as PNG or SVG
**Status:** validated
**Dependencies:** UI-SCHEMA-001
**Description:** The page can export the current plan schema: a PNG control downloads a raster
image of the fitted schema, and an SVG control downloads a vector image built from the same plan
data (outline, plates, montants, rails, edge labels). Both are generated client-side; nothing is
exported when there is no plan.

### UI-RECT-001
**Title:** Rectangle shortcut for outline entry
**Status:** validated
**Dependencies:** UI-SCHEMA-001
**Description:** The page offers a rectangle shortcut: the user enters a width and a height in
meters and, on applying it, the edge list is filled with the four right-angle edges of that
rectangle (width, height, width, height, each at 90 degrees) and the plan is computed. Non-
positive dimensions are ignored.
