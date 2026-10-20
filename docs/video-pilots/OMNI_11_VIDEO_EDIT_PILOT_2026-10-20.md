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

## Current conclusion and remaining gate

The local video-to-video transport and optional prompt workflow work. The output
is an experimental architectural concept, not an approved fidelity-preserving
render. Nothing from this pilot has been pushed or deployed.

Following the visual failure, the prompt's blanket instruction to create clear
glazing was removed, and preserving open façades and building separation was
made explicit. The revised prompt remains short and passes regression tests,
but **has not received another paid generation test**. The provider option now
explicitly says experimental. Original submitted prompts and pixels remain
immutable in the external evidence directory.

Two provider requests were submitted total, including the HTTP 400 rejection;
the server allowance is exhausted. No third request, quota reset or provider
purchase was made. Completing a replacement baseline trial requires the pending
user authorization. Before any student rollout, review a closer source with
recognizable actors and recheck all buildings, voids, roofs, parks and streets
against their source. Prompt instructions alone cannot guarantee that fidelity.
