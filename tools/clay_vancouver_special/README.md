# Vancouver Special house (RLASM v6.1 architectural clay)

Candidate I1 of wave I of 2026-10-20, one of the ten catalogue additions the user approved
(four buildings, three parks and squares, three streets); a building option from the building catalogue. State: **stopped at v003 by the stopping rule (two consecutive non-improving reviews); v001 is the candidate**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `vancouver_special / variant_0`
(catalogue variant id `vancouver_special_v0`) from `frontend/public/archetypes/buildings/vancouver-special/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,198,511 | `d35ea463c540674c` |
| oblique | `variant_0_angle_60.jpg` | 869,740 | `052e9e31318baf4b` |
| top | `variant_0_angle_90.jpg` | 846,284 | `4eb1722a8e99aee7` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 11 x 9 m, 10.3 m to the highest point; 2 storeys (raised ground floor (suite, entry hall) and the main living floor above off the front balcony).
- storey programme: raised ground floor (suite, entry hall) and the main living floor above off the front balcony
- plan: 10.8 x 9.2 m box (top view) under one front-gable roof with 0.6 m overhangs; balcony across the east two thirds of the front
- facade: red-orange brick ground storey on the street front, white stucco above and on all other walls; bronze aluminium sliders; white door with sidelight; aluminium picket railings
- inferred: interiors, the west face and the rear face are teaching assumptions; the rear carries a small upper deck as glimpsed in the front view
- levels (m): 0.90, 3.95, 6.69

## Construction and delivery (Phases C to F)

`family_vspecial.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, balcony_rail, entry_stair, brick_base, east_side, side_entry, roof_ridge, interior`.

Run:

```
python tools/clay_vancouver_special/lock_sources.py
python tools/clay_vancouver_special/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_vancouver_special/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_vancouver_special
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

Candidate: `clay-vancouver-special-clay-v001.glb`. The v003 independent review (`evidence/v003/independent-review.md`) left these P0/P1 findings open:

- **P1** (front_corner vs locked oblique; front vs locked front; rear; roof_ridge): The front gable is too steep for a "low wide" Vancouver Special gable. In the matched oblique, apex rise above the line joining the two eave tips is 0.195 of the tip-to-tip span in front_corner (tips 234,367 / 991,608; apex 556,314) against 0.13 in the locked oblique (tips 167,277 / 782,497; apex 420,282). The two... Likely fix: Lower the roof to about 15° (3.25:12), keeping eave height, overhang depth, the centred front-to-back ridge, fascia depth and outrigger spacing (re-space outriggers along the shorter rake). Re-render front,...
- **P1** (front_corner, aerial, top, roof_ridge, left_side, right_side, rear_side; phone-01): The roof reads as a light pinkish taupe, not the source's medium-dark brown-grey asphalt. Median roof luminance is about 135–143 (front_corner 141,136,132; top W 148,143,138, E 138,133,129) against 90–115 in the sources (oblique 93,91,89; top E 93,91,88, W 126,114,102). This holds even though the render's white... Likely fix: Set the shingle material to the sampled source colour (about sRGB 95,90,86 for field shingles, with the ridge cap slightly darker), and keep the course geometry. Acceptance: in front_corner, the roof median luminance...
- **P1** (architecture_close (x≈1056–1062, y≈482–515), front (x≈900–905, y≈157–162)): At the front-east eave (the hero corner), there is a near-black slit about 3 px wide and 30 px tall where the downpipe outlet stub drops out of the gutter, between the gutter's inner face and the outlet's west side. Luminance falls to 8 (72 px under 30). The v002 must-hold says no black faces on any downpipe... Likely fix: Centre the outlet stub in the drop hole and make the hole no larger than the stub, or cap the gap with a brown gutter-bottom plate. Give any interior gutter face the brown trim material. Acceptance: minimum luminance...

The candidate v001's own open findings are in `evidence/v001/independent-review.md`.
