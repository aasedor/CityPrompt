# CityPrompt high-resolution RLASM media pilot

Status: **finite pilot complete; review evidence only; not a keeper**

Date: 2026-08-31

CityPrompt project: `e7e01e0b-993d-4336-8dfb-2341f078dfd5` (`RLASM Scale + Public Realm Trial v001`)

This trial exercised the two-stage high-resolution workflow:

1. CityPrompt supplied a source-locked RLASM control scene on Google Tiles.
2. Image and video providers were asked to improve finish while preserving the control scene.

The authorized finite budget was used exactly: four image-provider calls and two video-provider calls. No further provider calls were made. The outputs remain review evidence because the holistic builder gate still has P0/P1 blockers. No `KEEPER.json` was created.

## Locked sources

| Asset | Locked path | SHA-256 |
| --- | --- | --- |
| Calgary bungalow source GLB | `artifacts/rlasm-calgary-inner-city-bungalow-v020/model/calgary-inner-city-bungalow-v020.glb` | `94794941a0b266797e87a78d246087d84b0d9eeb8143761a57071e7254ce3987` |
| Calgary bungalow CityPrompt delivery GLB | `artifacts/cityprompt-rlasm-delivery-2026-08-31/models/calgary-bungalow-v020-cityprompt-v001.glb` | `d5b32558a15d4771f28efb84c81b06fcf3b7e98fc59abf7aab1dae62c6628416` |
| Farnsworth pavilion source GLB | `artifacts/rlasm-farnsworth-house-glass-pavilion-v004/model/farnsworth-house-glass-pavilion-v004.glb` | `3d6beea2a8eca8f70e90d63813a70401fe74ac5fc7b19e121ca4b081aabce774` |
| Farnsworth pavilion CityPrompt delivery GLB | `artifacts/cityprompt-rlasm-delivery-2026-08-31/models/farnsworth-v004-cityprompt-v002.glb` | `6a5a1cde4b6839eb32ba6ee9734c5dec1f2f76d93a3612f3e84fa7aa46ff2515` |
| Farnsworth glass optical source | source-conditioned material input | `54134892f4dbd5317d39d6eb1fcd1ada26eda698ead6baa64f95161def32a1ac` |

The complete source and delivery provenance remains in:

- `artifacts/cityprompt-rlasm-delivery-2026-08-31/provenance/calgary-bungalow-v020-cityprompt-v001.json`
- `artifacts/cityprompt-rlasm-delivery-2026-08-31/provenance/farnsworth-v004-cityprompt-v002.json`
- `artifacts/cityprompt-rlasm-scale-park-street-trial-2026-08-31-v001/TRIAL_MANIFEST.json`

The CityPrompt trial placed three bungalow scales (0.72x, 1.00x, and 1.35x) and one 1.10x pavilion at a shared terrain elevation of `1025.677204212151`. The scene policy was continuous level grade, no tile mask, no floating or buried mass, and no grey carrier polygon.

## Image-provider record

All four image calls used `gpt-image-2` and cost 92 local render credits each. Street-view calls used the Documentary preset. The main pavilion call additionally used this source-preservation prompt:

> Close architectural documentation of the source-locked RLASM glass pavilion. Preserve the exact long low Farnsworth-derived massing, white steel columns and fascia, stone and golden wood floor planes, clear glass curtain wall, sliding entry, stair and stringers, isolated columns and footings, roof edge/caps, and visibly occupied kitchen depth behind glazing. Keep this camera and proportions. Replace the white or grey carrier pad with continuous level site ground and physically believable contacts. Do not redesign, add generic materials, float, bury, or hide the pavilion.

| # | Render | Audit ID | Pixel-gate result |
| --- | --- | --- | --- |
| 1 | [Bungalow rear documentary](renders/01-bungalow-rear-documentary.png) | `4c828f6c-90b5-4ed4-9b5e-d960da3599fd` | Review. Grade contact and no-pad policy pass, but identity is genericized and front porch/dormer proof is absent. |
| 2 | [Bungalow porch-angle documentary](renders/02-bungalow-porch-angle-documentary.png) | `27c5363d-06c6-4fd0-9a0d-2932b5ee6603` | Review. Public realm is coherent, but the target is too small and the requested porch, dormer, opening depth, and contact details are not proven. |
| 3 | [Pavilion glass-depth safety return](renders/03-pavilion-glass-depth-safety-return.png) | `75f352ef-60c1-4659-b39f-060be6ea3217` | Fail/P0. Provider drift was rejected and the server correctly returned the authoritative source frame; that frame still exposes a large white/brown carrier pad and coarse tile context. |
| 4 | [Pavilion stair/glass south documentary](renders/04-pavilion-stair-glass-south-documentary.png) | `61767c66-5cc6-4d4e-8b5d-16a8ebb49d70` | Fail/P0. The enhanced output omits the pavilion entirely. |

## Video-provider record

Both calls used Gemini Omni `gemini-omni-flash-preview` in preview-video edit mode. Each route used a deterministic 192-frame, 24 fps, eight-second source video, rendered at 2560x1440 and downsampled to 1920x1080 H.264. Both videos remain saved in the CityPrompt project and are intentionally not stored as ordinary Git blobs.

| # | Route | Trial ID | Fidelity | Pixel-gate result |
| --- | --- | --- | --- | --- |
| 1 | Street walkby | `8435879e-78f2-4fbd-ad5c-ea218db2756c` | 58.9/100; checkpoints 57.3, 53.9, 51.1, 61.2, 70.9 | Review/P1. Coherent motion and architectural atmosphere, but the pavilion is redesigned and exact source identity is lost. |
| 2 | Detail flythrough | `6b4e33da-4902-4efb-9497-083a27ce5881` | 68.0/100; checkpoints 73.0, 59.4, 62.7, 70.2, 74.8 | Review/P1. Stronger temporal result, but the output follows generic bungalow/public-realm imagery instead of the intended pavilion close-up. |

The first video preflight observed 2,057 building meshes, 2,116 PBR materials, 44 instanced detail meshes, and 2,087 shadow casters. The largest visible building texture was 1,254 px, below the intended 2K close-detail target. A first attempt at the second route was rejected before provider submission because source frame 4 contained clipped/blank foreground; the corrected version passed. This preserved the two-call limit.

## Builder review

The control-bundle implementation worked as intended in important ways: it preserved source-specific material boundaries, produced lossless semantic/instance/depth/normal/material passes, detected material-family conflicts before spending credits, rejected one provider drift result, and rejected a clipped video route before provider submission.

The pilot does **not** pass the strict RLASM builder gate:

- **P0 — target presence:** one pavilion still omits the target completely.
- **P0 — physical contact/carrier:** the authoritative pavilion source frame still shows a large carrier pad instead of continuous ground and resolved supports.
- **P1 — camera registration:** several close-up requests frame the wrong facade, hold the target too small, or follow the context rather than the selected model.
- **P1 — source identity:** provider outputs genericize the authored RLASM materials, openings, pavilion structure, and occupied depth.
- **P1 — close-detail resolution:** visible source textures top out at 1,254 px, below the 2K target for these routes.
- **P1 — opening/detail proof:** carrier cut, reveal/return, frame, recessed pane/screen, separate occupied depth, and signature contacts are not all legible in the accepted frames.

Because these are holistic blockers, neither the scoped material/contact improvements nor the better of the two video scores can promote a keeper. An independent keeper review is intentionally deferred until the next source-locked correction version has zero builder P0/P1 blockers.

## Next correction version

1. Bind close-up still and video cameras to the selected model's world-space bounds and named architectural targets, not only the map pin or a cardinal route.
2. Require target-presence, projected target coverage, complete-envelope, and protected-instance thresholds before provider submission and again before accepting output.
3. Remove carrier-pad geometry from the pavilion delivery asset and resolve terrain contact through physical columns, stairs, footings, and continuous grade.
4. Promote source-conditioned building textures to at least 2K for close routes while retaining the original PBR material roles.
5. Provide locked source/model boards or registered source views as identity conditioning, then reject outputs that substitute generic materials or redesign protected geometry.
6. Capture close views that visibly prove opening depth, glass layers, occupied interiors, roof/flashing contacts, and load paths.
7. Repeat a finite correction batch and run a separate holistic source-locked visual review before creating any keeper record.

## Process evidence

The [process folder](process/) contains 26 screenshots covering camera placement, deterministic control frames, still preflights, provider results, the rejected clipped video preflight, corrected routes, and final video fidelity scores. File hashes and provider provenance are recorded in [TRIAL_RESULT.json](TRIAL_RESULT.json).
