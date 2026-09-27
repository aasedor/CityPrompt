# Video Render: geometry-first finishing ("Structure Lock")

Branch: `claude/geometry-first-video` (2026-09-26). Companion docs:
`VIDEO_RENDER_QUALITY_BAR.md` (the goal post), `VIDEO_RENDER_INTERNAL_ENHANCE.md`
(the deterministic source), `video-pilots/OMNI_PILOT_3_BASELINE.md` (why short
prompts).

## Decision

City Prompt renders the 3D scene so the video engines do not have to. Until
now the engines were steered almost entirely by prose: `build_cinematic_prompt`
emitted about 8,500 characters of lock text plus a per-zone contract that grew
by ~590 characters per building, while the depth, normal and ID passes the
scene already produced were stored and never sent anywhere. The result was the
pattern every trial showed: edits relit but redrew the design, keyframe modes
kept the design but ignored the look, and the appearance score called a correct
night render "drift".

The video pipeline now works the way the image pipeline already does:

1. **Geometry travels as data.** The route capture encodes a second track beside
   the beauty preview: 8-bit inverse depth (bright = near) rendered from the
   same 192 camera poses through a linear-depth variant of the Direct 3D
   geometry material. Engines that accept a control video obey it; the scorer
   compares finished frames against it.
2. **The prompt is a look sheet.** The student picks a look (the same vocabulary
   as the Direct 3D image styles), people and vehicle toggles and an optional
   240-character note. The server composes at most 900 characters: the look,
   one camera sentence, one preservation sentence, the studio-reel motion clause
   and a clean-plate line. No zone IDs, no checksums, no lock walls.
3. **Geometry is scored separately from appearance.** `geometry_score` measures
   depth-silhouette recall and explained-edge precision after a contrast stretch
   and CLAHE, so a night finish keeps geometry 100 while image similarity drops.
   It is advisory until the evaluation harness calibrates its bands.
4. **Appearance comes from a verified still (the anchor frame).** The route
   capture keeps a complete Direct 3D bundle of frame 0. One click in the panel
   renders it through the existing image endpoint (same GPT Image model, same
   look vocabulary, people/vehicle toggles and note, fused and edge-checked
   server-side, normal image credits). The result travels as
   `anchor_image_base64`: Structure Lock uses it as `ref_image_urls[0]` and
   `first_frame_url` (it is literally the first frame from the same camera),
   Omni receives it as a second input beside the route video, and the prompt
   gains one sentence: "Match the materials, light and colour of the reference
   image." Grok's edit endpoint takes video only, so it never gets one. A frame
   rendered for another look, or with different entourage, is never sent.
   This is how the video reaches the quality bar of the image renders: the
   still is the target and the engine's job shrinks to carrying it across 192
   frames along a camera it did not have to invent.

## Engines

| Engine | Input it obeys | Prompt | Credits / cap | Output |
|---|---|---|---|---|
| Gemini Omni (`gemini-omni-1.1-flash`, task `edit`) | the beauty preview (camera, timing) + optional anchor frame | Omni look sheet: "Change only the look of this video: … Keep everything else the same …" | 50 / 49 | 1080p URI delivery |
| Structure Lock (fal `fal-ai/wan-22-vace-fun-a14b/depth`) | **the depth track** (`preprocess: false`), normalised to 720p grey H.264, + optional anchor frame as reference and first frame | positive end-state + fixed negative prompt; prompt expansion off | 50 / 12 | 720p |
| Grok Video (xAI `/videos/edits` on `grok-imagine-video`; image modes on `grok-imagine-video-1.5`) | the beauty preview; falls back to the guide frame if xAI rejects the video (`grok_reference_mode`) | Grok look sheet (edit) or lock + camera + look (image modes) | 75 / 20 | 720p, silent |
| Seedance Mini, Internal Enhance | unchanged | legacy prose / local contract | 125 / 4, 0 / ∞ | unchanged |

Registry: `backend/app/services/video_providers.py`. Prompts:
`backend/app/services/video_prompts.py`. Engines: `omni_video.py`,
`vace_video.py`, `grok_video.py`.

## The depth track

- Rendered by `createDirect3DLinearDepthSession` (`frontend/src/components/viewer/globe/direct3dCapture.ts`)
  inside the same frame loop as the beauty preview
  (`captureDeterministicVideoTracks`, `deterministicVideoCapture.ts`). One
  shader per source material, compiled once before the loop; tile demolition
  cuts, alpha cutouts and sidedness follow the beauty material policy.
- Encoding: `value = clamp((1/z − 1/far) / (1/near − 1/far), 0, 1)` from a
  view-space varying, so it is independent of the globe's logarithmic depth
  buffer and of the camera near/far planes. The window is constant per clip
  (`videoDepthWindow.ts`): aerial near = 0.35 × camera-to-route distance, far =
  5 ×; near-field routes 2 m … 400 m. Bright = near, black = far and sky.
- Grey H.264 at ≤ 6 Mbps; the luma channel carries the whole signal, so chroma
  subsampling cannot damage it. RGB-packed 24-bit depth would not survive.
- Sent as `control_videos[{role:'depth'}]`; validated by
  `backend/app/services/video_controls.py` (container magic, ≤ 12 MB, ≥ 150
  frames, dimensions equal to the preview, not flat); stored at
  `controls/depth-control.mp4`; hashed into the attempt.
- Browsers without WebCodecs record the beauty track only; Structure Lock then
  says so and the other engines still work.

## Verification status

- Unit tests: `backend/tests/test_video_prompts.py`, `test_video_controls.py`,
  `test_video_geometry_score.py`, `test_vace_video.py`, `test_video_providers.py`,
  `test_grok_video.py`, updated `test_omni_video.py`;
  `frontend/src/components/viewer/deterministicVideoCaptureTracks.test.ts`,
  `videoDepthWindow.test.ts`, `videoLookSheet.test.ts`,
  `VideoGeneratePanel.test.tsx`, `globe/direct3dLinearDepth.test.ts`.
- Paid smoke runs and the evaluation matrix (`docs/video-pilots/eval-<date>/`)
  are recorded here once they have been run.

## The anchor frame

- Captured by `captureVideoRouteControls` at route pose 0 as a complete
  Direct 3D bundle (`VideoRouteCaptureResult.anchorCapture`). High aerial
  routes reuse the checkpoint capture; Draft and near-field routes take one
  extra capture, and a failure there only disables the anchor.
- Rendered on demand from the Video Render panel ("Render anchor frame") with
  `useDirect3DRender` — the same call the image panel makes — using the look's
  `imageStyle`, the people/vehicle toggles and the student note. Review-flagged
  results are shown with a warning, not blocked.
- Sent as `anchor_image_base64` (PNG/JPEG, decoded like the guide frame);
  stored at `controls/anchor.{png|jpg}`; `anchor_attached` / `anchor_image_url`
  in the attempt ledger; hashed into `guide_sha256`. Only the preview edit of
  Omni or Structure Lock accepts it (400 otherwise).

## Open items

- VACE `preprocess: false` input format is confirmed by the first paid run; the
  fallback is `preprocess: true` on the beauty preview.
- Geometry bands (stable ≥ 68 / 55, review ≥ 48 / 32) are provisional.
- LTX-2.3 depth/canny and Luma Ray 3.2 Modify are the next engines once a key
  and a run budget exist.
