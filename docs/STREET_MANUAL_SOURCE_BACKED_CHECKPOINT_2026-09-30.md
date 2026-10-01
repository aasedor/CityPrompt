# Source-backed Street Manual checkpoint — 30 September 2026

Branch: `codex/street-manual-completion`. Local implementation; not published.

Twelve separately versioned street choices now use dimensions from the City of Calgary's [Detailed Cross-Sections](https://www.calgary.ca/content/dam/www/planning/temporary-pdfs/SM_DetailedCrossSections_Annotation.pdf), whose cover identifies **Draft 3, November 2024**. These are not represented as verified Draft 4 cross-sections. Source PDF SHA-256: `818106b3c318846db518375e3f1d92fe756a91489a64608fac3080492d37a2f2`.

| New selection | Width | PDF page |
| --- | ---: | ---: |
| Alley, no deep utilities | 6 m | 4 |
| Local residential, no parking | 16 m | 5 |
| Local industrial | 18 m | 7 |
| High-activity local | 21 m | 9 |
| Collector, parking both sides | 23 m | 11 |
| Industrial collector | 26 m | 12 |
| High-activity collector | 27 m | 13 |
| Four-lane arterial, 50 km/h | 30 m | 14 |
| Four-lane arterial, 70 km/h | 36 m | 15 |
| Six-lane arterial | 46 m | 16 |
| High-activity arterial | 36 m | 17 |
| Skeletal, horizontal surface layout only | 60 m | 18 |

## Runtime and compatibility

The twelve new identities have fixed metric band widths, source citations and content hashes mirrored in frontend and backend. They use the existing drawn-route lifecycle, materials and furniture. The wider arterial medians include planting where the source shows it. Tree intervals and furniture composition are visualization choices where not dimensioned in the source, and retain the existing tree-count cap on long routes.

All thirteen original manifest records remain unchanged and resolvable for saved projects. New selection uses the twelve sourced revisions. Editing a saved legacy section retains its original binding unless the user explicitly chooses a different street. Rural local is withheld from new selection because its recorded section has not been confirmed by this source set.

Draft 4B intersections corroborate some dimensions but differ elsewhere: collector parking is 2.1 m versus Draft 3's 2.2 m; industrial collector paths and some high-activity cycle dimensions also differ. Editions have not been blended. See the separate Draft 4B reconciliation. The missing Draft 4A standard cross-section drawings remain necessary to claim current Draft 4 fidelity.

## Verification

- 155 focused frontend tests and 30 backend tests passed; TypeScript check and Vite production bundle build passed. Vite reported normal large-chunk warnings. The build check is not a clean-install runtime test.
- Original thirteen records compared unchanged against `2852ce9ab`; frontend and backend JSON mirrors match byte for byte.
- All twelve revisions applied and saved through ordinary student controls on an existing bent route in a disposable prepared-level project. Aerial screenshots were visually reviewed.
- Walk reviewed for local residential, local industrial, collector, six-lane arterial and high-activity collector. Collector exact 3D preview reviewed. Collector and high-activity collector identity, width and route controls checked after reopening.
- Collector Undo/Redo buttons exercised, but the intermediate undone state was not independently verified; recorded as partial.
- No paid image requests. Existing user projects were not edited.

The machine-readable evidence ledger is `STREET_MANUAL_DRAFT3_REVIEW_2026-09-30.json`. All entries remain local pilots, with human visual approval pending and completion false. Applying twelve choices to one route does not substitute for independent new placement, junction, slope or full acceptance tests. Skeletal ditch grades, crown and interim ditch geometry are not implemented; its limitation is visible in the picker and citation. Utility depths and detailed curb profiles are outside this surface-layout verification.

## Local evidence

Disposable project: `http://127.0.0.1:5183/projects/60db592e-2d49-4cfb-8d53-fb8004c25784`.

Downloaded source, page extracts, browser screenshots and generated build output are outside Git at `C:/dev-artifacts/CityPrompt/street-manual-2026-09-30/web-source`. No heavyweight generated output is included in this checkpoint. Source changes comprise the versioned manifests, registry/legacy handling, profile/furniture support, tests and documentation.
