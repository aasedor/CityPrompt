# Functionalist mill V97 — Sticker LEGO pilot

This pilot tests whether the geometry-conditioned Sticker Method can produce the same archetype at several LEGO-compatible sizes without stretching a complete façade image.

## Result

**Production verdict — PASS (95/100).** V97.3 is approved as the first production-ready, discretely scalable Sticker LEGO building family for the validated 35 × 30 m / 4-floor, 50 × 40 m / 5-floor, and 65 × 50 m / 6-floor tiers. It preserves whole 5 m façade bays, whole 5 m floor modules, constant texel density, a singular recessed entrance wing, closed modular hip roofs, and fixed roof/annex identity without non-uniform skin stretching. Approval applies only to these bounded snapped tiers and this architectural contract; it does not authorize arbitrary continuous resizing or automatic catalogue-wide rollout without archetype-specific visual review.

The pilot produces three discrete, catalogue-valid tiers:

| Tier | Dimensions | Floors | Sticker carriers |
|---|---:|---:|---:|
| Small | 35 × 30 m | 4 | 149 |
| Canonical | 50 × 40 m | 5 | 232 |
| Large | 65 × 50 m | 6 | 335 |

All tiers use whole 5 m bays and whole 5 m floor bands. Window proportions and texel density remain constant. The system adds or removes middle-floor cells, ordinary wall bays, and roof strips; it does not resize the complete building skin.

Fixed identity assemblies remain singular at every tier: the narrow 5 m recessed stair/entrance wing and its finished eave, the recessed arched entrance tunnel, the two-storey rear service annex, the pitched timber roof dormer, top cornice role, two three-face hip ends, and three brick chimneys. Ground, middle, top, subordinate-roof, and main-roof roles are disjoint.

## Sticker sources

- Exact catalogue references: `variant_1.png`, `variant_1_angle_60.jpg`, and `variant_1_angle_90.jpg` under `functionalist_brick_industrial`.
- Two generated rectification calls produced a portal-free five-by-five façade atlas and a dedicated entrance-bay source.
- Preparation is crop-only for the entrance and procedural for slate/brick returns. Non-uniform post-generation scaling is forbidden.
- Every locked polygon has exactly one semantic surface owner. Uncovered clay, duplicate owners, roof-on-wall placement, and partial bays are hard failures.

## Review boards

- `01-canonical-archetype-comparison.png` compares the canonical render directly with the exact street reference.
- `02-lego-size-matrix-street.png` shows all three finished tiers at the same review role.
- `03-lego-size-matrix-roof.png` proves closed hips and roof continuity.
- `04-oblique-reference-and-extremes.png` compares the exact oblique reference with both size extremes.

The recommended product behavior is discrete polygon fitting: snap the footprint to whole 5 m bays and choose a valid whole-floor tier. Arbitrary continuous stretching remains prohibited because it would distort windows, brick scale, entrances, and roof identity.

## Verification

- Production preflight: pass for all three tiers.
- Locked-surface audit: pass, zero uncovered faces.
- Focused pytest contract: 6 passed.
- Blender 5.1 EEVEE review sets: nine views per tier.
- Independent architect gate: small 95, canonical 96, large 95; overall 95; no hard-stop defect.
