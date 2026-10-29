# Compact Claude crossings — local checkpoint

Claude crossings — local review checkpoint, 29 October 2026

Three compact fixed native trials are available on the isolated local test stack:
- Barcelona Passatge v006
- Brick Arch Viaduct v003
- Stone Arch Road Bridge v003, with compact-r002 runtime supports

Original GLBs are unchanged. Placement, 15-degree rotation, saving and clean reload were verified in project 467025e9-4f3c-432c-ba76-066a52467eb2 on localhost:5176 (API:8003). The user's 5174/8000 stack remains running.

The three exact-source PNGs contain no AI changes. Files labelled screenshot show the application UI. Picker screenshots use the original catalogue/source thumbnail, which may still show the original surrounding scenery. No paid image or video jobs, credit purchases, or deployment occurred.

The stone bridge has two bounded bank supports and thin asphalt caps derived from the original bank shapes. These 400 added triangles were independently checked for closed geometry and full-width support contact. Missing footways and orphaned vehicle glazing were also corrected. The final supported capture is stone-bridge-exact-source.png. Earlier unsupported-bank diagnostics are preserved locally and excluded from delivery.

Verification: 64 frontend tests passed; one unrelated railway-hotel asset regression was skipped because its GLB remains an LFS pointer locally. All 19 backend checks and TypeScript checks passed. Independent code, geometry and limited runtime pixel reviews passed.

Limits: production publication is still gated. Sloped terrain, surveyed public-road approaches, the full Undo/Redo matrix, and the browser's actual Download action remain untested. Extracting the free PNG proves its content, not the Download button. The bridge's 11 m deck needs deliberately designed adjoining elevated approaches; ground-level walking access is not claimed. These captures show independent test objects, not connected infrastructure.

The stepped plaza remains held because its raised rear carrier/drop needs separate work. Hospital, fire station, student residence and further bridge corrections are the next finite sequence; they are not claimed complete in this checkpoint.

Review folder: https://drive.google.com/drive/folders/1XWdPXl6pEhU_uojJXorA8_t-c2Gxv1BU

The three source packages and per-candidate runtime checklists are under tools/clay_barcelona_passatge, tools/clay_brick_arch_viaduct and tools/clay_stone_arch_road_bridge. Frontend/backend manifests and ownership contracts match. Support polygons record the source recipe SHA-256 and ownership revision.
