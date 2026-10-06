# Affordable housing, catalogue and Calgary planning review

The five affordable concepts and 20 recent zoning-coverage models are integrated into the searchable City Prompt catalogue. This branch also carries the existing/proposed zoning work, eight approved Local Area Plan Urban Form layers, and twelve MDP/CTP maps. This is a GitHub review checkpoint; Render production has not been deployed.

The affordable concepts use original generated references and metadata. They are inspired by the goal of attainable housing, not replicas of Attainable Homes Calgary projects or an endorsement. The five architectural-clay assemblies have full independent source/geometry reviews. They retain authored dimensions when students resize their plots.

| New option | Authored housing program | Storeys |
|---|---|---:|
| Porchlight Townhouse Row | Four two-bedroom townhouses | 2 |
| Juniper Courtyard Cottages | Four 49 m² one-bedroom cottages, shared garden, individual patios | 1 |
| Stackyard Stacked Townhomes | Six two-bedroom homes, two access stairs and an upper gallery | 2 |
| Aspen Walk Apartments | Twelve one-bedroom apartments, two stairs and a lift core | 3 |
| Switchback Modular Studios | Twenty-four studios in permanent modular construction | 4 |

These are design teaching models, not cost estimates or permit-ready designs. Permanent modular construction does not automatically make Switchback a Manufactured Home. Juniper uses the Cottage Housing Cluster route where specifically listed, including discretionary R-CG s.527(2)(f). Exact model revisions, use groups, native heights, district limitations and unresolved conditions are retained in catalogue matching.

## Browser views of the affordable batch

The model views below are genuine City Prompt browser captures in the Google 3D environment. Flat colours are the reviewed architectural-clay stage; no photorealistic material pass is claimed.

### Porchlight

![Porchlight in City Prompt](porchlight-small.png)

### Juniper

![Juniper courtyard, exact revision six](juniper-v6-exact-garden-seams.png)

### Stackyard

![Stackyard in City Prompt](stackyard-small.png)

### Aspen

![Aspen in City Prompt](aspen-small.png)

### Switchback

![Switchback in City Prompt](switchback-small.png)

## Student zoning and policy workflow

Existing Calgary districts and student proposals remain separate. Students can draw proposed zones, choose bylaw designations or a custom zone, inspect permitted/discretionary catalogue candidates, and adjust opacity. The site remains a flat placement surface when its fill is made transparent.

![Proposed R-CG and affordable candidates](proposed-rcg-affordable-matches.png)

![Flat site with 35 percent opacity](flat-site-opacity-35.png)

All eight Local Area Plan selectors, visibility controls and Urban Form meaning cards were checked. The Currie test site is outside several plan extents; the app correctly warns about this. The Westbrook capture demonstrates a map inside its coverage area. These are educational map extractions, not surveyed parcel boundaries. Building Scale and special-policy overlays are outside this Urban Form collection.

![Westbrook policy overlay and explanation](westbrook-policy-meaning.png)

All twelve MDP/CTP map controls and legends were checked. City-wide maps preserve the City's artwork and provide map-level explanations; individual feature classification is only available for LAP Urban Form polygons. CTP Map 4 is absent from the source consolidation and is explained in the UI.

![MDP Urban Structure and original legend](mdp-1-meaning.png)

![CTP 5A network and original legend](ctp-1-meaning.png)

## Browser test record

Every one of the 25 recent models was selected in the catalogue, placed on a prepared site, tried on a small and larger plot, rotated, saved/reloaded, and inspected close up. Models retain native scale. Browser error logs were empty for the recorded trials. This finite scope does not include every historical asset in the repository or a hosted classroom load trial.

The trial found and repaired coplanar faces in the equipment yard, Scandinavian row and Juniper courtyard. A backend selection bug could return an older row of the same variant: plans now carry an exact revision and fail clearly when that revision is not installed. A regression test checks both database orderings and the missing-revision case. Six obstructed inspection-start cases were retested after a bounded free-space camera search was added.

The [independent browser addendum](browser-visual-addendum-2026-10-06-v004.md) covers the three repaired surfaces and six camera cases. Per-model full geometry reviews and GLB hashes are in the [canonical library](../../../seed/model-library/rlasm-architectural-clay/library.json). The [machine-readable release record](release-verification.json) contains dimensions, hashes and screenshot paths. Invalidated and superseded evidence remains in external local storage.

| Model | Small plot m | Larger plot m | Rotation | Browser exterior | Close inspection |
|---|---|---|---:|---|---|
| Neoclassical office | 33 × 36 | 42 × 43 | 25° | [View](office-rotated-larger-plot.png) | [View](office-close-shell.png) |
| Brick-and-bronze faculty office | 38 × 39 | 52 × 53 | 27° | [View](faculty-final-small.png) | [View](faculty-final-close-shell.png) |
| Brick-and-timber Courtyard Office | 18 × 16 | 36 × 34 | 27° | [View](courtyard-office-final-small.png) | [View](courtyard-office-final-close-shell.png) |
| Classic retail strip | 36 × 22 | 54 × 40 | 27° | [View](retail-small.png) | [View](retail-close-shell.png) |
| Corten & Timber Equipment Yard | 42 × 34 | 60 × 52 | 27° | [View](yard-v3-exact-small.png) | [View](yard-v3-exact-close-shell.png) |
| Meadow Court Childcare Centre | 32 × 30 | 50 × 48 | 27° | [View](childcare-small.png) | [View](childcare-close-shell.png) |
| Daylight sawtooth factory | 58 × 36 | 76 × 54 | 27° | [View](sawtooth-small.png) | [View](sawtooth-close-shell.png) |
| Folded-Roof Materials Recovery Hall | 40 × 29 | 58 × 47 | 27° | [View](recovery-small.png) | [View](recovery-close-shell.png) |
| Garden Mews Courtyard Housing | 26 × 26 | 44 × 44 | 27° | [View](mews-small.png) | [View](mews-close-shell.png) |
| Horizon Manufactured Home | 18 × 13 | 36 × 31 | 27° | [View](horizon-small.png) | [View](horizon-close-shell.png) |
| Industrial shed | 17 × 25 | 35 × 43 | 27° | [View](shed-small.png) | [View](shed-close-shell.png) |
| Tilt-up industrial building | 58 × 43 | 76 × 61 | 27° | [View](tiltup-small.png) | [View](tiltup-close-shell.png) |
| Maple Porch Manufactured Cottage | 18 × 11 | 36 × 29 | 27° | [View](maple-small.png) | [View](maple-close-shell.png) |
| Copperline Municipal Works Depot | 49 × 28 | 67 × 46 | 27° | [View](depot-small.png) | [View](depot-close-shell.png) |
| Narrow-lot Craftsman Cottage | 13 × 20 | 31 × 38 | 27° | [View](craftsman-small.png) | [View](craftsman-close-shell.png) |
| Prairie Fold Manufactured Home | 20 × 10 | 38 × 28 | 27° | [View](prairie-small.png) | [View](prairie-close-shell.png) |
| RNDSQR contextual townhouses | 28 × 19 | 46 × 37 | 27° | [View](row-small.png) | [View](row-close-shell.png) |
| Tilt-wall logistics warehouse | 154 × 92 | 172 × 110 | 27° | [View](warehouse-small.png) | [View](warehouse-close-shell.png) |
| Provincial Brick school | 36 × 44 | 54 × 62 | 27° | [View](school-small.png) | [View](school-close-shell.png) |
| Scandinavian townhouse row | 38 × 27 | 56 × 45 | 27° | [View](peaks-v6-exact-small.png) | [View](peaks-v6-exact-close-shell.png) |
| Porchlight Townhouse Row | 26 × 18 | 44 × 36 | 27° | [View](porchlight-small.png) | [View](porchlight-close-shell.png) |
| Juniper Courtyard Cottages | 31 × 28 | 49 × 46 | 27° | [View](juniper-v6-exact-small.png) | [View](juniper-v6-exact-close-shell.png) |
| Stackyard Stacked Townhomes | 27 × 23 | 45 × 41 | 27° | [View](stackyard-small.png) | [View](stackyard-close-shell.png) |
| Aspen Walk Apartments | 29 × 24 | 47 × 42 | 27° | [View](aspen-small.png) | [View](aspen-close-shell.png) |
| Switchback Modular Studios | 29 × 22 | 47 × 40 | 27° | [View](switchback-small.png) | [View](switchback-close-shell.png) |

## Verification and remaining limits

- Frontend release features: 83 tests across 10 files passed. Policy-plan features: 32 tests across 8 files passed. TypeScript type-check passed.
- Backend assembly and exact-revision checks: 189 passed.
- Source-lock/compiler checks for the five finite batches: 36 passed. Promotion/library checks: 18 passed, 7 skipped (optional fixture-dependent cases).
- A broader catalogue run exposed 19 failed assertions and one failed suite across five inherited catalogue/park test files. The same failures reproduce at starting commit `34076e0d4`: `reviewedEntrances`, `canonicalParkPlacement`, `catalogue`, `parkTrioAssets`, and `validationCatalogue`. This checkpoint does not claim a clean full-suite or production release.
- Fourteen inherited local-only clay entries remain unchanged and unapproved. The 25 additions pass hydrated promotion checks; the global no-trials publication gate still rejects those inherited entries. They must be reviewed separately before a production catalogue release.
- Browser tests used local Windows Edge. The 40-student Render trial, macOS/iPad checks, final materials and production data migration remain future work.

The source, reviewed GLBs and selected screenshots are intentional Git deliverables. GLBs and screenshots use Git LFS. Blender scenes, failed candidates, render experiments, local databases and credentials remain outside the repository.

Related detail: [zoning catalogue](../../CALGARY_ZONING_CATALOGUE_2026-10-05.md), [height/relaxation assessment](../../CALGARY_CATALOGUE_FLEXIBILITY_REASSESSMENT_2026-10-05.md), [Local Area Plans](../../LOCAL_AREA_PLAN_MAPS_2026-10-05.md), [MDP/CTP maps](../../CITYWIDE_POLICY_MAPS_2026-10-05.md).
