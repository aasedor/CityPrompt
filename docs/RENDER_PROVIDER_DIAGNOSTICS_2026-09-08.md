# Direct 3D provider failures — 2026-09-08

## Evidence and limits

The three sports-park requests returned OpenAI HTTP 500 `server_error`, with
no image payload. Request IDs are recorded in `SPORTS_PARKS_TRIO_2026-09-08.md`.
The server error does not disclose an internal root cause or establish whether
OpenAI billed for processing. Do not describe it as moderation or insufficient
funds, or claim that a student geometry mistake caused it.

Official sources consulted:

- https://developers.openai.com/api/docs/guides/image-generation — GPT Image 2
  supports arbitrary sizes within documented limits, including multiples of 16;
  do not send `input_fidelity`. The submitted 1616 × 1008 size is within those
  limits. The general API reference's three-size enum is less complete than
  this model-specific guide.
- https://developers.openai.com/api/reference/resources/images/methods/edit —
  multiple PNG references and multipart `image[]` are supported.
- https://developers.openai.com/api/docs/guides/error-codes — HTTP 500 indicates
  a provider server error; request IDs support investigation.

## Controlled diagnostics

Used the same existing account/key and `gpt-image-2`. Each diagnostic makes one
explicit call with no automatic retries. External scripts refuse to overwrite
an existing attempt. No credentials are written into reports.

Artifacts and exact request manifests:
`C:/dev-artifacts/CityPrompt/render-diagnostics-2026-09-08/` (outside Git).

| Diagnostic | Result | Seconds |
| --- | --- | --- |
| One scene image, short prompt, 1024 square, low quality | HTTP 200, image returned | 40.30 |
| Full current browser capture, seven images, 1616 × 1008, high quality | HTTP 500 | 179.80 |
| Same full payload, only quality changed to low | HTTP 500 | 24.52 |
| Same low-quality prompt/size, only scene image attached | HTTP 500 | 76.67 |
| Full low-quality payload, only output changed to 1536 × 1024 | HTTP 500 | 43.89 |
| Full low-quality payload, only prompt changed to 105-character instruction | HTTP 200 | 42.38 |
| Full low-quality payload, revised 2904-character production prompt | HTTP 200 | 48.59 |
| Revised prompt, high quality through actual local API and server inventory | HTTP 200, both gallery records saved | 180.91 overall / 140.88 provider |

The minimal successful output is a connectivity diagnostic, not an approved
geometry-preserving render: it changes aspect ratio and omits design guides.
The full payload was captured from the browser with its outgoing request
intercepted before submission, then prepared by the actual backend service.
The offline comparison does not include the endpoint's server inventory.
Quality alone and auxiliary guides alone do not explain the failure pattern.
Changing only the prompt succeeds while attachment hashes and output dimensions
remain identical. This implicates the previous prompt in the observed failures;
it does not identify OpenAI's internal bug or prove a particular sentence caused
it. Revised scene prompts remove contradictory photographic-only context rules
for artistic styles, invitations to invent curbs/planting, and repeated locks.
The final shared design-authority lock, guide roles, reference mapping, camera,
occlusion protection, server validation and post-generation checks remain.
Historical tower requests used the same 1616 × 1008 size successfully; a
size-related failure here would not establish that all custom sizes are invalid.

## Student-credit repair and diagnostics

- Provider exceptions now retain HTTP status and `x-request-id`; response logs
  include elapsed time and capture fingerprint, without credentials.
- If no image was returned and provider billing is unknown, restore the
  student's City Prompt credits. Keep `tokens_spent` against the global provider
  budget until reconciled; do not falsely call the provider request unbilled.
- Refunds lock the audit row and carry a durable refund marker, preventing a
  duplicate credit. Existing produced-image handling remains separate.
- Repaired exactly the three identified failed sports trials in the isolated
  local DB: 249 credits restored, balance 8112 → 8361. Output keys were absent;
  provider-cap reservations remain. No production account was modified.
- Restarted the existing local backend on port 8002 and confirmed the browser
  loads the project and displays the restored balance.

Verification: 182 backend tests across Direct 3D, presentation and street modes
pass; touched-file Ruff passes. No catalogue files are included in this change.

## End-to-end result and remaining fidelity work

The final high-quality request returned an image and the API completed normally.
Provider request `req_dae7c11d41034b00a516e49386fc00a1`. Gallery records:
`88327366-5dfd-4b20-b88a-58b4df3ec026` (final) and
`7c59038e-bcbe-4557-b071-699f881b33c4` (untouched AI original).

The existing geometry checker reported new unsupported structure and returned
the authoritative 3D capture as the final, with `outcome=review_required`.
The AI original remains available separately. This is a fidelity-review outcome,
not a provider error; do not claim the AI finish passed geometry validation.
Further style-aware fidelity review is separate work. No thresholds were relaxed
to make this trial pass. The diagnostic PNGs, request bodies and reports remain
outside Git. No production push was performed.
