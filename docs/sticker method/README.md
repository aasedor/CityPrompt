# Sticker Method

This folder is the authoritative specification for high-fidelity,
image-locked 3D buildings and discretely scalable Sticker LEGO families.

## Release rule

A building is publishable only when:

- its unrounded independent architect-review mean is **greater than 95/100**;
- every rendered size tier scores at least **95/100**;
- every machine ownership, registration and export gate passes;
- no architectural hard-stop defect remains.

## Central rule

**A sticker is generated for its locked final 3D carrier and approved only as
part of the rendered 3D building.** It is never approved as a beautiful flat
image and then stretched onto approximate geometry.

Geometry owns silhouette, depth, roofs, openings and shadow-bearing
construction. Stickers own image-specific colour and fine surface identity.
PBR and optical layers own material response and glazing. Every visible
polygon—including returns, soffits, caps, entrances and subordinate roofs—has
exactly one semantic owner.

## Canonical documents

- [Production playbook](STICKER_METHOD_PRODUCTION_PLAYBOOK.md) — mandatory
  end-to-end workflow, LEGO rules, agent responsibilities and release gate.
- [Machine-readable contract](sticker_method_contract.json) — executable policy
  used by generation and review tooling.
- [95+ development record](STICKER_METHOD_95_PLUS_PLAN.md) — the V94/V95 path
  that established geometry-conditioned carrier-space stickers.
- [V97.3 scalable pilot](../reviews/catalogue-rollout-v97/functionalist-mill-sticker-lego-pilot/README.md)
  — first production-ready discrete Sticker LEGO family.
- [High-quality building memory](../HIGH_QUALITY_3D_BUILDING_MEMORY.md) — shared
  cross-pipeline lessons and hard stops.

## Proven modes

### Fixed landmark

Belle Époque Grand Magasin V95 established the locked-geometry Sticker Method:
198 fingerprinted carriers, zero exposed fallback faces and a 95/100 architect
score. This remains the reference for curved façades, domes, complex roofs and
unique select-and-place landmarks.

### Discrete Sticker LEGO family

Functionalist Brick Mill V97.3 established bounded size variation without
stretching:

| Tier | Footprint | Floors | Architect score |
|---|---:|---:|---:|
| Small | 35 × 30 m | 4 | 95 |
| Canonical | 50 × 40 m | 5 | 96 |
| Large | 65 × 50 m | 6 | 95 |

The unrounded mean is 95.3 with zero hard stops. Each tier uses whole 5 m wall
bays and 5 m floor bands at constant texel density. The entrance wing, annex,
pitched dormer, roof hips and chimneys stay fixed while ordinary bays, middle
floors and roof strips change capacity.

## What is prohibited

- billboard façades or a front-only skin on a generic box;
- arbitrary continuous or non-uniform building scaling;
- monolithic elevation textures stretched to new floor or bay counts;
- repeated entrances, ground floors, crowns or roof identity;
- painted doors where the reference requires a recessed tunnel;
- roof imagery on occupied floors;
- unowned blue-grey/clay polygons, returns, undersides or caps;
- generic glass or geometry covering sticker-owned windows and ornament;
- approval from a hero view without rear, roof and close-up inspection;
- release at an architect mean of 95.0 or below.

## Catalogue policy

Use finite, checkpointed batches. For every new archetype: lock reference
evidence, classify fixed and repeatable architecture, approve clay geometry,
generate carrier-conditioned stickers, pass machine audits, render the complete
review set, and obtain independent architect approval. A passing family proves
its own contract only; it does not waive review for the next building.
