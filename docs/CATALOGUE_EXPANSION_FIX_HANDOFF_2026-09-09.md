# Catalogue expansion fix handoff — 9 September 2026

History and recorded-trial review; priorities are recommendations. The subsequent integration on `codex/integrate-student-fixes-20260909` incorporates the committed fixes below and reruns verification. Uncommitted tower activations and unrelated OneDrive edits remain excluded. This does not claim the open product issues have been fixed.

## First: deliver a reproducible code baseline

Canonical remote: https://github.com/aasedor/CityPrompt. Fetched main: `4bd692f73` (September 7, PR #22). It already includes street/public-road integration (#21), park publication/terrain visibility (#22), and earlier building promotion work. Some changes were squash-merged: ancestry alone does not establish that code is missing.

Source checkpoint: local `codex/render-style-detail-pilot`, `a0ebd8396`, at `C:/dev/CityPrompt-building-next3`. The integration branch carries its net committed changes over main, avoiding duplicate squash-merged work. The separate `codex/publish-visual-review-gallery` contains images, not those application fixes. After the integration PR merges, use updated main as the receiving developer's baseline.

The integration preserves pilot labels and existing publication gates; it does not activate the pending tower models. Preserve the original OneDrive checkout's unrelated staged and unstaged work.

Clean-clone delivery is a prerequisite: the September 8 runtime used external `runtime-v4/public` assets and a restored `park-trio-v3` junction. Three missing foliage textures were masked by a procedural fallback. Hydrate declared LFS/runtime assets and seed storage, document environment setup, and verify a fresh project can place and reload buildings, parks and streets without Andrew's absolute paths or database. Never commit credentials.

## Priority fixes before broad expansion

| Priority | Open issue and evidence | Work and acceptance criteria |
| --- | --- | --- |
| 1 | Rough ground can hide valid buildings with `ground_not_ready`. Tower and Currie trials used boundary removal or prepared flat ground as workarounds. | Isolate unreliable terrain per footprint, retain verified geometry during updates, explain uncertainty, and preserve capture validation. Test rough boundary edits, resizing, Undo/Redo and reload with multiple objects, then 20 buildings. Unaffected placements must remain visible. Measure recovery time. |
| 2 | Today's residual-landscape operation hit a LEGO-plan revision conflict through full Generate to 3D. An incremental API compile succeeded. | Provide a normal UI operation for leftover landscaping without rebuilding buildings. Coordinate revisions with automatic compilation. Preserve existing geometry, pads, paths and roads; test reload and genuine concurrent edits. Do not bypass conflict checks. |
| 3 | Repeated native-house plots have one entrance anchor; irregular park corner edits can make entrance edge indices ambiguous. | Add stable per-instance doorway anchors and previews, preserve entrance identity through park edits, and test two-house resize/rotation/reload. Finish an internal-to-public-road fixture: the connected-block pilot's street remains about 13 m short. |
| 4 | Unsupported height edits can replace a detailed model with massing. Shape and slope support varies by park family. | Explain native dimensions, height limits and resulting representation before Apply. Test tennis, soccer, cinema, teaching-garden and concert irregular footprints separately or constrain them. Never compress/crop rigid courts. Basketball's final shape trial used a prepared level, not validated hillside surrounds. |
| 5 | Site DNA is invalidated server-side after boundary editing, but the open panel can show stale results until reload. | Immediately mark/invalidate displayed results, then fetch for the new boundary. Preserve unknown height/FAR and access uncertainty. Test with the panel open while editing. |

Ground starting points: `SharedSiteGroundProvider.tsx`, `sharedSiteGround.ts`, `buildingGroundContact.ts`, `AutomaticParkGround.tsx` and their focused tests. Entrance starting points: `features/pickPlace/ConnectionEditor.tsx`, `pedestrianConnections.ts`, and globe `parkAccessConnections.ts`. Landscaping touches generation controls, project write coordination and LEGO assembly services.

Intentional corridor cutting through parks is a separate feature: retain overlap rejection until amenities and paths can be replanned safely.

## Already implemented locally: integrate and retest, do not recreate

| Commit | Fix | Remaining limits |
| --- | --- | --- |
| `5cc59ac69` | Delete source drawings, coordinate same-tab writes, reconcile confirmed-absent 404s | Wider concurrent-editor and rapid-edit testing |
| `0922c9f68` | Tower framing and rejected-boundary recovery | Rough-ground isolation remains open |
| `33ad5a0a8`, `73438b589` | Sports duplicate pad/flicker, copied dimensions and seating | Slopes and wider camera coverage |
| `7da02ad98` | Direct 3D prompt fixes and failed-render refunds | Recheck failure accounting after integration |
| `7a8932418` | Move handle, public-road tolerance, authored camera ground, AI-first presentation | Missing foliage delivery and other gaps above |
| `ddc66becc` | Street endpoint snapping and detailed surface ownership | Complete public-road/entrance fixture |
| `972de8b64` | Irregular park outlines, basketball containment, ground-aware Undo | Other families and terrain interaction matrix |
| `a0ebd8396` | Source-only identity conditioning and render-style refinement | Broader visual regression, not guaranteed geometry |

These are local checkpoints, not claims of production deployment. Original reports record focused tests/type checks; rerun relevant checks after integration.

## Follow-ups and scale checks

- Still images: earlier roof/material drift and park/building swaps improved in the September 8 pilot. Preserve the explicitly approved photomontage benchmark and compare bounded matched-camera cases. Today's ten images are review candidates, not blanket approval. September 9 also notes lawn striping and disc-like tree crowns for asset refinement.
- Video: show rejected source checkpoints for low street-capture failures; switching camera mode currently clears routes. September 9 Omni outputs changed geometry and were 720p despite 1080p sources. Improve temporal fidelity and honest output dimensions before promising exact walkthroughs. This need not block a small approved static family.
- Performance: remeasure before adopting historical numbers. The September 4 report recommends lightweight catalogue metadata/thumbnails, texture compression/LODs, explicit runtime asset delivery and instrumented adaptive rendering. Verify 20-building use on actual tablet hardware before large-scale growth; do not substitute generic proxies for architectural identity.
- Quantities/classroom readiness: exact floor-plate metadata and wider touchscreen/collaboration trials remain documented gaps.

## Expansion exit criteria

1. Reproduce published assets from a clean clone with no workstation-specific junctions.
2. Integrate selected existing fixes. Run affected Vitest suites and `npm run type-check`, affected backend pytest suites, compiler tests when touched, and `git diff --check`.
3. Complete bounded ground/edit/entrance/landscape/reload trials with no hidden valid objects, false same-tab conflicts or lost geometry. Test genuine concurrent edits separately.
4. Publish capability limits. Retain tower/sports pilot gates. Follow RLASM v6.1: dry run, one-family pilot, source-locked review, explicit human activation, then bounded expansion. Never weaken a publication test to make a pilot pass.

## Evidence for the receiving developer

At local development checkpoint `a0ebd8396`, read these files under `docs/`:

- `CURRIE_STUDENT_COMMUNITY_TRIAL_2026-09-08.md`
- `CONNECTED_BLOCK_AND_IRREGULAR_PARK_PILOT_2026-09-08.md`
- `SKYSCRAPER_STUDENT_TRIAL_2026-09-08.md`
- `SPORTS_PARKS_TRIO_2026-09-08.md`
- `EDIT_DELETE_RELIABILITY_2026-09-07.md`
- `RENDER_STYLE_DETAIL_PILOT_2026-09-08.md`
- `STUDENT_20_BUILDING_TRIAL_2026-09-07.md`
- `STUDENT_READINESS_FOUNDATIONS_2026-09-06.md`
- `PERFORMANCE_BLOAT_REVIEW_2026-09-04.md`

Today's landscaping/video findings: local commit `2932a7d83`, `docs/showcase/landscaped-community-2026-09-09/README.md`. Preserve these reports with the source handoff; their local fixture IDs and screenshots are not automatically available to a fresh clone.

Historical August Wave 2 notes claim promotion while the current supplied AGENTS instructions retain approval/publication gates. Reconcile current manifests and explicit approval records; do not use conflicting historical notes alone as publication authority.
