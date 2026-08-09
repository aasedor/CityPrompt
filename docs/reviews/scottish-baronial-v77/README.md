# Scottish Baronial v77 - material and void contract

![Archetype, v76 and v77 comparison](01-v76-v77-material-void-comparison.png)

## Outcome

This bounded pass converts three useful catalogue phrases into executable 3D
requirements: `rusticated pink-grey granite ashlar`, `dark grey natural slate`
and `deeply recessed`. The production preflight checks the logical contract;
Blender repeats it against the texture library actually available at runtime.

V77 resolves granite on the primary walls, turrets, shaped gables and
crenellations, and Welsh slate on the main and turret roofs. The pointed gate is
no longer a decorated flat wall: the target mass is constructed around an open
11.73 m passage, the facade sheet is split around it, and the portal omits its
former back plane. All 17 runtime gates pass. The assembled model contains
149,730 triangles and used no paid API.

## What metadata contributes

Metadata is most useful as a semantic bridge between the image and the graph:

1. material phrases resolve to named PBR texture families;
2. architectural nouns identify fixed assemblies that must inherit them;
3. depth language such as `deeply recessed` becomes a minimum section depth;
4. the graph binds the passage to a target mass, portal and facade clearance;
5. preflight and Blender runtime fail instead of silently falling back.

The images remain the authority for geometry, colour calibration and visual
approval. Metadata cannot be allowed to overwrite contradictory evidence from
the selected street, oblique or aerial references.

## Remaining visual gap

This is review-only, not catalogue gold. The new controls prevent the exact
flat-material and bricked-passage regressions, but the turret drums still need
more visible stone-course registration and construction-depth window returns.
The roof also remains less articulated than the archetype: dormer arrays,
intersecting cross-gables, ridge and valley caps, chimney clusters, and the tall
crenellated gate-tower hierarchy are the next high-value authored kit.

The work reuses local granite and Welsh-slate textures. No new program,
subscription, model download or API charge is required for this phase.

## Reproduction

- Contract evaluator: `tools/archetype_compiler/generation_quality_contract.py`
- Production preflight: `tools/archetype_compiler/pipeline_preflight.py`
- Blender execution: `tools/archetype_compiler/blender_generate.py`
- Variant signature: `tools/archetype_compiler/architectural_signature_profiles.json`
- Pilot compiler: `tools/archetype_compiler/create_scottish_baronial_v77_pilot.py`
- Comparison publisher: `tools/archetype_compiler/create_scottish_baronial_v77_comparison.py`

The `.blend`, GLB and unreviewed render suite remain ignored under
`artifacts/material-void-v77/`.
