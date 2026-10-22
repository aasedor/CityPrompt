# Omni 1.1 video-edit pilot — 2026-10-20

Local initiative: `codex/omni-11-video-pilot`, based on `abbcf292750ad56b6a0a60b730ce15f2c82eb849`.
This pilot is not a production deployment. Paid authorization is exactly two
eight-second submissions, one with an optional user scene direction. No paid
retries, alternate providers, subscriptions or credit purchases are authorized.

## Research and prompt decision

Primary sources checked 2026-10-20:

- https://ai.google.dev/gemini-api/docs/omni
- https://ai.google.dev/gemini-api/docs/models/gemini-omni-flash
- https://ai.google.dev/gemini-api/docs/pricing

Google recommends short editing instructions and preserving everything outside
the requested edit. This integration sends one source video and a compact finish
instruction, camera/layout preservation, and at most one user direction. The
verbose internal scene contract remains in request validation and provenance;
it is not appended to the provider's video-edit prompt. Other providers and
experimental keyframe/single-frame modes retain their existing prompts.

The stable model is `gemini-omni-1.1-flash`. Google's legacy preview model is
scheduled to shut down on October 22. The native edit task accepts the existing
eight-second route recording. High quality requests `1080p`, which Google
describes as upscaled; draft requests `720p`. Output uses URI delivery to avoid
large inline responses. Authenticated downloads accept only Google's HTTPS API
host. URI delivery requires `store=true` at Google: the first real request
demonstrated this with HTTP 400, despite the documentation also recommending
`store=false` for speed. The corrected payload uses retained Google media only
for URI delivery. Its interaction ID is saved before bounded read-only file
readiness polling/download; failures preserve that receipt. Provider POST
transport retries remain disabled.

Suggested custom direction: **A woman walks her dog along the existing sidewalk.**
Avoid introducing several simultaneous actors, new camera directions, a second
storyboard, or a full textual reconstruction of the visible development.

Google lists approximately US$0.10 per second of 720p video output, plus input
tokens. Eight seconds is about US$0.81 of output at the listed token rate.
That is an estimate, not an invoice or a separately verified 1080p tariff.

## Implementation and safeguards

- Video tab: Gemini Omni 1.1 label, optional 600-character prompt box, clear
  guidance and honest upscaled-resolution wording.
- Changing the prompt invalidates the prepared request and requires a new free
  preflight. Only Omni preview-video edit sends this field as a scene direction.
- The direction is preserved with the owner's saved attempt and hidden from
  collaborators along with the existing private prompt/control data.
- Older requests without `custom_prompt` retain exact idempotent replay when
  the new direction is empty and the requester still matches. A changed prompt
  using the same request ID remains a conflict.
- Existing server admission, source revision validation, output persistence and
  reference-based fidelity scoring remain in use. A completed or interrupted
  provider request is never automatically submitted again.

## Test environment and evidence

External evidence directory:
`C:/dev-artifacts/CityPrompt/omni-11-video-pilot-2026-10-20/`.

Disposable local project `7bbf376c-62b6-4aea-8804-48193baebd88` contains seven
parkades, two authored parks, two authored streets and 30 detail trees. A local
operator allowance caps all video admissions in this project at two, including
failures. The test account received 84 internal local tokens (16 to 100) for the
two 50-token videos. This changes no production account or provider balance.
`trial-ledger.json` records the allocation and submissions.

A first free low-flight route was rejected for this visual trial because its
framing emphasized trees and roadway rather than buildings. It used no provider
call; its recording is retained as `source-preview-first-route.mp4`. The source
camera was brought closer before preparing the paid trial.

## Verification

- Backend: 66 tests passed across Omni helpers, durable recovery, scene
  revision, fidelity, Seedance and Internal Enhance. Providers are mocked in
  these tests; PostgreSQL recovery tests use disposable isolated schemas.
- Frontend: 34 tests passed across seven video panel/capture/route suites.
- TypeScript check and scoped ESLint passed.
- Catalogue/build prechecks and production TypeScript/Vite compilation passed.
  Compilation writes outside the repository and skips copying the already
  hydrated public asset directory. Existing large-chunk warnings remain.
- Independent review found the legacy replay issue; its regression failed
  before the compatibility fix and passed afterwards.

## Actual submissions

1. Baseline aerial, attempt `a48a5741-e5ee-46e1-89c6-85cc61931e5b`: Google
   rejected the request with HTTP 400 (`store=true` required for URI delivery).
   No video or interaction ID was returned. Billing has not been verified.
   This failed request consumes one of the conservative local admission slots;
   it was not automatically retried. The control recording is 1920×1080,
   192 frames at 24 fps, exactly 8 seconds, with six depth/normal checkpoints.

Free pedestrian previews were also recorded and inspected at 0, 2, 4 and 7.9
seconds. They showed façade detail but framed mostly buildings/grass rather
than the wider streets and parks. Their source audit reports 75 building meshes,
117 PBR materials, 24 instanced detail meshes, 82 shadow casters, textures up to
256 px, and no building normal maps. This is a source-material limitation, not
evidence of native 2K texture detail. Those free previews are preserved outside
Git; no provider call used them.

The second authorized slot was assigned to the full-scene custom-prompt trial.
A replacement baseline submission requires a new user authorization.

2. Custom full-scene aerial, attempt `37342a73-a57a-4a1f-b5cc-4e93a1cbc9b4`:
   **generation, storage and playback passed; architectural fidelity did not
   pass visual review**. The 92-word prompt included the woman/dog direction.
   The corrected URI request completed and its result survived project reload
   and played from Project Renders. Actual media: 1920×1080, 24 fps, 192 frames,
   exactly 8 seconds, 8,845,918 bytes. Provider submission to completion took
   about 96 seconds including download and local scoring. App estimate US$0.80;
   actual provider billing is unverified.

   - Control SHA-256: `39a29c5d2af93252196f1b10a3e74695090bde4793e9a66e9804d40dcf344c89`
   - Result SHA-256: `4570de3581eb529652510e72df176d98a5c67a0f3ac91beadfc61fd6e085f5e6`
   - Five matched-time samples at 0/2/4/6/7.9 seconds show a polished, continuous
     result but an invented bridge between the front buildings, enclosed open
     façades, altered roofs/openings and a new central landscape/path layout.
   - Image similarity is 71.4/100 (`review`), not an architecture-preservation
     score. Unchanged surrounding imagery can dominate this metric.
   - The requested woman and dog are not recognizably verifiable at this aerial
     distance; prompt compliance is **not confirmed**.
   - Full-resolution samples, source/result comparison, saved prompts, receipts,
     capture profile and browser proof are in the external evidence directory.

## Conclusion after the initial batch

The local video-to-video transport and optional prompt workflow work. The output
is an experimental architectural concept, not an approved fidelity-preserving
render. Nothing from this pilot has been pushed or deployed.

Following the visual failure, the prompt's blanket instruction to create clear
glazing was removed, and preserving open façades and building separation was
made explicit. The revised prompt remains short and passes regression tests,
but at this checkpoint **had not received another paid generation test**. The provider option now
explicitly says experimental. Original submitted prompts and pixels remain
immutable in the external evidence directory.

At this checkpoint two provider requests had been submitted, including the HTTP
400 rejection, and that allowance was exhausted. The subsequently authorized
follow-up batch is recorded below. Before any student rollout, review a closer source with
recognizable actors and recheck all buildings, voids, roofs, parks and streets
against their source. Prompt instructions alone cannot guarantee that fidelity.

## Follow-up batch: two more trials explicitly authorized

The user subsequently authorized two additional eight-second trials. The earlier
allowance and both attempt IDs were archived in a new external batch ledger;
the current local allowance admits exactly two new requests, including failures.
Both prior attempts remain in project history. The disposable local account
received 100 internal test tokens for these two requests; production balances
and provider subscriptions were unchanged.

Evidence: `C:/dev-artifacts/CityPrompt/omni-11-video-pilot-2026-10-20/followup-two-trials/`.
Source commit: `0d5668613`. No additional runtime source changes were made for
these tests. The Omni helper suite was rerun: 37 passed.

The existing Timber and Stone Square was moved between the front parkades in
the disposable local scene, and the camera was brought closer. Seven buildings,
two parks, two streets and the existing details remain. Because framing and
park position changed as well as the prompt, comparisons against the previous
trial do not isolate the prompt's effect.

### Follow-up 1: closer aerial, no added activity

- Attempt: `b433058a-d70e-46bc-a6fb-ce7871ffb63a`.
- Completed through the local app using `gemini-omni-1.1-flash` and the revised
  prompt. Actual result: 1920×1080, 24 fps, 192 frames, exactly 8 seconds,
  11,768,690 bytes. Every frame decoded at the expected dimensions.
- Source SHA-256: `54f3cd725692e83e7c650fd2e648b92f57bf6477190da01ff8ce20ae6cd327fc`.
- Result SHA-256: `df0110910504ae2204d83d5cc2aef6cf50e88955586b74df7faa9a1de8f845a6`.
- Five matched-time samples show the buildings remaining separate and the park
  remaining between them, without the prior invented connecting bridge.
- Roof panel and façade treatments still differ. This is improved concept
  fidelity, not exact architectural acceptance. Image similarity is 80.6/100;
  the metric is not a proof of preserved architecture.
- The submitted prompt, original control/result videos, full-resolution frames,
  comparison sheet, capture profile and admission receipt are retained outside
  Git. Provider billing remains unverified; the app's US$0.80 figure is an estimate.

### Follow-up 2: lower park route with custom direction

- Attempt: `67d577f4-89e6-47ea-9637-9bbf3b7bdbd4`.
- Optional direction: “A woman walks her dog along the existing park path.”
- Completed through the local app using `gemini-omni-1.1-flash`. Actual result:
  1920×1080, 24 fps, 192 frames, exactly 8 seconds, 11,099,900 bytes. Every frame
  decoded at the expected dimensions.
- Source SHA-256: `599b9c15c344f7afbed36da34f81d57565c0594e6927dc7b65d8e4d08d57d60a`.
- Result SHA-256: `ba5bf7e189fe5e35a7134778bc54b286f1cf0e0eb2c07d212ed5141bb27b238e`.
- The woman and leashed dog are clearly recognizable, walking across the park
  paving. Park paths, benches, planted beds and pergola remain recognizable.
- Architectural fidelity did not pass: the orange/brick-like parking structure
  becomes dark gray, and a brown background apartment building appears at the
  right where the control has Google context. Prompt compliance for the actor
  does not establish architectural preservation.
- Image similarity is 73.8/100. Both new results have the automated label
  `stable`; this pixel heuristic is not manual architectural acceptance.
- The final source uses the six-metre-high detail flythrough, approximately
  4.3 m of movement over eight seconds. It contains zero auxiliary geometry,
  depth, normal, instance, semantic or material checkpoints. The aerial source
  contains six checkpoints. Both sources are 1920×1080 at fixed 24 fps, using
  the high-quality 2560×1440 capture/downsample path and tile warmup.

### Follow-up verification and disposition

- Exactly two new provider submissions completed, about 97 and 98 seconds from
  submission to completion. Four submissions now exist across both batches,
  including the original HTTP 400. No further generations are authorized.
- The app estimate is US$0.80 per result (US$1.60 for this batch); actual
  provider billing has not been verified. The local test account has zero
  remaining internal tokens. No production account balances were changed.
- Both videos persisted in Project Renders after reload and played fully in
  the actual CityPrompt video lightbox: duration/current time 8 seconds,
  1920×1080, browser media readiness 4. Both source/result pairs also played
  fully in the comparison viewer, whose captured error log was empty.
- Fresh automated verification: `backend/tests/test_omni_video.py`, 37 passed.
  No runtime source edits were made during this follow-up batch; the prior
  runtime commit's frontend/type/backend checks remain separately recorded.
- External evidence includes `trial-ledger.json`, `saved-attempts.json`, both
  prompt files, source/result MP4s, media metadata, five matched-time comparison
  frames per result, the test log and actual saved-gallery browser screenshots.
- Local comparison viewer: `http://127.0.0.1:18116/index.html`. This loopback
  viewer is only available while its local server is running.

Generation, custom prompting, storage, reload and playback passed. Exact
architectural fidelity remains a limitation, so the provider stays experimental.
This follow-up is local only; no push or deployment was performed.
