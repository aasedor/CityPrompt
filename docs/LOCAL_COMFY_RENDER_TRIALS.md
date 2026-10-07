# Local ComfyUI render trials

This optional desktop pilot finishes a CityPrompt image. FLUX and Qwen appear
beside the regular GPT choices in the **Image engine** menu for Direct 3D aerial
and street renders. It runs native local ComfyUI graphs, uses zero CityPrompt
credits and makes no fal/OpenAI calls. Existing paid still, Kling and route-video
flows remain separate. The trial button is visible in development builds only;
the backend rejects production submissions even if the flag is enabled.

## Use

1. Start ComfyUI locally. For the 8 GB RTX 5060 / 16 GB RAM trial use:

   ```powershell
   cd C:\AI\ComfyUI_windows_portable
   .\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --disable-api-nodes --listen 127.0.0.1 --port 8188 --lowvram --cache-none --disable-pinned-memory --disable-async-offload --output-directory D:\ComfyUI-output
   ```

2. In the active checkout's ignored `backend/.env` set:

   ```dotenv
   COMFY_TRIALS_ENABLED=true
   COMFY_TRIALS_BASE_URL=http://127.0.0.1:8188
   ```

   Restart the backend and run the frontend development server. Only a loopback
   ComfyUI URL is accepted. Keep it bound to this computer, not a public network.

3. For a new view, choose **Present > Image > Advanced image controls > Image
   engine**, then **Qwen Image 2.1 · High quality · Local · Free** or
   **FLUX.2 Klein · Fast preview · Local · Free**.
   Generate normally. The current full-resolution 3D capture is saved first;
   its durable local job is polled and the generated image enters Project Renders.
   If interrupted, open **Local model trials** on that saved source to recover it.

   Alternatively, open a saved render in the project list, project gallery or image panel.
   Choose **Local model trials**, a model and a short prompt, then **Run local
   trial**. A saved 3D source can be finished with an image model. Availability
   lists missing model files or nodes. The local video experiment is shelved:
   it is excluded from image choices and new trial controls. Existing saved video
   results remain accessible. Masked Edit Render continues to offer GPT only;
   these local workflows do not support a pixel mask.

4. The panel polls and saves completed outputs to the usual persistent project
   gallery. Closing it pauses polling; reopening resumes the original job.
   Results can be viewed and downloaded in the panel. Image callbacks refresh
   the gallery; video callbacks use the existing saved-video pattern.

## Quality-focused local rendering (2026-10-06)

Select **Qwen Image 2.1 · High quality · Local · Free** for the quality-first
trial. It now uses 40 denoising steps and a native output budget up to
4,194,304 pixels, with a 2752-pixel longest edge. A square output is 2048 x 2048;
aspect ratio is retained to the model's 32-pixel grid. Smaller source captures
are resized before diffusion so the model generates the larger output directly.
This is not a post-generation enlargement. FLUX remains the fast-preview option.

The existing INT8 Qwen model and quantized text encoder fit this desktop through
CPU/RAM offloading; the full BF16 weights are not installed. Tiled VAE decoding
limits peak GPU memory. Larger images can take many minutes on the 8 GB card.
The UI waits up to one hour; closing the view preserves the original job for
recovery. No automatic lower-resolution substitution or repeat generation occurs.

The [official Qwen model guide](https://github.com/QwenLM/Qwen-Image-2.1) recommends
40 steps and native 2K-area resolutions. The previous 512-pixel/8-step settings
were a low-memory connectivity pilot, not a quality benchmark.

### High-resolution pilot

A single 2752 x 1472, 40-step local GPU run completed in 14 minutes 12 seconds
on this RTX 5060 / 16 GB RAM desktop. The full-resolution street-view source
and seed matched the earlier Qwen pilot; the prompt was refined to request
photographic materials and afternoon light, so this is not a settings-only
controlled comparison. Visual review found sharper brick, paving, foliage and
reflections while retaining recognizable building masses and window positions.
It is one reviewed sample, not a guarantee for every scene.

Evidence and the full output remain outside Git:
`C:/dev-artifacts/CityPrompt/local-quality-2026-10-06/`.
The source changes require a backend restart. Automatic approval review blocked
that restart during this turn; the previous server still uses the old preset.

## Installed model files / bounded defaults

| Preset | Diffusion model | Text encoder | VAE | Default |
| --- | --- | --- | --- | --- |
| FLUX.2 Klein 4B | `flux-2-klein-4b-fp8.safetensors` | `qwen_3_4b.safetensors` | `flux2-vae.safetensors` | 768px maximum edge, 4 steps, reference-latent image edit |
| Qwen Image 2.1 | `qwen_image_2.1_int8_convrot.safetensors` | `qwen3vl_8b_w4a8.safetensors` | `qwen_image_2.1_vae_bf16.safetensors` | Up to 4 MP / 2752px longest edge, 40 steps, native image-edit conditioning |
| Wan 2.2 TI2V 5B | `wan2.2_ti2v_5B_fp16.safetensors` | `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | `wan2.2_vae.safetensors` | 640px maximum edge, 20 steps, 49 frames at 24fps (~2 seconds), silent |

Place diffusion models, encoders and VAEs in ComfyUI's respective
`models/diffusion_models`, `models/text_encoders`, and `models/vae` directories.
Widths/heights are rounded to multiples of 32, preserving approximate aspect
ratio. The server reads the canonical full-resolution saved source from private
storage, then resizes that image for the GPU. Thumbnails and client-supplied
pixels, workflows, model paths and server URLs are never accepted.

The native graphs follow the official [FLUX Klein guide](https://docs.comfy.org/tutorials/flux/flux-2-klein),
[Wan 2.2 guide](https://docs.comfy.org/tutorials/video/wan/wan2_2) and
[ComfyUI server API](https://docs.comfy.org/development/comfyui-server/comms_routes).
Use an up-to-date ComfyUI that accepts client-assigned UUID `prompt_id` values.

## Recovery / provenance

Project metadata stores `local_comfy_trials`: requester, source render ID/hash,
prompt, models, seed, dimensions, steps and workflow version. A native ComfyUI
job UUID is committed **before** submission. Request-ID replay is idempotent;
changing intent under the same ID returns 409. Recovery reads that original job
and never resubmits. One unresolved local trial per project is allowed; ComfyUI
serializes the shared GPU queue. Project editor permission is required to submit
or recover; viewers can read saved history. There is no credit debit.

Images use existing gallery storage/dedupe, an illustrative label and a private
provenance JSON linking the source. Videos use the usual private video storage
and saved-video gallery, labelled local ComfyUI. Neither image nor video claims
verified geometry or a prescribed camera route.

Local image finishes do not enter the paid Direct 3D geometry-check, repair,
source-fusion or fallback pipeline. They show the generated pixels directly,
with a short style/custom prompt and a comparison notice. No application content
moderation node or prompt filter is added to these native image graphs. This
does not remove any behaviour learned by the model itself. Access checks,
loopback configuration, bounded GPU settings, request dedupe and storage
provenance remain active. Regular GPT processing is unchanged.

ComfyUI history is in memory. If it restarts before CityPrompt retrieves an
output, **Check saved job** may report a missing request. After two minutes,
**Mark missing job as failed** explicitly releases it only if the online ComfyUI
still confirms no queue/history record. A new run then requires an explicit new
trial. Existing files are not deleted. Outputs left only in ComfyUI must be
inspected/imported manually; no hidden generation loop attempts to replace them.

Model presence is not a promise of runtime stability or adequate memory. Low
resolution reduces inference memory but cannot fix incompatible native
dependencies. The first Wan pilot hit a native Torch access violation during
VAE construction after switching from the two image models. A fresh ComfyUI
process with the cache/offload flags above, followed by the dependency repair
below, completed the bounded video pilot. Restart ComfyUI between image and
video trials if this runtime becomes unstable; recover the original job before
explicitly starting a replacement.

## Original low-resolution desktop pilots

All three presets completed actual local GPU generation, persistent storage and
browser display on the RTX 5060 / 16 GB RAM desktop. Times below are ComfyUI
processing times, not guaranteed latency on other sources or hardware.

| Preset | Output | Processing time |
| --- | --- | --- |
| FLUX.2 Klein 4B | 768 x 416 image | 25.66 seconds |
| Qwen Image 2.1 | 512 x 288 image | 42.89 seconds |
| Wan 2.2 TI2V 5B | 640 x 320 MP4, 49 frames, 24fps, 2.04 seconds, no audio | 131.54 seconds |

The image pilots used the same saved 3D view. FLUX added more material and
landscape detail in this single comparison; Qwen stayed closer to the flat
source. Wan animated the cinematic street still and existing pedestrians, but
some frames softened architectural detail. These are experimental review
outputs, not evidence that either model preserves exact geometry or matches
Kling quality. Three bounded video submissions were needed: one native crash,
one blocked dependency, then the successful output. No paid provider calls or
CityPrompt credit debits occurred.

## Verification / local artifacts

Mocked tests cover native payloads, bounded dimensions, project/source ownership,
duplicate admission, receipt-loss recovery, gallery saving and missing-job
resolution. Set `CITYPROMPT_TEST_DATABASE_URL` to a disposable PostgreSQL
database for isolated-schema API tests. Run:

```text
backend: python -m pytest tests/test_comfy_trials.py tests/test_render_animation.py tests/test_kling_video.py -q
frontend: npx vitest run src/components/viewer/LocalComfyTrialButton.test.tsx src/components/viewer/AnimateRenderButton.test.tsx
frontend: npx vitest run src/services/localImageRender.test.ts src/components/viewer/globe/useDirect3DRender.test.ts src/components/viewer/useImageModelChoice.test.ts src/components/viewer/runImageModelBatch.test.ts src/components/viewer/StreetViewPanel.test.tsx src/components/viewer/globe/GlobeAIRenderPanel.direct3d.test.ts
frontend: npm run type-check
```

Runtime trials, model-download receipts, screenshots and dependency backups stay
outside Git in `C:/dev-artifacts/CityPrompt/local-comfy-trials-2026-10-07`.
The installed portable PyAV 19 library was blocked by Windows Application
Control. Its supported PyPI `av==17.0.0` replacement let ComfyUI start. The
installed SentencePiece 0.2.2 native library was also blocked; the trusted PyPI
`sentencepiece==0.2.1` replacement imported successfully and let Wan run. Both
prior packages were backed up in the artifact directory. No Windows security
setting was changed. These repairs apply to this installed portable runtime,
not to CityPrompt's backend Python environment.
