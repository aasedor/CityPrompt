# Next steps and release execution

Plan: complete repeatable visibility captures; run a bounded four-image occlusion comparison; correct release-check failures; package the exact existing runtime park assets; verify the combined student changes; commit and integrate into canonical `origin/main` without force-pushing.

Starting point: `097acf1b3`, 26 commits ahead of `origin/main`, no upstream divergence after fetch. Work is isolated on `codex/release-readiness`; other worktrees and unfinished catalogue candidates remain preserved. The duplex remains unactivated.

Initial release checks found stale login-test expectations and a street-reference test whose root detection relied on a hydrated public directory. The active park also needed its nine exact reviewed GLBs packaged in Git LFS and included in the release asset manifest, rather than relying on an external local public root.

Budget: retain the previous video's US$3 reservation and prior US$0.280668 estimate. Recalculate the three completed image requests from recorded usage using current standard rates (image input US$8/M, text input US$5/M, image output US$30/M), verified at https://developers.openai.com/api/docs/pricing on 5 September 2026. This is a usage-based estimate, not a settled invoice. The new pilot is capped at four requests and US$1.25 reserved per request; no automatic retries or new videos.

Execution results and any remaining release blockers will be recorded below before integration.

## Results

- Captured six native views of the existing student scene, with per-instance visibility and filtered references. Case A has no visible park; case C hides both infill houses behind the bungalow; case D exposes only a thin part of the park; case F reveals the park with the houses outside the frame. Evidence and a local comparison page are in ignored `artifacts/occlusion-pilot/review.html`. These are native captures, not proof of AI fidelity.
- The first attempted provider request returned HTTP 429, `credit_balance_exhausted`. No image was produced and the local student reservation was refunded. The remaining three requests were not attempted. The prior usage estimate plus retained video reservation is US$3.972317; available account credit is a separate constraint. Refill the provider account before resuming the finite A/B batch, and retain the failed-attempt ledger.
- Preflight exposed exact-coordinate equality rejecting an unchanged boundary after a PostGIS/GeoJSON/JavaScript round trip. The discrepancy was approximately 2e-14 degrees. Coordinate comparison now permits only 1e-12 degrees absolute noise, with zero relative tolerance; boundary ID, update timestamp, topology and retained-terrain checks remain strict. Tests accept serialization noise and reject an actual coordinate change.
- Packaged the existing nine v5 park GLBs (4,722,724 bytes), source manifest and foliage licence. All nine models pass hash, dimension and ground-contact verification, including individual rock contacts. GLBs are Git LFS pointers in source control. The new runtime collection is included in the release manifest; no new duplex or other candidate is activated.
- Updated stale login tests and sparse-worktree reference-root detection. Registered the free GPU capture check as an npm command and the standalone park review as a deliberate development entry. Fixed the GPU script's browser-global lint annotations.
- Applied compatible dependency lockfile updates: Browserslist, humanfs, fflate and selector-parser advisories now clear. Installed the lockfile into an isolated ignored dependency directory and pointed only this worktree's dependency junction there; the original checkout's dependencies were preserved.
- Verification on the updated dependencies: all 1,393 frontend tests passed; TypeScript, production JS/CSS build, lint, dead-code check and dependency audit passed. The 671 backend tests covering changes since `main` passed. The free GPU capture check passed with no browser errors. Catalogue checks verified 624 open-space references and 55 historical pilot references. The normal build passed; the final dependency rebuild omitted public-file copying because assets were verified separately.
- The existing localhost:5174 student scene reloads with the expected object choices and no reported page errors. Automatic approval review blocked restarting the existing servers and starting a replacement frontend, giving only “blocked by policy.” Existing servers were preserved. A separate backend on port 8004 loaded the corrected code with media providers disabled.

## Integration and remaining work

Pre-integration `origin/main`: `679b76a3557f84e7e3ea02e8c13f710493bc1533`. Integrate this verified branch by fast-forward only, without importing unrelated dirty worktrees. Keep all trial images and runtime logs out of the source commit. A repository push is not evidence that a hosted deployment has completed.

After API credit is available, resume the four-image comparison with explicit accounting for the failed request. Review raw provider and delivered images separately. Finer park-component and repeated-house identities remain subsequent work if the partial-occlusion trial demonstrates a need; the current conservative fix omits composition-heavy park references. No image-model fidelity guarantee or completed paid A/B result is claimed.
