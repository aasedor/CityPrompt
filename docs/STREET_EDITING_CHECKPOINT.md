# Street editing and connected surfaces checkpoint

Phase 5 interaction slice; natural-slope grounding and final presentation remain
release gates. Existing street recipes, catalogue identities and review gates
are retained.

## Behavior

Canonical street placement now uses the existing section resolver's real width.
The selected-street panel exposes type, variant and supported width choices.
A width choice visibly selects a compatible catalogue type before Apply. It
does not stretch traffic lanes/sidewalks or claim arbitrary custom section
engineering. All current eligible variants are checked against that resolver.

Type, properties, original centreline and regenerated buffered footprint save
atomically through the existing revision/undo queue. Existing streets are not
silently migrated. A catalogue section marker must agree with its source and
variant before the simple route editor is used.

Connected surface ownership now supports 45–135 degree approaches, preserving
actual bearings and perpendicular section widths. The same affine frame is used
for the joined pavement, sidewalk, ramps, furniture exclusion and exact triangle
clipping. A remote route bend no longer disables the segment entering a node.
Insufficient arm length, disconnected skew endpoints, inconsistent through-arm
sections and reviewed network atlases are still rejected by this adapter.
This remains conceptual urban-design geometry, not construction design.

## Browser evidence

Separate local project `38dd548d-3d42-4467-b7fc-7d9aa5d17bd3` used an API-created
copy of the benchmark's prepared site only. All four streets were drawn through
the UI: straight, square T, four-way crossing and a bent shared-street approach.

The angled approach initially crossed the sidewalk without a joined surface;
`PHASE5-ANGLED-NETWORK.png` retains that failure. The corrected surface is shown
in `PHASE5-SKEW-AFTER.png`. T, skew and X pedestrian screenshots were visually
inspected for pavement continuity, missing arms and surface overlap.

The main street changed from 16 m local to 20 m collector. In a fresh loaded
session it changed back to 16 m; Undo restored the collector/20 m and Redo the
local/16 m. API evidence retains each state (`phase5-fresh-*`). All four authored
centrelines remained exactly equal. Rebuffering the changed road at its original
width differed by at most 0.00047 m; other footprints remained exactly equal.

The frozen Gold Standard was reopened without authoring changes. Aerial, main
street and intersection captures use the original camera poses and 1600 × 1000
viewport (`PHASE5-GOLD-1600-*`). The prepared site edge and simplified public
realm status remain visible; this checkpoint does not claim improved landscaping
or ground presentation. The 1366 × 768 test views also show the scrollable street
panel without overlapping the view controls.

102 focused frontend tests, TypeScript and targeted ESLint pass. Browser error
count remained unchanged at 442 from the prior asset recovery, and the fresh
session reported no failed resource responses. No paid image/video calls.

## Remaining gates

Acute joins outside the bounded range, curved engineering transitions, natural
slope contacts, full final novice journey and paid source/final image comparison
remain open. Existing shared-street entourage needs the phase 9 presentation
review. An early-load camera initialization can supersede an immediately chosen
view; phase 7/navigation hardening must address it. HMR tests were discarded in
favor of a full-reload persistence test. Generated evidence stays outside Git.
