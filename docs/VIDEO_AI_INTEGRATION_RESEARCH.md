# Video AI Integration Research Report

**Date:** March 31, 2026
**Scope:** Feasibility analysis for adding AI video generation to SiteForge / City Prompt
**Primary technology:** Google Veo (2.0, 3.0, 3.1) via Vertex AI / Gemini API

---

## Table of Contents

1. [Paper Summary](#1-paper-summary)
2. [Veo API Documentation and Capabilities](#2-veo-api-documentation-and-capabilities)
3. [Competitor Landscape](#3-competitor-landscape)
4. [Architecture Visualization Industry Context](#4-architecture-visualization-industry-context)
5. [Integration with SiteForge](#5-integration-with-siteforge)
6. [Use Cases for SiteForge](#6-use-cases-for-siteforge)
7. [Cost Estimates](#7-cost-estimates)
8. [UI Wireframes](#8-ui-wireframes)
9. [Phased Implementation Plan](#9-phased-implementation-plan)
10. [Risk Assessment](#10-risk-assessment)

---

## 1. Paper Summary

**Source:** "Integration of Generative Video AI and Geospatial Foundation Models in Urban Planning Platforms" (~44K characters)

### Core Thesis

The paper argues that generative video models (specifically Google Veo) can produce photorealistic, temporally consistent video for urban planning, but only if they are rigorously constrained by deterministic geospatial data. Without spatial grounding, diffusion models suffer from topological hallucinations, structural morphing, and violations of architectural physics.

### Key Technical Contributions

**1. Spatial Grounding Pipeline**
The paper describes a multi-layered framework that chains: (a) 3D city model geometry from sources like Calgary Open Data LiDAR, (b) CesiumJS or ArcGIS Pro deterministic rendering for camera snapshots, (c) Gemini API grounding with Google Maps for verified place data, and (d) Veo video generation constrained by first/last frame anchoring.

**2. Camera Trajectory Translation**
A middleware layer converts GIS camera coordinates (Cartesian3 position + Heading/Pitch/Roll orientation) into cinematic prompt vocabulary that Veo understands. For example, a lateral coordinate shift with decreasing altitude becomes "tracking right and tilting down" in the prompt. The paper provides a full translation matrix from coordinate deltas to camera movement terms.

**3. Depth-Aware Conditioning**
The paper surveys ControlNet integration for depth map guidance, the "Depth Any Video" model for temporal depth consistency across 150+ frames, and Align3R for retroactive camera pose estimation from generated video. These ensure sub-pixel geometric fidelity.

**4. Georeferencing with MISB ST 0601**
Generated videos are converted from raw MP4 into georeferenced transport streams using KLV metadata encoding (via GStreamer). This allows the video to be ingested into ArcGIS Pro Full Motion Video, where users can click any pixel and derive real-world coordinates.

**5. Deterministic JSON Prompting**
Rather than freeform text, the paper advocates structured JSON prompts with explicit parameters for camera dynamics, environmental conditions, and zoning constraints, validated against municipal regulations before being sent to Veo.

### Relevance to SiteForge

The paper's architecture maps closely to SiteForge's existing pipeline. SiteForge already has: (a) zone-based site layouts with colored overlays, (b) archetype reference images for style conditioning, (c) a Gemini-based render endpoint that sends multi-image payloads, and (d) a clay massing model for spatial reference. The video extension would add temporal animation to what is currently a single-frame generation workflow.

---

## 2. Veo API Documentation and Capabilities

### Available Models (as of March 2026)

| Model | Resolution | Duration | Audio | First/Last Frame | Style Ref | Status |
|-------|-----------|----------|-------|-------------------|-----------|--------|
| `veo-2.0-generate` | 720p | 5-8s | No | No | Yes (style image) | GA |
| `veo-2.0-generate-exp` | 720p | 5-8s | No | No | Yes (style image) | Preview, deprecating Apr 2 2026 |
| `veo-3.0-generate` | 720p-1080p | 4-8s | Yes | No | No | GA |
| `veo-3.1-generate` | 720p-1080p | 4-8s | Yes | Yes | Asset refs only | GA |
| `veo-3.1-generate-fast` | 720p-1080p | 4-8s | Yes | Yes | Asset refs only | GA |

### Key API Features

**Image-to-Video Generation**
Send a static image (e.g., a SiteForge render) and a text prompt. Veo animates the scene, adding movement, weather, lighting changes, and people. This is the primary integration point for SiteForge.

**First/Last Frame Conditioning (Veo 3.1)**
Provide start and end frames to force the model to generate a smooth transition between two known states. Critical for fly-throughs where start and end positions are known from the 3D viewer.

**Reference Images ("Ingredients to Video")**
Up to 3 asset images for subject/character consistency, or 1 style image (Veo 2 only) for aesthetic transfer. SiteForge archetype card images could serve as style references.

**Content Credentials**
SynthID watermarking and C2PA provenance metadata are embedded automatically, marking output as AI-generated. Important for professional planning contexts.

### API Request Structure (Vertex AI)

```
POST https://us-central1-aiplatform.googleapis.com/v1/
  projects/{PROJECT}/locations/us-central1/
  publishers/google/models/veo-3.1-generate:predictLongRunning

{
  "instances": [{
    "prompt": "Cinematic wide shot, camera slowly tracking forward...",
    "image": { "bytesBase64Encoded": "<base64 of SiteForge render>" },
    "referenceImages": [
      { "referenceType": "asset", "image": { "bytesBase64Encoded": "..." } }
    ]
  }],
  "parameters": {
    "aspectRatio": "16:9",
    "sampleCount": 1,
    "durationSeconds": 8,
    "resolution": "1080p",
    "generateAudio": false
  }
}
```

### Important Constraints

- Maximum 8 seconds per generation (plan around this)
- Aspect ratios: 16:9 (landscape) or 9:16 (portrait) only
- Async operation: returns an operation name, poll for completion
- Generation time: 30-120 seconds depending on model/resolution
- No inpainting/outpainting in video (Veo 2 preview only)
- Output is MP4 (H.264), returned as base64 or to a GCS bucket

---

## 3. Competitor Landscape

### Head-to-Head Comparison

| Feature | Veo 3.1 | Runway Gen-4.5 | Kling 2.0 | Pika 2.0 | Sora 2 |
|---------|---------|----------------|-----------|----------|--------|
| **Max Resolution** | 1080p (4K provisional) | 1080p | 1080p | 1080p | 1080p |
| **Max Duration** | 8s | 10s | 10s | 10s | 20s |
| **Image-to-Video** | Yes | Yes | Yes | Yes | Yes |
| **First/Last Frame** | Yes | No | No | No | No |
| **Style Reference** | Veo 2 only | Yes (visual refs) | No | No | No |
| **Audio Generation** | Yes (native) | No | No | No | No |
| **API Available** | Yes (Vertex AI) | Yes | Yes | Limited | Yes (ChatGPT) |
| **Price/sec (API)** | $0.10-0.40 | $0.05-0.15 | ~$0.03-0.08 | ~$0.05 | $0.10-0.50 |
| **Physics Simulation** | Strong | Best-in-class | Good | Moderate | Strong |
| **Camera Control** | Prompt-based | Motion brush | Motion brush | Limited | Prompt-based |

### Platform Strengths for Architecture Use

**Veo 3.1 (Recommended for SiteForge)**
- First/last frame conditioning is uniquely valuable for spatial accuracy in fly-throughs
- Native audio adds ambient sound (wind, traffic, birds) without post-production
- Already integrated with Google Cloud (where SiteForge backend runs via Vertex AI)
- Grounding with Google Maps provides verified place context
- Style reference via Veo 2 for architectural vernacular enforcement

**Runway Gen-4.5**
- Superior temporal consistency and motion control
- Professional editing tools (motion brush, extend, outpaint)
- Hollywood-adopted, high credibility for client presentations
- Higher cost ceiling but better fine-grained control

**Kling 2.0**
- Best cost-per-second for bulk generation
- Motion brush for element-level animation control
- Good for generating many social media variants quickly

### Recommendation

Use Veo 3.1 as the primary engine due to: (a) existing Vertex AI integration, (b) first/last frame anchoring for spatial accuracy, (c) native audio, and (d) Google Maps grounding. Offer Runway Gen-4 as a premium alternative for users who need finer control.

---

## 4. Architecture Visualization Industry Context

### Current State of AI Video in Architecture (2026)

The architecture visualization industry has rapidly adopted AI video. Key players include:

- **Rendair AI** -- Combines image generation, editing, and animation in one platform targeted at architects. Generates walkthrough animations from static renders.
- **ArchiVinci** -- AI Image-to-Video module that analyzes depth and spatial relationships to simulate realistic camera movements from renders.
- **Chaos Veras** -- AI visualization plugin for CAD tools (SketchUp, Revit, Rhino). 12 animation presets for cinematic architectural walkthroughs.
- **mnml.ai** -- One-click 10-second 1080p animation generation from architecture renderings.
- **Krea AI** -- Video upscaling and enhancement for architectural walkthroughs to 4K.

### Market Opportunity for SiteForge

None of these tools integrate video generation with **site planning and zone-level design**. They all operate on individual building renders. SiteForge's unique position is generating video of an **entire site plan** -- showing how multiple buildings, streets, open spaces, and infrastructure relate spatially. This is a gap in the market.

### What Architecture Firms Want

Based on industry trends:
1. **Before/after transformation videos** for public consultations and council presentations
2. **Ambient "living renders"** with animated people, weather, and lighting
3. **Fly-through sequences** combining multiple viewpoints of a development
4. **Seasonal/time-of-day variations** showing how a space performs across conditions
5. **Quick iteration** -- change a zone's archetype and regenerate the video in minutes

---

## 5. Integration with SiteForge

### Current Render Architecture

The existing `backend/app/api/v1/render.py` endpoint reveals:

**Request Flow:**
1. Frontend sends base64 map screenshot + archetype reference images + prompt
2. Backend builds a multi-part Gemini payload with structural anchor, spatial layout, archetype references, and optional mask
3. Gemini generateContent returns a single rendered image
4. Post-processing (sharpening, contrast, color) is applied
5. Token accounting deducts from user's weekly allowance
6. Audit log saved to S3

**Key Patterns to Preserve:**
- `RenderRequest` model with `image_base64`, `archetype_images`, `prompt`, `guidance_scale`
- Dual auth: `GEMINI_API_KEY` (direct) or Vertex AI service account
- Token-based billing (`_MODEL_TOKEN_COST` dict, weekly allowance)
- S3 audit logging of input/output
- Post-processing pipeline

### Proposed Video Endpoint

A new endpoint `/api/v1/render/video/generate` alongside the existing `/api/v1/render/generate`:

```python
class VideoRenderRequest(BaseModel):
    """Payload for video generation."""
    # Reuse existing fields
    image_base64: str                    # Starting frame (SiteForge render)
    prompt: str                          # Cinematic prompt
    archetype_images: list[ArchetypeImage] | None = None

    # Video-specific fields
    end_frame_base64: str | None = None  # Last frame for fly-through
    duration_seconds: int = 8            # 4, 6, or 8
    resolution: str = "1080p"            # "720p" or "1080p"
    aspect_ratio: str = "16:9"           # "16:9" or "9:16"
    generate_audio: bool = False         # Ambient sound
    camera_motion: str | None = None     # "tracking_forward", "orbit_left", etc.
    model: str = "veo-3.1-generate-fast" # Model selection

class VideoRenderResponse(BaseModel):
    video_base64: str | None = None      # Inline for short clips
    video_url: str | None = None         # GCS URL for larger files
    duration_seconds: float
    operation_id: str | None = None      # For async polling
    status: str                          # "completed" | "processing" | "failed"
```

### Backend Architecture Changes

```
[Frontend]
    |
    v
[POST /api/v1/render/video/generate]
    |
    +-- Validate tokens (video costs 5x image render)
    +-- Build Veo API payload from SiteForge render + prompt
    +-- Submit async to Vertex AI Veo endpoint
    +-- Return operation_id immediately
    |
[GET /api/v1/render/video/status/{operation_id}]
    |
    +-- Poll Vertex AI operation status
    +-- On completion: download from GCS, save audit, deduct tokens
    +-- Return video_url or video_base64
```

### Key Implementation Decisions

1. **Async pattern required** -- Veo takes 30-120s to generate. Return an operation ID and let the frontend poll. Consider WebSocket for real-time status updates.

2. **GCS bucket for video storage** -- Videos are too large for inline base64 in most cases. Store in GCS, return a signed URL.

3. **Prompt construction** -- Reuse the existing multi-image payload builder but add cinematic camera directives. The paper's coordinate-to-prompt translation matrix is directly applicable.

4. **First/last frame from viewer** -- When the user defines a camera path in the 3D viewer, capture screenshots at start and end positions. Send both to Veo 3.1 as first_frame and last_frame.

5. **Token cost multiplier** -- Video generation costs significantly more than image. Propose 5-10x the image token cost per generation.

### Frontend Changes Required

- New "Generate Video" button in the render panel (alongside existing "Generate Render")
- Camera motion selector (dropdown: forward, orbit left, orbit right, crane up, etc.)
- Duration selector (4s, 6s, 8s)
- Video preview player with playback controls
- Async progress indicator (generation takes 30-120s)
- Video gallery alongside existing render gallery
- Optional: camera path editor in 3D viewer for first/last frame definition

---

## 6. Use Cases for SiteForge

### Use Case 1: Living Renders

**Description:** Animate a static SiteForge render to add life -- people walking, trees swaying, clouds drifting, cars moving, lighting shifting.

**Implementation:**
- Input: existing SiteForge render (image_base64)
- Prompt: "Animate this architectural rendering. Add pedestrians walking along sidewalks, gentle wind in trees, dappled afternoon sunlight, subtle cloud shadows moving across facades."
- Model: `veo-3.1-generate-fast` (cost-effective for ambient animation)
- Duration: 8 seconds, loopable
- Audio: Enable for ambient city sounds

**Token cost:** ~40-65 tokens per generation (5x image render)
**Generation time:** ~30-60 seconds

### Use Case 2: Before/After Site Transformation

**Description:** Show the transformation from existing conditions to proposed development. Critical for public consultations and council presentations.

**Implementation:**
- Input: first_frame = render of existing site conditions, last_frame = render of proposed development
- Prompt: "Smooth cinematic transition from existing urban conditions to proposed mixed-use development. Camera holds steady. Buildings gradually emerge, landscaping fills in, pedestrians appear."
- Model: `veo-3.1-generate` (standard quality for presentations)
- Duration: 8 seconds

**Token cost:** ~65-100 tokens
**Generation time:** ~60-120 seconds

### Use Case 3: Fly-Through Animation

**Description:** Camera moves through the site, combining multiple street view angles into a continuous sequence.

**Implementation:**
- Capture 3-4 camera positions from SiteForge 3D viewer
- Generate 2-3 connected 8-second segments using first/last frame chaining
- Chain: segment 1 last_frame = segment 2 first_frame
- Prompt per segment includes specific camera motion from the translation matrix

**Token cost:** ~130-300 tokens (for 3 chained segments)
**Generation time:** ~2-6 minutes total

### Use Case 4: Seasonal/Time-of-Day Variations

**Description:** Show how a space performs across different conditions -- summer/winter, day/night, sunny/rainy.

**Implementation:**
- Input: same SiteForge render as starting frame
- Generate 4 variants with different prompts:
  - "Golden hour summer, long shadows, warm light, people dining outdoors"
  - "Snowy winter morning, bare trees, warm interior glow from buildings"
  - "Rainy evening, wet reflections on pavement, umbrella pedestrians, neon signage"
  - "Bright midday, harsh shadows, active street life, food truck"
- Compile into a comparison grid or sequential montage

**Token cost:** ~160-260 tokens (4 generations)
**Generation time:** ~2-4 minutes

### Use Case 5: Street-Level Walkthrough

**Description:** Simulate walking down a proposed street, experiencing the space at pedestrian scale.

**Implementation:**
- Use the existing street view camera from SiteForge as the starting frame
- Prompt: "Smooth tracking forward shot at eye level, walking pace, through mixed-use neighborhood street. Pedestrians pass, shops visible, dappled tree shade, cyclist in bike lane."
- Model: `veo-3.1-generate` for maximum realism at eye level

**Token cost:** ~65-100 tokens
**Generation time:** ~60-120 seconds

---

## 7. Cost Estimates

### Per-Generation Costs (Vertex AI direct)

| Model | Per Second | 8s Clip (no audio) | 8s Clip (with audio) |
|-------|-----------|--------------------|-----------------------|
| Veo 3.1 Fast | $0.10 | $0.80 | $1.20 |
| Veo 3.1 Standard | $0.27 | $2.16 | $3.20 |
| Veo 3.0 | $0.50 | $4.00 | $6.00 |
| Veo 2.0 (style ref) | $0.35-0.50 | $2.80-4.00 | N/A (no audio) |

### Proposed SiteForge Token Costs

Using the existing token economy ($0.005 per token, 1000 tokens/week free):

| Video Type | Google Cost | SiteForge Tokens | Margin |
|-----------|------------|-----------------|--------|
| Living Render (8s, Fast, no audio) | $0.80 | 40 tokens ($0.20) | Subsidized during beta |
| Living Render (8s, Fast, audio) | $1.20 | 50 tokens ($0.25) | Subsidized during beta |
| Presentation (8s, Standard, audio) | $3.20 | 100 tokens ($0.50) | Subsidized during beta |
| Fly-through (3x8s chained) | $3.60-9.60 | 200-400 tokens | Near break-even |
| Seasonal set (4x8s) | $3.20-12.80 | 200-500 tokens | Near break-even |

### Monthly Cost Projections

| Scenario | Users | Videos/User/Week | Monthly Google Cost | Monthly Revenue (tokens) |
|----------|-------|-------------------|--------------------|--------------------------|
| Soft launch | 50 | 3 | $480-1,920 | $120-300 |
| Growth | 500 | 5 | $8,000-32,000 | $2,000-5,000 |
| Scale | 5,000 | 8 | $128,000-512,000 | $32,000-80,000 |

**Key takeaway:** At current token pricing, video generation would be heavily subsidized. Two options: (a) introduce a separate video credit tier at higher token cost, or (b) offer video as a premium/paid-only feature.

### Cost Optimization Strategies

1. **Use Veo 3.1 Fast for drafts**, Standard for final output only
2. **Disable audio** when ambient sound is not needed (saves 33%)
3. **Cache renders** -- if the same site layout is re-animated, reuse the base image
4. **720p for previews**, 1080p only for export/download
5. **Rate limit** video generations more aggressively than image renders
6. **Batch generation** during off-peak hours for lower latency

---

## 8. UI Wireframes

### 8.1 Video Generation Panel (in Render Sidebar)

```
+-----------------------------------------------+
|  RENDER                          [Image] [Video]|
+-----------------------------------------------+
|                                                 |
|  [Rendered Image Preview / Video Player]        |
|  +-------------------------------------------+  |
|  |                                           |  |
|  |    (current render or video playback)     |  |
|  |                                           |  |
|  |              [> Play]  0:00 / 0:08        |  |
|  +-------------------------------------------+  |
|                                                 |
|  Video Settings                                 |
|  +-------------------------------------------+  |
|  | Camera Motion: [v Tracking Forward      ]  |  |
|  | Duration:      ( ) 4s  (*) 8s             |  |
|  | Quality:       (*) Fast  ( ) Standard     |  |
|  | Resolution:    (*) 720p  ( ) 1080p        |  |
|  | Audio:         [ ] Include ambient sound   |  |
|  +-------------------------------------------+  |
|                                                 |
|  Prompt Override (optional)                     |
|  +-------------------------------------------+  |
|  | "Add gentle wind in trees, afternoon      |  |
|  |  sunlight, pedestrians on sidewalks"      |  |
|  +-------------------------------------------+  |
|                                                 |
|  Cost: ~50 tokens                               |
|  Est. time: ~45 seconds                         |
|                                                 |
|  [ Generate Video ]              [65 tokens left]|
|                                                 |
+-----------------------------------------------+
```

### 8.2 Camera Motion Selector Options

```
Camera Motion Dropdown:
+--------------------------------------+
| > Tracking Forward  (walk through)   |
|   Tracking Backward (pull back)      |
|   Orbit Left        (rotate around)  |
|   Orbit Right       (rotate around)  |
|   Crane Up          (rise upward)    |
|   Crane Down        (descend)        |
|   Pan Left          (lateral slide)  |
|   Pan Right         (lateral slide)  |
|   Static + Life     (fixed, animate) |
|   Custom...         (type your own)  |
+--------------------------------------+
```

### 8.3 Async Generation Progress

```
+-----------------------------------------------+
|  Generating Video...                            |
|  +-------------------------------------------+  |
|  | [=========>              ] 45%             |  |
|  |                                           |  |
|  | Model: Veo 3.1 Fast                       |  |
|  | Elapsed: 22s / Est. 50s                   |  |
|  |                                           |  |
|  | [Cancel]                                  |  |
|  +-------------------------------------------+  |
+-----------------------------------------------+
```

### 8.4 Video Gallery (Project Level)

```
+-----------------------------------------------+
|  Project: Downtown Revitalization               |
|  Tab: [Renders] [Videos] [Documents]            |
+-----------------------------------------------+
|                                                 |
|  +--------+  +--------+  +--------+            |
|  |  [>]   |  |  [>]   |  |  [>]   |            |
|  | thumb1 |  | thumb2 |  | thumb3 |            |
|  +--------+  +--------+  +--------+            |
|  Living     Fly-through  Winter                 |
|  Render     Segment 1    Variant                |
|  8s | Fast  8s | Std     8s | Std               |
|  Mar 31     Mar 31       Mar 30                 |
|                                                 |
|  [Download All as MP4]  [Create Montage]        |
+-----------------------------------------------+
```

### 8.5 Before/After Mode

```
+-----------------------------------------------+
|  Before/After Transformation                    |
+-----------------------------------------------+
|  First Frame         Last Frame                 |
|  +-----------+       +-----------+              |
|  | [Existing |  -->  | [Proposed |              |
|  |  site]    |       |  design]  |              |
|  +-----------+       +-----------+              |
|  [Use Current View]  [Use Current View]         |
|                                                 |
|  Transition: (*) Gradual build  ( ) Cut         |
|  Duration:   (*) 8s  ( ) 4s                     |
|                                                 |
|  [ Generate Transformation ]    ~100 tokens     |
+-----------------------------------------------+
```

---

## 9. Phased Implementation Plan

### Phase 1: Living Renders (Weeks 1-3)

**Goal:** Add "animate this render" as the simplest video feature.

**Backend:**
- New endpoint `POST /api/v1/render/video/generate`
- New endpoint `GET /api/v1/render/video/status/{operation_id}`
- Veo 3.1 Fast integration via Vertex AI (async long-running operation)
- GCS bucket for video output storage
- Video token cost model (separate from image tokens)
- Audit logging for video generations

**Frontend:**
- Add [Image] / [Video] toggle to render panel
- Camera motion dropdown
- Duration and quality selectors
- Async progress indicator with polling
- Inline video player for results
- "Save to Gallery" for videos

**Infrastructure:**
- GCS bucket provisioned for video output
- Increase httpx timeout to 300s for video operations
- Add `VEO_MODEL` config to settings

**Token economy:**
- Video renders cost 40-100 tokens (vs 8-27 for images)
- Same weekly allowance, users choose how to spend

### Phase 2: Fly-Throughs and Before/After (Weeks 4-6)

**Goal:** Spatial video features that use first/last frame conditioning.

**Backend:**
- First/last frame support in video endpoint
- Segment chaining logic (last frame of segment N = first frame of segment N+1)
- Batch generation for multi-segment fly-throughs
- Video concatenation (ffmpeg or similar for joining segments)

**Frontend:**
- Camera path editor in 3D viewer (define waypoints)
- Before/After mode with dual frame capture
- Segment timeline showing chained clips
- Automatic prompt generation from camera trajectory (translation matrix from paper)
- Progress indicator per segment

**Technical:**
- Camera trajectory export from CesiumJS/Three.js viewer
- Coordinate delta to cinematic prompt translation middleware
- ffmpeg integration for segment concatenation

### Phase 3: Style Conditioning and Advanced Features (Weeks 7-10)

**Goal:** Leverage archetype images for style-consistent video and add seasonal variations.

**Backend:**
- Veo 2 integration for style reference image support
- Parallel generation for seasonal/time-of-day variant sets
- Video montage compilation (4-up grid or sequential)
- Audio toggle and ambient sound presets

**Frontend:**
- "Generate Variants" button for seasonal/lighting sets
- Side-by-side comparison player
- Archetype-aware prompt templates
- Audio preview and toggle
- Export options: individual clips, montage, or presentation deck

**Integration:**
- Archetype card images as Veo style references (Veo 2)
- Asset images from archetype catalog as subject references (Veo 3.1)
- Seasonal prompt templates mapped to aesthetic catalog entries

### Phase 4: Premium Features and Optimization (Weeks 11-16)

**Goal:** Polish, optimize costs, and add premium capabilities.

**Features:**
- Video upscaling to 4K via post-processing
- Longer sequences via advanced chaining (24s, 32s)
- Custom camera path recording from 3D viewer mouse movement
- Video-to-video refinement (iterative improvement like dual anchoring for images)
- Depth map extraction from SiteForge 3D viewer for enhanced conditioning
- WebSocket-based real-time generation status
- Video sharing with embed codes
- Premium tier with higher video allowance
- Runway Gen-4 as alternative backend for users who need it

**Optimization:**
- Generation caching (same layout + prompt = cached result)
- 720p preview with on-demand 1080p upgrade
- Batch scheduling for off-peak generation
- CDN for video delivery

---

## 10. Risk Assessment

### Technical Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Veo temporal drift in generated video | Medium | First/last frame anchoring, prompt engineering, quality validation |
| API deprecation (preview endpoints) | High | Use GA endpoints only; veo-2.0-generate-exp deprecated Apr 2, 2026 |
| Generation time exceeding user patience | Medium | Async pattern with progress polling; Fast model for drafts |
| Video file size overwhelming storage | Medium | GCS with lifecycle policies; compress aggressively; 720p default |
| Hallucinated architecture in video | High | Use existing render as input frame (image-to-video, not text-to-video) |
| Cost overruns at scale | High | Aggressive token pricing; rate limiting; Veo 3.1 Fast default |

### Business Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Low adoption (users prefer static renders) | Medium | Default to "Living Render" which requires one click |
| Token cost too high for free tier | High | Separate video credit pool; offer 2-3 free videos/week |
| Competitors add video first | Medium | Phase 1 is 3 weeks; fast follow on market opportunity |
| Quality not meeting professional standards | Medium | Offer Runway Gen-4 as premium alternative; iterate on prompts |

### Regulatory Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| AI-generated video mistaken for real footage | Medium | C2PA/SynthID watermarking (automatic in Veo); clear UI labeling |
| Data privacy (municipal data in API calls) | Low | Only send rendered images, never raw GIS data |
| Copyright of AI-generated architectural video | Low | Generated from user's own site plans and archetype selections |

---

## Summary and Recommendation

Video generation is a natural extension of SiteForge's existing render pipeline. The technical architecture aligns closely -- the current Gemini-based image generation endpoint can be extended with a parallel Veo-based video endpoint sharing the same auth, token, and audit infrastructure.

**Recommended approach:** Start with Phase 1 (Living Renders) using Veo 3.1 Fast. This provides immediate value with minimal complexity -- users click "Generate Video" on an existing render and get an 8-second animated version with ambient life. Cost is $0.80-1.20 per generation, mapped to 40-50 tokens.

**Model selection:** Veo 3.1 Fast for drafts and most use cases; Veo 3.1 Standard for presentation quality; Veo 2.0 when style reference images are needed (time-limited, migrating to Veo 3.x when style support arrives).

**Timeline:** Phase 1 in 3 weeks, Phase 2 in 6 weeks, full feature set in 16 weeks. Phase 1 alone would make SiteForge the first site-planning tool with integrated AI video generation.
