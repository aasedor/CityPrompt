# Timber bridge route pilot — runtime review — 2026-10-30

Local classroom pilot only. Based on docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md.
Exact variant: urban_pedestrian_footbridge / timber_covered_bridge_route_v1.
Original source v004 SHA256 0dbeb2731dbe390ead3b053d65853262887454aecaf36fb8a9d16a5b66a195ad is unchanged.
Recipe revision timber-v004-bridge-only-1 / 4275b01adc0228982522fa7e5201d026e5823ee264f549e4ebda29ef56ebeeed.
Five derived modules and semantic/material provenance are locked in tools/drawn_bridge_routes/provenance/timber-v004-bridge-only-1.json.
Compiler/source units: 3669ff4b7, 686db04f4, ab3c88427, d8855bb87; frontend delivery commit follows this review.

Supported: straight two-endpoint 32–240m route on prepared level ground;6m envelope,4m clear walk,3.45m raised deck,18 compact stair treads at each end. Width/height/end structures stay fixed; middle bays repeat with a small longitudinal remainder adjustment. Native geometry excludes water,banks,remote guards and broad context paving. Old fixed saves retain original identity. Discovery replacement is development-only; production publication remains gated.

## Gate results

| Gate | Status | Exact evidence |
| --- | --- | --- |
| C1 identity | PASS scoped | Exact source/module hashes; mirrored manifest/compiler locks; ordinary picker selects new route ID; old fixed ID remains resolvable. |
| C2 dimensions | PASS scoped | 45/80/150m metric tests, reverse/oblique routes; min32/max240 validator bounds. Browser authored oblique122m,short39m,extended roughly83m,and another short route by double-click. Native width/height unchanged. |
| C3 support | PASS prepared-level only | Browser stairs at grade; retained original end pier/abutment feet extended to grade. No terrain/hillside claim. |
| C4 freshness | PASS scoped | Draft uses native modules without forged persisted recipe. Saved compile/load after endpoint edits and clean reload. Broader interrupted-download matrix NOT TESTED. |
| C5 continuity | PASS scoped | Ordinary Walk starts at approach,W climbs stairs and travels through covered bays. Ground paths allowed only through clear central span; no automatic motor-road junctions. Full end-to-end walk of all spans NOT TESTED. |
| C6 edit/recovery | PASS scoped | Endpoint handle extend; Undo restores short bridge; Redo restores extended bridge; clean reload shows all3 detailed bridges. |
| C7 failure/recovery | PASS scoped | Reproduced failed endpoint edit500, corrected invalid PostgreSQL enum query; repeated browser edit succeeds. Invalid lengths/bends/NaN rejected by tests. Asset-network interruption NOT TESTED. |
| C8 exact capture | PASS | Free current-view capture,real Download action,PNG2048x1110,945792bytes,SHA7bb62a36429d16821efdf5981cea353d0027217bb17e1dbb92b3ac25831aca63. No paid AI comparison requested/submitted in this turn. |
| C9 controls | PASS scoped | First click+hover shows3D;2chosen points+cursor motion keeps preview;further click adjusts endpoint;Finish and double-click save. Sparse2handles edit span. Mobile handlers share coords/height cap;actual touch-device UI NOT TESTED. |
| S1 section | PASS scoped | 1m reserve+4m clearwalk+1m reserve; actual module width/native axis and instancing unit scale tested. |
| S2 topology | PASS scoped | Straight bridge,protected stairs/end supports;intersecting bridges/motor roads reject in both orders;exact zero-lane finite path can cross underclearspan. Browser attempted collision rejected NOT TESTED;policy/API/capture regression tests exercised. |
| S3 grade | PASS prepared-level only | Stair/deck walking and underside ground remain distinct. Unsupported natural/sloped modes fail validation. |
| S4 clearance | PASS scoped | Full footprint/route attestation;14.8m structural end reservations;source-specific pathway exceptions;whole bridge modules not deleted as overhead furniture. |
| B/P gates | N/A | This candidate is a street/path,not a building or park. |

## Browser evidence

Disposable project b7893113-5e33-4e31-b9cd-b1b2933d0b9e;boundary950d642a-a604-4cb6-9f9f-384ad1d562ad,2.8ha172x164m vacant parcel east of BMO Centre. Ordinary UI authoring only;original user projects untouched.
Browser first-point preview,confirmed2point preview,shortsave,longsave,endpoint-edit/Undo/Redo,reload and stair/deck walking screenshots live outside Git in the dated delivery folder. Final console-error read after reload was empty. Screenshots are not AI renders. Offline exact-module QA includes12PNG1500x1000 at43.6/45/80/150m aerial/deck/underside. These are distinct from browser evidence.
The near-camera diagonal/transverse timber ends were independently traced to original portal/bay knee braces with source contact;no new cut-fragment/duplicate evidence. Core guards are longitudinal side rails,not bars across the opening.

## Open scope / limitations

Concept visualization,not a structural or accessibility design. Long spans retain source end supports;engineering support design is not asserted. No new span-specific human keeper approval or production publication. Other imported bridge styles still use fixed review placement and require separate topology-specific conversions;ring and curved flyover must not be flattened into this linear adapter. Browser source fidelity proven for timber only. Remaining template cases (mixed scenes,terrainholes,lateassetfailure,allangles,paidimages/videos) remain NOT TESTED. No extra generation/purchase/deployment.

Independent review caught/fixed collision gaps and double-click truncation;actual browser caught/fixed module404 and PostgreSQL enum500. Publication gates and original performance budgets were retained.
