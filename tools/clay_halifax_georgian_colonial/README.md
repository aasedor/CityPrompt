# Halifax Georgian colonial house (RLASM v6.1 architectural clay)

Candidate J2 of wave J of 2026-10-22, one of five catalogue additions the user asked to be chosen
(four buildings and one street); a building option from the building catalogue. State: **stopped at v003 by the stopping rule (independent review PASS_ZERO_P0_P1); v003 is the candidate, not keeper-approved**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `halifax_georgian_colonial / variant_0`
(catalogue variant id `halifax_georgian_colonial_v0`) from `frontend/public/archetypes/buildings/halifax-georgian-colonial/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,498,415 | `045d4918a6bd8121` |
| oblique | `variant_0_angle_60.jpg` | 948,192 | `b8f2b88fca6db22d` |
| top | `variant_0_angle_90.jpg` | 881,769 | `0ef686bee41cd16f` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 21 x 17 m, 15.6 m to the highest point; 2 storeys (two storeys on a low stone plinth, with an attic under the hipped roof).
- storey programme: two storeys on a low stone plinth, with an attic under the hipped roof
- plan: 21.2 x 14.7 m main block, seven bays by four, a 7.2 m centre pavilion projecting 0.6 m on the south front, two 5.8 x 2.15 m rear wings at the back corners with a recessed court between (top view); 7.5 m portico on a stone platform
- facade: red brick with a stone plinth, a stone string course and a modillioned white eave cornice; tall nine-over-nine sashes three panes wide with shouldered stone lintels and stone sills; centre pavilion with four giant stone pilasters and a brick pediment with an oval cartouche; one-storey Tuscan portico of four columns with a low hipped standing-seam roof
- roof: hipped blue-grey slate roof truncated in a flat lead deck with four brick chimney stacks and clay pots at its corners; the pavilion gable and the rear-wing hips run into the main roof
- inferred: interiors, the rear wings and the north front follow the visible grammar; metric dimensions are authored teaching assumptions
- levels (m): 0.60, 4.95, 8.95, 9.60

## Construction and delivery (Phases C to F)

`family_hfxgeorgian.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, porch_columns, glass_close, cornice_chimneys, west_front, roof_deck, rear_wings, interior, garden_fence`.

Run:

```
python tools/clay_halifax_georgian_colonial/lock_sources.py
python tools/clay_halifax_georgian_colonial/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_halifax_georgian_colonial/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_halifax_georgian_colonial
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

## Open blockers after v003 (x)

x
