# Omni 1.1: research for lifelike CityPrompt video

Research date: 2026-10-21 UTC (2026-10-20 Edmonton).
Runtime inspected: `0d5668613`, on `codex/omni-11-video-pilot`.
This is research, not a tested prompt change or production deployment.

## Corrected creative target

The user clarified that the video should improve the scene and look lifelike.
Changing flat materials, lighting, vegetation, sky and atmospheric detail can
therefore be a successful transformation. Exact source-pixel preservation is
not the objective. Preserve the development's recognizable spatial design:
building locations, principal massing, park/road connections and camera route.
An invented bridge is a spatial redesign; more convincing masonry or reflections
are visual improvements. A material change alone is not an automatic failure.
The earlier transport test results and original media remain unchanged.

## Primary sources and example review

- [Google's Omni 1.1 launch and demo gallery](https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-omni-1-1-flash/).
  Reviewed its real-estate walkthrough, cinematography and upscaling montages.
  Google describes inexpensive 360p exploration and first/last-frame control.
  These are selected promotional examples, not a success-rate evaluation.
- [DeepMind's prompt guide](https://deepmind.google/models/gemini-omni/prompt-guide/).
  It emphasizes visual style, illumination, framing and action, with reference
  images (including Nano Banana output) to establish consistent appearance.
- [Gemini API guide](https://ai.google.dev/gemini-api/docs/omni).
  Editing guidance favors focused instructions. The API distinguishes an edit
  source from style/subject references and start/end frames. 1080p and 4K are
  upscaled outputs. A higher resolution is not evidence of better realism.
- [DeepMind capability examples](https://deepmind.google/models/gemini-omni/).
  The sketch-to-realistic-video example demonstrates explicitly requesting
  a change in visual representation instead of preserving the sketch's look.
- [Model card](https://deepmind.google/models/model-cards/gemini-omni-flash/).
  Temporal consistency and complex motion remain acknowledged limitations.

Three public demo files were downloaded only for local research. Six frames
per file were inspected; this was not a full motion/physics audit. URLs, hashes,
container metadata and sample sheets are retained in
`C:/dev-artifacts/CityPrompt/omni-realism-research-2026-10-21/`.
Do not republish these vendor videos as CityPrompt outputs.

| Example | Visual observation from sampled frames | Transfer to CityPrompt |
| --- | --- | --- |
| Listing Walk In, 35.67 s promotional montage | Photographic room appearance is already present in the input display. Wood, fabric, windows and shaded corners provide a convincing starting appearance. The on-screen demo labels sequences shortened and screen images simulated. | Use a reviewed, photorealistic image of the actual project as the visual target. The montage is not evidence that a raw clay city automatically reaches that result. |
| Cinematography, 32.04 s montage | Close framing, a readable person, textured stone, directional light, shadow and perspective depth. | Compose a shot with a clear subject and meaningful camera movement; judge people at a useful screen size. |
| Upscaling, 22.76 s montage | Fish, fur and translucent leaves have coherent texture, depth and light before the resolution comparison. The downloaded web montage itself is 1920×1080. | Establish convincing appearance first. A 4K label or export cannot repair a synthetic-looking scene by itself. |

## Diagnosis of our trials

The active `preview_video` prompt contains about 100 words. Its first sentence
asks for realistic materials/daylight/shadows; much of the remainder is camera
and preservation constraints. No appearance reference is attached: the request
contains the raw 3D video plus text. This is evidence from the actual code and
the saved submitted prompts, not a guess about provider settings.

The matched park frames retain flat lawns, sparse trees and an orderly rendered
appearance, despite improved paving, shadows and an added woman/dog. The framing
has a large amount of lawn and a parking structure in the background. The scene
does not provide a strong photographic reference for skin, planting or building
surface detail. This plausibly contributes to the result; it is not an isolated
causal finding because prompt, framing and scene position changed across trials.

Other control-mode prompt branches contain stricter pixel/style preservation.
Those branches were not used by the two follow-up video-edit submissions. Do not
mistakenly attribute their prohibitions to the submitted 100-word prompts.

The current similarity score combines SSIM, edges and color histograms. It does
not measure whether a video resembles photographed reality. A result that
retains simplistic source pixels can score well. Evaluate visual realism and
spatial design separately; retain the original score as a diagnostic only.

## Recommended approach, not yet validated

First compare a concise transformation prompt against the same existing source,
without adding an actor. This isolates prompt intent at minimal scope. Then
test the same request with a reviewed photorealistic still of that exact scene
as an appearance reference, while the original video controls the route/layout.
Adding a new reference input requires a local payload/UI pilot; it is not
supported by the current `preview_video` request builder.

Reference-first is the stronger hypothesis for a substantial quality jump:
show the desired finished world instead of asking Omni to infer it entirely
from a schematic recording. Use an existing suitable saved image when available;
otherwise generating the reference itself also consumes paid credits.

Start/end photorealistic frames are a separate optional experiment supported by
the model, not interchangeable with a source video. They may improve appearance
but provide less evidence of exact route reproduction. Independently generated
end frames can disagree about materials or geometry; they require review before
being used together. Do not silently replace video-to-video with this mode.

For the park shot, use a legible foreground subject with buildings and road
connections visible behind it. Allow realistic planting, subtle leaf movement,
material texture and reflections. Avoid requesting crowds, traffic maneuvers,
weather changes and elaborate camera moves in the same first test. A gimbal
walk or modest drone pass fits the intended presentation better than an almost
stationary distant overview. Keep one continuous shot and stable geometry.

## Proposed prompts, untested

### Direct video transformation baseline

> Transform this 3D architectural preview into convincing live-action footage
> of the completed development. Render its surfaces and vegetation as real
> materials, with natural daylight, believable reflections and grounded shadows.
> Keep the same building massing, site layout and camera movement throughout
> one continuous shot. The scene should look filmed on location.

Optional activity sentence, tested only after the visual treatment works:

> A woman walks her dog naturally along the park path.

### Video with a reviewed appearance reference

> Use the video for the development layout and camera movement. Use the image
> for the finished photographic appearance. Transform the whole clip into
> live-action footage with that material and lighting treatment. Keep the
> buildings and routes in place in one continuous shot.

Bind media roles explicitly using the current API contract when implementing;
do not rely on input ordering alone. Neither proposed prompt has been submitted.

## Evaluation and next pilot

Use three independent checks: (1) does it look photographed, including materials,
light and vegetation; (2) does motion remain coherent, including feet, contact,
reflections and camera parallax; (3) is the development still recognizable,
including building count/massing and road/park connections. Review all three
over time, not just the nicest still. Improved appearance should pass even when
source pixels change. Invented structures or melting geometry remain failures.

A bounded comparison would reuse one source and vary only the prompt, then the
presence of an appearance reference. Review before adding people or increasing
resolution. Google offers 360p drafts, but the local app currently maps draft
to 720p; no 360p workflow has been implemented or tested here. Low-resolution
drafts cannot establish final detail quality, and later generations are not
guaranteed to reproduce an approved draft exactly.

No new generation, credit allocation, source change, push or deployment was
performed for this research. Existing paid allowances remain exhausted.

## Creator-video deep dive after the user's example

The user supplied [Dom's 33-use-case tutorial](https://www.youtube.com/watch?v=LVeZ0UcR9_4).
Reviewed relevant moving-video sections in the browser, on-screen prompts and
exported auto-generated transcripts across five Omni creator videos. Also
reviewed one Blender/Seedance comparison, excluded from Omni capability claims.
These were targeted section reviews, not uninterrupted end-to-end viewing of
every long tutorial. Some captions are auto-translated; paraphrases require
the visible footage and current official API contract as cross-checks.

Browser screenshots and their actual playback timestamps/URLs are retained in
`C:/dev-artifacts/CityPrompt/omni-creator-research-2026-10-21/`. Transcripts stay
in that external private working directory and are not repository deliverables.

| Creator/source | Sections reviewed | Finding and CityPrompt relevance |
| --- | --- | --- |
| [Dom / Tech Tutor Zones](https://www.youtube.com/watch?v=LVeZ0UcR9_4) | Chapter/transcript review across all 33 cases; visual review of the opening screen-to-object example, drawn aerial route around 15:57, floor-plan source at 18:46 and interior at 18:59, whiteboard/result around 19:14–19:19. | The architectural case assigns the floor plan a structural-reference role and supplies an interior material/look direction. The visible result has textured concrete, wood and directional light. It is labeled 720p in the creator's interface. The broader sequence also shows map/route inaccuracies and actor/traffic mistakes. The video is original Omni Flash from July, not a verified 1.1 run. |
| [AI with Surya](https://www.youtube.com/watch?v=ZsKcGk6Ke4c) | Transcript and visual sections around 0:05, 0:45, 1:22 and 1:33; description explains the original office/static-camera source. | Photographic subject appearance is retained while environments, illumination and clothing are substantially regenerated. This is full creative transformation, not mild source cleanup. Creator assertions about perfect continuity are not independent measurements. |
| [Creative AI Show](https://www.youtube.com/watch?v=tJwi05PA9SQ) | Full transcript; visual examples around 1:40, 3:01 and 4:23. | Astronaut visor/suit detail and wet street reflections look convincing, while the creator shows broken physics and a morphing transition between endpoint images. Strong material realism does not imply sound camera/scene continuity. |
| [NextGen IA Hub](https://www.youtube.com/watch?v=gqRW6VhEYPs) | Transcript; house/reference workflow 7:57–9:46, visual day/night result from 10:35 through 10:53, and the removal-failure explanation. | The house starts from a finished-looking reference. Day/night treatment changes the illumination substantially. A useful workflow distinction: reusing a prompt may reuse the original image, whereas attaching the actual generated clip edits that result. The creator also shows incomplete tree removal. Regional-workaround advice was not followed. |
| [Carlos Alarcón](https://www.youtube.com/watch?v=3Ta45Ye_Or4) | Transcript of reference and editing/API sections; visual character result around 4:09 and API result around 37:05. | Source motion and reference appearance can be assigned separate roles through the API, not only a vendor UI. The demonstration is character replacement, not proof of accurate architectural reconstruction. Technical claims remain subject to the current official API documentation. |
| [Higgsfield + Blender comparison](https://www.youtube.com/watch?v=OiULPvTJ-0E) | Opening workflow/transcript and 4:34 source/result comparison. | Rough 3D blocking becomes live-action-style output with authored timing and camera control. That demonstrated request uses Seedance 2.5, not Gemini Omni. It supports the workflow concept only and is not evidence of an Omni result. No provider switch was made. |

### Revised conclusion

The user's example strengthens the case for an explicit representation change:
use the input for structure/motion, and rebuild the appearance as filmed reality.
A photorealistic input image is **not a necessary precondition** for a compelling
output; the floor-plan and whiteboard examples show appearance invention. A
reviewed appearance reference remains a useful control option, not a requirement
or a guarantee. This qualifies the earlier reference-first recommendation.

The primary problem to trial is therefore the requested transformation and media
roles, rather than assuming 1080p is inadequate. For CityPrompt, describe the
completed development as filmed on location, explicitly allowing new material
detail, coherent lighting, natural planting and modest activity. Keep principal
building massing, footprints, road/park arrangement and route recognizable.
Do not preserve the preview's flat grass, schematic shading or coarse tile
surface appearance just because they occurred in the input recording.

A concise experiment should state that the whole video changes visual medium.
Provide a small, scene-appropriate appearance brief; avoid assigning every
surface the same generic material or overwhelming the shot with several actions.
The preview-video branch currently omits its supplied `scene_brief`, so a future
implementation must deliberately choose a short visual brief instead of simply
appending the entire internal scene contract.

Proposed direct-transform prompt (not submitted):

> Use this clip as the 3D layout and camera guide. Re-render the entire shot as
> live-action footage of the completed development, with photographic building
> materials, natural planting, believable reflections and coherent afternoon
> light. Replace the simplified preview appearance throughout. Keep the building
> massing, road and park layout, and camera route recognizable in one continuous
> shot. A woman walks her dog along the existing park path.

For the next controlled comparison, first omit the activity sentence and use
the same recorded source. Compare that result against the same prompt plus one
reviewed appearance reference. Assess convincing appearance and temporal/spatial
continuity separately. Neither arm has been tested here and no additional paid
generation is authorized by this research request.

## Exact polygon-animation-to-Omni examples

The user's next reference is [this Seedance playblast tutorial](https://www.youtube.com/watch?v=ikPGQGoUjQ0).
The focused search below excludes ordinary photo animation and real-footage
editing. Three matching deliveries were found from two independent authors:

1. **Blender town to realistic street video, Shirakawa Mio / Usagi development.**
   The author supplies a minimally rendered Eevee town animation and a separate
   character image to Gemini Omni. A published comparison shows the simplified
   buildings, street, sidewalk and mannequin beside the realistic result.
   [Comparison](https://www.youtube.com/watch?v=O2b8LbKjlkE),
   [raw animation](https://www.youtube.com/watch?v=IpORMmRf4RE),
   [result](https://www.youtube.com/watch?v=ig_bXygYD-c),
   [creator's workflow](https://note.com/shiramio/n/n8394e2dac8a9).
   The comparison was visually inspected in the browser; it is a particularly
   close match to CityPrompt's outdoor-scene use case.

2. **Blender classroom animation to realistic interior, same author.**
   Simplified humanoid motion and classroom geometry are rendered as a guide;
   Omni generates a person and finished classroom appearance. The author
   describes lightweight Eevee export rather than a final Cycles render.
   [Source](https://www.youtube.com/watch?v=tRdIew-2N4k),
   [Omni result](https://www.youtube.com/watch?v=Bsw3z8Pm4jE),
   [creator's workflow](https://note.com/shiramio/n/n53e3f0bce755).
   Both source and result were visually inspected in the browser. These are
   multiple shots, not evidence that every camera transition remains exact.

3. **Nanode Blender animation re-render, Kovname.**
   [Three-way video showcase](https://github.com/Kovname/nano-banana-render#video-examples):
   an Eevee knight/forest animation, the Omni finish, and a stylized version.
   Source and output frames were decoded and compared at 1/3.5/6 seconds.
   The middle result adds convincing metal and forest treatment; the third is
   intentionally illustrated. Public API code explicitly calls
   `gemini-omni-flash-preview`, corroborating the Omni model family.

The town/classroom articles date to July 2026 and do not establish a specific
Omni 1.1 model ID. Nanode's inspected code uses the older preview ID. These are
direct evidence of the **Omni-family workflow**, not receipts proving 1.1.
The creator model attributions are not independently audited provider receipts.

Pinned Nanode revision: `1f441ecb553625eadbc9a30618bc058dc810a72e`.
The guide is 7.5 seconds at 1920×1080/30 fps; its two outputs are 8 seconds at
1280×720/24 fps. Therefore, equal timestamps are approximate comparison points,
not exact frame correspondence or proof of preserved timing. Media URLs,
SHA-256 hashes, sample sheet and browser screenshots are retained outside Git:
`C:/dev-artifacts/CityPrompt/omni-polygon-examples-2026-10-21/`.
Downloaded third-party code was read as text only; nothing was installed or run.

[Node Composer's Blender guide](https://www.node-composer.studio/learn/blender/)
also documents flat-color, gray-clay and random-color animation guides feeding
Gemini Omni. Treat this as supporting tool documentation, not an additional
independently inspected source/result video.

## Additional research before further spending

No paid generations were submitted in this round. No application behavior,
provider settings, deployment or billing configuration was changed.

### An explicit Omni 1.1 architectural comparison

[Scenario's Twenty Minutes](https://www.scenario.com/explorations/twenty-minutes/)
publishes a four-pane comparison: Blender, Seedance 2.5, Runway Aleph 2 and
Gemini Omni 1.1 Flash Edit. The downloaded 7.167-second comparison was decoded
and inspected at 0.5, 3 and 5.5 seconds. The Omni pane has a convincing filmed
street appearance but noticeably changes the person and shopfronts. The source
also transitions into a textured, lit street; this is not purely gray input
throughout. The site's main 30-second film uses Seedance, not Omni. This is
vendor-curated evidence, not independently audited provider receipts or a
success-rate benchmark.

Public comparison media:
<https://www.scenario.com/explorations/twenty-minutes/media/compare.mp4>.
SHA-256: `062502843ae8cfe7347caf58c87e3566de907e254b00f7e4b69dbdfb44a184a6`.
4,077,672 bytes; 1920×1080, 24 fps, 172 frames. Video, sampled frames and
metadata remain outside Git in
`C:/dev-artifacts/CityPrompt/omni-pre-render-research-round4-2026-10-21/`.

[npaka's September workflow](https://note.com/npaka/n/nab05d90f95b7)
explicitly names Omni 1.1 Flash and assigns 3D animation the role of motion,
camera, composition and timing guide, with separate appearance references.
Its requested output is hand-drawn anime. It supports the media-role workflow,
not a claim about photographic architecture.

### Comparison with CityPrompt's actual request

The active `preview_video` branch of `build_cinematic_prompt` in
`backend/app/services/omni_video.py` already asks for realistic materials,
daylight and contact shadows. It also locks individual windows/roofs and says
to keep everything else the same. It does not attach an appearance reference;
`scene_brief` is not included in this branch. Thus a concise, explicit target
appearance is a useful hypothesis to test, not a proven root-cause fix.
The stricter language in other control modes was not used for these trials.

Nanode's inspected legacy implementation also contains strong identity locks.
Its success does not establish that simply deleting preservation clauses will
produce realism. Its old model ID and transport choices should not be copied
into the current integration without a separate compatibility check.

[Google's current guide](https://ai.google.dev/gemini-api/docs/omni)
distinguishes a primary edit video from appearance/subject references. Explicit
source/reference tags can express those roles. They do not guarantee exact
geometry or camera reproduction. An appearance image would be optional and
must not accidentally become the initial frame.

### Spend gate for a future trial

1. Review the existing source video for clipped/smeared tiles, awkward framing,
   flicker and camera speed using local playback. Fix source defects before
   paying a model to reinterpret them.
2. Reuse one existing eight-second source and a short appearance-only request.
   Preserve recognizable building massing, street layout and camera movement;
   explicitly allow physically convincing surfaces, lighting, reflections and
   planting detail. Initially add no new activity. Judge realism and layout
   continuity separately. This is an untested proposal.
3. Submit only one newly approved generation, review it, and stop before
   another. A later appearance-reference comparison should change that one
   variable while retaining the same source and text. Do not spend a batch
   allowance automatically, rerun unchanged requests, or upscale weak content.

[Official pricing](https://ai.google.dev/gemini-api/docs/pricing) lists
5,792 output tokens per second of 720p video at US$17.50/million: eight seconds
is approximately US$0.81 for video output, plus input and any text output.
This is not a verified all-in price for our earlier 1080p calls. The current
pricing table does not supply a separate 360p tariff; the app does not expose
a 360p draft mode. Confirm the selected resolution's actual charge before
offering a cheaper draft price. No additional render authorization is implied
by this research.

## Follow-up: lessons from public Git repositories

This review read source files and test definitions; third-party scripts were
not installed or executed. No additional model calls were made. Downloaded
source text is outside Git at
`C:/dev-artifacts/CityPrompt/omni-public-git-review-2026-10-21/`.

- **Nanode**, revision `1f441ecb553625eadbc9a30618bc058dc810a72e`:
  `_build_omni_prompt` in `nano_banana_render/render_engine.py` separates
  geometry/camera preservation from the requested appearance and optional style
  reference. It retains substantial subject locks, so preservation instructions
  alone do not explain our disappointing realism. Its default target is a
  polished cinematic 3D render, not live-action footage. `_prepare_omni_capture`
  supports reusing an existing motion guide. For CityPrompt, reuse one captured
  source and explicitly describe the desired photographic medium. This remains
  an untested recommendation. The inspected implementation uses the older Omni
  preview model elsewhere; do not copy its model/API assumptions blindly.
  [Source](https://github.com/Kovname/nano-banana-render/blob/1f441ecb553625eadbc9a30618bc058dc810a72e/nano_banana_render/render_engine.py).

- **Google Gemini skills**, revision
  `ee9da52195752ca83c2fca701d96bcb5a9c08d2d`: `inspect_video.py` uses ffprobe
  for actual duration, resolution, frame rate and audio. `prep_video.py` provides
  source trimming/conversion and post-conversion inspection. These support free
  preflight checks before generation, not claims about achieved realism.
  [Inspector](https://github.com/google-gemini/gemini-skills/blob/ee9da52195752ca83c2fca701d96bcb5a9c08d2d/skills/gemini-omni-flash-api/scripts/video/inspect_video.py).

- **CxOAGI Gemini Media MCP**, revision
  `d9d454b0cd60b90dddb8b4c0e070587aaa72bc4a`: `src/omni.py` distinguishes
  requested and measured duration, checks whether resolution survives SDK
  serialization, and builds explicit media-role declarations. Budget/lifecycle
  tests cover refusal before a paid chain starts. Its reported duration mismatch
  is maintainer evidence, not reproduced here. Therefore an eight-second source
  should not become an unconditional eight-second cost guarantee. Check actual
  output and usage. The repository also contains stale model-sunset wording;
  use current official docs for model lifecycle/pricing.
  [Source](https://github.com/CxOAGI/gemini-media-mcp/blob/d9d454b0cd60b90dddb8b4c0e070587aaa72bc4a/src/omni.py).

Prompt collections and third-party-provider wrappers were lower-value evidence:
prompt recipes are not measured output, and wrapper-specific costs/controls do
not establish what the Gemini Developer API accepts. No production changes are
implied by this review.
