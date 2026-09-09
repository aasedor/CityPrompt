# Render style detail pilot — 8 September 2026

## Accepted visual direction

The student-authored 3D scene owns the design. Rendering improves materials,
lighting and the selected artistic medium while retaining building identity,
camera, circulation and occlusion. People are optional and belong on existing
walking surfaces or seats.

The user explicitly approved the baseline street photomontage in this pilot:
`photomontage-provider_original-02fe5846.png`. Its matching source is
`02-audit-input_image_key.png`. Keep this pair as the human-approved visual
benchmark. An automated `review_required` result must not invalidate that
approval or hide a useful illustration. This change retains the existing
advisory comparison and original-image saving behaviour.

## Live trial

Project: **Currie Commons - student community trial**,
`bb4a6a7b-479f-45a1-b7f2-94f50b84e696`.

Calls were made through City Prompt's actual render controls. Street views used
the pegman, **Add People** on and vehicles off. The aerial tests used the prompt
box for camera, roof and occlusion instructions. Free captures were inspected
before spending. Every reviewed image below is the provider output, not a
source fallback presented as an AI success.

| Call | View / style | Finding |
| --- | --- | --- |
| 1 | Oblique aerial, baseline watercolour | Attractive medium, but changed the foreground timber roof into a hipped roof. |
| 2 | Close north-facing street, baseline photomontage | User-approved benchmark: recognizable buildings and park, plausible people and materials. |
| 3 | Same street, baseline watercolour | Grey/wood infill became brick/red material; extra cafe furniture appeared. |
| 4 | Same street, revised medium/people text | Improved painted treatment; material drift and extra furniture remained. |
| 5 | Same street, revised text plus source-only identity conditioning | Grey-and-timber facade retained; no extra cafe furniture observed. Expressive painted finish preserved. |
| 6 | Restored close street, revised photomontage | Photographic character retained, natural walking/seated people, recognizable grey-and-timber buildings and park. |
| 7 | Very close 30-degree timber-building view, charcoal | Shallow roof, balcony screen and visible openings retained. Park remained partly hidden; no added people or cars observed. |

All **7 provider calls completed and saved**, within the authorized maximum of
10. Each consumed 83 application credits (581 total). No automatic retry or
additional video generation was used. Calls 6 and 7 returned provider images in
about 108 and 97 seconds respectively; these observations are not a latency
guarantee. Saved source comparisons are additional gallery files, not extra
provider calls.

Useful final examples: `watercolour-provider_original-dc1e8317.png`,
`photomontage-provider_original-102c747a.png`, and
`charcoal-provider_original-bc22803c.png` in the evidence directory below.

Calls 2 and 3 used byte-identical source images. The source images for 3 and 4
were nearly identical (mean absolute RGB difference about 0.019/255). Call 6
followed a local runtime restart and camera restoration, so it is a regression
example rather than a controlled pixel-identical comparison. These are small
visual samples, not proof that generative geometry drift has been eliminated.

## Implemented changes

- All same-camera Direct 3D finishes now take identity from the captured model.
  Catalogue photos and design-identity prose are excluded for precise, balanced
  and expressive policies. The server's full inventory still validates the
  project; geometry/instance/depth/material guides remain. Explicit projection
  changes retain their existing reference path.
- Watercolour describes transparent washes, pigment granulation, paper and
  selective dry-brush edges while retaining openings, roofs and path boundaries.
- Charcoal describes actual marks, rubbed tones and lifted highlights;
  risograph confines ink misregistration to surface texture.
- Photomontage and survey no longer prescribe an aerial camera to a street
  capture. Development, atmospheric, winter and night no longer request new
  furniture or unselected people/vehicles.
- **Add People** supplies scale, pose, ground contact and occlusion guidance.
  The existing people/vehicle toggles retain control.
- Both panels skip catalogue-reference downloads for same-camera finishes,
  removing unnecessary preparation work. Render help text now describes saved
  illustrations and advisory comparison consistently with the result panel.

The [official image prompting guide](https://developers.openai.com/api/docs/guides/image-prompting)
supports explicit visual descriptions, clearly separated editable attributes
and invariants, and distinct roles for references. These changes apply that
guidance to the pilot's observed failures. The first Image 2.5 comparison should
keep source, prompt and quality constant so a model change can be evaluated.

## GPT Image 2.5 setup

The integration already supports Flare, Sunburst and a two-call comparison from
one source capture; see [integration notes](GPT_IMAGE_25_INTEGRATION_2026-09-08.md).
The fresh read-only check at **2026-09-09 03:56 UTC** returned:

| Model | Listed by current key | Model lookup |
| --- | --- | --- |
| `gpt-image-2` | Yes | HTTP 200 |
| `gpt-image-2.5-flare` | No | HTTP 404 `model_not_found` |
| `gpt-image-2.5-sunburst` | No | HTTP 404 `model_not_found` |

Consequently these live results are **Image 2**, not a demonstrated 2.5
comparison. No paid requests were sent to unavailable engines. The error does
not establish whether rollout, project permissions or verification is the
specific cause.

The account owner should check the organization/project used by City Prompt's
API key in [organization settings](https://platform.openai.com/settings/organization/general)
and its model access. Complete verification only if the console requests it;
the [generation guide](https://developers.openai.com/api/docs/guides/image-generation)
says it may be required. If verification is already complete and these model
IDs remain unavailable, request access/help for that API project. Additional
credits alone do not resolve a `model_not_found` response.

After access changes, reopen City Prompt after its five-minute discovery cache
expires and select **Flare + Sunburst · 2 images**. Each engine receives the same
capture; Sunburst does not edit Flare's output. Start with this approved street
camera, then one oblique pair, before altering quality settings or scaling up.

The provisional app-credit envelope remains an estimate. The central
[pricing table](https://developers.openai.com/api/docs/pricing) lists 2.5 rates
at twice Image 2, while the Sunburst model page currently contains conflicting
"rates match" prose. Reconcile actual provider usage before treating the
application multiplier as a measured per-image cost.

## Verification and local evidence

- Backend: 182 tests passed in `test_direct_3d_render.py` and
  `test_direct_3d_presentation_first.py`.
- Frontend: 39 tests passed across `useDirect3DRender.test.ts`,
  `StreetViewPanel.test.tsx` and `GlobeAIRenderPanel.direct3d.test.ts`.
- TypeScript: `tsc --noEmit` passed after the final panel preparation cleanup.
- React review: reference downloads are conditional on their actual use;
  no new effects, subscriptions, network polling or dependencies were added.
- Visual outputs, call ledger, audit inputs/outputs and model-access evidence
  live outside Git at
  `C:/dev-artifacts/CityPrompt/render-style-detail-pilot-2026-09-08/`.

Local restart recovery reuses the original database and media volume. MinIO
uses port **19002** because Windows reserved the former **59002** port. Vite
uses the prepared `runtime-v4/public` asset directory; pointing it at the raw
checkout omits the park pilot GLBs/textures. These machine-local launchers and
generated outputs are not source deliverables or production deployment changes.
The prepared root also needed its `park-trio-v3` junction restored to
`C:/dev-artifacts/CityPrompt/park-trio-2026-09-06/public/landscape-pilots/park-trio-v3`
for community-garden beds, labels and shelter. The final reload was checked
against the browser's accumulated error count after restoring these assets.
