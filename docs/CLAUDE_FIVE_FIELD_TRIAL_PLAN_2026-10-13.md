# Claude five: repairs, vacant-field trial and Git delivery

User authorization (13 October 2026): finish Claude buildings, trial them in an empty field, up to five aerial plus five street-view AI renders, then push validated work to Git. No video, extra retry batch, merge or deployment is authorized by this plan.

## Accepted checkpoint

All five exact candidates passed independent holistic architectural-clay review with zero P0/P1: hotel v006 unchanged, Zinc Corner v007, Grand Magasin v008, Modernista Market v007 and City Hall v010. Earlier failed candidates remain evidence only. Exact GLB hashes, repairs, limitations, static costs and ZIP hashes are recorded in [the runtime review](CLAUDE_FIVE_RUNTIME_REVIEW_2026-10-13.md) and `seed/claude-five-trial/library.json`.

All five accepted GLBs passed Khronos validation with zero errors/warnings. A fresh isolated local schema/bucket passed installation, readback, idempotence, runtime-descriptor and conflict-refusal checks, then was removed. Focused backend tests: 12 passed. Five proof ZIPs totaling 151,387,790 bytes preserve the exact inspected evidence and authoring sources under the existing LFS-covered `seed/model-library/objects/claude-five/evidence/` path; CRC, hashes, sizes and LFS filters verified.

Static one-copy totals: 25,967,576 GLB bytes, 25,846,518 packed geometry bytes, 489,217 triangles and 93 base primitive draws. No asset textures. Same-parser comparison with the canonical verified Victorian Station artifact is in the runtime review. These are static counts, not a frame-time benchmark or laptop suitability result.

## Trial and remaining sequence

1. Completed: bounded versioned repairs, exact-GLB camera/phone evidence and independent review. Preserve original deliveries and failed studies.
2. Completed installation verification: use the default manifest-relative installer, hydrate LFS objects/references, and apply only to loopback DB/storage with an existing local owner project. The frontend roster is enabled by DEV or `VITE_CLAUDE_FIVE_TRIAL=true`; production defaults off.
3. Completed: all five native models inspected in browser aerial/walking views and reloaded. Additional hotel/City Hall UI checks and all-five isolated API move/rotate/delete checks are separated in the final runtime review.
4. Completed: exactly five aerial and five street images, 1,020 application tokens; all saved with source captures. No extra paid retry or video.
5. Completed verification: 91 focused frontend tests, TypeScript check, 12 backend tests, exact DB/storage verification and independent code review. Commit and push the coherent package to origin/codex/claude-five-runtime-review; no merge/deployment.

## Installation and evidence locations

From `backend/`, with local environment configured:

```text
python ../scripts/claude_five_library.py
python ../scripts/claude_five_library.py --apply --owner-project-id <existing-local-project-id>
python ../scripts/claude_five_library.py --verify
```

Default package root: `seed/claude-five-trial`, with model paths relative to its manifest. `--artifact-root` is an optional external-delivery override. Reviews are byte-preserved under `seed/model-library/rlasm-architectural-clay/evidence/claude-five-*.json`; portable proof ZIPs include original-path-to-entry mappings. The installer refuses conflicting DB/storage state.

Repairs path `C:/dev-artifacts/CityPrompt/claude-five-repairs-2026-10-13` now points through a junction to `D:/CityPrompt-trial-backup/claude-five-repairs-2026-10-13`. Its tools and locked source copies remain available at the original path. The original source ZIP was moved to D: after checksum verification; extracted originals remain in `C:/dev-artifacts/CityPrompt/claude-five-review-2026-10-13/source`.

Git preflight: `origin=https://github.com/aasedor/CityPrompt.git`; work is on `codex/claude-five-runtime-review`. Preserve existing ancestry and unrelated work. Final rendering/UI results are recorded in the runtime review; the authorized feature-branch backup follows verification.

Explicit `--artifact-root PATH` uses `PATH/models/<candidate>.glb` for validation and upload, while retaining the manifest hash/reference/review checks and source provenance. The old original-only external delivery lacks the four repaired files; prefer the hydrated default Git package.
