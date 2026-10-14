# Nano Banana 2.1 render option — 2026-10-14

Source initiative: `codex/nano-banana-21`, based on deployment-version's
optional-site-trees checkpoint. This document does not certify a production
deployment or paid Google output.

## Behavior

- `Nano Banana 2.1 · Google` is selectable for aerial/street Direct 3D images
  and saved-image edits. Existing defaults and the three-OpenAI comparison
  remain unchanged. Selection uses the existing project render draft.
- The backend calls `gemini-nano-banana-2.1` once through Google's Interactions
  REST API, using `GEMINI_API_KEY`. OpenAI credentials are not required for
  Google queue admission. The frontend never receives this key.
- Direct 3D requests 2K PNG output. Unsupported viewport aspects are padded
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

Read-only model-discovery requests using the local and Render API credentials
returned HTTP 403 with Google's message: “Your API key was reported as leaked.
Please use another API key.” They are the same key; no key value is recorded
here. The Render worker has no Gemini key configured. Known revoked keys
disable this option. No production setting was changed during these checks.

Before activation, replace the rejected Gemini key through the existing secret
configuration and confirm model access. For Render, the API and worker need
the same working `GEMINI_API_KEY`; no frontend key is needed. Do not put the
secret into Git, a screenshot, or chat. The owner has now authorized exactly
two aerial and two street-view Nano Banana 2.1 renders after finalization.
All four remain unrun while key replacement is pending. Record each outcome,
actual geometry fidelity and available usage/cost evidence; do not duplicate
an attempt with an unknown provider outcome. No paid call was made for this
initiative, and no production setting was changed.

Google Cloud promotional credits are not assumed to cover Gemini Developer API
billing. This adapter uses the Developer API; it does not silently migrate
Vertex AI credentials or billing.

## Authority

- [Google changelog, October 6](https://ai.google.dev/gemini-api/docs/changelog#october-6-2026)
- [Image generation guide](https://ai.google.dev/gemini-api/docs/image-generation)
- [Interactions REST contract](https://ai.google.dev/api/interactions-api)
- [Model pricing](https://ai.google.dev/gemini-api/docs/pricing#gemini-nano-banana-21)
