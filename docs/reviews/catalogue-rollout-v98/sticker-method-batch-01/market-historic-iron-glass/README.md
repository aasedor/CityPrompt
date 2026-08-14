# Historic Iron-and-Glass Market Hall - Sticker Method V98

Building 10 of Sticker Method Batch 01 is approved as one fixed landmark. The
45 x 60 m canonical tier scored 95.14 in independent architect review with
zero hard stops. No alternate size or arbitrary resizing is approved.

## Locked evidence

- Archetype: `food_hall_market_hall::market_historic_iron_glass`.
- Exact references: `variant_0.png`, `variant_0_angle_60.jpg`, and
  `variant_0_angle_90.jpg`; hashes are locked in `release-evidence-scaffold.json`.
- Final geometry: canonical `5b200136...fa729a`, 1,177 meshes.
- Approved tier: 45 x 60 m, one occupied hall plus two fixed partial galleries.
- Fixed identity: open cavernous nave, physical heritage-green cast-iron frame,
  barrel glazing and fans, ridge lantern, brick-and-stone side aisles, recessed
  timber stalls, and asymmetric slate-left/zinc-right aisle roofs.
- Sticker hard stops: every visible face exactly once; no fallback; physical
  glass separated from bounded occupied cards; roof and soffit faces disjoint;
  explicit terminal ownership; no card leak or arbitrary texture stretching.

## Formal score

- Archetype identity: 28.20
- Geometry and massing: 19.12
- Sticker and material fidelity: 19.06
- Coverage and registration: 14.16
- Release and landmark readiness: 14.60
- Total: **95.14**, with zero hard stops

## Evidence

- `01-exact-reference-comparison.png` - exact front identity and approved render.
- `02-oblique-and-detail-comparison.png` - iron frame, glass, masonry and stalls.
- `03-roof-reference-comparison.png` - barrel, lantern and asymmetric aisle roofs.
- `04-nave-and-rear-comparison.png` - cavernous nave, galleries and constrained rear.
- `visual-approval.json` - independent score and fixed-landmark approval.
- `machine-evidence.json` - locked sources, renders, face audit and validation.

## Reproduction commands

```powershell
pytest -q tools/archetype_compiler/tests/test_market_historic_iron_glass_geometry_v98.py tools/archetype_compiler/tests/test_market_historic_iron_glass_v98_assets.py tools/archetype_compiler/tests/test_market_historic_iron_glass_compiler_v98.py
python -m py_compile tools/archetype_compiler/create_market_historic_iron_glass_v98_review.py
python tools/archetype_compiler/create_market_historic_iron_glass_v98_review.py
git diff --check
```

The publisher refuses changed references, geometry, source packages, generated
outputs, provenance or formal evidence; failed preflight or validation; any
surface-audit failure; a score not strictly above 95; a nonzero hard-stop count;
or any semantic change to catalogue orders 1-9.

## Fixed-landmark contract

The user selects and places this 45 x 60 m landmark. Continuous, vertical,
depth and nonuniform scaling are forbidden. The one hall, two partial galleries,
open nave, barrel, lantern and roof identity kit remain indivisible. A new size
requires separately authored geometry and Sticker Method review.

## Known bounded limitations

Rear and service surfaces are constrained completions of the exact front,
oblique and aerial evidence. The assembled export has 1,247 materials and is
8.1 MB against an 8 MB texture budget; consolidation is a nonvisual follow-up.
