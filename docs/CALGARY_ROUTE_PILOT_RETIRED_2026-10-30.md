# Calgary Routes pilot retired

The user requested removal of the Calgary Routes function. Remove the one-click
importer from both Site Context and Map layers, its fetch code and the boundary
failure message that directed students to it. Authored streets/pathways, street
name labels, generic GIS imports and other City data controls remain available.

The shared reference-layer hook excludes saved pilot snapshots from the layer
list and map, even if old personal visibility settings marked them visible.
Identify the snapshots by their City source plus the pilot filename or transport
source markers; do not hide unrelated imports or zoning that shares a City URL.
Retain the original records and decode them only for compatibility with existing
saved park connections. This avoids deleting shared project data or breaking
authored connections while retiring new route imports and their visual overlay.
The legacy connection editor may keep a park's already saved mapped target, but
must not offer other retired routes for new connections. Full snapshot geometry
still supports recovery and collision checks.

Verify filtered layer visibility, saved connection data, generic imports and
street names; run boundary-save recovery and park-access tests. Check Site
Context and Map layers in the browser, along with the absence of old imported
route lines. No backend data migration or live deployment is part of this change.

Verified locally on port 5177: Site Context and Map layers have no Calgary Routes
control or imported route layer; the map retains student streets and pathways.
111 focused frontend cases passed, including connection compatibility and
boundary-save recovery. TypeScript, scoped ESLint, production bundle limits and
independent review passed. The runtime inventory removed only the retired button
source entry; no catalogue asset changed.
