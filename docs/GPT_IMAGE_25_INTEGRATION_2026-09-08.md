# GPT Image 2.5 and two-image comparison

## Student workflow

The aerial Direct 3D panel, pegman street render, and masked render editor now
offer **Flare + Sunburst · 2 images**. This is the default when the server's
OpenAI account lists both engines. Single-engine choices remain available.

The pair makes two separate, sequential image edits: Flare first, then Sunburst.
Both receive the same captured source, controls, style and customization. For
masked edits both use the original saved image and the same mask. Sunburst does
not refine Flare's output. Each successful result is saved before proceeding;
the first result remains available if the second request fails. An error stops
the batch without retrying or silently switching engines. Progress and call
counts are visible before and during the action. Video generation is unchanged.

## API contract and account rollout

Supported new IDs: `gpt-image-2.5-flare` and `gpt-image-2.5-sunburst`.
Both use the existing multipart `/v1/images/edits` adapter. Direct 3D keeps its
high quality, PNG output, explicit normalized dimensions, geometry attachments,
visibility inventory, source comparison and original-image retention. No
`input_fidelity` parameter or extra provider retry was added. Responses, audit
reservations and gallery records carry the engine actually used.

An authenticated, read-only `/api/v1/render/image-models` endpoint checks the
provider model list. It caches account capabilities for five minutes, keyed by
a credential hash; discovery errors have a shorter cache and are represented as
unknown availability. API keys are never sent to the browser. Older clients and
discovery failures retain the existing Image 2 default. Reopening the page checks
again; there is no scheduled polling or automatic image generation.

**Observed local access on 2026-09-08:** the configured key returned HTTP 404
`model_not_found` for both 2.5 model lookups. Image 2 returned HTTP 200 and the
model list included Image 2 but neither 2.5 engine. The local UI therefore keeps
Image 2 selected and marks the new engines as awaiting access. This establishes
current discovery access, not a live image-generation quality or latency result.
No paid image requests were made during this integration.

## Credits

Each image reserves credits independently and retains existing refund rules.
New-engine reservations provisionally use twice the previous engine's envelope:
the published per-token image/text rates are twice Image 2's. Both 2.5 engines
currently have equal per-token rates, but may consume different token counts.
This multiplier is an application credit policy, **not a measured per-image
provider cost**. Review it against actual usage after access and live trials.
New `xhigh`/`max` quality levels are not enabled in this change.

## Verification

- Backend: 185 passing tests covering multipart requests for all three engines,
  retained geometry prompts/masks, model-specific reservations, gallery metadata,
  refunds, account discovery and legacy compatibility.
- Frontend: 33 passing tests covering shared-capture sequencing, partial failures,
  street comparison, model forwarding and the render controls. TypeScript passes.
- Browser: actual-account fallback verified; pair controls checked with a clearly
  simulated availability response, then interception removed. Free geometry
  capture succeeded. The fixture account remained at 7,605 application credits.
- Visual evidence/logs live outside Git under
  `C:/dev-artifacts/CityPrompt/gpt-image-2-5-2026-09-08/`.

## Official references

- [Launch announcement](https://openai.com/index/introducing-chatgpt-images-2-5/)
- [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation)
- [Flare model](https://developers.openai.com/api/docs/models/gpt-image-2.5-flare)
- [Sunburst model](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)
- [API pricing](https://developers.openai.com/api/docs/pricing)

Next live pilot, once access is available: one close aerial pair and one street
pair, with identical capture fingerprints within each pair. Compare facade
identity, court dimensions, cropped/occluded assets, geometry drift, latency and
actual cost. No extra paid trial was scheduled by this change.
