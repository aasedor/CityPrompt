# Amsterdam bell-gable semantic-clay pilot

This is the second architectural-clay building pilot. It derives a texture-free
conditioning model from the approved RLASM v6.1 Amsterdam Bell Gable House
geometry while preserving its complete front, sides, rear, roof, dormer,
openings, circulation, and occupied depth.

Status: `BUILDER_VERIFIED_FOR_USER_VISUAL_REVIEW`. The source RLASM keeper is
approved, but that approval does not automatically make this new clay export a
keeper.

| Front | Front corner |
| --- | --- |
| ![Front architectural-clay view](01-front.png) | ![Front-corner architectural-clay view](02-front-corner.png) |

| Aerial | Rear corner |
| --- | --- |
| ![Aerial architectural-clay view](03-aerial.png) | ![Rear-corner architectural-clay view](04-rear-corner.png) |

![True-top architectural-clay proof](05-true-top.png)

## Result

- Source geometry: `10-amsterdam-bell-gable-house-rlasm-v10`.
- Full RLASM reproduction: 15,347,168 bytes.
- Semantic-clay GLB: 3,719,376 bytes.
- Data reduction: 75.8%.
- Runtime geometry: 553 mesh objects and 51,060 polygons.
- Material payload: seven semantic materials, zero images, and zero textures.
- Bounds: `[-4.62, -9.16, 0.0]` to `[4.62, 8.02, 14.05]` metres.
- Review context removed: the evidence ground and street are not in the clay
  GLB.

The local binary and full export report remain outside Git at
`artifacts/amsterdam-bell-gable-semantic-clay-2026-09-01/`. The reviewed QA
views above are the intentional Git LFS deliverables.

## How this uses RLASM

Architectural clay is not a separate shortcut around RLASM. It is a deliberate
stop after the architectural model is proven:

1. Exact source lock and measured proportions are reused.
2. The complete unskinned envelope, bell-gable profile, closed roof graph,
   full-depth dormer cut, physical openings, supports, contacts, stairs, and
   occupied depth are reused.
3. Source-specific PBR textures, detailed UV work, and final optical polish are
   replaced by stable semantic roles: masonry, trim, roof, glass, timber,
   interior, and hardware.
4. Front, corner, aerial, rear, and true-top QA cameras are rerun on the clay
   export.

In RLASM phase terms, clay keeps Phases A, B, C, E, and the geometry/QA parts
of F. Phase D is intentionally reduced from final material authorship to
semantic material ownership. The clay candidate still needs its own visual
review and does not inherit Phase G keeper approval.

## LEGO scaling rule

This is a narrow fixed-identity canal house. City Prompt should not stretch
the bell gable or invent extra bays inside one house. Wider sites should repeat
complete house modules side by side, retaining one entrance, gable, roof,
dormer, and opening schedule per unit. That makes this archetype a good test of
the intended LEGO process: repeat whole semantic modules rather than deforming
identity-bearing geometry.

## Reproduction

The reusable exporter is
`tools/archetype_compiler/export_semantic_clay.py`. It now accepts RLASM Blend
sources, automatically excludes marked review context, emits a machine-readable
report, and produces the five-view clay QA set.

Machine-readable measurements and provenance are in `TRIAL_RESULT.json`.
