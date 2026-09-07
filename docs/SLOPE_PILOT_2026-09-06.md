# Slopes: first pilot and implementation direction

## Student experience

Students should choose how their development meets a hillside without needing to
manage a terrain mesh. The intended progression is:

1. Inspect existing terrain without changing the design.
2. Keep buildings upright on level pads; allow larger sites to have several
   terraces instead of flattening the entire boundary.
3. Let landscape and ordinary paths follow appropriate grades; keep playgrounds,
   courts and other level amenities on local pads.
4. Connect street, sidewalk, park and building entrance anchors using explicit
   grades and landings. Highlight excessive grades or an unconnected entrance in
   the report rather than inventing access or declaring a design impossible.
5. Render the resulting saved geometry. AI finishing must not reconstruct the
   slope, move amenities or turn retaining edges into new buildings.

Existing Google tiles are context and visible-surface measurements, not a surveyed
bare-earth model. Future imported terrain must carry its vertical reference.

## Implemented in this pilot

Branch `codex/slope-retaining-edge-pilot`, based on `73184906b`.

- Opening **Review ground** inspects the original Google surface while leaving a
  prepared site's ground and buildings in place. Inspection does not write data
  or change capture readiness. Its extra sampling camera is released on close.
- Optional **Add retaining edges · slope pilot** uses boundary heights interpolated
  from two repeatable measured grid passes. Every contributing support sample
  must be finite and agree within the existing 0.08 m repeatability tolerance.
  Interior discontinuities can still make ground-following unavailable; that
  decision is separate from saving a reviewed concept edge profile.
- The profile is saved on the site boundary as `terrain_edge_profile`: version,
  Google visible-surface source, WGS84 ellipsoid reference, exact boundary ring
  and ordered `[longitude, latitude, height]` samples. No missing heights are filled.
- Retaining faces connect the proposed level to the saved profile for both cut
  and fill. Geometry splits at grade crossings, respects concave notches and is
  disposed when replaced. The former horizontal seam overlap is removed when
  retaining faces are present.
- Editing the boundary invalidates old profiles; stale walls are hidden and the
  ground review explains how to rebuild them. Changing only the prepared level
  reuses the saved existing-ground profile.
- The UI reports maximum boundary cut/fill heights, not earthwork volumes. The
  pilot bounds perimeter geometry to 512 samples, spaced at most 2.5 m along
  each edge. Unsupported boundaries receive an explanation and can still use
  an ordinary level surface.
- Existing projects have no retaining edges unless selected. Buildings, parks,
  streets and their current prepared-level logic are otherwise unchanged.

## Live trial

Isolated local frontend at `http://127.0.0.1:5178`, backend 8002; original checkout
and port 5174 were preserved. Signed in as the existing local smoke-test student.

Hillside project B: `7e314bbc-cebd-4d9c-a8fe-a67cf48e7622`.

- Inspected without switching off redevelopment mode.
- Saved 63 edge measurements at the existing 1052.5 m proposed level.
- Boundary cut: up to 1.99 m. Boundary fill: up to 1.81 m. These are relative to
  the sampled visible mesh, not survey quantities.
- Inspected near views: uphill faces and the low downhill edge are visible.
  Trees and changing Google tile detail still complicate visual assessment.
- Undo and redo worked. Reopening retained all 63 samples and the proposed level.
- Free exact 3D export succeeded with the new faces. No paid AI image, video or
  street-view renders were run. App balance remained 9,445.
- No uncaught browser errors observed. Undoing the boundary update also reframed
  the camera, so screenshots are not a registered before/after comparison.

Evidence remains outside Git in
`C:/dev-artifacts/CityPrompt/student-beta-2026-09-06/`, particularly
`slope-pilot-reopened-close.png` and `slope-pilot-detail.png`.
Local project data is not part of the source commit.

## Verification

- 45 tests passed across GroundReviewPanel, preparedSiteEdges,
  SharedSiteGroundProvider, sharedSiteGround, sharedGroundCapture,
  sitePreparationSurface and groundReview.
- The 9 affected edge/UI tests passed again after the final input-limit message.
- TypeScript and targeted ESLint passed.
- No backend changes; existing zone-property persistence was exercised through
  the browser and verified after reloading.

## Limits and next pilot

These are concept faces, not engineered walls. The pilot does not design footings,
drainage, fall protection, accessible entrances or earthwork volumes. Do not label
the whole site construction-ready or automatically place entrances across walls.
Interpolation between grid samples and later Google LOD changes can leave local
contact differences. Saved profiles intentionally do not shift with camera motion.

The next bounded pilot should add **two user-defined terraces and one explicit
connection** on this hillside:

- Introduce one saved proposed-ground resolver shared by buildings, parks, roads,
  pathways, previews and capture. A zone's pad elevation must take precedence over
  the site default in every consumer, including compiled assets and masks.
- Keep terrace boundaries inside the site and protect neighbouring objects from
  accidental regrading. Show the proposed terrain before committing it.
- Connect two known entrance/sidewalk anchors with an editable path profile;
  derive length and grade from geometry and flag missing or impractical access.
- Check moved/resized buildings, cut/fill contacts, save/reopen, undo/redo and exact
  captures from both uphill and downhill viewpoints before scaling to parks and
  streets. Add advisory report findings using these same measurements.

The single level retaining-edge pilot is a foundation for that workflow, not its
completion. No catalogue expansion, main push or deployment was performed.
