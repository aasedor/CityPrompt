# Courtyard mixed-use mid-rise (RLASM v6.1 architectural clay)

Candidate M2 of the towers and mixed-use batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `rndsqr_terraced_mixed_use_midrise / variant_0`
(catalogue variant id `rndsqr_midrise_courtyard`) from `frontend/public/archetypes/buildings/rndsqr-terraced-mixed-use-mid-rise/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,234,206 | `558a2af42e940e5c` |
| oblique | `variant_0_angle_60.jpg` | 907,543 | `aa238e6af3c002b1` |
| top | `variant_0_angle_90.jpg` | 815,380 | `c5fd47f730f1dc2f` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); none (no hero file in this directory).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- 38 x 30 m read from the top view; wings 13 m wide; courtyard 12 x 20 m open to the south; rear bar 10 m deep; streets south and east.
- Levels 0.15 / 4.5 / 7.7 / 10.9 m; wing roofs 14.1 m; penthouse storey to 17.3 m.
- Dark vertically ribbed metal panels; floor-to-ceiling black-framed windows; one recessed cedar-lined balcony with a glass balustrade per wing face per storey; storefronts at street level.
- Concrete stair 6 m wide rising 4.5 m from the sidewalk to the courtyard deck in a slot between the retail units; courtyard planters, benches and tree.
- Penthouse boxes 11.5 x 10 m at the wing fronts with roof terraces and glass rails; rooftop units on the rear bar.

## Construction and delivery (Phases C to F)

`family_courtyard_midrise.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `courtyard_stair, retail_corner, balcony_close, roof_terrace, cladding_contact, interior, rear_lane`.

Run:

```
python tools/clay_courtyard_mixed_use_midrise/lock_sources.py
python tools/clay_courtyard_mixed_use_midrise/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_courtyard_mixed_use_midrise/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_courtyard_mixed_use_midrise
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 1 MiB (Git LFS
  uploads are refused from the cloud build host).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture
  audit, reviewer brief, independent review record, and sub-megabyte JPEG copies
  of every render and phone board.
- Full-resolution PNG renders, the locked sources and the GLB were delivered to
  the user as a zip archive per version.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`),
zoning use program, picker enrolment, catalogue splice and human activation.

## Open blockers after v003 (no further version permitted)

- P0: each wing's top storey is a set-back pavilion over the front half of the wing only, so the rear half of each wing is one storey lower and the east face shows three window rows where the front source shows four flush tan rows; the sources show one continuous top-storey roof plane across both wings into the rear bar with the mechanical screens on it. Fix is a full-length tan top storey on each wing at the rear-bar roof level.
- P0: a black slot runs the full stair width between the top tread and the courtyard deck (stair landing and deck edge do not meet); fix is to extend the landing under the deck edge or the deck over the landing with no coplanar faces.
- P1: black band at the stair foot where the first tread meets the sidewalk; fix is to seat the stair prism on the sidewalk slab.
- P1: rear bar courtyard face material inverted (dark piers and light slab edges where the source shows cedar piers and dark fascias); fix is cedar carrier piers and dark balcony fascias.
- P1: west wing street face still three bays plus balcony plus one where the source shows four narrow bays with the balcony two-thirds across and a tan end bay; east wing has three narrow bays where the source shows one wide bay.
- P1: the balcony back-wall opening is a flat unframed dark rectangle on all six front balconies; fix is a framed glazed door with a reveal.
- P2 (recorded): oversized penthouse roof cap, ribs reading as battens with dash rows, half-opaque balustrade glass, stair filling the slot wall to wall without the west planter wall, retail fascia not wrapped on the east face, under-lit interior.
