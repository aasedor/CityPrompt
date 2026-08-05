# Park depth kit batch 1

Status: **staging only — not integrated into the live viewer**.

This bounded batch extends the reviewed basketball workflow with three
catalogue-referenced park kits. Every model is metric, uses a ground-contact
origin at `z=0`, and retains a fixed footprint for later mask alignment.

| Kit | Catalogue reference | Surface contract | Footprint | Triangles |
| --- | --- | --- | ---: | ---: |
| Tennis court cluster | `tennis_court_cluster_v0` — base, 60°, 90° | Depth only; drape supplies court surface and linework | 42 × 78 m | 12,828 |
| Skate park | `skate_park_v3` — base, 60°, 90° | Sculptural overlay; 3D supplies bowls and ramps | 52 × 42 m | 6,336 |
| Dog park | `dog_park_v1` — base, 60°, 90° | Depth only; drape supplies turf and paths | 42 × 30 m | 15,556 |

## QA views

### Tennis court cluster

- [Overview](tennis_overview.png)
- [Top](tennis_top.png)
- [Net and fence detail](tennis_detail.png)

### Skate park

- [Overview](skate_overview.png)
- [Top](skate_top.png)
- [Bowl detail](skate_detail.png)

### Dog park

- [Overview](dog_park_overview.png)
- [Top](dog_park_top.png)
- [Agility and canopy detail](dog_park_detail.png)

## Staged assets

- [`tennis-court-cluster-v0-depth-kit.glb`](../../assets/park-depth-kits/staging/tennis-court-cluster-v0-depth-kit.glb)
- [`skate-park-v3-depth-kit.glb`](../../assets/park-depth-kits/staging/skate-park-v3-depth-kit.glb)
- [`dog-park-v1-depth-kit.glb`](../../assets/park-depth-kits/staging/dog-park-v1-depth-kit.glb)
- [Machine-readable asset manifest](../../assets/park-depth-kits/staging/manifest.json)
- [Catalogue reference and mask contract](../../tools/park_asset_compiler/park_depth_batch1_reference_spec.json)

## Pilot gate

Before any kit is registered in the viewer, pilot it independently against its
actual archetype mask. Confirm center/rotation, footprint fit, the shared
`0.32 m` drape elevation, terrain seating, material response, and mobile/desktop
LOD. Do not integrate this batch wholesale.
