# Video Render Quality Bar (geometry-first video pipeline)

Research date: 2026-09-26. Scope: what the most-liked / award-winning architectural video
looks like in 2025–2026 (AI and traditional), distilled into a rubric we can design and score
against. Engagement numbers are quoted only where a page exposed them; YouTube and Vimeo
counts were not retrievable through our fetcher and are marked "n/a". Nothing here is invented.

Two findings frame everything below:

1. **The bar is set by CGI studios, and it is about restraint, not spectacle.** The 2025
   CGarchitect 3D Awards film winners (Arqui9, Kunkun Visual) and nominees (Brick Visual) are
   Corona/V-Ray films with one intentional camera move per shot, a single lighting state, and
   a narrative. Kunkun's winner *used AI in production* and still won — AI is acceptable when
   geometry is CGI-owned and AI only finishes the look. That is exactly our architecture.
2. **Practitioners already converged on "geometry-first" as the fix for AI video.** Kling
   2.6 first/last-frame workflows, Fenestra's "nothing is redrawn between them", Seedance 2.5
   clay-render (white-model) referencing, Runway Aleph video-to-video, and Peter Guthrie
   (The Boundary) calling Luma Ray3.14 "production-ready" all describe the same recipe we
   use: a deterministic camera/geometry track, an AI pass that changes only the finish.

## Reference table

| # | Title / creator | Tool | Date | Engagement | What it shows | Why it reads as high quality |
|---|---|---|---|---|---|---|
| 1 | **Skyrise** (Binghatti, Dubai) — Arqui9 Visualisation. CGarchitect 3D Awards 2025 *Best Commissioned Film* [S1][S2] | Corona + 3ds Max, "No AI used" | Oct 2025 | Award; Vimeo plays n/a | Tower told through an architect's process, live action blended with CGI; exterior hero views in real city context | Narrative structure; one move per shot; CGI matched to plate lighting; the building is the subject, the camera serves it |
| 2 | **Silent Recall** — Kunkun Visual. CGarchitect 2025 *Best Non-Commissioned Film*; AVA Digital Awards Platinum 2026 [S1][S3][S4] | Corona + 3ds Max, "AI: for production" | Oct 2025 / Jan 2026 | Two awards; views n/a | A man returns to Bromo (Tanatap Sunrise); memory, decay, atmosphere | Proof that hybrid CGI+AI reaches the top tier when AI is "a creative partner for consistency", not the geometry source |
| 3 | **National Museum of Archaeology, Rabat** — Brick Visual (2025 nominee) [S5]; also BIG's Gelephu Mindfulness City and Tadao Ando's Dubai Museum of Art animations [S6] | V-Ray + 3ds Max, "No AI used" | 2025 | Award nominee; views n/a | "Short, atmospheric… serene introduction… quiet elegance" | Slow, calm, low-contrast atmosphere; single lighting mood held for the whole film |
| 4 | **The Boundary** animations/cinemagraphs [S7][S8]; Peter Guthrie on Luma Ray3.14 [S9] | V-Ray/Corona; Ray3.14 for AI tests | Jan 2026 (post) | n/a | High-end residential, "evocative CGI content that drives off-plan sales"; cinemagraphs = still frame + minimal motion | Obsessive material/light control; Guthrie's AI criteria: "stable subjects across frames, cleaner outputs, controlled motion, styles hold together" |
| 5 | **MIR** (Bergen) [S10][S11] | V-Ray/Corona | ongoing | Vimeo counts n/a (SSO wall) | The "MIR style": rich atmosphere, evocative natural settings, weather | Atmosphere over polish; imperfect, photographic light; haze and weather carry depth |
| 6 | **D5 Film 2025 showreel** — D5 Official (YouTube S9orAYny2vM) [S12][S13] | D5 Render (real-time path tracing) | 2025 | views n/a | "Dynamic camera choreography, refined landscaping, immersive interior studies" | Real-time bar: photoreal materials, atmospheric lighting, foliage that moves |
| 7 | Hassan Ragab, Midjourney V5 architecture video, reposted by The AI LIVE Show (LinkedIn) [S14][S15] | Midjourney V5 + AnimateDiff/ComfyUI + Topaz | Apr 2023 | **4,964 reactions, 108 comments** (repost) | Morphing concept-art buildings, "every frame is a creative building" | Highest engagement found — but it is *art*, where morphing is the point. Counter-example for photomontage: virality ≠ fidelity |
| 8 | Ismail Seleit (Foster + Partners, personal), "Custom-trained LoRA × Kling Pro 2.1" (LinkedIn) [S16] | Custom LoRA stills → Kling 2.1 Pro | Jun 2025 | **531 reactions, 20 comments** | Sequence of short shots, fixed/locked cameras, music | Commenters singled out *fixed-camera* animation, composition and realism — restraint reads as premium |
| 9 | renderdrop, "Is KLING 3.0 finally ready for ARCHITECTURE Animation?" (YouTube 1A7uOdk9Sng) [S17]; renderdrop on Nano Banana Pro [S18] | Kling 3.0; Nano Banana Pro | 2026 | views n/a | Facade/animation stress tests | Documents the tells: "large camera rotations produce hallucinations and architectural drift" |
| 10 | CraftsPhile Academy, "From Google Maps to Cinematic Animation (Nano Banana + Veo 3.1)" (YouTube WFimhEJ4Aqg) [S19]; Urban Decoders / BIM Design Studio Veo 3.1 guides [S20][S21] | Nano Banana Pro → Veo 3.1 | late 2025–2026 | views n/a | Map → site render → 8 s Veo clip; closest public analogue to our flow | Works because the image is authored first and the video prompt is only camera + atmosphere |
| 11 | Salmaan Mohamed, "Edit Renders & Walkthroughs with AI — Runway Aleph for Architects" (YouTube ng9-4WlMRIQ) [S22][S23] | Runway Aleph (video-to-video) | 2025 | views n/a | Existing walkthrough restyled (materials, weather, entourage) | Video-to-video keeps the camera path — same authority split we use |
| 12 | Kling 2.6 First & Last Frame archviz workflow (AI Fire) [S24][S25] | 3ds Max/Blender frames → Kling 2.6 | early 2026 | n/a | Two rendered frames → 5–10 s clip, 1080p, Topaz to 4K | "80 % production-ready"; fails on spiral moves and extreme close-ups; $250 vs $2,500 per project |
| 13 | Seedance 2.5 clay-render / white-model referencing (ByteDance; Dreamina blockout→video) [S26][S27][S28] | Seedance 2.5 | Jul 2026 | n/a | Untextured 3D blockout locks camera, pacing, blocking; model adds materials, light, entourage; up to 30 s | Industry validation of geometry-first: composition "closely matches the creator's expectations" |
| 14 | Luma Ray3 / Ray3.14 architectural-viz positioning [S29][S30][S31] | Ray3.14 | Jan 2026 | n/a | Native 1080p, 16-bit HDR EXR, start/end frame, draft mode 5× cheaper | Guthrie: "motion feels more intentional… far fewer glitches"; HDR keeps glazing/reflections honest |

Low-engagement control point: Ofek Ben Shalom's Veo 3 archviz commercial test (LinkedIn, Jul 2025)
drew 7 likes; the 8 s cap forced stitching and the model would not follow the script [S32].

## Quality rubric (score 0–2 per criterion, 28 max; ship at ≥ 22 with no criterion at 0)

0 = visibly fails, 1 = acceptable with a tell, 2 = indistinguishable from a CGI studio clip.

| # | Criterion | 2 points looks like | Tell-tale failure (0) |
|---|---|---|---|
| 1 | **Geometry persistence** | Facade grid, mullions, roof lines, courtyard/lightwell *counts* identical first→last frame [S33][S34] | Windows drift, floors added/removed, "architectural drift" on rotation [S18] |
| 2 | **Context fidelity** | Existing neighbours, roads, trees untouched; only the authored site changes | Invented buildings, moved streets |
| 3 | **Camera language** | One intentional move, constant velocity with ease-in/out, level horizon, ~35 mm, no drift; "static locked shot" when no move is wanted [S35][S36] | Camera wander, orbit creep, dolly-zoom, altitude pumping |
| 4 | **Camera speed / travel budget** | Walk-by ≈ 1 m/s or slower; aerial ≈ 1.5–3 m/s equivalents; "subtlety reads as premium" [S37][S38][S39] | Too fast to read the facade; multiple competing motions |
| 5 | **Lighting / time-of-day coherence** | One lighting state, sun-side facade, shadows fixed to geometry, exposure stable | Sun angle or exposure drifts mid-clip; shadow flicker [S34] |
| 6 | **Materials & glazing** | Reflections "that actually reflect", no texture swimming, glass stays glass [S40] | Glazing flicker, material shimmer, mullion morph [S33][S41] |
| 7 | **Vegetation & water motion** | Leaves and water move gently and rhythmically; built form perfectly still [S42][S43] | Frozen trees, or windstorm foliage, or trees that "breathe" in size |
| 8 | **People & vehicles** | Sparse, natural scale, grounded with contact shadows, orderly continuous motion, focus stays on architecture [S44] | Floating feet, gait morph, "one figure does something strange", crowd multiplication |
| 9 | **Atmospheric depth** | Subtle haze; distance goes cooler and less saturated; "felt, not seen" [S45][S46] | Flat aerials with no depth cue, or fog soup |
| 10 | **Grade & grain** | Restrained film grade, light grain, vignette you "barely feel" [S47] | Over-saturation, HDR halos, plastic AI sheen |
| 11 | **Temporal stability** | No flicker in signage/glazing/shadows; no exposure pumping [S48][S49] | Frame-to-frame shimmer, "swimming" surfaces |
| 12 | **Framing & structure** | Clear subject, establishing → hero, ends on a calm **hero hold** [S41][S50] | Cuts inside an 8 s clip, subject leaves frame, ends mid-move |
| 13 | **Scale believability** | 3 m floors, door/car/tree proportions correct against the building | Toy-town or giant furniture; wrong car scale |
| 14 | **Delivery hygiene** | 16:9, 24 fps, 1080p, 5–10 s, clean plate: no route line, pins, labels, borders [S51][S52] | Visible UI/mask, letterboxing, 30/60 fps "video" look |

Tell-tale failure modes to check explicitly (from [S18][S33][S34][S41][S44][S48][S49]): morphing
facades, invented geometry, floating people / missing contact shadows, glazing flicker, illegible
signage, over-saturation, wrong scale, camera wander, hallucinated extra figures, exposure drift.

## Mapping to City Prompt controls

| Rubric # | Our control | How it is exercised / scored |
|---|---|---|
| 1, 2, 13 | **Geometry score** — `assess_structural_edge_fidelity` in `backend/app/services/direct_3d_render.py` (`beauty_edge_recall`, `coarse_edge_recall`, `semantic_edge_recall`, `semantic_component_min_recall`, `building_internal_edge_recall`) | Already gates stills. For video: score first, middle, last frame against the depth preview; fail if any frame drops or the spread exceeds tolerance (temporal version of criterion 11) |
| 3, 4, 12 | **Camera motions** in `backend/app/services/omni_video.py` `MOTION_PROMPTS`: `path_follow` (constant-altitude aerial truck, ≤ 2 % scale change), `street_walkby` (1.7 m, 35 mm, ≤ 4 m travel), `detail_flythrough` (6 m low drone, no orbit/zoom) | Deterministic route preview owns speed and easing; the prompt already forbids orbit, zoom and altitude pumping. Add ease-out + hero hold (see cheap wins) |
| 5, 9, 10 | **Look sheet** in `backend/app/services/video_prompts.py` `VIDEO_LOOKS`: `photorealistic`, `atmospheric`, `night`, `winter`, `overcast`, `after_rain`, `documentary`, `survey` | One look = one lighting state per clip (criterion 5). `atmospheric`/`overcast`/`after_rain` should carry the haze language of criterion 9; `survey`/`documentary` are the low-grade, no-grain references |
| 6, 7, 11 | Look sheet "change only the look" clause + Wan VACE depth negative prompt (`build_vace_depth_prompt`) | Depth track keeps built form still; look text should explicitly allow only foliage/water/sky motion |
| 8 | **Entourage toggles** `add_people`, `add_vehicles` (`ENTOURAGE` table: "a few pedestrians at natural scale… sparse slow traffic in existing lanes") | Keep density low by default; request contact shadows; `survey` look should default both off |
| 14 | Output contract: 16:9, 24 fps, `resolution: 1080p`, `duration_seconds` (8 s), clean-plate check in the Omni prompt | Matches Veo 3.1 (24 fps, 4/6/8 s, 720p/1080p) and Kling/Ray3.14 1080p norms [S51][S52][S30] |

## Cheap wins to adopt now

1. **Hero hold.** Decelerate the deterministic preview over its final ~20 % and freeze the last
   ~24 frames (1 s) so every clip ends on a calm, sharp composition — the closing-hero-frame
   convention of studio reels [S41][S50]. The Omni prompt already asks for "one intentional hero
   hold"; making the control video do it removes the ask from the model.
2. **Slower easing and a per-clip motion budget.** Ease-in/ease-out on the route preview instead
   of constant velocity; keep one move per 8 s clip; when the move is tiny (street walk-by), add
   the "static locked shot / locked-off camera" phrasing that Runway and HumanAlloy found
   necessary to stop drift [S35][S44].
3. **Sun-side framing.** Choose the route heading (or flip the walk-by direction) so the sun
   is behind or beside the camera for the `photorealistic` and `atmospheric` looks; lit facades
   and long shadows are the cheapest realism cue in every studio reel [S46].
4. **Post-side grade, grain and haze, not prompt-side.** Apply a light film grain, a
   barely-felt vignette and a gentle S-curve in our own post step (deterministic, repeatable),
   and add distance haze language ("far objects cooler and less saturated") to the aerial looks
   [S45][S47]. This suppresses the over-saturated AI sheen without asking the model for "cinematic".
5. **Gentle foliage and water motion, everything built still.** Add one clause to each look:
   "leaves and water move gently in a light breeze; every building, road and wall stays
   perfectly still" — the subtle-environmental-motion pattern that makes clips feel alive without
   distracting from the design [S42][S43].
6. **Temporal geometry score.** Reuse `assess_structural_edge_fidelity` on three sampled frames
   of the finished video against the depth preview; report min and spread alongside the still
   score, so flicker and drift (criteria 1, 11) are caught by the same gate that protects stills.

## Sources

- [S1] Architizer, "The 21st CGarchitect 3D Awards…" — https://architizer.com/blog/inspiration/industry/the-21st-cgarchitect-3d-awards/
- [S2] CGarchitect 3D Awards 2025 winners / Arqui9 entry — https://3dawards.chaos.com/contests/15-2025-cgarchitect-3d-awards/winners ; https://3dawards.chaos.com/contests/15-2025-cgarchitect-3d-awards/gallery/35885/info ; https://vimeo.com/1023173484
- [S3] Kunkun Visual entry — https://3dawards.chaos.com/contests/15-2025-cgarchitect-3d-awards/gallery/36367/info
- [S4] Kunkun Visual, "Silent Recall wins Platinum…" — https://www.kunkunvisual.com/post/starting-2026-with-gratitude-silent-recall-wins-ava-digital-awards-architectural-visualization-film ; showreel https://www.youtube.com/watch?v=1sLG8pHGxdA
- [S5] Brick Visual nominee entry — https://3dawards.chaos.com/contests/15-2025-cgarchitect-3d-awards/gallery/36041/info
- [S6] Brick Visual animation portfolio — https://brickvisual.com/works-by-type/animation/
- [S7] The Boundary, CGIs / animations / cinemagraphs — https://www.the-boundary.com/cgis-animations-cinemagraphs
- [S8] The Boundary on Vimeo — https://vimeo.com/theboundaryuk
- [S9] Peter Guthrie on Luma Ray3.14 (LinkedIn) — https://www.linkedin.com/in/peter-guthrie-3a383b13b/
- [S10] Architizer, "Are These the Most Atmospheric Renderings…" (MIR) — https://architizer.com/blog/practice/materials/the-art-of-rendering-mir/
- [S11] MIR on Vimeo — https://vimeo.com/mirnorway
- [S12] D5 Film 2025 showreel — https://www.youtube.com/watch?v=S9orAYny2vM
- [S13] Novedge on D5 Film 2025 — https://novedge.com/blogs/design-news/3d-architectural-visualization-animation-showreel-d5-film-2025
- [S14] The AI LIVE Show repost of Hassan Ragab video (LinkedIn) — https://www.linkedin.com/posts/artificialinspiration_video-ai-architecture-activity-7051885850418147328-pWfO
- [S15] Hassan Ragab, PAACADEMY / workshop notes — https://parametric-architecture.com/ai-conceptual-architecture-4-0-studio-hassan-ragab/
- [S16] Ismail Seleit, "Custom-trained LoRA model x Kling pro 2.1" — https://www.linkedin.com/posts/ismailseleit_ai-lora-architecture-activity-7335904331654701056---yh
- [S17] renderdrop, "Is KLING 3.0 finally ready for ARCHITECTURE Animation?" — https://www.youtube.com/watch?v=1A7uOdk9Sng
- [S18] RebusFarm / renderdrop, Nano Banana Pro for archviz — https://rebusfarm.net/news/renderdrop-nano-banana-pro-for-architectural-visualization
- [S19] CraftsPhile Academy, Google Maps → cinematic animation — https://www.youtube.com/watch?v=WFimhEJ4Aqg
- [S20] Urban Decoders, Veo 3.1 + Nano Banana guide — https://www.youtube.com/watch?v=hb6XFEKpZaQ
- [S21] BIM Design Studio, Veo 3.1 architecture tutorial — https://www.youtube.com/watch?v=NgmmjT_Z6so
- [S22] Salmaan Mohamed, Runway Aleph for architects — https://www.youtube.com/watch?v=ng9-4WlMRIQ
- [S23] Runway, Introducing Aleph — https://runway.com/research/introducing-runway-aleph
- [S24] AI Fire, "AI vs. Render Farm: Professional Archviz Workflow 2026" — https://www.aifire.co/p/ai-vs-render-farm-professional-archviz-workflow-2026
- [S25] Fenestra, AI architectural animation generator — https://www.fenestra.app/solutions/ai-architectural-animation-generator
- [S26] ByteDance Seed, "Introducing Seedance 2.5" — https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5
- [S27] Dreamina, Seedance 2.5 3D blockout to video — https://dreamina.capcut.com/seedance/seedance-2-5-3d-blockout-to-video
- [S28] Higgsfield, Seedance 2.5 — https://higgsfield.ai/blog/seedance-2-5-on-higgsfield-2026
- [S29] Luma, architectural visualization with Ray3 — https://lumalabs.ai/use-case/architectural-visualization-with-dream-machine-ray-3
- [S30] Luma, Ray3.14 release — https://lumalabs.ai/news/ray3_14
- [S31] Luma, Ray3 — https://lumalabs.ai/ray3
- [S32] Ofek Ben Shalom, testing Veo 3 for archviz — https://www.linkedin.com/posts/ofek-ben-shalom-a53916201_ai-veo3-archaido-activity-7346825182050672641-Ibe-
- [S33] Visiomake, best AI tools for architectural animation 2026 — https://visiomake.com/en/blog/best-ai-tools-for-architectural-animation-2026
- [S34] LearnArchitecture, AI video generation tools — https://learnarchitecture.net/artificial-intelligence/33845-ai-video-generation-tools.html
- [S35] Runway, photo-to-video prompting tips — https://runway.com/resources/photo-to-video-tips
- [S36] Curious Refuge, Kling 3.0 review ("geometric tethering") — https://curiousrefuge.com/blog/kling-3-ai-video-generator-review
- [S37] Genense, 3D walkthrough guide (walking pace) — https://www.genense.com/blog/3d-walkthrough-animation-guide/
- [S38] Praxis Studio, architectural animation guide — https://3dpraxisstudio.com/journal/architectural-animation-guide/
- [S39] Pix-Pro, drone speed for photogrammetry (1.5–3 m/s) — https://www.pix-pro.com/blog/photogrammetry-speed
- [S40] Ricardo Eloy, "Sora and Archviz" — https://cgconnect.chaos.com/features/articles/96ea9663-sora-and-archviz-evolution-or-a-new-challenge
- [S41] Visiomake, AI walkthrough from still renders (2026) — https://visiomake.com/en/blog/ai-architecture-walkthrough-video-from-still-renders-2026
- [S42] Chaos, "AI architecture animation: animate your renders with Veras" — https://blog.chaos.com/ai-architecture-animation
- [S43] Pincel, animate architecture (subtle environmental motion) — https://blog.pincel.app/animate-architecture/
- [S44] HumanAlloy, bringing static archviz people to life with AI video — https://humanalloy.com/pages/bringing-static-archviz-3d-people-to-life-with-ai-video
- [S45] D5, atmospheric perspective for aerial rendering — https://www.d5render.com/posts/atmospheric-perspective-for-aerial-rendering
- [S46] 3DAS, atmospheric realism — https://www.3dastudio.com/rendering-tips/atmospheric-realism
- [S47] Maxon, architectural visualization guide (grain, vignette, "less is more") — https://www.maxon.net/en/article/architectural-visualization-guide
- [S48] Atlas Cloud, quality report on 4 AI video APIs — https://www.atlascloud.ai/blog/guides/quality-performance-report-4-leading-ai-video-apis-for-visual-fidelity-and-motion-stability
- [S49] Creatide, why AI video motion looks unnatural — https://creatide.ai/blog/why-ai-video-motion-looks-unnatural-and-how-to-fix-it
- [S50] ArchiCGI, types of shots in architectural animation — https://archicgi.com/cgi-services/types-of-shots-in-animation/
- [S51] Veo 3.1 specs (24 fps, 4/6/8 s, 720p/1080p/4K) — https://fal.ai/models/fal-ai/veo3.1 ; https://deepmind.google/models/veo/
- [S52] Kling 3.0 specs — https://kling.ai/quickstart/klingai-video-3-model-user-guide ; Kling 2.6 first/last frame — https://www.cometapi.com/kling-2-6-full-analysis-how-to-use-and-prompt/
- Further context: EvolveLAB forum, construction animation with Veras + Veo 3.1 — https://forum.evolvelab.io/t/construction-animation-using-veras-with-veo-3-1-video-model/11412 ; Redraw vs Higgsfield (architecture fidelity) — https://www.redraw.pro/en/blog/redraw-vs-higgsfield-architecture-2026 ; Architizer on Nano Banana — https://architizer.com/blog/practice/tools/nano-banana-google-viral-ai-architectural-visualization/ ; Studio Tim Fu (AEC Magazine) — https://aecmag.com/ai/studio-tim-fu-ai-driven-design/ ; Rendair 3D-model-to-video workflow — https://rendair.ai/blog/3d-model-to-cinematic-video ; mnml.ai Video AI presets — https://mnml.ai/app/video-ai ; Krea walkthrough node — https://www.krea.ai/nodes/app/spaciousdetachabledeer/walk-through-video ; AI Architecture Awards — https://competitions.archi/competition/ai-architecture-awards/
