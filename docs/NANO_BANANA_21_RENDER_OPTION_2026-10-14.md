# Nano Banana 2.1 render option — 2026-10-14

Source initiative: `codex/nano-banana-21`, based on deployment-version's
optional-site-trees checkpoint. This document does not certify a production
deployment. The four authorized local paid trials below are complete.

## Behavior

- `Nano Banana 2.1 · Google` is selectable for aerial/street Direct 3D images
  and saved-image edits. Existing defaults and the three-OpenAI comparison
  remain unchanged. Selection uses the existing project render draft.
- The backend calls `gemini-nano-banana-2.1` once through Google's Interactions
  REST API, using `GEMINI_API_KEY`. OpenAI credentials are not required for
  Google queue admission. The frontend never receives this key.
- Direct 3D requests 2K JPEG output. The live model rejects PNG output with
  HTTP 400, despite the generic guide's PNG example. PNG control images remain
  supported. Decode the returned JPEG once and retain a canonical PNG of its
  decoded pixels; this does not recover detail lost in provider JPEG encoding.
  Unsupported viewport aspects are padded
  consistently across same-camera controls; the aligned presentation removes
  only that padding. Canonical provider pixels are retained separately in
  recovery/audit/gallery paths. Existing source-preservation checks still
  apply and outputs remain subject to review.
- Geometry controls are retained. Google allows 14 image attachments; current
  v2 projection-changing captures collect at most seven optional archetype
  references. Schema validation budgets the controls and optional edit mask
  before queue submission. Same-camera finishes use captured geometry without
  archetype artwork, as before.
- Application credit reservations remain conservative: Direct 3D uses the
  existing Image 2 reservation formula; legacy saved-image edits reserve 25
  credits. These are application allowances, not measured provider charges.
  Unknown/produced Google edit outcomes retain reservations; confirmed
  unproduced outcomes refund. Existing Direct 3D recovery policy is unchanged.
  There are no automatic paid retries or switches to another provider.

## Verification and remaining work

Mocked backend checks cover routing, official response parsing, image framing,
original-image preservation, masks, admission without OpenAI, errors and
reservation handling. Frontend checks cover selectors, persisted choice,
single-call aerial/street requests and unchanged comparison behavior.
TypeScript checking passes. The real selector was also exercised on
localhost:5174 using a temporary component harness with mocked availability;
this is not a live paid render test.

The old local and Render API Gemini credentials are revoked (HTTP 403, reported
as leaked). The Render worker has no Gemini key. A newer existing **City Prompt**
key, created August 2, was found in the same Google project; model discovery
returned HTTP 200. Only the ignored local backend configuration was updated.
No key was created, permissions changed, or billing/subscription changed.
For production the API and worker need this working `GEMINI_API_KEY`; no
frontend credential is needed. Its transfer to Render still needs the owner's
specific confirmation. No production setting was changed in this initiative.

## Four authorized real-app trials

All four ran through the browser's normal Direct 3D workflow on localhost:5174,
using an isolated regular editor account and a copy of the five-building empty
field project. The original project was preserved. The copied building IDs
initially failed source fingerprints before any provider call; normal recipe
compilation refreshed the clone without bypassing validation or changing models.

Project: `6ecad402-d416-4400-a708-d453e34c193d`.
Evidence outside Git: `D:/CityPrompt-production-update-2026-10-14/`.
Receipts: `nano-four-render-trial.json`, `nano-trial-results.json` (audit IDs,
gallery IDs, hashes, source/provenance, warnings); images `nano-aerial_1.png`,
`nano-aerial_2.png`, `nano-street_1.png`, `nano-street_2.png`; comparison board
`nano-four-render-source-comparison.jpg`; actual browser screenshots retained.

| Trial | API time | Result and fidelity limitation |
| --- | ---: | --- |
| Oblique aerial | 27.09 s | Produced/saved. Five buildings recognizable; facade/roof detail and context shift. Registration luminance 0.607 / structure 0.542 failed. |
| Overhead aerial | 33.44 s | Produced/saved. Five footprints remain separate; roof/courtyard/vegetation changes. Silhouette/layout agreement failed. |
| Street facade | 24.41 s | Produced/saved. Convincing brick, stone and glazing; window/balcony rhythm broadly retained. Capture had less than 10% immutable context, so registration could not certify it. |
| Street market | 33.01 s | Produced/saved. Roof peaks and coloured awnings recognizable; stronger materials. Translation exceeded the existing Direct 3D limit. |

**Generation, gallery persistence and reload passed for all four. Automated
geometry acceptance did not pass for any of the four.** All are
`review_required`; the gallery retains each provider original alongside its
authoritative 3D fallback, for eight saved files. The UI deliberately shows the
paid provider image for review. Do not describe these as approved faithful plans
or silently weaken the safeguards. The street results are promising visually,
but this finite trial does not establish superiority over the existing engine.

Four produced images used 372 application credits (93 each). Two earlier known
HTTP 400 PNG-output rejections produced no image and their application credit
reservations were refunded. Six HTTP generation requests total, four produced;
no automatic retries or provider fallbacks. Google invoice cost is unavailable;
application credits are not a provider charge measurement. No further paid
generation is authorized by this four-image test batch.

The live trial also exposed an incorrect `GPT High` display on Google results;
the Direct 3D frontend now attaches OpenAI quality labels only to GPT models.
Latest verification after these fixes: 242 relevant backend tests, 67 frontend
tests and `npm run type-check` passed; `git diff --check` passed. The initial
broader feature verification before this live fix was 268 backend / 66 frontend.
Existing React act/Three.js and pytest/Pillow deprecation warnings remain.

Production remains unchanged. This document is not a cityprompt.ca deployment
certificate, nor a paid saved-image-edit or video test certificate.

Google Cloud promotional credits are not assumed to cover Gemini Developer API
billing. This adapter uses the Developer API; it does not silently migrate
Vertex AI credentials or billing.

## Authority

- [Google changelog, October 6](https://ai.google.dev/gemini-api/docs/changelog#october-6-2026)
- [Image generation guide](https://ai.google.dev/gemini-api/docs/image-generation)
- [Interactions REST contract](https://ai.google.dev/api/interactions-api)
- [Model pricing](https://ai.google.dev/gemini-api/docs/pricing#gemini-nano-banana-21)
