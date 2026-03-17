# AI Render Feature — Claude Code Instructions

## What this adds

Three new files that extend the existing Mapbox massing component with a
FLUX.1 Depth AI rendering pipeline. The user can capture the current 3D
massing view, send it to fal.ai, and get back a photorealistic building render
that is overlaid on the map pinned to the correct geographic bounds.

---

## Files to drop in

| File | Where it goes | What it is |
|---|---|---|
| `useAIRender.ts` | Same folder as the map component | React hook — handles fal.ai API call, progress state, result |
| `AIRenderPanel.tsx` | Same folder as the map component | UI panel — style picker, prompt input, reference image, render button |
| `MapboxTiltedAerialReplacement.tsx` | Replace existing file | Updated map component — adds `preserveDrawingBuffer`, mounts panel, overlays result |

---

## Setup steps

### 1. Install fal.ai client (optional but recommended)
The hook uses plain `fetch` so no install is needed. If you later want the
fal.ai JS client for streaming progress, run:
```bash
npm install @fal-ai/client
```

### 2. Add environment variable
```bash
# .env.local  (Vite)
VITE_FAL_KEY=your_fal_api_key_here

# .env.local  (Next.js — must be prefixed NEXT_PUBLIC_ to reach the browser)
NEXT_PUBLIC_FAL_KEY=your_fal_api_key_here
```

Get a key at https://fal.ai — the FLUX.1 Depth endpoint costs ~$0.075/megapixel.

### 3. Update the token read in useAIRender.ts if using Next.js
In `useAIRender.ts` around line 185, the env read is:
```ts
(typeof import.meta !== 'undefined' && (import.meta as any)?.env?.VITE_FAL_KEY) || ''
```
Add a fallback for Next.js if needed:
```ts
(typeof import.meta !== 'undefined' && (import.meta as any)?.env?.VITE_FAL_KEY) ||
(typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_FAL_KEY) ||
''
```

---

## How the pipeline works

```
User clicks "Generate Render"
        │
        ▼
map.getCanvas().toDataURL()        ← requires preserveDrawingBuffer: true
        │
        ▼
POST https://fal.run/fal-ai/flux-general
  body: {
    prompt: "aerial oblique view, modern glass tower…",
    controlnets: [{ path: "depth", control_image_url: <base64 PNG> }]
    // optional: ip_adapter: [{ ip_adapter_image_url: <reference> }]
  }
        │
        ▼
fal.ai extracts depth map from screenshot,
runs FLUX.1 dev with depth ControlNet,
returns { images: [{ url }] }
        │
        ▼
map.addSource(AI_RENDER_SOURCE_ID, {
  type: 'image',
  url: result.imageUrl,
  coordinates: [[W,N],[E,N],[E,S],[W,S]]   ← bounds from map at capture time
})
map.addLayer({ type: 'raster', ... })
```

---

## Key parameters to tune

| Parameter | Default | Effect |
|---|---|---|
| `controlStrength` | 0.85 | How closely AI follows the massing geometry. Lower = more creative. |
| `num_inference_steps` | 28 | More steps = higher quality, slower. 20–35 is a good range. |
| `guidance_scale` | 3.5 | FLUX recommendation. Don't change unless testing. |
| Raster overlay opacity | 0.92 | In `MapboxTiltedAerialReplacement.tsx` `applyAIRenderOverlay()`. |

---

## Using the hook directly (advanced)

If you want to trigger renders programmatically without the panel UI:

```tsx
import { useAIRender } from './useAIRender';

const { render, isRendering, result } = useAIRender();

async function handleCustomRender() {
  const result = await render(mapRef.current, {
    style: 'modern-glass',
    customPrompt: 'rainy evening, reflective puddles',
    controlStrength: 0.8,
  });
  console.log(result.imageUrl);
}
```

---

## Hiding the built-in panel

Pass `showAIPanel={false}` to the map component to suppress the UI and manage
rendering yourself via the hook:

```tsx
<MapboxTiltedAerialReplacement showAIPanel={false} ... />
```

---

## Known limitations & next steps

- **One render at a time** — the hook doesn't queue concurrent requests.
- **Overlay is 2D** — the image source is a flat raster draped over the map. It
  does not re-project in 3D with terrain. This is fine for the massing/tilted
  views at zoom 16 but may look stretched at extreme pitch.
- **fal.ai latency** — typical render time is 8–20 seconds for 1024×1024 with
  FLUX.1 dev depth. The pro variant is faster.
- **Reference image IP-Adapter** — the IP-Adapter path in `useAIRender.ts` uses
  SD1.5 weights. For FLUX you may want to swap to the FLUX IP-Adapter when it
  is more widely available on fal.ai.
- **Capture resolution** — the screenshot is whatever the canvas DPR produces.
  For retina screens this is already 2048px+, which is ideal.
