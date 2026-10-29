# Student final fixes — October 29, 2026

Local branch: `codex/student-final-fixes-20261029`, based on handoff snapshot `baf5af30`.
Browser project: `7ca0e1cf-4847-479e-a3f5-1a895a7ec114`, disposable local student account.

| Reported issue | Change | Verification |
| --- | --- | --- |
| Ground finishes block images/free exact captures | Recognized finishes use landscape capture ownership without an archetype compile. Geometry/material hashes bind their capture revisions, including boundaryless and unfilled sites. | Black pavers overlapping the building/court: image action enabled, free exact preview succeeds. Independently reproduced stale geometry/material requests reject unbilled. |
| Tower storey edits rejected for a new student | Private local installers retain the existing owner's legacy IDs and give additional accounts deterministic private IDs. No permissions or immutable object bytes changed. | Eighteen exact installed objects verified before and after additive QA bindings. Brick Podium changes from 13 to 25 to 40 storeys; detailed model updates; 40 storeys / 131.1 m survives reload. Other five programmes' bindings verified; their browser heights were not rerun in this batch. |
| Court turn near a street rejects despite an available fit | Decompose concave obstacles and evaluate bounded contact-plane intersections, retaining full collision checks and the 30 m search cap. | Original saved 21 × 36 m court rotates 0→15° and saves/reloads. Translation is approximately 4.28 m west / 29.63 m north. This is substantial; a 5° diagnostic needs about 1.52 m. No-fit proposals still remain unchanged. |
| Pale bands repeat across long street travel lanes | Give longitudinal asphalt/cycle bands priority over fixture-centred access paving, preserving actual crossings and junction geometry. | Saved roughly 240 m avenue has continuous lanes, with 90° and approximately 60° intersections intact after reload. Material-level tests also cover 253 m routes and reversal. |

Final combined verification: **210 frontend tests** across 15 files; **399 backend/installer tests**; TypeScript and `git diff --check` pass. Independent focused suites also passed. Ten additional opt-in isolated PostgreSQL video-appearance tests were skipped in the agent's wider run because `CITYPROMPT_TEST_DATABASE_URL` is unset; they are not counted as passes.

Local API, database, Redis, storage and image/reference worker readiness pass. Walking entry, movement and exit were exercised after the tower edit. No paid images/videos, GLB generation, catalogue publication, deployment or remote push occurred.

The long-running browser tab recorded three module-load errors while the API was deliberately restarted during source synchronization. Subsequent module requests returned 200; a fresh tab loaded the saved project with zero console errors. These transient restart errors remain in local evidence and are not counted as a clean uninterrupted session.

The app serves a lightweight source export at `D:/CityPrompt-review-artifacts/storage-and-stress-20261029/handoff-source`; reviewed production changes were mirrored there and the API/idle worker restarted. The Git worktree above remains the source of record. Heavy assets remain in their existing external runtime directory.

Evidence: `D:/CityPrompt-review-artifacts/student-final-fixes-20261029/`.
Private Drive review: https://drive.google.com/drive/folders/1aroll2NQfIETlqj6VrxJrAZFz19211f3 . Screenshots are labelled as screenshots; they are not AI originals or downloaded exact PNG originals. The exact-preview download automation disconnected; original-file export delivery remains unverified. No paid render jobs were created.

These fixes do not finish the separate 74-model catalogue audit or publish private tower pilots. Surface-only scenes still need the existing compiled-scene readiness contract for paid rendering.
