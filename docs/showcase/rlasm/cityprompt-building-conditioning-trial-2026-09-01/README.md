# CityPrompt building-conditioning trial

**Status:** complete single-sample research pilot

**Date:** 2026-09-01

**Subject:** approved external keeper `rlasm-calgary-inner-city-bungalow-v020`

This package compares three ways to condition an image model for an accurate
architectural render:

1. a measured coloured planning polygon;
2. the complete building geometry rendered as architectural clay; and
3. the complete RLASM building with its material-role assignments.

Each lane used the same locked source board, camera target, 4:3 output brief,
architectural inventory, appearance target, and prohibitions. Exactly one
built-in image-generation call was made per lane, with no retry, variant, or
cross-lane result conditioning.

![Guides and one-call results](review/guide-result-contact-sheet.png)

## Result

Architectural clay was the strongest default tradeoff. It retained the roof
graph, dormer, chimney, porch construction, footprint, and visible opening
cadence while allowing the image model to supply photographic materials,
planting, lighting, and neighbourhood context. Full RLASM remained strongest
for exact material-role placement and expected multi-shot/video stability.

The coloured polygon produced an attractive image but not the approved design:
it changed camera side, rewrote the roof and opening composition, and omitted
the required right roof-plane dormer.

This is directional evidence from one building and one stochastic call per
lane, not a statistical benchmark or a new keeper promotion. See
[`FINDINGS.md`](FINDINGS.md) for the lock-by-lock comparison and
[`PROMPTS.md`](PROMPTS.md) for the submitted prompt content.

## Package contents

- `guides/`: deterministic polygon, clay, and full-RLASM conditioning images;
- `generated/`: the three one-call image-model results;
- `references/`: the exact locked source board used by every lane;
- `review/`: static review boards, manifests, options, and contact sheets;
- `scripts/render_guides.py`: deterministic Blender guide renderer;
- `experiment-manifest.json`: input/output hashes, dimensions, controls, and
  recorded limitations.

The source `.blend` and `.glb` remain in external artifact storage and are not
promoted by this research package. All PNGs in this showcase are tracked
through the repository's existing `docs/showcase/**/*.png` Git LFS rule.
