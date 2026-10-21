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
- **No coplanar faces:** lobes interpenetrate, and adjacent bedding bands meet in a soil valley.

### API

**Setup**

| function | what it does |
|---|---|
| `pk_palette(PALETTE)` | Adds the kit roles (`pk_leaf`, `pk_pink`, and so on) without overriding any role the family already defines. |
| `kit = PlantKit(module, instancing=True)` | Creates the prototype registry. |
| `kit.place(proto, x, y, z, rot, s)` | Places a prototype. With instancing on, it becomes linked instances; with instancing off, it is merged per role. |
| `kit.flush()` | Merges the batches and records the counts. Call it once after planting. |
| `kit.stats()` | Returns the plant, node and prototype counts. |

**Prototype plants** (each returns a proto to place)

- **`flower_head_cluster(kit, name, head=...)`**: a leafy mound of keeled, blunt-ovate leaves springing from a small
  core, with stems carrying smooth heads. `head` is one of:
  - `'daisy'`: a scalloped, drooping ray disc round a boss;
  - `'spike'`: separated whorl beads;
  - `'umbel'`: a flat-topped floret plate;
  - `'mophead'`: hydrangea balls on a shrubby mound.
- **`arching_grass(kit, name, ...)`**: 40 to 70 keeled, tapering blades arching from a dark buried crown. It can add
  feathery multi-lobe plumes.
- **`shrub_mass(kit, name, ...)`**: a broad buried base lobe, overlapping billowy lobes (lighter at the crown) and
  sunlit tip lobes.

**Beds and carpets** (unique geometry, merged)

- **`pk_bed(name, outline, soil_z, kerb=...)`**: a granite kerb ring (smooth around, crisp at the profile corners)
  and a mulch surface.
- **`groundcover(name, poly, z, kerb=..., dots=...)`**: a Delaunay heightfield carpet with soft-billow cushions,
  clipped to the bed minus the kerb. Its edge dives under the soil, so the edge is clean with no teeth. It can add
  floret dots.
- **`bedding_band(name, outline, z, d_out, d_in, role, dots=...)`**: one Victorian carpet-bedding ribbon between two
  inward offsets. Neighbouring bands meet in a soil valley.

**Placement and outlines**

- **`perennial_drift(kit, poly, z, mix, kerb=...)`**: assigns Poisson-spaced plants to species by low-frequency noise
  fields, so species form interlocking drifts, not salt-and-pepper. It never places a footprint over the kerb.
- **`pk_scatter(poly, spacing, kerb, margin, seed)`**: Poisson-disc points inside the bed outline minus the kerb and
  the item's footprint.
- **`pk_ellipse`, `pk_leaf`, `pk_blob`, `pk_region`**: bed outlines, and the plantable region inside a kerb.

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

Smoke build at 480 px and 8 samples, 149 plants on 463 instance nodes:

| | instanced (shipped) | joined (`--no-instancing`) |
|---|---|---|
| Showcase GLB | 3,338,232 B (under the 4 MiB cap) | 15,861,936 B (fails the cap) |
| Stored triangles | 143,020 | 667,084 |
| Plant bytes | 1,691,114 | 14,214,818 |
| Plant bytes per plant | about 11.3 KB, including the shared prototypes | about 95 KB |
| Each further plant | about 1.9 KB: 3.1 nodes at about 615 B each, mostly glTF extras | about 95 KB |

The joined run rendered `front_corner` only, for the size comparison. The build passes `build_valid` with
`PASS_CARRIER_APERTURES` and a round-trip delta of 0.0.

### Rules for park families

- Instance every prototype plant.
- Merge anything under about 20 triangles per role, such as dots and florets, because a node costs more than its
  geometry.
- Budget the carpets: they are unique geometry and, with the kerbs, they are most of the non-plant bytes.
- Copy `keep_instances()` and the dedupe of the triangulate loop into the family `build.py`. A one-line change to
  `clay_core.deliver()`, skipping `rlasm_instance` objects in the join, would remove the need for the shim. That is a
  separate decision.

## Running it

```
python tools/clay_planting_kit_showcase/build.py --version 1 --output <dir> --resolution 480 --samples 8
python tools/clay_planting_kit_showcase/build.py --version 1 --output <dir2> --cameras front_corner --no-instancing   # size comparison
python tools/clay_planting_kit_showcase/phone_board.py --candidate <dir>
```

The build writes `evidence/planting-kit-size.json`, with the GLB bytes, stored and scene triangles, nodes, plants and
prototype triangles.

## Layout and cameras

There are eight kerbed beds on a 29 × 22 m lawn with two gravel walks:

- **South row:** flower heads, perennial drift, arching grass, shrub mass.
- **Middle row:** groundcover, bedding rings, the Halifax-style leaf carpet bed.
- **North:** the Prince's-Island-style perennial bed.

There are ten cameras:

- `front_corner`: an elevated oblique of the whole showcase;
- `top`;
- eight eye-level views at 1.6 m, one per bed.

## Open points

- The showcase has not had an independent review. Its eye-level quality is only the builder's reading of a 480 px
  smoke.
- Shrub masses can still read as lumpy topiary rather than loose foliage at 1440 px.
- Daisy heads are small at the distance of the bed cameras.
