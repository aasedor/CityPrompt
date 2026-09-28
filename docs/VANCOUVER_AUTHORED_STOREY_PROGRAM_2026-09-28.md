# Vancouver authored storey programme — 28 September 2026

The Vancouver balcony and podium tower now restores bounded vertical editing
without stretching the reviewed architecture. The original 16-storey
`vancouverism-tower-podium-clay-v004.glb` remains unchanged and is still used
when the building stays at its native height.

For taller choices, the runtime assembles three exact source bands:

- the complete 13 m, three-storey mixed-use podium;
- one complete 3.2 m residential storey, repeated as a discrete module; and
- the complete 4.2 m roof terrace, penthouse and plant level.

The accepted and recommended range is 16–40 storeys. The derived height is
`13 + (storeys - 3) × 3.2 + 4.2` metres. This produces 58.8 m at 16 storeys,
87.6 m at 25 storeys and 135.6 m at 40 storeys. Arbitrary height edits and
storeys outside the finite range remain unsupported rather than deforming the
model.

The plot can also change within a reviewed gentle footprint band. Its default
is 52 × 44 m, its minimum is 51.1 × 43.1 m, and its maximum is 57.5 × 47.5 m.
The complete modular assembly scales uniformly in plan from approximately
1.06× to 1.19×; balconies, windows, setbacks, podium and roof keep their
relative proportions.

`tools/archetype_compiler/blender_extract_vertical_module.py` performs the
reproducible GLB clipping. The machine-readable source planes, dimensions,
file sizes and SHA-256 locks are in
`seed/model-library/rlasm-architectural-clay/vancouverism-classic-storey-program-v001.json`.
`scripts/vancouver_tower_storeys.py` verifies those locks offline and can add
the three module rows and objects to a loopback-only City Prompt installation.

The loopback runtime API was checked against the installed, hash-verified
modules. It returned the unchanged single assembly at 16 storeys, a 24-instance
podium/floor/roof plan at 25 storeys, and a 39-instance plan at 40 storeys. The
assembled heights were 58.8 m, 87.6 m and 135.6 m respectively; 41 storeys was
rejected. Offline Blender QA also inspected the 25- and 40-storey assemblies
from aerial and walking-height angles.

Source/runtime implementation and automated checks are complete. A disposable
student project then placed the tower, changed it to 25 storeys at the minimum
footprint, changed it to 40 storeys at the maximum footprint, and reopened the
saved project. Both detailed models mounted without console or page errors and
retained the authored podium, roof, balconies and window rhythm. This local
browser acceptance does not publish the tower or imply that other fixed
buildings can be scaled.
