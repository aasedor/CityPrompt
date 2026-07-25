# Kinnaird-quality Lego pilot

This pilot moves the procedural builder from generic decorated massing into an
architecture-specific London heritage grammar. It uses the public
[Kinnaird House model by 99.Miles](https://sketchfab.com/3d-models/free-london-kinnaird-house-ff13d8c9407f4796886a689a758dc862)
as a quality bar, without copying its geometry or textures.

## Implemented

- `heritage_stone` facade system selected from catalogue prose.
- True `mansard` roof type rather than mapping mansards to generic gables.
- Modular podium, two alternating body floors, upper, crown and roof GLBs.
- Deep occupied multi-pane sash windows with dark frames, stone returns,
  architraves, lintels and triangular/segmental pediments.
- Rustication, string courses, quoins, pilasters, dentils, modillions, portico
  entrance and front balustrade.
- Slate roof skirt, dormers, four occupied corner pavilions, chimneys, lead top
  deck and lit lantern.
- GPT Image Portland-stone and Welsh-slate sources, converted locally to
  tileable albedo/normal/roughness sets at metric UV scale.
- 256 px AO bake on each delivery module and Cycles review renders.

## Verified pilot

| Metric | Kinnaird reference | Lego v6 pilot |
|---|---:|---:|
| Triangles | 53.9k | 106,702 assembled |
| Vertices | 30.1k | generated per modular export |
| Materials/textures | 4K baked PBR + two emissive maps | tiled PBR + interior atlas + AO |
| Delivery | bespoke low-poly asset | 6 reusable GLB modules + assembled review |
| Size | not reported on page | 9.1 MB assembled |
| Validation | reference viewer | PASS |

The pilot now reaches the same architectural-detail category: it has a composed
silhouette, layered construction depth, readable base/body/crown hierarchy and
lighting-aware materials. Kinnaird remains the better optimized asset and still
has richer unique baked relief. Production rollout should add a baked ornament
atlas and LOD1/LOD2 reductions rather than removing the hero geometry.

## Reproduce

```bash
python tools/archetype_compiler/generate_family.py \
  --archetype-id london_heritage_mansion_block \
  --variant-id london-heritage-mansion-portland-stone \
  --output build/lego-kinnaird-v6/portland-stone \
  --floors 5 \
  --textures tools/archetype_compiler/textures_kinnaird_v6 \
  --presentation-engine cycles \
  --presentation-samples 64
```

The generated GLBs stay under `build/` and are intentionally ignored by Git.
The tracked boards and raw review renders in this folder document the output.
