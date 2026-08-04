# Video Render: Internal Enhance

## Product decision

Internal Enhance is a self-hosted restoration pipeline, not a second scene
generator. The deterministic City Prompt route preview remains the authority
for camera motion, Google-tile context, building geometry, embedded GLB skins,
open-space assets, and timing. This deliberately trades Omni-style invention
for much stronger frame-to-frame identity.

The Video Render panel exposes two local tiers:

- **Fast Cleanup** (default): conservative denoising, antialiasing, tonal
  stabilization, sharpening, H.264 delivery, and fidelity scoring. It runs on
  CPU, costs $0, and should finish in seconds.
- **GPU Detail** (explicit): the same source lock plus Real-ESRGAN NCNN Vulkan
  super-resolution before final downsampling. It is meant for queued final
  exports, has a hard model timeout, and automatically saves Fast Cleanup if
  the model cannot finish.

Neither tier may add, remove, replace, or reshape an object.

## Reused City Prompt resources

No new skin library is required for the pilot. The captured route video
already contains the resources assigned to the project. Each saved attempt
records the discovered resource families and render-locked asset count.

The Calgary pilot resolved:

- `parisian-haussmann-classic-v1-renderlocked`
- `parisian-boulevard-corner-v1-renderlocked`
- `open-space:beer_garden:beer_garden_v0`
- seven render-locked building asset instances

This is the safest way to reuse existing skins today: enhance their rendered
pixels instead of asking a generative model to reconstruct them from names or
prompts.

## Pipeline

The panel defaults to **High Quality**. Draft remains available for quick path
checks on integrated-GPU laptops.

1. Resolve the camera path, switch the camera to a true 16:9 projection, and
   perform a dry traversal of all 192 route poses. High Quality waits for tile
   stability at 25 evenly spaced checkpoints, lowers the Google-tile screen
   space error target, raises texture anisotropy, and temporarily holds the
   warmed tile cache for the complete take. Draft uses six warmup poses.
2. High Quality renders each indexed frame into a 2560×1440 WebGL backing
   surface with antialiasing, then downsamples to a 1920×1080 delivery frame.
   Draft renders and delivers at 1280×720. Each frame's camera pose and
   timestamp come from its index (24 fps over eight seconds), never from
   browser render speed.
3. At the six route checkpoints, capture synchronized beauty, semantic class,
   stable instance ID, depth, and view-space normal passes. Record all 192
   fixed camera-motion samples. These controls are currently retained as
   capture-audit metadata and establish the inputs for the temporal neural
   cleanup stage; they are not sent to Omni.
4. Encode those frames locally as a high-bitrate H.264 MP4 with explicit
   timestamps. Browsers without WebCodecs use a paced WebM compatibility path;
   the backend rebuilds its timestamps from decoded frame order.
5. Save the guide, route preview, source-quality preset, capture-pass audit,
   resource provenance, and an idempotent run reservation before processing.
6. Run Fast Cleanup, or GPU Detail when explicitly selected and installed.
7. Fall back to Fast Cleanup if GPU Detail times out or fails.
8. Encode an eight-second H.264 MP4 with fast-start metadata. High Quality
   preserves 1920×1080 delivery; Draft uses 1280×720.
9. Score five temporal samples against the deterministic preview.
10. Save the MP4, fidelity report, engine, processing time, and fallback
    warning to the project render log. Local runs consume no credits.

The same fixed-frame preview can be supplied to Omni in preview-video mode.
In that workflow Omni is asked to animate an already complete City Prompt
camera take; it is not asked to infer the route or reconstruct the scene from
one image. This reduces, but cannot entirely eliminate, generative drift.

The 192 frames remain canvas surfaces until they enter the
native encoder; City Prompt does not hold or upload 192 PNG files. This keeps
the deterministic frame sequence practical on student laptops while avoiding
the wall-clock frame skipping of live canvas recording.

High Quality is intentionally a bounded two-pass workflow: tile warmup first,
then one deterministic render/encode pass. If the browser reports a texture
limit below the 2560×1440 target, the panel fails clearly instead of silently
producing a degraded or incomplete source.

## Pilot result (2026-08-03)

Two attempts completed and are downloadable from the project render log.

- Fast Cleanup attempt `3ffa83ae-ad15-499c-80d4-bc947357db98`:
  1280×720, 24 fps, 8.0 seconds, H.264; **95.2/100 (stable)**
  fidelity; 2.4 seconds of server processing
- GPU Detail attempt `108c5749-cdad-40d6-8663-9238c95d960d`:
  **94.4/100 (stable)** fidelity; its model exceeded the original 15-minute
  guardrail, so the attempt saved the deterministic Fast Cleanup output as
  designed
- Cost and credits: **$0 / 0 credits**
- Existing automatic Omni benchmark: 91.7/100 fidelity

The score measures source identity, not photorealism. The internal result is
more geometrically faithful than the benchmark but remains limited by the
detail and lighting present in the Direct 3D source.

## Local model installation

Set `INTERNAL_VIDEO_UPSCALER_PATH` on a render worker to the official
`realesrgan-ncnn-vulkan` executable. Keep its binary and model files in ignored
local artifacts or a worker image; do not commit them to the application repo.
Preflight rejects GPU Detail when the optional model is unavailable. Fast
Cleanup only requires `ffmpeg`.

## Roadmap toward a stronger internal model

1. Improve the deterministic source before adding more generation: PBR
   materials, shadows, atmospheric lighting, antialiasing, higher-resolution
   capture, and authored vegetation.
2. Expand the synchronized beauty, depth, class-ID, instance-ID, and normal
   controls from six audited checkpoints to all 192 frames, and derive dense
   motion vectors from the recorded camera/object transforms.
3. Train a small temporally consistent enhancement model on City Prompt's own
   render pairs, conditioned by depth and instance identity. Losses should
   heavily penalize silhouette, courtyard, roofline, and context drift.
4. Add tiled inference and persistent worker queues so GPU Detail is reliable
   and does not hold a browser request open.
5. Keep Omni as an optional animator or final polish stage only after the local
   fidelity gate passes.

An internal model should never learn to redesign the site. Its competitive
advantage is that City Prompt owns the geometry, camera, semantic masks, skins,
and temporal identity that a general video model must guess.
