# Catalogue foundation checkpoint

The local picker now reads a shared asset registry at
`frontend/src/features/pickPlace/assetRegistry.ts`. It contains the existing
infill, bungalow, neighbourhood park and Calgary local street. No candidate
model was promoted or generated. All four remain **pilot** entries, not a
declaration that the classroom catalogue is complete.

## Contract

Each record has a stable saved ID, definition version, exact variant ID,
available model revision, model method, Calgary classification, readiness,
placement properties and reshape mode. Objects declare plot dimensions and
limits; streets declare a fixed section width. The existing dimensional planner
and adaptive park composer remain responsible for geometry.

The picker searches names, descriptions, Calgary collection labels and district
examples. Category options include only available entries. Candidate and retired
entries are excluded from browsing; retired object definitions can still resolve
existing saved placements. Filtering never edits the project. The street card
uses the existing route-drawing workflow, including its original tour anchor,
rather than the rectangular object preview.

Existing saved IDs, variant properties, native floors, plot clearances and street
section are unchanged. New placements carry `pick_place_definition_version`.
Legacy placements without that field continue to resolve by their original ID.

**Version limitation:** definition versions are provenance, not immutable model
pinning. The two existing clay deliveries have `model.revision: null` because
the frontend has no established immutable model revision to assert. Their exact
variant IDs still resolve through the existing reviewed runtime loader. Park
kit and street source revisions are recorded. Do not replace a model in place
and assume saved projects are pinned; immutable delivery/version resolution is
a later asset-loading task.

## Adding a choice

1. Prepare and review the exact model using the applicable existing workflow.
2. Add a unique registry ID and retain previous IDs for saved-project lookup.
3. Choose the Calgary collection and a supported placement/reshape contract.
   A record does not implement modular floors or arbitrary deformation.
4. Enter dimensions measured from the complete model envelope, exact variant
   properties, model revision where established, and an existing thumbnail.
5. Keep the entry `candidate` until its geometry, assets and placement are
   verified. `pilot` is local trial availability; `ready` requires release review.
6. Run `validateRegistry` through its tests, plus the relevant placement tests,
   type checking and a browser placement/save/reopen trial.

The first three objects retain repeat-native/adaptive behaviour. The street
retains its 16 m section and legacy saved-route recognition. A future new street
section also needs compatible route validation and editing; adding its metadata
alone does not implement another section renderer.

## Verification

Focused tests cover duplicate IDs, category/variant mismatches, readiness
filtering, district search, legacy and new saved properties, unchanged street
identity, geometry limits, automatic rebuild coordination, toolbar behaviour
and selection/cancellation. Browser verification checks the real saved pilot,
thumbnail loading, search, street activation and object preview cancellation.
Generated browser evidence stays in ignored `artifacts/occlusion-pilot/`.

No backend schema migration, generated models, paid image calls or production
deployment are part of this checkpoint. Local runtime services remain available
for the user's trial.
