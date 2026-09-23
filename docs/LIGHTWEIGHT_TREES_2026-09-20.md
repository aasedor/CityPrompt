# Lightweight tree crown pilot

Goal: inexpensive vegetation placeholders that fit the kit. The user rejected
the first rounded photographic crowns as broccoli-like; those are not an
accepted design or reusable recipe.

## Revised recipe

The shared GlobeLandscapeTreeStand uses a branching skeleton, small folded
matte leaf clusters, muted greens and gaps through the crown. It requires no
new assets, animation or paid generation. Geometry is created once per mounted
species group and instanced, with no per-frame geometry work.

Each deciduous tree has 2,304 foliage triangles, 180 branch triangles and a
small tapered trunk. Three draws per occupied species group replace four.
Triangle count increases; no faster-frame-rate or low-end-device claim is made.
Existing metric dimensions, overall height, planting coordinates, rotations and
terrain bases remain authoritative. Stable tint survives reload. Vertex colours
use linear colour space. Palms and park-owned GLB tree assets remain unchanged.

Future streets, residual landscaping and procedural parks should reuse this
shared stand and metric profiles, preserving species constraints and circulation
clearances. This pilot does not approve every catalogue tree.

## Evidence

Disposable Currie project: 7e1e9037-b98c-4d18-8502-839160315869.
No saved project properties or geometry edited.

- PASS: reload renders 48 shared crowns in three species groups.
- PASS: final browser run has no page errors or grounding issues; street ready.
- PASS: free exact 3D preview includes revised foliage.
- PASS: 10 geometry-budget/envelope and species tests, TypeScript, changed-file
  ESLint. The 30 direct-capture tests also passed during this initiative.
- PENDING: user visual acceptance of the revised branching style.
- NOT TESTED: low-end devices, night lighting, every species at pedestrian
  height, and all park-owned tree models.

External evidence in C:/dev-artifacts/CityPrompt/: trees-branching-oblique.png,
trees-branching-export-preview.png and trees-branching-verification.json.
Earlier trees-new-* images belong to the rejected rounded version. Different
camera zoom distances are not a pixel-aligned comparison or performance test.
