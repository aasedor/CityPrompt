# Courtyard primary school with hall block (RLASM v6.1 architectural clay)

Candidate 4 of the ten-building batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `ecole_republicaine / variant_3`
(catalogue variant id `ecole-republicaine-art-deco`) from `frontend/public/archetypes/buildings/ecole-republicaine/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_3.png` | 1,323,463 | `353d70cf1e6d860e` |
| oblique | `variant_3_angle_60.jpg` | 990,119 | `ad3f15097e602c85` |
| top | `variant_3_angle_90.jpg` | 904,476 | `c833b66c8e3184ba` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; depicts the catalogue hero, not enrolled). Catalogue label says Art Deco school; the locked pixels show a contemporary brick courtyard school and govern..

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- Mid-block corner site 40 x 46 m (570 x 650 px in the top view); party walls west and north; courtyard 19 x 18.5 m opening south.
- Two-storey brick U (levels 0.15 / 4.0 m, roof 7.8 m, parapet 8.3 m): west wing, north-west block, north hall block with a paved terrace, south-east entrance block.
- Corten third storey 16 x 22 m over the north-west block (roof 11.4 m) with its own gravel roof and rail.
- Open concrete-framed entrance passage at the south-east corner under a corten canopy (4.0 m) that also roofs the east edge of the playground.
- Strip windows with coloured fins on the upper floor, full-height classroom glazing to the court, concrete floor and parapet bands, gravel roofs with rails, street fence with a gate, play structure and benches.
- The catalogue label (Art Deco school) conflicts with the pixels; the pixels govern.

## Construction and delivery (Phases C to F)

`family_school.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `entrance_passage, courtyard, fins_close, canopy_contact, penthouse_terrace, interior, playground`.

Run:

```
python tools/clay_courtyard_primary_school/lock_sources.py
python tools/clay_courtyard_primary_school/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_courtyard_primary_school/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_courtyard_primary_school
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

## Open blockers after v004 (v005 in progress)

- P0 pure-black vertical slot the full upper-window-band height at the entrance block's south-west upper corner above the canopy attachment (open-faced box dressed as a corner window; no source shows a window there).
- P0 pure-black slot the full height of the main entrance recess between the concrete frame and the clay reveal, plus a sliver along the lintel soffit.
- P1 entrance block ground floor is a solid clay box with a shallow recessed porch where the sources show an open concrete-framed passage under the overhanging upper floor (about 58 percent of the block width, post and lintel band, door deep inside, open west to the canopy bay; canopy lacks its south leg over the passage mouth).
- P1 canopy west end face pure black (missing or inward-facing end face).
- P2: shadowed inner north-east courtyard corner; fins over glass instead of on piers and none on the courtyard ground floor; corten storey glazing, coping and rails simplified; gravel and paved roofs indistinguishable, north-east patch lacks its inner rail; small black mitre notches at window-frame corners; one to two pixel black kerb and slab-edge lines.
