# Concert hall pilot: Timber Acoustic

An RLASM 6.1 architectural-clay model of `concert_hall_modern` / `concert_timber_acoustic`
(variant 2, "Timber Acoustic"), generated in pure Python from measured constants. It is a
local pilot: not in the catalogue, not runtime-tested and not approved for publication.

![Oblique board](evidence/phone-oblique.jpg)

## What the model is

- **Podium:** a rounded rectangle 88 m by 64.4 m (a superellipse, exponent 3.3). Every ring of
  the podium shares one list of polar angles that includes each opening's exact edges, so the
  band, the glazing and what lies behind an opening start and stop together.
  - The glazed ground floor runs to 6.0 m, set 1.0 m back under the band, with mullions
    about every 4.8 m, a sill, a transom at 3.4 m and a foyer behind it.
  - A band of close bronze fins runs from 6.0 m to the 11.2 m coping. At the west end a
    ribbon window sits in a 0.35 m reveal with jambs, sill and head; the fins break above
    and below it, and slats cross it.
  - A closed upper storey runs right round behind the band: slab at 6.4 m, ceiling at
    10.1 m, an inner wall 9 m in, and cross walls between rooms.
- **Doors:**
  - The curtain wall is cut at both entrances. Six glazed 1.2 m leaves fill the main bay at
    the south centre and four the east bay, under a head and a transom light, with stiles
    at every joint. Thresholds sit 0.13 m above the 20 mm apron.
  - A service door is recessed 0.15 m in a framed opening in the opaque back-of-house at
    the north-east.
  - Three doors lead from the foyer into the hall drum.
- **Foyer stair:** a solid flight with a sloping soffit and glass balustrades, 35 risers of
  0.18 m, rising from the west foyer through a well cut in the ceiling and slab to the upper
  storey, guarded on three sides.
- **Roof garden** at 10.6 m:
  - a glass guard standing on the coping;
  - a winding path loop midway between the shells and the guard, a south-west walk, a
    spur to a flight of steps up to the oculus lip, and a spur to the roof entrance;
  - the roof entrance: a portal cut into the foot of the west shell, with jambs, a head, a
    glazed screen, and a lobby with the head of a stair going down;
  - drifts of low domed meadow, green and shrub mounds with pale flower clumps.
- **Shells:** two spiral sheets clad in bronze battens round an oval oculus 23.8 m by 18.8 m,
  centred 11.4 m east and 1.7 m south of the podium centre.
  - The west sheet rises to 23.6 m and the east to 21.6 m.
  - Their outer walls lean in 0.28 m per metre of rise, and the rims carry a dark cap.
  - At the north they meet in a radial notch, where the west sheet steps up over the east.
  - The east sheet runs on under the west as a narrow ring on the oculus lip.
- **Auditorium,** seen through the clear oculus glazing:
  - 11 raked tiers with seat strips (about 340 stalls seats) facing a timber stage on the east;
  - choir terraces behind the stage;
  - two balcony rings and vertical acoustic panels.
- **Apron:** a 6 m paved apron round the podium. The complete model is 100 m by 76.4 m by
  23.7 m, with about 69,000 triangles in 34 clay roles, 4.9 MB, and no textures.

## Sources and conflicts

| Role | File | Use |
|---|---|---|
| Oblique | `variant_2_angle_60.jpg` | Heights, facade, the shells' form, the hall |
| Roof | `variant_2_angle_90.jpg` | Plan positions, at 0.0991 m/px |
| Street (excluded) | `variant_2.png` | The grey preview of the old LEGO model, not this building |

Gate A was ruled on 2026-11-23: variant 2 has no usable street view, and a person accepted that the
oblique and roof views govern (`integration/promotion.json`, `human_decisions`).

Open for a person to rule on:

1. **The oculus position.** The oblique puts the oculus about 3.5 m east of the podium
   centre and the roof view 11.3 m. The roof view governs plan positions; the oblique
   governs heights.
2. **Heights.** A pinhole camera fitted to 39 traced podium points in the oblique fits about
   equally well (31 px RMS) for an 11 m or a 21 m podium. The podium therefore takes the
   catalogue's two 5 m floors.
3. **Inferred parts.** The interiors, the north and east ground floor, the roof-garden
   entrance and the hall's size are inferred. The hall is only as large as the oculus.

`prework-manifest.json` records the locks, measurements, conflicts and assumptions.

## Files

| File | Purpose |
|---|---|
| `build.py` | The generator. Writes the GLB, `build-report.json` and `prework-manifest.json` into a new directory |
| `cameras.json` | The 17 review cameras, including the fitted `match_oblique` and `match_top` |
| `review.html`, `render.cjs` | Review renders in headless Chromium (three.js, ambient occlusion, sun, fill and shadows) |
| `boards.py` | Four 1080 by 1920 phone boards: oblique, roof, construction and programme |
| `verify.py` | 77 deterministic delivery checks; writes `delivery-verification.json` |
| `test_concert_hall.py` | Generator tests: byte-for-byte rebuild, container, outline, shells, openings on shared ring vertices, the stair and its well, doors, sources and cameras |
| `candidate.json` | The recorded candidate: hash, bounds, doors, auditorium and review status |
| `evidence/` | Builder review, delivery verification and independent review records |
| `integration/` | The unapproved promotion package and the runtime review (every gate NOT TESTED) |

## Reproduce

```bash
python3 tools/catalogue_concert_hall_pilot/build.py --output artifacts/concert-hall/v009 --version 9
python3 -m http.server 8765 --bind 127.0.0.1 &          # from the repository root
node tools/catalogue_concert_hall_pilot/render.cjs artifacts/concert-hall/v009/concert-timber-acoustic-clay-v009.glb artifacts/concert-hall/v009/renders
python3 tools/catalogue_concert_hall_pilot/boards.py artifacts/concert-hall/v009
python3 tools/catalogue_concert_hall_pilot/verify.py artifacts/concert-hall/v009
python3 -m pytest tools/catalogue_concert_hall_pilot
```

`build.py` refuses an existing directory, and `render.cjs` and `boards.py` never overwrite
a file. Review builds live under the ignored `artifacts/concert-hall/`. The references are
Git LFS files: `git lfs pull --include="frontend/public/archetypes/buildings/concert_hall_modern/*" --exclude=""`.

## Checkpoints

- Builder review: pass (`evidence/builder-pixel-review.json`).
- Independent architectural-clay review: v007 was refused with four P1 findings
  (`evidence/independent-review-v007.json`). v009 passed on 2026-11-22 with zero P0, zero P1
  and three P2 (`evidence/independent-review-v009.json`):
  - five fins over the service door stand 8 to 18 cm off the cladding;
  - the lobby stair behind the roof portal ends at a closed wall;
  - two minor coplanar faces at the stair well and a north mullion.
- Gate A: accepted by a person on 2026-11-23. The oblique and roof views govern; the LEGO street view
  stays excluded.
- Install: a dry run of `prepare` (trial only, no writes) accepts the ruled-out street view but
  stops at the review record, which lacks `unresolved_p0`, `unresolved_p1` and an
  `inspected_files` list naming the reference hashes (`docs/BUILDING_CATALOGUE_WORKFLOW.md`).
  A conformant review record is needed before a trial install.
- Runtime integration: NOT TESTED. Publication and activation: not authorized. Only a
  person can activate the model.
