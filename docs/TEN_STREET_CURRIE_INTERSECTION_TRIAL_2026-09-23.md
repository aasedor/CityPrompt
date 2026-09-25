# Ten native streets crossed on the vacant Currie parcel

Date: 2026-09-23. Source branch: `codex/ten-street-currie-trial`. This is an
assisted local browser and image-render review of the ten accepted street
candidates from [the bounded asset batch](TEN_STREET_ASSET_BATCH_2026-09-22.md).
The [machine-readable record](TEN_STREET_CURRIE_INTERSECTION_TRIAL_2026-09-23.json)
locks the ten model hashes, saved zone IDs, capture hashes and five render IDs.
This document records the pre-junction baseline. The later
[native junction runtime pilot](NATIVE_STREET_JUNCTION_RUNTIME_2026-09-23.md)
adds the first graph-owned crossing treatment to this same Currie scene.

## Setup and result

The fresh disposable City Prompt project
[Currie — Ten Street Concepts Together](http://127.0.0.1:5176/projects/34972f9d-dd8e-4d63-a590-0ce1b0e8fbf1)
uses only the six-point vacant Currie boundary copied from the earlier public
realm trial. Its prepared datum is 1098.1770006728689 m. Ten exact-size native
GLBs are arranged as five perpendicular crossing pairs, each with both full
footprints more than 1 m inside the boundary. A geometry dry run proved that
only the intended pairs overlap; the persisted project reload returned one
boundary and ten road zones. All ten review-layer models reached `ready` in the
actual editor, with surrounding Google 3D Tiles and a blue sky.

**Finding: these fixed native sections do not form proper intersections.** The
renderer displays two complete street surfaces in the same place. Their
markings, paving units, planted areas and furniture are not clipped or
reorganized at the crossing. This is a visible classroom blocker if intersecting
these variants is advertised as a working road-network action. The models
remain useful as isolated local concepts; this review does not approve them
for student picker publication.

| Pair | Native overlap | Exact 3D observation |
| --- | ---: | --- |
| Main Street × Cycle Avenue | 552 m² | Complete slabs and paint overlap; planting remains in the junction envelope. |
| Transit Street × Market Street | 486 m² | Market paving and furnishings continue through the transit movement area. |
| School Street × Grand Promenade | 441 m² | The blue school-route marking passes through without a designed crossing. |
| Planted Lane × Heritage Mews | 120 m² | Paving meets visually, but furniture and planting are not reorganized. |
| Boardwalk × Green Alley | 132 m² | Deck, railing and alley paving overlap without an accessible tie-in. |

The [side-by-side gallery](http://127.0.0.1:5176/__review/ten-street-crossings/index.html)
shows an exact editor capture beside one GPT Image 2.5 Flare image for each
pair. All five image calls succeeded and were saved to the project's Render
gallery. They used 130 local image credits (458 before, 328 after). Despite
explicit preservation prompts, the image model made several junctions appear
connected and moved or invented surface and landscape detail. The exact 3D
capture, not the AI finish, is authoritative for testing intersection behavior.
The locally served comparison pack is
[CityPrompt-Currie-ten-street-crossings.zip](http://127.0.0.1:5176/__review/ten-street-crossings/CityPrompt-Currie-ten-street-crossings.zip).

## Runtime scope and reproducibility

The source GLBs remain under
`C:/dev-artifacts/CityPrompt/streets-ten-2026-09-22/`. The reviewed copies are
under the ignored public root
`C:/dev-artifacts/CityPrompt/student-design-transformation/public/public-realm-trials/ten-streets-2026-09-23/`.
`tools/public_realm_assets/hydrate_street_trial.py` verified each accepted
package's byte count and SHA-256, then registered its native dimensions,
surface regions and tree wells in the development-only
`publicRealmTrialAssets.json`. Its dry run passed before copying. The review
layer now recognizes asphalt as an owned ground material while retaining native
paving tiles and painted detail above that ground. The existing surface and
tree-well test covers all 15 local public-realm trial assets; the ten new streets
contribute 36 hardscape wells, for 44 total.

These ten trial streets are not student-picker variants and do not yet use the
normal Generate to 3D compiler. The editor's Present > Image control remained
disabled for that reason. The five illustrations used the existing authenticated
City Prompt capture, image-generation and project-save APIs against the actual
browser scene. The five crossings are isolated review nodes, not a connected
internal road graph or connections to the public perimeter roads. Student UI
placement, snapping, editing, Undo, external-road connection, terrain variants
and exact export were not tested in this run.

## Next integration work

1. Add a shared intersection resolver that recognizes compatible street/path
   crossings and determines the junction envelope in metres. It must distinguish
   vehicular, transit, cycling, pedestrian and boardwalk treatments.
2. Cut back the two full-section grounds, paint and paving at the junction;
   place one owned junction surface with continuity for the intended movements.
   Relocate or suppress trees, beds, bollards, shelters and furniture that block
   the crossing, while retaining tree wells on hardscape outside the envelope.
3. Pilot Main Street × Cycle Avenue and one pedestrian pair in this disposable
   project. Verify overhead, low view, exact capture, reload and export before
   scaling the treatment to the remaining eight models. Compare AI output to
   the same-camera source and present source fallback if it changes the design.

This finding is now included in the shared
[archetype runtime checklist](ARCHETYPE_RUNTIME_INTEGRATION.md) so future street
variants must prove pairwise junction behavior, not only isolated appearance.
