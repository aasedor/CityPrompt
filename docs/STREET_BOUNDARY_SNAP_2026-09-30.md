# Street boundary entrance checkpoint

Initiative: `codex/street-boundary-snap`, based on `2b5f4b2b7`.

Drawing near an active site boundary now snaps either route end within 6 m
to a full-width entrance. An 8 cm inward offset avoids point-on-edge ambiguity
and geographic projection round-off. Flexible streets get a short normal
approach followed by the existing rounded bend. The complete rounded footprint
must fit the actual parcel; containment and obstacle checks remain enabled.

Straight-only BRT, tram, canal and bridge layouts remain straight. Their end
can align to an inward waypoint only within the same snap distance. Tight
corners, insufficient approach space, oblique rigid corridors and concave
crossings can still be rejected. No equipment is stretched or clipped.

Globe preview, final creation and the legacy 2D drawing path share the geometry
helper. Saved routes retain their explicit approach controls. Existing saved
roads are unchanged. Explicit public-road extensions retain their current
behavior. Google tiles provide visual context, not a verified road-edge
network: automatic connections to roads inferred from those tiles are not
implemented. The existing **Connect to a public road** control supports a
manually positioned, bounded proposed connection.

## Verification

- PASS: 74 focused Vitest tests across boundary snapping, drawing geometry,
  street snapping/placement, live preview, palette, public-road connections
  and route curves. All catalogue section widths meet all four rectangular
  edges. Tests cover rotated/reversed boundaries, both ends, near-outside
  clicks, concave rejection, interior preservation and rigid corridors.
- PASS: frontend `npm run type-check`; `git diff --check`.
- PASS: ordinary browser selection, drawing, live preview, save, automatic
  compilation and reopening of a Main Street entering the west boundary.
  Disposable project: `d3794c04-7c7b-4b6f-a3ba-fdf6c8af953f`.
  Snapped road: `1e6e0f1e-43b8-4884-bde9-6343aec69e72`.
  Database/API readback reports compiled geometry and a fully contained
  polygon; first control is 0.08 m inside, approach handle 28.83 m inside.
- NOT TESTED in the browser: legacy 2D map and every individual street variant.
  Shared geometry has automated coverage; this is not a new catalogue-wide
  visual acceptance claim. No paid renders, pushes or user-project edits.
- The reused browser session retains earlier park-revision errors. This street
  trial does not certify or modify those unrelated park assets.

Evidence remains outside source control in
`C:/dev-artifacts/CityPrompt/live-street-preview-2026-09-30/`:
`boundary-preview3.png`, `boundary-reopened.png`,
`boundary-snap-readback.json`. Earlier numbered previews include exploratory
clicks; the third preview is the confirmed boundary-snapped route.
