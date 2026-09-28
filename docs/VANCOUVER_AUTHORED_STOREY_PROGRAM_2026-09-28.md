# Vancouver authored storey programme — 28 September 2026

The Vancouver balcony and podium tower now restores bounded vertical editing
without stretching the reviewed architecture. The original 16-storey
`vancouverism-tower-podium-clay-v004.glb` remains unchanged and is still used
when the building stays at its native height.

For taller choices, the runtime assembles three exact source bands:

- the complete 13 m, three-storey mixed-use podium;
- one complete 3.2 m residential storey, repeated as a discrete module; and
- the complete 4.2 m roof terrace, penthouse and plant level.

The accepted range is 16–40 storeys, with 25–40 presented as the recommended
Vancouverism range. The derived height is
`13 + (storeys - 3) × 3.2 + 4.2` metres. This produces 58.8 m at 16 storeys,
87.6 m at 25 storeys and 135.6 m at 40 storeys. Arbitrary height edits and
storeys outside the finite range remain unsupported rather than deforming the
model.

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

Source/runtime implementation and automated checks are complete. In-app
browser visual acceptance remains deliberately open; this checkpoint does not
approve the scaled tower for publication or imply that other fixed buildings
can be scaled.
