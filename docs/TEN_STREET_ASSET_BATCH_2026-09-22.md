# Ten more streets — native asset batch

Initiative: `codex/ten-street-asset-batch`, based on `eb7ec7c20`.
User requested ten more streets, continuing the offline asset workflow with
browser testing deferred. No production catalogue/seed/runtime edits or push.

## Finite scope and pilot

Ten distinct reference-informed concepts: Neighbourhood Main Street, Protected
Cycle Avenue, Planted Service Lane, Transit Stop Street, Pedestrian Market
Street, Ruelle Verte Community Alley, Heritage Mews Lane, Waterfront Timber
Boardwalk, Playful School Street, Grand Promenade Boulevard.

Authoritative source images were inspected from
`frontend/public/archetypes/streets` in the primary local repository. Each exact
image is copied and hash-locked into its external package. Recipes separate
observed features from adaptations; dimensions are original concept sections,
not dimensions inferred as facts from a perspective image. Neighbouring
buildings, people and vehicles are omitted. Existing student IDs are untouched.

All ten dry runs passed before the main-street pilot. Four recipe tests passed.
Pilot: `C:/dev-artifacts/CityPrompt/streets-ten-2026-09-22/pilot/main_street`.
The actual exported/reimported GLB passed 1,422 material-aware clear-route rays,
18 endpoint rays, eight tree-root/well checks, native module envelopes and
ground contacts. Agent visual review of aerial, top, detail and street views
passed for the concept. Independent human and browser review remain pending.

Remaining nine: bounded native build and review after the pilot checkpoint.
Final accepted paths, hashes and any revisions will be recorded here and in the
companion JSON before completion.

## Reusable method

- Metric band recipes own every floor cell. Fine stone/brick/cobble/deck patterns
  preserve world-space phase across cell partitions. No coplanar slab overlays.
- Furnishing bays preserve clear walks, cycle tracks and carriageways. Every
  hardscape tree goes through the shared physical tree-well preparation.
- Fourteen origin-based amenity types include lanterns, bollards, a glazed stop
  shelter, stop pole, market stall, fountain, planted trellis, timber fence,
  boardwalk guard, hammock and kiosk, plus three existing cafe/seating models.
- Render actual reimported GLBs, audit module bytes/envelopes/supports, retain
  exact image references and per-candidate pending runtime review forms.
- These straight, level fixtures are not route meshes. Runtime must rebuild
  bands on the shared sampled centreline/ground, place rigid modules at native
  scale and let the street network own junctions, crossings, ramps and endpoints.
  Never bend, stretch or repeat the full preview assembly.

Run `tools/public_realm_assets/run_street_batch.py` with an explicit `--kinds`
list, `--blender`, `--kit`, `--reference-root` and fresh `--output`; use `--dry-run`
first. The queue uses at most two workers, refuses existing packages and calls
`verify_street_batch.py` after each build. No paid APIs are called. Heavy GLBs,
reference copies and rendered images stay under the external artifact root.

All runtime gates remain **NOT TESTED**: Currie terrain/context, bent/reversed
routes, intersections, access connections, edit/Undo/Redo/reload and exact export.
Flush concept streets are not certified traffic, drainage or accessible designs.
