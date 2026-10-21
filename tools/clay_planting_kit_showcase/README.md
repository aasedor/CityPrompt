# Planting kit showcase (kit showcase, not a catalogue candidate)

> **This is not a catalogue candidate.** It has no locked sources and no `sources.json`, and it maps to no
> catalogue archetype or variant. Nothing here is keeper-approved, runtime-integrated, enrolled in a catalogue,
> seeded or activated. The family exists so that the shared planting kit can be reviewed once, at eye level,
> before park families reuse it.

## Why the kit exists

The wave H and wave I park families stopped on close-up planting:

- **Green bridge:** boulders, then gumdrops and lilac capsules.
- **Halifax Public Gardens:** faceted gem heads.
- **Prince's Island Park:** cone heads, flat straw ribbons and bare fill between the mounds.

The kit replaces those per-family primitives with one shared vocabulary that follows
`docs/HIGH_QUALITY_3D_PARK_MEMORY.md`, which sets the conservatory benchmark: a legible plan, controlled richness
and grounded, complete 3D at pedestrian height.

## The kit chunk

The kit is a shared helper chunk, `plantkit.py`. Assemble a park module like this, with the kit after `gcommon.py`:

```
cat <key>_head.py common.py gcommon.py plantkit.py <key>_body.py > tools/<family>/<module>.py
```

The chunk starts at the line `# ---- shared planting kit` in `family_plantkit.py`. That copy is the reference text:
keep every family's copy identical to it.

These rules apply to every builder:

- **Grounded:** every plant base and every carpet edge sits `PK_SINK` (2.5 cm) below the soil top. The flat caps are
  buried.
- **Shading:** curved surfaces are smooth-shaded. Buried caps are flat-shaded.
- **No coplanar faces:** lobes interpenetrate; adjacent bedding bands meet at a lapped clipped step (the lower band
  runs 5 cm under the higher, which is at least 1.5 cm taller), never on a shared plane and never in a soil valley.
- **No ridged noise:** every displaced surface uses soft signed noise, so nothing reads as creased, spurred or
  crumpled (the v001 shrub, hydrangea, yarrow and carpet failures all came from `abs(noise)`).
- **Clearance rule (kit-wide):** `kit.fits()` / `kit.place_in()` keep every plant's buried base `PK_CLEAR` (5 cm)
  inside each registered bed edge and off every obstacle; only canopy above kerb height may overhang a kerb, and an
  obstacle taller than 0.3 m (a rail, a wall) keeps the whole canopy clear. `kit.audit()` counts placements that break
  it; the showcase build fails unless it is 0.

### API

**Setup and placement**

| function | what it does |
|---|---|
| `pk_palette(PALETTE)` | Adds the kit roles (`pk_leaf`, `pk_pink`, `pk_groundcover`, `pk_shrub_core`, and so on) without overriding any role the family already defines. |
| `kit = PlantKit(module, instancing=True)` | Creates the prototype registry. Each proto records `base_r` (buried footprint below kerb height), `canopy_r` and `height`. |
| `pk_bed(..., kit=kit)` / `kit.register_bed(region)` | Registers a plantable region (bed minus kerb) for the clearance rule. |
| `kit.add_obstacle(geom, top)` | Registers a rail, wall or post footprint and its height above the soil. |
| `kit.place_in(proto, x, y, z, rot, s, region=, aspect=, lean=)` | Places a prototype only if it passes the clearance rule (trying 1.0, 0.85 and 0.72 x s), else skips it. |
| `kit.place(proto, x, y, z, rot, s, sz=, sy=, lean=)` | Places without checking: non-uniform scale and a small lean, as linked instances or merged per role. |
| `kit.audit(detail=False)` | Counts (or lists) placements that break the clearance rule. |
| `kit.flush()` / `kit.stats()` | Merges batches and records counts, violations and rejections. |

**Prototype plants** (each returns a proto to place)

- **`flower_head_cluster(kit, name, head=..., leaf_w=, leaves=)`**: a leafy mound (a small hidden core, keeled leaves
  arching to a basal skirt; `leaf_w` 0.5 lanceolate, 0.3 divided) with stems carrying smooth heads. `head` is one of:
  - `'daisy'`: a scalloped, drooping ray disc round a boss (coneflower, rudbeckia);
  - `'spike'`: a tapered core packed with floret whorls (salvia, veronica);
  - `'umbel'`: a flat-topped corymb of small smooth floret domes (yarrow, sedum);
  - `'cup'`: a bowl of four broad petals round a dark boss (poppy, tulip);
  - `'panicle'`: a loose conical floret panicle (astilbe, panicle hydrangea, phlox);
  - `'mophead'`: hydrangea heads of smooth floret-cluster domes in a leaf-skinned shrubby mound.
- **`lavender(kit, name, ...)`**: a grey-sage mound of needle leaves under a dome-shaped haze of thin stems with slim
  smooth spikes (lavender, catmint, perovskia).
- **`arching_grass(kit, name, ..., plumes=, plume_height=)`**: keeled blades arching from a low crown; optional plumes
  are a slim spindle wrapped in hair-fine spikelets on a nodding rachis.
- **`shrub_mass(kit, name, radius, height, ...)`**: a very dark smooth hull of overlapping lobes skinned in broad cupped
  leaf cards (lighter above); use 0.4, 0.8, 1.2 and 1.6 m sizes with two seeds for repeats.
- **`bedding_cushion(kit, name, ...)`**: a low smooth leafy cushion studded with floret domes (begonia, ageratum,
  alyssum).
- **`pot_plant(kit, name, plant='geranium'|'box'|None)`**: a terracotta pot with a rolled rim and a soil top, holding
  a geranium, a leaf-skinned box ball, or nothing (the root pot of a climber).

**Beds, carpets and drapes** (unique geometry, merged)

- **`pk_bed(name, outline, soil_z, kerb=..., kit=)`**: a granite kerb ring and a mulch surface.
- **`groundcover(name, poly, z, kerb=..., dots=, grain=)`**: a softly cushioned carpet lapped 3 cm under the kerb,
  with a clean clipped rim (an outline ring and a shoulder ring, no teeth); optional micro-floret and leaf-grain specks.
- **`carpet_bands(name, outline, z, bands, kerb=...)`**: the Halifax module: flat clipped bands (bump <= 4 mm,
  near-vertical 2.5 cm shoulder) following the outline, with automatic laps and height steps and micro-florets
  (`pk_dots`, 100-300 per m2, two hue roles). `bedding_band(...)` builds one band.
- **`wall_drape(name, p0, p1, out, profile, curtain, openings=, trunks=)`**: a wall-trained climber or parapet cascade
  (bougainvillea): a leafy canopy shell draped over a wall cross-section, cut clear of doors and windows, with an
  irregular hanging edge and fringe, lumpy bract masses studded with papery bract flecks, leaf cards and woody trunks
  rising from a pot.

**Placement and outlines**

- **`perennial_drift(kit, poly, z, mix, kerb=..., underlay='pk_groundcover')`**: assigns Poisson-spaced plants to
  species by low-frequency noise fields, so species form interlocking drifts. Every plant passes the clearance rule
  with its own base radius and gets a non-uniform scale and a small lean; a groundcover underlay hides the fill by
  default.
- **`pk_scatter`, `pk_dots`, `pk_ellipse`, `pk_leaf`, `pk_blob`, `pk_rounded_rect`, `pk_region`**: scatter, specks,
  bed outlines and the plantable region inside a kerb.

## Instancing and how to adopt it

### Findings

**glTF instancing survives export and reimport.** In Blender 4.2.0, linked duplicates export as one mesh with many
nodes, and reimport gives one mesh datablock.

| experiment | joined | instanced |
|---|---|---|
| 200 copies of a 2,048-triangle plant | 9,908,488 B | 79,556 B |

**`clay_core.deliver()` joins every object per role,** which would turn instances back into geometry. This family's
`build.py` therefore adds two family-local shims; `clay_core` itself is not edited:

- `keep_instances()` renames each instance's role to `<role>_instanced`, so the join loop skips it. The true role is
  kept in `cityprompt_base_role` and on the shared material.
- The triangulate pass runs once per shared mesh.

Everything else in `deliver()` runs unchanged: bounds, the carrier aperture audit, the GLB round trip, the renders
and `build-report.json`.

### Measured on the showcase

v002 smoke build at 480 px and 8 samples: 159 plants from 27 prototypes on 399 instance nodes, plus the unique
carpets, kerbs, plaza walls and climber drapes.

| | v002 (instanced, shipped) | v001 (instanced) |
|---|---|---|
| Showcase GLB | 3,931,904 B (under the 4,194,304 B cap) | 3,338,232 B |
| Stored triangles | 134,728 | 143,020 |
| Scene (rendered) triangles | 587,044 | 667,084 |
| Prototype triangles | 83,536 | 68,832 |
| Clearance violations | 0 | not measured |

For v001, the same scene joined (`--no-instancing`) came to 15,861,936 B, and each further instanced plant costs
about 1.9 KB (3.1 nodes at about 615 B each, mostly glTF extras). The build passes `build_valid` with
`PASS_CARRIER_APERTURES` and a round-trip delta of 0.0.

### Rules for park families

- Instance every prototype plant.
- Merge anything under about 20 triangles per role, such as dots and florets, because a node costs more than its
  geometry.
- Budget the carpets: they are unique geometry and, with the kerbs, they are most of the non-plant bytes. Carpets
  under plants can use `grid=.22`; leaf-card skins cost about 100 B per leaf, specks about 110 B each.
- Register every bed with `kit=` and every rail or wall with `kit.add_obstacle()`, place with `place_in()` or
  `perennial_drift()`, and fail the build unless `kit.audit()` is 0.
- Copy `keep_instances()` and the dedupe of the triangulate loop into the family `build.py`. A one-line change to
  `clay_core.deliver()`, skipping `rlasm_instance` objects in the join, would remove the need for the shim. That is a
  separate decision.

## Running it

```
python tools/clay_planting_kit_showcase/build.py --version 2 --output <dir> --resolution 480 --samples 8
python tools/clay_planting_kit_showcase/build.py --version 2 --output <dir2> --cameras front_corner --no-instancing   # size comparison
python tools/clay_planting_kit_showcase/phone_board.py --candidate <dir>
```

The build writes `evidence/planting-kit-size.json`, with the GLB bytes, stored and scene triangles, nodes, plants and
prototype triangles, clearance violations and rejected placements.

## Layout and cameras

There are nine kerbed beds and a paved plaza corner on a 41 × 22 m lawn with two gravel walks:

- **South row (y = -6.5):** B1 specimens of every head type (mophead, coneflower, rudbeckia, salvia, yarrow in two
  colours, panicle, poppy, lavender) over an underlay; B2 perennial drift; B3 arching grasses; B4 shrub size range
  (0.4, 0.8, 1.2 and 1.6 m); B9 green-bridge strip (lavender, poppies, fountain grass and small shrubs held clear of a
  railing by the clearance rule).
- **Middle row (y = +1):** B5 groundcover with florets and leaf grain; B6 clipped bedding rings with bedding cushions
  round a salvia; B7 the Halifax-style leaf carpet bed (flat clipped silver, begonia, ageratum and pink bands with
  micro-florets round white hydrangeas).
- **North (y = +8):** B8 the Prince's-Island-style perennial bed: a layered shrub backdrop at 1.3 m spacing, drifts of
  perennials, panicles and grasses over a groundcover.
- **East (x = +17 to +26):** B10 the stepped-plaza corner: a 3 m rendered wall with a door and a window carrying a
  bougainvillea trained from a pot up and over its coping, a 1.1 m terrace wall with a parapet cascade, and geranium and
  box pots.

There are fifteen cameras:

- `front_corner`: an elevated oblique of the whole showcase;
- `top`;
- `eye_flower_heads`, `eye_specimen_close` (1.5 m, close on the hydrangea, yarrow and panicle), `eye_perennial_drift`,
  `eye_arching_grass`, `eye_shrub_mass`, `eye_lavender_rail`, `eye_groundcover`, `eye_bedding_band`, `eye_carpet_bed`,
  `eye_perennial_bed`, `eye_b8_rear` (looking south at the backdrop shrubs and the rear kerb), `eye_climber_wall` and
  `eye_cascade_pots`, all at 1.5-1.6 m.

## Version history

- **v001:** independent review FAIL, P0 = 0, P1 = 6, P2 = 9 (`evidence/v001/independent-review.md`): crumpled shrub
  masses, puffy carpet tubes with saw-tooth crests and mulch valleys, crumpled hydrangea heads, jagged yarrow plates,
  faceted feather-reed pods, and a placement rule that let a shrub cut its kerb.
- **v002 (this module):** reworks all six and adds the lavender, cup, panicle, bedding-cushion, pot-plant and
  wall-drape modules, the shrub size range and the rail clearance rule. See `VERSIONS.md` once it is reviewed.

## Open points

- v002 has not had an independent review. Its quality is the builder's reading of 480 px smokes and 1440 px
  close-ups.
- Shrub and hydrangea leaf skins are flat 4-vertex cards; up close they read as leafy but slightly angular.
- Lavender mounds read as grey needle cushions; salvia spires still show their whorl beads at 1.5 m.
- The bougainvillea is a draped shell with bract masses; it has no free-hanging branches away from the wall.
- The GLB has about 260 KB of headroom under the cap; a park family must budget its own carpets and drapes.
- Instances are glTF node instances, not `EXT_mesh_gpu_instancing`; a runtime loader should batch shared meshes.
