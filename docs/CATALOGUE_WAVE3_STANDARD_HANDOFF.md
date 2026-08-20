# Catalogue Wave 3 — classic everyday buildings

## Working location

- Repository: `C:\Users\wbesh\OneDrive\Desktop\Projects\CityPrompt-catalogue-wave1`
- Branch: `codex/catalogue-expansion-wave3-standard`
- Base: Wave 2 commit `e2899185f`
- State: local review checkpoint; not pushed
- Memory contract: `2026-08-02-clean-3d-no-prisms-runtime-v118`

## New families

1. Craftsman Brick Bungalow
2. Red-Brick Edwardian Foursquare
3. Plateau Stone Montreal Duplex
4. Victorian Brick Rowhouse Terrace
5. New-Law Brick Walk-Up Apartments
6. Mid-Century Balcony Apartment Slab
7. Classic Neighbourhood Strip Mall
8. Classic Corner Bodega Mixed-Use
9. Tilt-Up Light-Industrial Workshop
10. Provincial Brick Neighbourhood School

Each family contains a fixed assembled GLB, six semantic LEGO modules, eight review renders, preserved catalogue goalpost, clean PBR near/far maps, validation report, quality assessment, and comparison sheet. Catalogue thumbnails were not overwritten or promoted.

## Verification checkpoint

```powershell
python tools/archetype_compiler/assess_wave16_standard_families.py
python -m pytest tools/archetype_compiler/tests/test_wave16_standard_families.py -q
```

Expected result: ten geometry validations pass and `41 passed`. Quality status remains `review` until a person approves the comparisons.

## Review

- Local gallery: `http://127.0.0.1:5174/families/wave16-classic-everyday-review.html`
- Overview image: `frontend/public/families/wave16-classic-everyday-overview.jpg`

The two material-rich apartment families use an adaptive 832 px near / 416 px far texture ceiling so their assembled GLBs remain below the shared 9 MB delivery budget.
