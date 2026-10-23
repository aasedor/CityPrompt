# Toronto streetcar street (RLASM v6.1 architectural clay)

Candidate I10 of wave I of 2026-10-20, one of the ten catalogue additions the user approved
(four buildings, three parks and squares, three streets); a street or path option, not a building. State: **stopped at v006 by the stopping rule (after the user reopened the family, v005 and v006 each scored 0 / 1 and did not lower v002's count); v002 is the candidate, not keeper-approved**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `toronto_streetcar_street / variant_0`
(catalogue variant id `toronto_streetcar_street_v0`) from `frontend/public/archetypes/streets/toronto-streetcar-street/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,379,433 | `a871fbf65e99fc36` |
| oblique | `variant_0_angle_60.jpg` | 973,141 | `2281194ddb33d5c0` |
| top | `variant_0_angle_90.jpg` | 917,016 | `c8ae807e89cde4d1` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 118 x 140 m, 34.7 m to the highest point; 3 storeys (street option: a streetcar main-street section; the storefront blocks and condominiums are the street wall it is read with).
- storey programme: street option: a streetcar main-street section; the storefront blocks and condominiums are the street wall it is read with
- plan: 25.4 m building line to building line, 16.2 m curb to curb (top view), an 80 m run north of a cross street and 50 m of context south of it
- facade: pale scored concrete sidewalks with red brick-paver furnishing strips, grey steel poles with span wires, contact wires and cobra-head lights, a concrete track slab with twin grooved-rail tracks, white lane dashes and a yellow centre line; a red-and-white articulated streetcar; red-brick storefront blocks with stone and white trim, brick and charcoal condominiums with glass balconies
- inferred: the block interiors, rear walls, the back lanes and the context south of the cross street are teaching assumptions
- levels (m): 0.00, 0.15, 4.62, 8.20, 11.80, 5.60

## Construction and delivery (Phases C to F)

`family_streetcar.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`streetcar_nose, pantograph_wire, track_slab, span_wire_pole, intersection_crossing, corner_storefront, victorian_arches, condo_balconies, east_sidewalk, roof_skylights`.

Run:

```
python tools/clay_toronto_streetcar_street/lock_sources.py
python tools/clay_toronto_streetcar_street/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_toronto_streetcar_street/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_toronto_streetcar_street
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

## Open blockers after v006 (stopped)

Candidate: `clay-toronto-streetcar-street-clay-v002.glb`. The v006 independent review (`evidence/v006/independent-review.md`) left these P0/P1 findings open:

- **P1** (top (primary)): Dark slot behind the east corner block. A near-black line, about 6 px wide (about 0.5 m at 12.6 px/m), runs north-south between the east corner block's rear parapet and the pale east context block. It spans x 1286-1292, y 704-859. Its core is RGB about 31-37 and it fades to the shaded back lane at its north end. At... Likely fix: Close the slot the way v006 closed the slab gaps. Either deepen the East corner block to 28.8 m (rear face at x 42.2, 0.2 m into the neighbour), or start the neighbour box at x 41.2. For the same reason, also butt...

The candidate v002's own open findings are in `evidence/v002/independent-review.md`.
