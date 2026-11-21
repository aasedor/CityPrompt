# Snug footprints — newest building batch, 29 October 2026

The user requested footprints as snug to buildings as possible, limited to the newest batch.
This follow-up supersedes the unchanged-plot limitation in the earlier building-only review.
18 exact retained models now use their actual geometry bounds for native dimensions, default
plots, minimum sizes, backend compilation fit and packaged quantitative-report facts.

No GLB or seed library source was edited. Original source hashes remain identical. Floors,
roof forms, podiums, projecting steps and other retained geometry remain at scale 1.0.
Each horizontal bound rounds outward to the next 0.1m after 0.02m TOTAL numeric tolerance:
about 1–6cm per side. This is an architectural bounding rectangle, not a zoning setback or
an irregular floor-plate/roof silhouette. Internal voids within that rectangle remain empty.

Scope: 18 exact candidates from `buildingOnlyContracts.json`. The held Mews source and older
batches remain unchanged. No automatic saved-project migration happens on load. An explicit
new model selection fits its new rectangle in the same centre/orientation through one validated
save; older oversized plots have Fit footprint to building. Place another starts snug.
Missing-revision legacy saves retain their coordinates on unchanged Apply building.

Runtime target: deployment-version base `62e31ad621238c6ce1da62934710128831df3b5e` plus
`codex/building-only-20261029`; browser port5175, backend port8002. Local patch only; no push,
publication or live deployment. Both frontend extraction and backend fit/data must ship together.

Evidence: https://drive.google.com/drive/folders/1D8BLu_6GwmwHzuftQb8_ylUohqQvuV6i
Local originals: `D:/CityPrompt-review-artifacts/building-only-20261029/snug-footprints`.

## Measured exact candidate matrix

The following per-variant records complete the changed C1/C2/C9/B1 scope of the runtime review
in `docs/BUILDING_ONLY_RUNTIME_REVIEW_2026-10-29.md`; its unrun terrain/access gates remain open.

| Exact candidate | Previous default (m) | Retained native X/Z (m) | Snug default/minimum (m) | Offline exact hash/native fit |
| --- | --- | --- | --- | --- |
| `clay-calgary-cbe-brutalist-hq-clay-v004` | 88 Ã— 93 | 43.300 Ã— 40.600 | 43.4 Ã— 40.7 | PASS |
| `clay-cmu-dock-warehouse-clay-v006` | 60 Ã— 48 | 30.190 Ã— 28.425 | 30.3 Ã— 28.5 | PASS |
| `clay-gastown-heritage-commercial-clay-v003` | 85 Ã— 65 | 27.900 Ã— 25.500 | 28 Ã— 25.6 | PASS |
| `clay-halifax-georgian-colonial-clay-v003` | 55 Ã— 51 | 22.286 Ã— 20.242 | 22.4 Ã— 20.3 | PASS |
| `clay-halifax-waterfront-warehouse-clay-v006` | 63 Ã— 47 | 26.840 Ã— 19.400 | 26.9 Ã— 19.5 | PASS |
| `clay-led-grow-block-clay-v007` | 33 Ã— 34 | 22.060 Ã— 23.060 | 22.1 Ã— 23.1 | PASS |
| `clay-slab-balcony-tower-clay-v007` | 41 Ã— 41 | 26.400 Ã— 26.400 | 26.5 Ã— 26.5 | PASS |
| `clay-toronto-bay-and-gable-house-clay-v004` | 27 Ã— 29 | 8.400 Ã— 16.240 | 8.5 Ã— 16.3 | PASS |
| `clay-arched-mill-mixed-use-clay-v005` | 41 Ã— 37 | 22.760 Ã— 22.680 | 22.8 Ã— 22.8 | PASS |
| `clay-brick-podium-condo-tower-clay-v006` | 57 Ã— 47 | 44.900 Ã— 33.240 | 45 Ã— 33.3 | PASS |
| `clay-campus-shed-office-clay-v009` | 52 Ã— 43 | 43.955 Ã— 34.140 | 44 Ã— 34.2 | PASS |
| `clay-courtyard-primary-school-clay-v009` | 49 Ã— 54 | 40.400 Ã— 46.400 | 40.5 Ã— 46.5 | PASS |
| `clay-garden-court-senior-residence-clay-v006` | 93 Ã— 91 | 74.500 Ã— 65.000 | 74.6 Ã— 65.1 | PASS |
| `clay-baronial-railway-hotel-clay-v006` | 82 Ã— 76 | 61.600 Ã— 56.743 | 61.7 Ã— 56.8 | PASS |
| `clay-ctrain-elevated-station-clay-v004` | 83 Ã— 103 | 76.400 Ã— 96.000 | 76.5 Ã— 96.1 | PASS |
| `clay-energy-centre-clay-v010` | 48 Ã— 42 | 36.110 Ã— 34.130 | 36.2 Ã— 34.2 | PASS |
| `clay-old-montreal-limestone-commercial-clay-v004` | 131 Ã— 83 | 108.830 Ã— 51.160 | 108.9 Ã— 51.2 | PASS |
| `clay-plus15-glass-office-tower-clay-v006` | 55 Ã— 86 | 37.700 Ã— 65.850 | 37.8 Ã— 65.9 | PASS |

## Bounded browser review

Codex agent simulation, Edge1681x1280, mouse/keyboard; prepared level vacant QA project
`2715f44e-9ca9-4fc7-976f-350302496ccc`. This is not an independent student usability study.

| Case / gate | Actual result |
| --- | --- |
| C1 identity | PASS for exact18 hydrated source SHA/count/bbox tests, unchanged originals |
| C2 native dimensions/transform | PASS: new native dimensions and backend scale1 for all18 in tests; no undersized fit |
| B1 native runtime | Browser PASS for Brick repair45Ã—33.3m, OldMontreal replacement108.9Ã—51.2m, Toronto fresh8.5Ã—16.3m |
| C6 persistence | Both OldMontreal and Toronto reloaded visibly; read-only DB proves saved dimensions and scale[1,1,1] |
| C9 controls | Fresh Toronto catalogue card/default drop; Brick Fit footprint; OldMontreal atomic explicit replacement |
| C8 capture | Native screenshots and provided original free source PNG exported; actual Download action NOT TESTED |
| Legacy unchanged Apply | Tested matching/absent saved revision preserves coordinates; independent review caught missing-revision case before fix |
| All18 UI drop/reload at new minima | NOT TESTED this follow-up; prior road-removal run loaded/saved all18 with oversized test plot |
| C3/C5/B2-B5 terrain/access | NOT TESTED in full. Prepared-level appearance only; no new access/route acceptance |
| C4/C7 async/failure | NOT TESTED in this browser run; existing shared code and source immutability tests retained |
| Undo/Redo, slope/natural ground, tight street adjacency, mixed park/street scene | NOT TESTED; not claimed by these screenshots |
| S1-S4/P1-P4 | N/A: building footprints only |

Quantitative dimensions are envelope facts, not surveyed floor plates or guaranteed usable area.
The native-model contract generation changes exactly18 records, dimensions only; asset/variant/
revision IDs and old families stay identical. The prebuild checks enforce that companion.

## Verification

- 181 frontend tests in8 relevant files passed, including19 actual-GLB tests. After the review's
  missing-revision guard fix,150 selection/control/geometry tests passed again in4 files.
- Frontend `npm run type-check`: exit0.
- Backend237 envelope/planner tests passed; after packaged facts update,43 envelope/model-contract
  tests passed. These sets overlap and are not an additive unique-test count.
- Independent read-only code review: no P0/P1; one missing-revision P2 fixed with red/green
  regression. Reviewer independently confirmed20 footprint tests and the fix.
- Production build status is recorded separately in build-result.txt. Initial preflight found
  stale packaged dimensions, now regenerated by check-model-contract.mjs --write. A second
  attempt correctly rejected LFS-pointer example images; the hydrated-assets build then ran out of D: space while copying public assets. A separate
  production code-bundle check uses the shared hydrated public root with public copying off;
  it does not establish a completed full asset package.
- Review screenshots are SCREENSHOT files. The exact3D source PNG contains no AI changes.
  No AI jobs, paid generations or video outputs were requested or created in this follow-up.
- Before/after frames use different camera framing; they are not pixel-registered comparisons.

Decision: scoped snug-footprint patch verified for the stated cases. Mews still requires a new
isolated reviewed asset; Energy Centre's existing architectural P1 remains open. No live deployment.

## Build-storage limitation

The full-asset build left a generated partial copy at
`D:/CityPrompt-review-artifacts/building-only-20261029/snug-footprints/production-dist`.
D: reached 0GB free. Automatic approval review rejected removal with reason "blocked by policy".
No alternative deletion or move was attempted. The folder requires manual deletion by the user.
Final evidence/receipts are stored separately at
`C:/dev-artifacts/CityPrompt/snug-footprints-20261029-final/evidence`; public originals are untouched.

Production code bundle: Vite exit0,3842 modules,16.22s with public-copy disabled. This is not a completed deployment package: full asset copying ran out of space and existing source-imported demo media remain LFS pointers in this checkout. See build-result.txt.
