# Modernista iron-and-glass market hall (RLASM v6.1 architectural clay)

Candidate C3 of the five-building wave of 2026-10-13. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `barcelona_mercat / variant_0`
(catalogue variant id `mercat_modernista`) from `frontend/public/archetypes/buildings/barcelona-mercat/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,903,324 | `0f36972485949c74` |
| oblique | `variant_0_angle_60.jpg` | 1,034,373 | `34a74012d1eb1fc3` |
| top | `variant_0_angle_90.jpg` | 934,010 | `63b0b905caa5e7fc` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; composite hero, not a locked view).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- 46 x 46 m single-storey square hall on a paved plaza (top view): four 18 m gabled wings in a pinwheel cross around a 14 m square lantern, lower lean-to roofs in the four corner quadrants with gablets along their eaves.
- Section: tiled dado 1.3 m, cast-iron columns at 4.6 m with iron-framed glazing to the aisle eave at 6.8 m; wing eaves at 10 m over the quadrant roofs with clerestory glazing; wing ridges at 15 m; lantern to 18 m with a pyramid roof to 21.6 m.
- Each gable end a semicircular iron arch 16 m across with a glazed tympanum (stained glass and a coat of arms on the south), iron lattice spandrels, bargeboards and a wrought-iron crest; the south gable over the main entrance between stone piers.
- Coloured canvas awnings over every perimeter bay; bollards, lamp posts and trees on the plaza; stalls of produce in four aisles meeting under the lantern.
- The north, east and west gables repeat the south grammar with clear glass; interiors are teaching assumptions.

## Construction and delivery (Phases C to F)

`family_mercat.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier, faces that no source shows carry
lighter window assemblies to keep the delivered GLB under the 4 MiB blob cap, every
vertex sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `great_arch, aisle_arcade, lantern_roofs, crest_contact, plaza_awnings, interior, rear_court`.

Run:

```
python tools/clay_modernista_market_hall/lock_sources.py
python tools/clay_modernista_market_hall/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_modernista_market_hall/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_modernista_market_hall
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

## Open blockers after v003 (v002 P0 (trusses through the roofs) and the monitor-end and ridge-seam P1 resolved in the pixels. Improved from 1 + 3 to 0 + 3; becomes the candidate.)

P1 interior: the ceiling is still an opaque brown soffit with no lantern glazing, skylight strips or nave trusses visible from inside (v002 finding, half fixed after one fix); P1 lantern-roof junction: black corner posts stop in mid-air over a blown-out patch, blank translucent grey triangles without mullions fill down to the valleys, no sill on the roofs; P1 quadrant pyramid glass is a few huge red, yellow, blue and green triangles per facet where the sources show a grid of small leaded panes in muted teal, blue-green and amber with opaque metal outer zones
