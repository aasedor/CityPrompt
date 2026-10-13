# Belle Epoque department store with glass dome (RLASM v6.1 architectural clay)

Candidate C2 of the five-building wave of 2026-10-13. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `grand_magasin / variant_0`
(catalogue variant id `grand-magasin-belle-epoque`) from `frontend/public/archetypes/buildings/grand-magasin/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,498,973 | `502d6d50e7b5ca03` |
| oblique | `variant_0_angle_60.jpg` | 1,019,929 | `acf6e2d1ff51f77f` |
| top | `variant_0_angle_90.jpg` | 915,820 | `945b348e6548ae6b` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; composite hero, not a locked view).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- 44 x 36 m corner block with a 10 x 8 m light well (top view), streets south and west, a 7 m radius curved corner bay under the dome.
- Levels 0.15 / 6.2 / 10.0 / 13.6 / 17.2 m (double-height ground floor plus four storeys); cornice 21.0 m; zinc mansard set in 1.4 m over 3.4 m with arched dormers at every bay and a flat zinc top.
- Bays at 5.0 m: display windows 4.2 x 4.1 m with transoms under a glass marquise projecting 2.4 m with a dark red sign band; upper bays 3.6 x 3.0 m of iron-and-glass with gilded balcony fronts at every storey between limestone pilasters; round-arched top storey.
- Quarter-round glazed corner bay on seven facets between stone piers with glazed doors at the centre; glazed drum 12 m across and 4.6 m high standing above the mansard; ribbed glass dome 12.4 m across and 5.8 m high with sixteen iron ribs and purlin rings, glazed lantern and finial; second glass dome 5.6 m across at the north end of the west face.
- North and east faces repeat the grammar without balconies; light-well faces plain.

## Construction and delivery (Phases C to F)

`family_magasin.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier, faces that no source shows carry
lighter window assemblies to keep the delivered GLB under the 4 MiB blob cap, every
vertex sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `corner_dome, marquise_sign, gilded_balconies, mansard_dormers, roof_domes, interior, rear_court`.

Run:

```
python tools/clay_grand_magasin/lock_sources.py
python tools/clay_grand_magasin/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_grand_magasin/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_grand_magasin
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 4 MiB (Git LFS
  uploads are refused from the cloud build host; limit lifted from 1 MiB on 2026-10-12).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture
  audit, reviewer brief, independent review record, and sub-megabyte JPEG copies
  of every render and phone board.
- Full-resolution PNG renders, the locked sources and the GLB were delivered to
  the user as a zip archive per version.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`),
zoning use program, picker enrolment, catalogue splice and human activation.

## Open blockers after v006 (Both v005 P1s resolved in the pixels (the drum burial did not survive its second fix: straight glazed lower tier with full-height posts down to the balustrade; court dome with 16 continuous ribs to the cap). Same count as v004 and v005 (0 + 2): second consecutive review that did not lower P0+P1, so the stopping rule (rule 2) ends the run; v004 stays the candidate. v006 is evidence only.)

P1 missing attic storey: both locked views show a stone attic storey with windows between the gilded cornice balustrade and the zinc mansard (the roofline reads one storey low and the drum is flanked by sloped zinc cheeks instead of vertical stone attic returns); P1 the gilded balcony fronts were thinned to flat boards with sparse bosses whose centres render pure black
