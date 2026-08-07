# Park LEGO Meshy object catalogue v3

This catalogue adds archetype- and variant-specific detail objects to the City Prompt park LEGO builder. It is not a generic prop library: each accepted GLB is routed to the exact park archetype variant whose reference image informed its form, material language, scale, and placement role.

## Batch result

- Programme: 32 park families, four variant briefs per family (128 planned objects)
- Generated: 126 objects
- Accepted and promoted: 118 GLBs
- Rejected or not completed: 10 objects
- Meshy credits used: 4,992 (balance 6,309 to 1,317)
- Runtime normalization: maximum 12,000 faces, 512 px PBR textures, metric dimensions
- Content constraints: no people and no large buildings

The two uncompleted Halifax objects were stopped when the programme reached its 5,000-credit allowance. They remain explicit rejects in the Wave D review manifest and are not referenced by City Prompt.

## Runtime methodology

1. The selected archetype and exact variant resolve to a reviewed asset entry in `parkMeshyArchetypeAssetsV3.ts`.
2. Each entry supplies its intended metric dimensions, normalized site coordinates, orientation, placement role, and whether it may repeat on oversized sites.
3. The park layer fits the complete object inside the drawn polygon using a minimum-oriented frame. An object that cannot fit is omitted rather than cropped or distorted.
4. Only objects marked `repeatOnOversize` may duplicate, and only when the site is sufficiently large.
5. Terrain height is sampled at each resolved placement before the metric GLB is mounted.

This preserves the archetype's elements and atmosphere while allowing the LEGO assembly to adapt logically to different polygon sizes and shapes.

## Visual QA

`meshy-park-object-catalog-v3-complete-sheet.png` is the single-sheet overview of all 128 archetype-variant briefs. It groups each park family into a four-variant row and marks promoted objects in green and rejected or incomplete objects in red.

The 16 mobile-friendly comparison sheets in this directory show, for every brief:

- the exact archetype reference image;
- the isolated multi-view generation input; and
- the normalized runtime render.

Green entries were promoted. Red entries remain external audit artifacts. Review manifests and rejection reasons are recorded in:

- `tools/park_skin_compiler/meshy_park_object_batch_v3a_review.json`
- `tools/park_skin_compiler/meshy_park_object_batch_v3b_review.json`
- `tools/park_skin_compiler/meshy_park_object_batch_v3c_review.json`
- `tools/park_skin_compiler/meshy_park_object_batch_v3d_review.json`

The raw Meshy experiments and Blender QA renders are intentionally kept outside the repository under `C:\dev-artifacts\3D-Maps`.
