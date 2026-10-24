# Barcelona passatge (covered passage) (RLASM v6.1 architectural clay)

Candidate K5 of wave K of 2026-10-23, one of five catalogue additions the user asked for
(all four variants of the climbing wall building, and the covered passage); a street or path option, not a building. State: **stopped at v003 by the stopping rule (the upper-bay finding survived two targeted fixes); v002 (0 P0 / 2 P1) is the candidate, not keeper-approved**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `barcelona_passatge / variant_0`
(catalogue variant id `barcelona_passatge_v0`) from `frontend/public/archetypes/streets/barcelona-passatge-covered-passage/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,623,910 | `81100da89fdcde1e` |
| oblique | `variant_0_angle_60.jpg` | 973,696 | `91e5b7b486005a0c` |
| top | `variant_0_angle_90.jpg` | 941,432 | `c13e0acab15bcb53` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 70 x 81 m, 20.5 m to the highest point; 3 storeys (street option: a covered pedestrian passage; the three-storey brick facades with shops below and flats above are the walls it is read with).
- storey programme: street option: a covered pedestrian passage; the three-storey brick facades with shops below and flats above are the walls it is read with
- plan: 11 m between the passage facades and 30 m from the open south mouth to the end wall (top view); a 1.2 m brick end wall with a round-arched portal to the north street; a tiled square in front of the mouth
- facade: red-orange brick with cream stone pilasters, belts and arch surrounds; timber shopfronts with green gilt-lettered signboards; round-arched French windows with wrought-iron balconies; wall lanterns
- vault: pointed glass vault on five transverse wrought-iron ribs with lattice brackets on pilaster corbels, dense glazing bars, three purlins a side, crests on the ribs, a glazed north lunette and an ornamental south end arch
- inferred: shop interiors, upper rooms, the outer faces of the passage block and the surrounding blocks are context and teaching assumptions; metric dimensions are authored from the pixel ratios
- levels (m): 0.00, 0.12, 5.00, 8.00, 10.80, 15.92

## Construction and delivery (Phases C to F)

`family_passatge.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, interior, roof_vault, south_portal, north_portal, shopfronts, floor_tiles, pavilion_finial`.

Run:

```
python tools/clay_barcelona_passatge/lock_sources.py
python tools/clay_barcelona_passatge/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_barcelona_passatge/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_barcelona_passatge
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

## Open blockers after v004

Candidate: `clay-barcelona-passatge-clay-v002.glb`. The v004 independent review (`evidence/v004/independent-review.md`) left these P0/P1 findings open:

- **P1** (front, interior, south_portal, left_side, right_side, top, facade_close vs source front, oblique, top): Wrong bay rhythm. The vault has 6 crested main ribs and bays along its length (right_side crop: ribs at about x=25, 195, 330, 465, 600, 735, then the north end; top shows the same spacing of about 115 px). The locked top has 8 bays: crested ribs at about y=50, 165, 300, 435, 580, 735, 900, 1065, 1250 in a 2x crop.... Likely fix: Rebuild the facade, rib and corbel module at 8 bays over the 30 m passage (about 3.75 m centres). Narrow each recessed arch to about 2.7 m (keep the 0.6 m reveals). Keep crown, springing, entablature and cornice...
- **P1** (front (end wall), shopfronts, floor_tiles, south_portal (far end) vs source front): Wrong material on the lower stage of the north end wall. Below the continuous stone impost band, the flanks on both sides of the portal piers are brick panels with coursing lines (front crop x=60-180 and 815-940 at 2x; shopfronts x=90-210). In the locked front, everything below the impost band is cream stone... Likely fix: Give the end-wall flanks from floor level up to the underside of the impost band the stone material, with faint ashlar joints at most. Keep brick above the band. Frame the west side doorway in the same stone....

The candidate v002's own open findings are in `evidence/v002/independent-review.md`.
