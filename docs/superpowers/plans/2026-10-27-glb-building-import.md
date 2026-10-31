# GLB Building Import Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans for this inline implementation. No catalogue publication or deployment.

**Goal:** A prominent Import GLB button immediately above Walk lets students place their own private building, then save and reload it.

**Architecture:** Upload a self-contained GLB into project-protected storage and represent it as a completed private Building source. Reuse user-generated discovery, click placement, terrain, persistent source binding and compiler protection. Preserve original mesh/material bytes and Y-up proportions. No AI calls or credits.

**Tech Stack:** React/TypeScript, existing Three.js loader, FastAPI, existing trimesh/numpy, PostgreSQL/S3.

## Design and scope
- Button above Walk in the Design palette. Dialog: GLB file, optional name, model units (metres, centimetres, millimetres, feet), optional real-world height, upload/place; clear progress and retryable errors.
- GLB v2, embedded resources, up to 50 MiB and one million triangles. Measured supported starting footprint 2-100 m per axis; height 0.25-500 m. Explain GLB Y-up and embedded textures.
- Authenticated project editor required; private project storage and normal asset access. Source records are discoverable only to their owner. Repeated placements copy the GLB into their destination project without source photos or public catalogue registration.
- Preserve imported colours/PBR. Use existing grounding and proportional fitting. Imported building models are static; do not promise archetype-specific entrances/interior navigation.
- Existing owner work, catalogue and 5174 runtime retained. Isolated existing linked worktree; new initiative branch from clean tower checkpoint.

## Review focus
- Invalid/truncated/oversized files, external URLs and missing geometry fail before storage.
- Units, node transforms and offset origins produce measured dimensions and grounded placement.
- Upload failure retains file/name/units for retry; no bogus success or lost project edits.
- Source/placed model stays private, saves and survives reload without a compiler replacement.
- Textures and source colours remain visible; importer sits above Walk and keyboard dismissal works.

## Tasks
- [x] Backend tests first: GLB measurement/rejection, upload editor authorization, storage failure, private source discovery and unchanged payload.
- [x] Implement focused GLB validation/upload service and model-library endpoint; reuse protected storage and source attachment.
- [x] Frontend tests first: button order, successful file upload/placement, input validation and recovery.
- [x] Implement dialog/API integration and imported-model material preservation; expose imported files under Your models.
- [x] Run narrow backend/frontend suites and TypeScript check. Inspect diff and independent code review.
- [ ] Browser trial: upload real detailed GLB, click-place, rotate/move, reload, bad file recovery. Save screenshots and delivery note to private Drive; record honest limitations.

## Execution ledger
- Initial git state clean at f3cc9c74e; new branch codex/glb-building-import-20261027, existing isolated worktree reused.
- User supplied concrete feature and button location; routine import defaults selected to reuse existing private-model flow.

## 2026-10-27 external GLB trial checkpoint

- Three unchanged third-party Kenney CC0 GLBs, redistributed as embedded-texture GLBs by Hidencod/tge-assets at commit 37f5baddf99899547ae661668880809c42b450f0: commercial building-j, commercial building-skyscraper-c, suburban building-type-b. Real-world target heights 10 m, 40 m and 7 m.
- Private local project 22202017-d9dd-41d1-89ea-647eeef1edac. Authenticated application upload endpoint passed for all three. Browser catalogue placement, 90-degree house placement, full reload and exterior walking/moving/turning verified visually. Protected placed GLBs match original SHA-256 bytes and retain completed imported_glb source bindings.
- File chooser end-to-end remains UNVERIFIED: Edge extension file-URL permission prevented browser file selection. No permission was changed or bypassed. External files were uploaded through the normal authenticated application endpoint. Invalid-file recovery, size checks and retained form settings passed component/API tests, not native browser file selection.
- Review corrections: remove lower/upper scale clamps and raw-size cutoffs so millimetre and very small arbitrary-scale exports retain measured physical height; bound all accessor allocation; validate embedded texture resources; do not invent imported storey counts; rename private catalogue to Your models.
- Verification: backend 24 tests; frontend 53 tests across six relevant files (including 14 placement checks); TypeScript passes. Initial regression tests failed before fixes. Diff check passes. Read-only independent review performed; remaining follow-ups are upload retry idempotency and repeated-image verification caching.
- Bounded render trial: two Sunburst/GPT High photographic images, 184 local QA tokens each. Initial insufficient-token attempt 40f3a8b4-01f7-4695-b5e3-b1c3b1c4a404 rejected before billing. Local QA balance topped up to 368 for the two-image test; no money purchase or production balance edit.
- Street job acf4264b-4729-4cbe-a4de-3dccb1c0a464 and aerial job 60217f7b-cc9e-414c-b002-1345bb751979 completed. Native AI originals are 1616 x 1136. Both fidelity checks returned review_required; automatic canonical outputs are clean 3D safety fallbacks. AI originals, exact sources and comparisons are separately labelled. This is a generation pass, not a fidelity approval.
- Existing Google tile tearing remains visible at ground level around this parcel. Imported geometry remains intact. Static exterior walking is verified; imported interiors, animated/skinned files and compression extensions are not certified.
- Drive review batch: https://drive.google.com/drive/folders/1x0y2myqsLJKykqfV1w0Qej3PtCvy89sJ . Local evidence and delivery receipts: C:/dev-artifacts/CityPrompt/external-glb-trial-20261027. Generated output remains outside the source tree.
- Native chooser test remains pending; therefore the final browser-trial checkbox is intentionally incomplete. No deployment or push.
