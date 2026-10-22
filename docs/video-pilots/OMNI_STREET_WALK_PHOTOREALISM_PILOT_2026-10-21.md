# Omni photographic street walk — local pilot

The user authorized local changes based on the public-repository research and
exactly one paid street-walk test. They then requested a brisker reference.
This initiative stays on `codex/omni-11-video-pilot`; no push or deployment is
authorized by this task. Evidence dates use UTC.

## Changes

- The existing Omni preview-video prompt targets live-action architectural
  footage. Source video guides camera/layout; materials, reflections, shadows
  and planting can become more photographic. Massing, roof forms, openings,
  street layout and building separation remain constrained. Other providers
  and original image/keyframe modes retain their existing prompts.
- Free preflight decodes the complete source and checks the deterministic
  eight-second/24 fps recording before a new Omni submission. Header bytes
  alone no longer establish source readiness.
- Output decoding happens after paid pixels are durably saved. Actual decoded
  dimensions, frames, fps and CFR duration are retained and shown in the video
  panel. Inspection failures preserve paid output and report a warning.
- Provider usage is retained when returned. The edit estimate allows ten
  output seconds at the published 720p rate, with an input-charge caveat;
  it is not a hard billing cap or an invoice.
- Existing idempotency, preview reuse, admission and no-retry safeguards remain.
  Independent review caught validation occurring before saved-request replay.
  A failing regression demonstrated that problem, then passed after moving
  new media validation behind the existing-request return and before admission.

Appearance-reference uploads and a 360p pricing tier were not added. Their
benefit and tariff have not been validated for this application.

## Scene and reference

Local project: `c4864790-f468-505a-9148-96f7b48022e4`.
It is a separate disposable project with six existing native building
assemblies flanking a 175.298 m CityPrompt quiet residential street. Original
projects and model files were preserved. The scene preparation script and exact
template provenance remain in the external evidence folder.

The street was rebuilt through the normal Community 3D compiler after the free
preflight caught an inherited recipe target that did not match its new geometry.
No validation guard was bypassed and no paid generation occurred before this
was corrected.

The first free walk-by looked across façades. For the forward-facing reference,
the existing bicycle camera rig was used at walking speed; it remains labelled
`bicycle_ride` in saved metadata. The final route is 13.1 m over eight seconds,
approximately 1.64 m/s / 5.9 km/h, at 1.6 m eye height. The source has 192 decoded
1280×720 frames at 24 fps. It uses draft source capture with six tile warmup
poses and no depth/normal checkpoints. Some model textures in the inspected
scene resolve only to 256 px; source inspection does not establish native 2K
texture quality. Development reloads interrupted one free preparation; it was
recaptured before any paid submission.

Source SHA-256:
`01ca2ef0d20957e799bd1ec0ca885027b016f54f91c87cd7dcfc8482e868552c`.

## The single paid result

- Attempt: `e7a35e55-f73b-4b50-b4a0-e7f8dce7f2eb`.
- Request: `c8b97226-707c-491d-92b8-01a1333539ed`.
- Model: `gemini-omni-1.1-flash`, requested 720p; empty custom-activity prompt.
- Submitted at 2026-10-21 02:01:43 UTC; completed at 02:02:46 UTC, about 63 s.
- Actual output: 1280×720, 24 fps, 192 frames, eight seconds; 6,720,194 bytes.
- Output SHA-256:
  `73a777ed628f2a01ac0093cdbae51f0d1765e0cc6c2051e2458036fd0ed09d56`.
- Exactly one admission/provider submission; no retries or additional renders.
  Fifty internal tokens were assigned to the disposable local test account and
  consumed. Production balances and provider subscriptions were not changed.
- Returned usage: 44,841 input tokens, 46,336 video output tokens and 469 thought
  tokens. Applying the published input/video/text rates gives approximately
  US$0.8824. This is a usage-based estimate; the billing invoice is unverified.
  Reference: <https://ai.google.dev/gemini-api/docs/pricing>.

Five matched-time samples show more photographic asphalt, natural foliage,
surface variation and lighting. Camera movement remains continuous, with no
requested new actors. However, façade patterns/materials changed, the broad
paved crossing disappeared, and distant context was reinterpreted. The source
and prompt both differ from the prior park/aerial trials, so this is not a
controlled measurement of the prompt's individual contribution.

Automated image similarity is approximately 56/100, not a quality or
architectural-acceptance score. Photographic finish improved in this reviewer’s
assessment; exact design fidelity did not pass. Source speed is calibrated;
generated world-space speed has not been independently measured.

## Verification

- Backend: 62 passed across `test_video_media.py`, `test_omni_video.py`,
  `test_video_recovery.py` and `test_video_fidelity.py`. Recovery tests use real
  isolated PostgreSQL schemas and mocked paid providers. The URI usage-retention
  regression separately failed before its implementation and passed afterward.
- Frontend video panel: four tests passed, including measured output facts and
  warning display. TypeScript and scoped ESLint passed.
- Vite compilation passed with the configured hydrated public/catalogue root;
  static assets were not copied into the external build. Existing chunk warnings
  remain. The plain worktree public root lacks some externally hosted assets and
  is not the configured local runtime asset root.
- Actual local app: free source preview, final preflight and one paid generation
  passed. The saved result played fully at 1280×720/eight seconds. Persistence
  after reload is recorded with browser evidence in the external folder.

External evidence (not staged/generated binaries):
`C:/dev-artifacts/CityPrompt/omni-street-walk-2026-10-21/`.
It contains the immutable source/result, prompt, usage/admission ledger, media
hashes, comparison frames, compilation log, scene preparation and reconciliation
scripts, and a local comparison viewer. No production rollout was performed.
