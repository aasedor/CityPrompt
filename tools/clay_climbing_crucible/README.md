# Climbing wall building: The Crucible (RLASM v6.1 architectural clay)

Candidate K1 of wave K of 2026-10-23, one of five catalogue additions the user asked for
(all four variants of the climbing wall building, and the covered passage); a building option from the building catalogue. State: **stopped at v003 by the stopping rule (the east curtain-wall finding, first raised at v001, recurred after targeted fixes in v002 and v003); v003 (0 P0 / 2 P1) is the candidate, not keeper-approved**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `climbing_wall_building / variant_0`
(catalogue variant id `climbing_crucible`) from `frontend/public/archetypes/buildings/climbing_wall_building/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,254,544 | `a2b53e14adb38bae` |
| oblique | `variant_0_angle_60.jpg` | 815,928 | `8443b0f6a5b3da03` |
| top | `variant_0_angle_90.jpg` | 896,561 | `cb1a5bf529bebca5` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 101 x 28 m, 28.1 m to the highest point; 4 storeys (a climbing hall behind the sloped wall, a glazed east hall of three upper levels over a ground-floor lobby).
- storey programme: a climbing hall behind the sloped wall, a glazed east hall of three upper levels over a ground-floor lobby
- plan: 101 m by 28 m block (landmark fit of the front and oblique; the AI-rendered top view is not consistent with them): a 62 m climbing wall between a 22 m west Corten block and a 17 m east Corten block
- facade: south: dark charcoal hexagonal panels on a wall leaning back slightly (1.5 m over 28 m) that folds into a darker facet near the east block, with amber LED route lines and holds; Corten panel grid on the end blocks; east: Corten frame round a mullioned curtain wall over a projecting band and recessed ground glazing
- roof: green roof of native grasses inside a coped parapet; red running-track loop with lane lines and a second run closing a loop round the west bed, dark pavilion, sunken half-round seating bowl, concrete paths, north walkway with a rail, two vent boxes
- site: black rubber fall-zone apron with a white edge, a bent steel bouldering frame and a disc; boulders, lawn, curving path, shrub beds; paved east plaza
- context: white smokestack north-east, red-brick gabled warehouses, road, parking and harbour water beyond (simple massing)
- inferred: interiors behind the east glazing, the north face and the west end face follow the visible grammar; metric dimensions are authored teaching assumptions
- levels (m): 0.15, 9.00, 14.50, 20.00

## Construction and delivery (Phases C to F)

`family_crucible.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`climbing_wall, route_holds, fall_zone, glass_close, architecture_close, facade_close, east_entrance, roof_track, roof_pavilion, interior`.

Run:

```
python tools/clay_climbing_crucible/lock_sources.py
python tools/clay_climbing_crucible/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_climbing_crucible/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_climbing_crucible
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 4 MiB (Git LFS uploads are
  refused from the cloud build host).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture audit, reviewer
  brief, independent review record, and sub-megabyte JPEG copies of every render and phone board.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`), zoning use
program, picker enrolment, catalogue splice and human activation.

## Open blockers after v003 (stopped)

Candidate: `clay-climbing-crucible-clay-v003.glb`. The v003 independent review (`evidence/v003/independent-review.md`) left these P0/P1 findings open:

- **P1** (front, front_corner, aerial, top, climbing_wall, route_holds, fall_zone): Holds are illegible and do not cluster. In the envelope views the holds are 2–4 px near-black specks on charcoal panels and are effectively invisible. In route_holds each hold is about 1/10 of a hex panel and they are scattered thinly across the whole eastern field, between routes as well as on them. Source front... Likely fix: Make holds about 2.5× larger (roughly 0.35–0.45 m across). Place 70–80 % of them within about 0.6 m of the two eastern route corridors, at about 3× the current density in those corridors, and thin out the field...
- **P1** (front, front_corner, right_side, glass_close, east_entrance): East curtain wall has the wrong mullion rhythm. The upper curtain wall is a near-square grid of about 13 columns × 11–13 rows, with panes about 1:1 to 1:1.3. Source oblique and front show a much finer vertical rhythm: about 20–22 slender columns of tall panes (about 1:3 to 1:4), with strong vertical mullions and... Likely fix: Halve the vertical-mullion spacing to about 1.1–1.25 m (about 20–22 bays across the frame opening). Space transoms about 3.5–4 m apart (3–4 transoms over the upper wall). Apply the same vertical module to the...
