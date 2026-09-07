# Calgary existing-pathway pilot

## Verdict

Keep this as optional site guidance. It improves the physical logic of a scene:
the new park has an approach to an existing mapped route instead of an isolated
loop. It does not improve the asset's textures, planting or photorealism. The
data import was small and straightforward; choosing an entrance and working
around the existing all-or-nothing ground sampler were considerably harder.
Do not make this a prerequisite for drawing or rendering.

## Local trial and evidence

Project: http://127.0.0.1:5178/projects/d2eba9c9-9b6b-4602-801c-49ce29e410b9

Name: Existing paths pilot - Riley Park

This is a conceptual open-lawn test at Riley Park, not a claim that this public
recreation land is available for development. It is a new project and a new
site, separate from the previous Fort Calgary fixture. The bounded pilot tests
one neighbourhood park and one existing route; it does not test a complete
new building/street network or AI image fidelity.

Actual student controls used:

1. Created a project, searched for a site, then selected a resolved street
   address in Edit Project. Initial search for Pearce Estate Park produced no
   chosen address and creation silently used the default downtown location.
   Switched to Riley Park (800 12 Street NW) for open ground.
2. Drew a boundary through More Tools, opened Layers and clicked the new
   **Load nearby Calgary streets & paths** button.
3. Picked and placed a neighbourhood park; used the reshape panel and drag
   controls. The first 40 by 35 m placement/boundary caught nearby tree canopy.
4. Resized to 32 by 30 m, moved onto the clearing, deleted/redrew the test
   boundary and adjusted its two northern vertices. All changes used the UI.
5. Opened Connections, chose the existing shared access route, reviewed its
   suitability and ground level, selected the right edge and a 25% position.
6. Hid the reference overlay. Disabled the connection, saved, captured the
   before view, then used Undo to restore it and captured the after view.
7. Used **Check Direct Capture**, with no paid image/video generation. The
   capture passed at 1600 by 936 with 1.5% park proposal coverage. Existing
   infrastructure was not re-created as proposal geometry.

Read-only API and scene diagnostics supplemented the UI trial. The final
oblique inspection also used the existing development camera-framing helper.
No project or asset was created by a fixture-seeding script for this trial.

Evidence lives outside Git:
`C:/dev-artifacts/CityPrompt/existing-pathway-pilot-2026-09-06/`

- `before-clean.png` / `after-clean.png`: same overhead camera, route disabled
  versus restored, reference overlay hidden in both.
- `context-loaded.png`: mapped routes over the existing Google scene.
- `connected-oblique.png`: final scene from above at an angle.
- `final-audit.json`: saved geometry, reference counts and ground quality.

The snapshot has 34 features (12 road lines, 22 eligible path lines), 38,028
bytes of GeoJSON. It covered the initial site plus a 100 m buffer; subsequent
boundary edits do not silently fetch or move the reference snapshot. The
selected feature is City GLOBALID `{1A5DE245-894D-4602-87D4-9BA24BCB425E}`:
ASSET_TYPE `CONX-ACCESS ROAD`, USAGE_TYPE `MULTIUSE`, WIDTH `3`, MATERIAL
`ASPHALT`, lifecycle `ACTIVE`, operational `OPEN`. The new approach is 2.2 m
wide and approximately 5.4 m from the park edge to the recorded route edge.

## Implemented for this pilot

- One bounded public-service fetch/import action in Layers. All three sources
  must return before one reference layer is saved. Truncated/oversized queries
  fail explicitly; this prototype does not silently import an incomplete page.
- A separate transport adapter preserves identifiers and source attributes,
  deduplicates overlapping routes, filters inactive/closed or explicitly
  private/bridge/tunnel/stair paths, and distinguishes shared access routes.
  Access-road records require pedestrian or multiuse classification.
- Park Connections lists nearby existing pedestrian targets. A saved link
  follows park edits and uses the recorded route width when known. Unknown
  width uses a centreline target; neither case asserts surveyed curb accuracy.
- A new approach must fit inside the site and clear authored objects and mapped
  road centrelines. Existing paths are opt-in; importing context does not
  invent entrances. No automatic motor-road crossings are created.
- Source changes invalidate the derived park snapshot. Hiding an overlay is
  personal display state and does not change the saved connection. Removing
  its layer makes the connection unresolved.
- New geometry uses the existing shared Google ground surface and capture
  ownership. Imported GIS Z values do not replace the vertical datum. Reference
  lines remain excluded from final scene captures.

## Accepted product decision

After reviewing the pilot, the user agreed to keep existing street/path context
optional through student-initiated layer imports. Do not automatically load
transport data or require it for placing, reshaping, saving or rendering a
community. Keep this capability in Layers rather than adding a mandatory step
to the core workflow. Imported references remain separate from design objects;
eligible path connections are an explicit student choice. Arbitrary imported
datasets remain visual references unless a supported adapter interprets them.

The current pilot already follows this opt-in behaviour. Map-click entrance
selection and richer network awareness remain possible follow-ups, not required
next work or approval to expand the pilot.

## Friction found and follow-up priorities

1. **Ground feedback is the largest problem.** The first boundary had no missing
   samples, but tree canopy caused a discontinuity (max slope 7.74, local
   residual 8.35 m). The UI said it needed a clear view, although camera framing
   was not the actual problem. It hid the entire park. A tighter boundary still
   caught a canopy tip; moving its northern edge about a metre resolved it.
   Final ground: 252 samples, max slope 0.110, local residual 0.095 m. Improve
   diagnostic wording and highlight problematic sample locations. A future
   ground-work initiative should investigate resolving safe local patches
   without guessing heights or treating tree tops as bare earth.
2. **Prefer choosing the path on the map.** Dataset names and percentage-based
   entrance controls work, but a student should be able to click an existing
   route and see a suggested entrance. The current dropdown distances are from
   the park centre, while the 8 m limit applies to the approach from its edge;
   clarify this before wider release. Provide a visible preview before saving.
3. **The smaller park becomes visually sparse.** At 32 by 30 m, the current
   catalogue layout reduced to lawn and a loop, with no playground or pavilion.
   Network data cannot fix that. Preserve a modest planting/bench programme in
   compact layouts and harmonize the approach material with the internal path
   as a separate park-layout improvement.
4. **Resolve location explicitly.** A typed but unresolved address should not
   silently create a project downtown. Explain that an address suggestion must
   be selected or let the student deliberately choose a map location.
5. **Keep existing context optional.** Showing every line over an oblique scene
   adds clutter. The overlay is cartographic and uses a common display height;
   it is most useful overhead, not as an assertion of exact surface alignment.
   Hide it for presentation while retaining connection awareness.

## Limits and next bounded trial

This is park-to-existing-path support, not general placement snapping, automatic
building access, imported road construction, citywide routing, accessibility
certification or grade-separated network inference. Road centreline barriers
do not describe complete carriageway widths. Missing bridge/access metadata
cannot be inferred safely from this dataset alone. Student visual review is
still required; new paths outside the site need a separate explicit connection
scope in a future iteration, not expansion of the construction boundary.

Keep the local pilot for review. Next, trial a map-click entrance selector and
clear ground diagnostics before extending the adapter to building entrances.
No catalogue assets or unrelated terrain code were changed or published.

Sources:

- [Street Centreline](https://services1.arcgis.com/AVP60cs0Q9PEA8rH/ArcGIS/rest/services/Street_Centreline/FeatureServer/0)
- [Pathways](https://services1.arcgis.com/AVP60cs0Q9PEA8rH/ArcGIS/rest/services/Pathways_close_view/FeatureServer/0)
- [Sidewalk connections](https://services1.arcgis.com/AVP60cs0Q9PEA8rH/ArcGIS/rest/services/Walkway_Sidewalk_Connections_view/FeatureServer/0)

Street Centreline explicitly references Calgary Open Data Terms. The two public
pathway-service items are owned by `calgary.ca` but lack licence metadata; their
reuse terms should be confirmed before redistributing packaged data.

Validation: targeted reference-layer, connection-editor and park-access tests;
TypeScript check and targeted ESLint. Browser reported no uncaught page errors.
Source changes are on `codex/existing-pathway-pilot`; visual evidence and the
new local database project are separate from Git deliverables.
