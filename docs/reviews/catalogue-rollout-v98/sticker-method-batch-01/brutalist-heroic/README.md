# Brutalist Heroic - Sticker Method V98

Building 9 of Sticker Method Batch 01 is approved as one fixed landmark. The
50 x 42 m canonical tier scored 95.05 in independent architect review with
zero hard stops. No alternate size or arbitrary resizing is approved.

## Locked evidence

- Archetype: `brutalist_institutional::brutalist_heroic`.
- Exact references: `variant_0.png`, `variant_0_angle_60.jpg`, and
  `variant_0_angle_90.jpg`; hashes are locked in `release-evidence-scaffold.json`.
- Final geometry: canonical `ed97781e...b8b07`, 245 meshes.
- Approved tier: 50 x 42 m, two fixed occupied storeys.
- Fixed identity: heroic blind upper concrete volume, deep projecting light
  boxes, four articulated front pilotis, glazed recessed base, panelized side
  tower, two sunken roof courts, and three fixed rooftop service volumes.
- Sticker hard stops: every visible face exactly once; no fallback; physical
  glass separated from subdued interior cards; metric board-form scale; no
  square/checker cadence; explicit terminal and piloti collar ownership; roof
  membrane and dark courts remain disjoint.

## Evidence

- `01-exact-reference-comparison.png` - exact front identity and approved render.
- `02-oblique-and-detail-comparison.png` - concrete, light boxes, pilotis and glazing.
- `03-roof-and-court-comparison.png` - roof membrane, courts and service volumes.
- `visual-approval.json` - independent score and fixed-landmark approval.
- `machine-evidence.json` - locked sources, renders, face audit and validation.

## Reproduction commands

```powershell
pytest -q tools/archetype_compiler/tests/test_brutalist_heroic_geometry_v98.py tools/archetype_compiler/tests/test_brutalist_heroic_v98_assets.py tools/archetype_compiler/tests/test_brutalist_heroic_compiler_v98.py
python -m py_compile tools/archetype_compiler/create_brutalist_heroic_v98_review.py
python tools/archetype_compiler/create_brutalist_heroic_v98_review.py
git diff --check
```

The publisher refuses changed references or source packages, altered formal
evidence, failed preflight or validation, any surface-audit failure, a score not
strictly above 95, or a nonzero hard-stop count.

## Fixed-landmark contract

The user selects and places this 50 x 42 m landmark. Continuous, vertical,
depth, and nonuniform scaling are forbidden. There is no extended tier. A new
size requires a separately authored geometry and Sticker Method review.

## Known bounded limitation

The recessed glass and rear undercroft are intentionally dark, matching the
reference hierarchy. The assembled export has 517 materials and should receive
later consolidation without changing visible ownership or the reviewed result.
