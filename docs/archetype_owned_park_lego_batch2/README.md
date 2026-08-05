# Archetype-owned park LEGO batch 2

This batch extends the park LEGO pilot with five deliberately different spatial
programs. Each family is authored from one exact catalogue render, owns a fixed
metric program, and combines role-specific surface skins with reusable 3D depth
assets. It does not use the master planner, AI draping, people, generic park
dressing, or large buildings.

![Five archetypes compared with three authored model angles](comparison-mobile.png)

## Families

| Catalogue archetype | Family | Fixed program | Receiving zone | Depth assets |
| --- | --- | ---: | ---: | --- |
| Tennis Court Cluster / Professional Grade | `park_tennis_cluster_v0` | 82 x 46 m | 84 x 48 m | net, 6 m fence, floodlight, spectator bleacher |
| Nature Play Area / Forest Adventure | `park_nature_play_v0` | 40 x 30 m | 42 x 32 m | water rill, balance log, log fort, willow tunnel, stepping stump, boulders |
| Pump Track / Asphalt Competition | `park_pump_track_v0` | 50 x 30 m | 52 x 32 m | continuous pump-track loop, start mound |
| Outdoor Fitness / Urban Calisthenics | `park_outdoor_fitness_v0` | 30 x 25 m | 32 x 27 m | calisthenics rig, parallel bars, sit-up bench, rings |
| Memorial Garden / Classical Formal | `park_memorial_garden_v0` | 50 x 40 m | 52 x 42 m | reflecting pool, fountain, memorial wall, urn |

The receiving zone is intentionally 2 m larger in each dimension. That gives
the authored program a stable one-metre tolerance at its perimeter without
stretching courts, equipment, or axial geometry to an arbitrary site polygon.

## Skin contract

Every family points to its own `adaptive-v1` material set under
`frontend/public/park-skins/<family-slug>/`. The compiler samples colour and
material statistics from the exact catalogue image, then creates stationary,
role-specific PBR maps for paver, lawn, asphalt, planting, safety surface, and
timber. Source pixels are not projected across the site, so this is neither an
AI drape nor a photo texture laid over the whole park.

The skin manifest records the exact source image, crop coordinates, scale,
procedural structure, and generated albedo/normal/roughness/AO files. Thousands
of future variants can therefore remain archetype-owned while sharing the same
runtime material roles and assembly mechanism.

## Site-aware assembly rules

1. Select one catalogue archetype and variant before geometry generation.
2. Preserve the family program in metres; rotate and translate it to the site,
   but do not non-uniformly stretch regulation or equipment geometry.
3. Use the authored ground grammar to organize paths, pads, planting, and open
   space, then place the family GLBs on that grammar for depth.
4. Compile only one park zone during validation. The result must report zero
   buildings, one park, and zero streets.
5. Keep people and large buildings out of the park family. They belong to later,
   separate render passes.
6. Reject generic fallback dressing whenever an archetype-owned family exists.

## Visual QA findings

- Tennis reads correctly as four complete courts, with nets, fencing,
  floodlights, and bleachers visible across three reference angles.
- Nature play initially read as a blue tube on a bright surface. It was revised
  to a shallow stone-edged rill on darker forest ground, while retaining logs,
  fort, willow tunnel, stumps, and boulders.
- Pump track initially read as a raised brown sculpture. It was revised to a
  flatter, dark asphalt figure-eight ribbon with restrained rollers and berms.
- Fitness retains four separate rubber exercise pads and four distinct equipment
  groups rather than collapsing into generic playground equipment.
- Memorial garden preserves the axial pool/fountain composition, symmetrical
  parterre paths, memorial wall, urns, and evergreen structure.

## City Prompt trial record

Project `Park Test 2` (`ba6a6fe3-d4d1-4bb4-88a1-e2e628d67ffb`) was reused as a
single-zone harness. Trials 6 through 10 replaced that one zone sequentially;
the master planner was never invoked. All five compiled with the status:
`0 buildings · 1 parks · 0 streets` and the archetype-owned skin/depth message.

One photorealistic Direct 3D capture was saved for each family. The project
render count increased from 4 to 9. Each render prompt froze the exact program,
forbade people and buildings, and prohibited adding, removing, moving,
multiplying, enlarging, or restyling program elements.

## Verification and next gate

The batch is ready for review as a bounded pilot, not yet for open-ended
catalogue generation. Before scaling, compare the five City Prompt renders with
the mobile sheet and accept or revise each family independently. The next batch
should exercise irregular site boundaries and orientation choices while keeping
the same one-archetype, one-zone, three-angle-QA checkpoint.

Meshy is not required for these five assets: their geometry is compact,
dimension-sensitive, and reproducible in Blender/procedural generation. Reserve
Meshy credits for organic or sculptural catalogue objects that fail a manual
silhouette and topology pilot.
