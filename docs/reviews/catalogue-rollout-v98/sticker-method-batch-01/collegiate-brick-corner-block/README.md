# Collegiate Brick Corner Block — Sticker Method V98

Building 8 of Sticker Method Batch 01 is approved for two bounded horizontal
LEGO tiers. The 42 × 38 m canonical tier scored 95.20 and the 49 × 38 m
extended tier scored 95.05, for an exact family mean of 95.125. The independent
architect and Sticker Method reviewer found zero hard stops.

## Locked evidence

- Archetype: `graduate_family_housing::collegiate_brick_corner_block`.
- Exact references: `variant_0.png`, `variant_0_angle_60.jpg`, and
  `variant_0_angle_90.jpg`; hashes are locked in `release-evidence-scaffold.json`.
- Final geometry: canonical `a3dc8607…b740`; extended `62d7b04a…8bd7`.
- Canonical tier: 42 × 38 m, five fixed storeys.
- Extended tier: 49 × 38 m; adds one complete 7 m horizontal module.
- Fixed identity: perimeter courtyard, singular bronze corner oriel and crown,
  adjacent recessed entrance and pale blades, all courtyard elevations, and
  layered gravel/dark-membrane roof with bounded screened plant.
- Sticker hard stops: every visible face exactly once; no generic fallback;
  physical glass separated from 4×2 interior cards; 2.4 m brick UV; pale datum,
  sill, underside, and terminal contracts; disjoint gravel and membrane roofs.

## Evidence

- `01-exact-reference-comparison.png` — exact identity beside both tiers.
- `02-corner-reference-comparison.png` — corner oriel, entry and datum registration.
- `03-roof-reference-comparison.png` — courtyard and disjoint roof finishes.
- `04-sticker-and-size-comparison.png` — constant texture and aperture scale.
- `visual-approval.json` — independent score and bounded approval.
- `machine-evidence.json` — render hashes, face audits and validation evidence.

## Reproduction commands

```powershell
pytest -q tools/archetype_compiler/tests/test_collegiate_brick_corner_block_geometry_v98.py tools/archetype_compiler/tests/test_collegiate_brick_corner_block_v98_assets.py tools/archetype_compiler/tests/test_collegiate_brick_corner_block_compiler_v98.py
python -m py_compile tools/archetype_compiler/create_collegiate_brick_corner_block_v98_review.py
python tools/archetype_compiler/create_collegiate_brick_corner_block_v98_review.py
git diff --check
```

The publisher refuses missing manifests, views, validation, preflight, surface
audit, source hashes, reference hashes, or an approval mean not strictly above
95 with zero hard stops.

## LEGO contract

The extended tier inserts one complete 7 m horizontal courtyard-ring module.
It does not stretch brick, openings, pale datums, floor height, depth, roof or
interior cards. The singular bronze corner oriel/crown, recessed entry, complete
courtyard and screened roof kit remain fixed.

## Known bounded limitations

Residential glazing and occupied depth are darker than the exact reference;
secondary/rear completion is constrained rather than exact; membrane variation
and roof plant remain restrained. The exports also exceed preferred triangle,
material and texture budgets. These are recorded deductions and optimization
work, not release blockers for the two reviewed tiers.
