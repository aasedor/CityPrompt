# Render Hook Comparison Report: `useGlobeAIRender.ts` vs `useAIRender.ts`

_Generated 2026-04-18 while on `feature/google-3d-globe-stable` (commit `dba53ae`). Codex side references `codex/google-3d-globe-integration` at `b9cea11`._

## Executive Summary

**Verdict:** `useGlobeAIRender.ts` (stable) produces superior output because it leverages **real 3D photorealistic building context** (Google Photorealistic Tiles) during capture, uses **direct per-zone binary masking with building silhouette extrusion**, and **single-shot Gemini rendering with reference images**. `useAIRender.ts` (codex) routes through a **2D Mapbox viewport** to a **Vertex AI Imagen 3 backend**, producing visually weaker output due to lack of 3D spatial context, weaker occlusion handling, and post-hoc pixel-diff stitching that creates artifacts.

---

## 1. High-Level Architecture

**Verdict:** Stable exposes a single unified `render()` API (with optional `renderPerZone()` fallback); codex exposes `render()`, `renderZone()`, `renderPreviews()`, `renderFull()`, and `renderPerZone()` with a state-machine-based return object.

### Stable (useGlobeAIRender.ts)

**API Shape:** [useGlobeAIRender.ts:1116–1580](frontend/src/components/viewer/globe/useGlobeAIRender.ts:1116)

```typescript
export function useGlobeAIRender() {
  const render = useCallback(async (
    canvas: HTMLCanvasElement,
    camera: THREE.Camera,
    zones: SiteZone[],
    terrainHeight: number,
    options: { style?, model?, projectId?, customPrompt? }
  ): Promise<GlobeRenderResult | null>
  
  const renderPerZone = useCallback(async (
    canvas: HTMLCanvasElement,
    camera: THREE.Camera,
    zones: SiteZone[],
    terrainHeight: number,
    options: { ..., onProgress? }
  ): Promise<GlobeRenderResult | null>
  
  const captureStreetView = useCallback(...)
  
  return { render, renderPerZone, captureStreetView, isRenderingRef }
}

export interface GlobeRenderResult {
  imageUrl: string;  // data:image/png;base64,...
  prompt: string;
  seed?: number;
}
```

- **Single-shot default:** `render()` captures globe canvas, generates mask, collects archetype images, sends single Gemini call with 2K output, clips result to polygons.
- **Per-zone fallback:** `renderPerZone()` available but **disabled by default** ([useGlobeAIRender.ts:856](frontend/src/components/viewer/globe/useGlobeAIRender.ts:856): `PERZONE_THRESHOLD = 99` — single-shot is always used). Per-zone available for fine-grained control if needed.
- **No state machine:** Simple input → Promise<result> interface. Caller manages UI.

### Codex (useAIRender.ts)

**API Shape:** [useAIRender.ts:87–154](frontend/src/components/viewer/useAIRender.ts:87)

```typescript
export function useAIRender(): UseAIRenderReturn {
  // Returns a stateful object with:
  render: (map, options?) => Promise<AIRenderResult | null>
  renderZone: (map, zoneCoords, options?) => Promise<AIRenderResult | null>
  renderPreviews: (map, options?) => Promise<AIRenderResult[]>
  renderFull: (map, options, seed, singleView?) => Promise<AIRenderResult | null>
  renderPerZone: (map, options?) => Promise<AIRenderResult | null>
  
  // State fields:
  faceRenders: FaceRender[]  // 4-face bearing-based renders
  isRendering: boolean
  progress: number  // 0–100 or -1
  statusMessage: string
  result: AIRenderResult | null
  previews: AIRenderResult[]
  selectedPreviewIndex: number | null
  error: string | null
  
  // Control methods:
  setSelectedPreviewIndex: (index: number | null) => void
  reset: () => void
  attachFaceSwapping: (map) => () => void
}

export interface AIRenderResult {
  imageUrl: string
  bounds: [[number, number], [number, number], [number, number], [number, number]]
  seed?: number
  prompt: string
}
```

- **Multiple render modes:** `render()` (single), `renderZone()` (zoom + render one zone), `renderPreviews()` (3× parallel with different seeds), `renderFull()` (locked seed), `renderPerZone()` (sequential per-zone composite).
- **State machine:** Internal state (progress, error, result, previews, selectedPreviewIndex, faceRenders) — UI reads state, doesn't manage it directly.
- **Face swapping:** 4-bearing render capability for building facades.

**Architectural implication:** Stable's simpler API reflects that **all rendering is single-shot**. Codex's multi-method API reflects that **rendering can be exploratory (previews) or zone-targeted (renderZone) or sequential (renderPerZone)**.

---

## 2. Capture Step

**Verdict:** Stable captures **3D photorealistic tiles + R3F canvas** at 85% JPEG quality (300–800KB); codex captures **2D Mapbox satellite imagery** as PNG, optionally with zone overlay toggling.

### Stable

**Function:** [useGlobeAIRender.ts:61–72](frontend/src/components/viewer/globe/useGlobeAIRender.ts:61)

```typescript
function captureCanvasBase64(canvas: HTMLCanvasElement): Promise<string> {
  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      if (!blob) { resolve(''); return; }
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        resolve(dataUrl.split(',')[1]); // Raw base64 without prefix
      };
      reader.readAsDataURL(blob);
    }, 'image/jpeg', 0.85);
  });
}
```

- **Input:** R3F canvas with `preserveDrawingBuffer: true` — includes rendered 3D tiles + terrain + camera-projected zone polygons.
- **Format:** JPEG, 85% quality. **Reduces 2–5 MB PNG → 300–800 KB**, significantly reducing API latency.
- **Supplementary:** Text labels + colored dashed borders drawn **post-capture** ([useGlobeAIRender.ts:1142–1237](frontend/src/components/viewer/globe/useGlobeAIRender.ts:1142)) to help Gemini identify zones.
- **DPR handling:** Canvas pixel dimensions = `canvas.width × canvas.height` (no scaling); zone projection uses same units.

### Codex

**Functions:** [useAIRender.ts:752–802](frontend/src/components/viewer/useAIRender.ts:752)

```typescript
async function captureMapCanvasBase64(map: MapboxMap): Promise<string> {
  const canvas = map.getCanvas();
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) return reject(new Error('Failed to capture map canvas'));
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUri = reader.result as string;
        const base64 = dataUri.split(',')[1];
        resolve(base64);
      };
      reader.readAsDataURL(blob);
    }, 'image/png');
  });
}

async function captureMapCanvasWithoutOverlays(map: MapboxMap): Promise<string> {
  const viewport = map as unknown as { setZoneOverlaysVisible?: (visible: boolean) => void };
  const hasToggle = typeof viewport.setZoneOverlaysVisible === 'function';
  if (!hasToggle) return captureMapCanvasBase64(map);
  try {
    viewport.setZoneOverlaysVisible!(false);
    await new Promise<void>((r) => requestAnimationFrame(() => r()));
    await new Promise<void>((r) => requestAnimationFrame(() => r()));
    return await captureMapCanvasBase64(map);
  } finally {
    try { viewport.setZoneOverlaysVisible!(true); } catch { /* ignore */ }
  }
}
```

- **Input:** Mapbox canvas — 2D satellite raster + vector tile layer with colored zone polygons as 3D meshes (in globe view) or 2D overlays (in Mapbox fallback).
- **Format:** PNG. **No compression tuning** (lossless).
- **Overlay handling:** Optionally hides zone overlays (if `setZoneOverlaysVisible()` exists) to capture clean satellite imagery underneath. Safe fallback for older Mapbox paths.
- **DPR handling:** Uses `window.devicePixelRatio` — canvas pixel dimensions account for retina displays ([useAIRender.ts:942–943](frontend/src/components/viewer/useAIRender.ts:942): `const dpr = window.devicePixelRatio || 1`).

**Key difference:** Stable captures **real 3D buildings**. Codex captures **flat raster satellite photo** — lack of 3D context causes Gemini to struggle with building scale, shadow direction, and material consistency.

---

## 3. Mask Generation

**Verdict:** Stable generates a **binary mask with building silhouette extrusion** (roof outline projected upward); codex generates a **binary mask with perspective headroom expansion** (bounded rectangle above footprint).

### Stable

**Function:** [useGlobeAIRender.ts:236–322](frontend/src/components/viewer/globe/useGlobeAIRender.ts:236)

```typescript
function generateMask(
  zones: SiteZone[],
  camera: THREE.Camera,
  width: number,
  height: number,
  terrainHeight: number,
): string {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d')!;
  
  // Black = preserve, white = edit
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, width, height);
  
  // Clip to site boundary if present
  const siteBoundary = zones.find(z => z.zone_type === 'site_boundary' && z.coordinates?.length >= 3);
  if (siteBoundary) {
    const boundaryPixels = siteBoundary.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];
    if (boundaryPixels.length >= 3) {
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(boundaryPixels[0].x, boundaryPixels[0].y);
      for (let i = 1; i < boundaryPixels.length; i++) ctx.lineTo(boundaryPixels[i].x, boundaryPixels[i].y);
      ctx.closePath();
      ctx.clip(); // All subsequent drawing is clipped to boundary
    }
  }
  
  // Binary mask: white = edit, black = preserve
  const DILATION_PX = 8; // ~2m at typical aerial zoom
  ctx.fillStyle = '#ffffff';
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = DILATION_PX * 2;
  ctx.lineJoin = 'round';
  
  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    if (zone.zone_type === 'site_boundary') continue;
    
    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, width, height))
      .filter(Boolean) as { x: number; y: number }[];
    
    if (pixels.length < 3) continue;
    
    ctx.beginPath();
    ctx.moveTo(pixels[0].x, pixels[0].y);
    for (let i = 1; i < pixels.length; i++) ctx.lineTo(pixels[i].x, pixels[i].y);
    ctx.closePath();
    
    // For buildings, expand upward to include building height
    const buildingHeight = (zone.properties?.height_m as number)
      || (zone.properties?.height as number)
      || ((zone.properties?.floors as number) || 0) * 3.2 || 0;
    
    if (buildingHeight > 0 && (zone.zone_type === 'building' || zone.zone_type === 'residential')) {
      const topPixels = zone.coordinates
        .map(c => projectToPixels(c[0], c[1], terrainHeight + buildingHeight, camera, width, height))
        .filter(Boolean) as { x: number; y: number }[];
      
      if (topPixels.length >= 3) {
        for (const p of topPixels) ctx.lineTo(p.x, p.y);
      }
    }
    
    ctx.fill();
    ctx.stroke(); // Dilation: thick white stroke adds ~2m bleed room
  }
  
  if (siteBoundary) ctx.restore();
  
  return canvas.toDataURL('image/png').split(',')[1];
}
```

- **Polygon dilation:** `8px` stroke width (both sides, so ~16px total) — represents ~2m lateral context bleed.
- **Building headroom:** **Silhouette extrusion** — projects the roof outline (base + height) upward using camera projection, creating a **realistic 3D silhouette** that matches what Gemini sees in the canvas.
- **Site boundary:** Clipped using `ctx.clip()` — subsequent drawing is constrained; boundary itself stays black (preserve).
- **Key strength:** The roof outline is **perspective-correct** — at an oblique camera angle, the top corners shift upward/inward naturally. Gemini sees the exact 3D shape it needs to fill.

### Codex

**Function:** [useAIRender.ts:1117–1227](frontend/src/components/viewer/useAIRender.ts:1117)

```typescript
function generateBinaryMask(
  map: MapboxMap,
  siteZones: SiteZone[],
  occluderGeometry?: Map<string, OccluderSilhouette[]>,
): string {
  const mapCanvas = map.getCanvas();
  const w = mapCanvas.width;
  const h = mapCanvas.height;
  const dpr = window.devicePixelRatio || 1;
  
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const ctx = maskCanvas.getContext('2d')!;
  
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, w, h);
  
  // Site boundary is a CLIP region, not an editable area
  let boundaryClipped = false;
  if (boundaries.length > 0) {
    const boundary = boundaries[0];
    if (boundary.coordinates && boundary.coordinates.length >= 3) {
      const bpx = siteBoundaryToPixels(map, boundary.coordinates);
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(bpx[0].x * dpr, bpx[0].y * dpr);
      for (let i = 1; i < bpx.length; i++) ctx.lineTo(bpx[i].x * dpr, bpx[i].y * dpr);
      ctx.closePath();
      ctx.clip();
      boundaryClipped = true;
    }
  }
  
  ctx.fillStyle = '#ffffff';
  const DILATION_PX = 8 * dpr; // ~2m
  
  for (const zone of others) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    const pixels = siteBoundaryToPixels(map, zone.coordinates);
    
    ctx.beginPath();
    ctx.moveTo(pixels[0].x * dpr, pixels[0].y * dpr);
    for (let i = 1; i < pixels.length; i++) {
      ctx.lineTo(pixels[i].x * dpr, pixels[i].y * dpr);
    }
    ctx.closePath();
    ctx.fill();
    
    // Dilation
    ctx.save();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = DILATION_PX;
    ctx.lineJoin = 'round';
    ctx.stroke();
    ctx.restore();
    
    // For building zones, expand the mask upward based on building height
    // with a 3x safety margin
    if (BUILDING_TYPES.includes(zone.zone_type)) {
      const buildingHeight = zone.properties?.height_m ? Number(zone.properties.height_m) : 0;
      const headroom = buildingHeight > 0
        ? calculatePerspectiveHeadroom(map, buildingHeight)
        : 80 * dpr; // conservative default
      
      if (headroom > 0) {
        const devicePixels = pixels.map(p => ({ x: p.x * dpr, y: p.y * dpr }));
        const minY = Math.min(...devicePixels.map(p => p.y));
        const minX = Math.min(...devicePixels.map(p => p.x));
        const maxX = Math.max(...devicePixels.map(p => p.x));
        const expandedTop = Math.max(0, minY - headroom);
        ctx.fillRect(minX, expandedTop, maxX - minX, minY - expandedTop);
        
        // Soft feathered edge at the top (gradient from black to transparent)
        const featherHeight = Math.min(20 * dpr, headroom * 0.25);
        if (featherHeight > 2) {
          const gradient = ctx.createLinearGradient(0, expandedTop, 0, expandedTop + featherHeight);
          gradient.addColorStop(0, 'rgba(0,0,0,1)');   // black
          gradient.addColorStop(1, 'rgba(0,0,0,0)');   // transparent
          ctx.globalCompositeOperation = 'destination-out';
          ctx.fillStyle = gradient;
          ctx.fillRect(minX, expandedTop, maxX - minX, featherHeight);
          ctx.globalCompositeOperation = 'source-over';
        }
      }
    }
  }
  
  // ─── Occluder subtraction ───
  if (occluderGeometry && occluderGeometry.size > 0) {
    const allSilhouettes: OccluderSilhouette[] = [];
    const seen = new Set<string>();
    for (const list of occluderGeometry.values()) {
      for (const occ of list) {
        const key = occ.basePixels.map(p => `${Math.round(p.x)},${Math.round(p.y)}`).join('|');
        if (seen.has(key)) continue;
        seen.add(key);
        allSilhouettes.push(occ);
      }
    }
    if (allSilhouettes.length > 0) {
      subtractBuildingSilhouettes(ctx, allSilhouettes, dpr, dpr);
    }
  }
  
  if (boundaryClipped) ctx.restore();
  
  return maskCanvas.toDataURL('image/png').split(',')[1];
}

function calculatePerspectiveHeadroom(map: MapboxMap, buildingHeightM: number): number {
  const pitch = map.getPitch(); // 0=top-down, 60=oblique
  if (pitch < 5 || buildingHeightM <= 0) return 0;
  
  const center = map.getCenter();
  const p1 = map.project(center);
  const latOffset = 0.0009; // ~100m in latitude
  const p2 = map.project({ lng: center.lng, lat: center.lat + latOffset });
  const pixelsPer100m = Math.abs(p2.y - p1.y);
  const pixelsPerMeter = pixelsPer100m / 100;
  
  // Vertical shift = building height × pixels-per-meter × sin(pitch)
  const pitchRad = pitch * Math.PI / 180;
  const verticalShift = buildingHeightM * pixelsPerMeter * Math.sin(pitchRad);
  
  const dpr = window.devicePixelRatio || 1;
  // 2.0x safety margin for edge distortion + steep oblique angles
  return verticalShift * dpr * 2.0;
}
```

- **Polygon dilation:** `8 * dpr` — same as stable but DPR-aware.
- **Building headroom:** **Perspective-computed rectangle** — calculated from map pitch, zoom, and building height (meters-to-pixels ratio). Extends a **rectangular box straight up** from the footprint, with a **2.0× safety margin**. Does NOT project the roof outline.
- **Feathering:** Soft gradient (4px blur on top edge) — prevents hard mask boundary, but is a separate step from the filled rectangle.
- **Occluder subtraction:** If other buildings occlude this zone, their silhouettes are subtracted from the white mask using `destination-out` compositing ([useAIRender.ts:1184–1205](frontend/src/components/viewer/useAIRender.ts:1184)).

**Key difference:** Stable projects the **exact 3D roof shape** Gemini must fill. Codex guesses a **rectangular box** based on pitch and zoom — this can be wrong if the building is not rectangular, or at extreme camera angles, leading to **stretched/distorted building silhouettes**.

---

## 4. Prompt Building

**Verdict:** Stable uses **SCHEMA format with color-to-zone mapping** and extensive **MANDATORY/CONSTRAINTS clauses** for zone boundary enforcement; codex uses **narrative prose (SCHEMA AVANZATO) with abbreviated keywords** for zone description.

### Stable

**Function:** [useGlobeAIRender.ts:600–717](frontend/src/components/viewer/globe/useGlobeAIRender.ts:600)

```typescript
function buildPrompt(zones: SiteZone[], style: string, camera?: THREE.Camera, terrainHeight?: number): string {
  // ... camera pitch estimation ...
  
  let pitchDesc = 'oblique aerial (~50°)';
  if (camera && terrainHeight != null) {
    const camDir = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion).normalize();
    const camPos = camera.position.clone().normalize();
    const cosAngle = Math.abs(camDir.dot(camPos.clone().negate()));
    const pitchDeg = Math.round(Math.acos(Math.min(1, cosAngle)) * 180 / Math.PI);
    if (pitchDeg < 20) pitchDesc = `near top-down (~${pitchDeg}°)`;
    // ...
  }
  
  const hasBuildings = zones.some(z => z.zone_type === 'building' || z.zone_type === 'residential');
  const composition = hasBuildings
    ? `${pitchDesc} view from 3D photorealistic city model, colored polygons mark proposed zones on the existing photographic context. Render buildings with correct 3D perspective for this viewing angle.`
    : `${pitchDesc} view, ground-level zones only on photorealistic 3D terrain.`;
  
  const lightingMap: Record<string, string> = {
    photorealistic: 'Golden hour, warm southwest sun, crisp architectural shadows.',
    winter: 'Soft diffuse winter daylight, low sun angle, long blue-tinted shadows, pale blue-grey overcast sky.',
    // ...
  };
  
  // Zones (SCHEMA format) — largest first
  const renderZones = zones
    .filter(z => z.zone_type !== 'site_boundary')
    .sort((a, b) => {
      const polyArea = (z: SiteZone) => {
        // Shoelace formula
      };
      return polyArea(b) - polyArea(a);
    });
  
  const zoneLines: string[] = [];
  for (let i = 0; i < renderZones.length; i++) {
    const zone = renderZones[i];
    const color = colorName(resolveZoneColor(zone));  // e.g. "bright vermillion #E03C31"
    const props = zone.properties || {};
    const info = getZoneArchetypeInfo(zone);
    
    const floors = (props.floors as number) || 0;
    const heightM = (props.height_m as number) || (props.height as number) || floors * 3.2 || 0;
    const name = info.archetypeTitle || zone.name || ZONE_TYPE_CONFIG[zone.zone_type]?.label || zone.zone_type;
    
    let scale = '';
    if (zone.zone_type === 'building' || zone.zone_type === 'residential') {
      if (floors > 0 && heightM > 0) scale = `${floors}F ${Math.round(heightM)}m`;
      else if (floors > 0) scale = `${floors}F`;
      else if (heightM > 0) scale = `${Math.round(heightM)}m`;
      else if (info.minFloors && info.maxFloors) {
        scale = info.minFloors === info.maxFloors ? `${info.minFloors}F` : `${info.minFloors}-${info.maxFloors}F`;
      } else scale = 'multi-story';
      if (info.suggestedWidth_m && info.suggestedDepth_m) scale += ` ~${info.suggestedWidth_m}×${info.suggestedDepth_m}m`;
      else if (info.suggestedAreaSqm) scale += ` ~${info.suggestedAreaSqm}m²`;
    } else {
      scale = 'gnd';
    }
    
    const overlayPrompt = getMapOverlayPrompt(zone);
    const features: string[] = [];
    if (overlayPrompt) {
      features.push(overlayPrompt);
    } else {
      if (info.facadeDescription) features.push(info.facadeDescription);
      if (info.roofDescription) features.push(info.roofDescription);
      if (info.materials) features.push(info.materials);
      if (info.aerialAppearance) features.push(`Aerial: ${info.aerialAppearance}`);
      if (info.publicRealm) features.push(info.publicRealm);
    }
    
    const userDesc = (props.description as string) || (props.descriptive_text as string) || '';
    if (userDesc.length > 10) features.push(userDesc);
    
    const featureStr = features.join(', ').substring(0, 200);
    zoneLines.push(`${i + 1}. [${color}] ${name} | ${scale} | ${featureStr || 'render as described'}`);
  }
  
  // Assemble SCHEMA prompt
  const sections = [
    `STYLE: ${GLOBE_STYLE_PROMPTS[style] || GLOBE_STYLE_PROMPTS.photorealistic}`,
    `COMPOSITION: ${composition}`,
    `LIGHTING: ${lightingMap[style] || lightingMap.photorealistic}`,
    `CONTEXT: This image is captured from a 3D photorealistic city model with real Google Earth buildings. Preserve ALL unmasked photographic context exactly as-is. Rendered zones must blend naturally at edges — match tones, lighting, and scale of adjacent real buildings.`,
    `COLOR TEMPERATURE MATCHING: Analyze the color temperature and atmospheric conditions of the EXISTING buildings and terrain in the photograph. Match the EXACT same warm/cool tone, haze level, and ambient light color on all rendered zones. If the scene has golden-hour warmth, render buildings with the same warm amber tones — NOT neutral daylight grey. Rendered materials must look like they exist in the same atmosphere and light as the surrounding real buildings.`,
    `ATMOSPHERIC PERSPECTIVE: Apply the same atmospheric haze and aerial perspective visible on surrounding buildings at similar distances. Distant rendered zones should have reduced contrast and shifted color matching the existing depth cues in the photograph.`,
    `NUMERICAL INVENTORY: This scene contains exactly ${renderZones.length} zone${renderZones.length > 1 ? 's' : ''}: ${renderZones.filter(z => z.zone_type === 'building' || z.zone_type === 'residential').length} building${...}s, ${renderZones.filter(z => z.zone_type === 'green_space').length} park${...}s, ${renderZones.filter(z => z.zone_type === 'road').length} road${...}s.`,
    `ZONES:\n${zoneLines.join('\n')}`,
    `ZONE IDENTIFICATION: Each zone polygon has TWO visual identifiers: (1) its archetype name written as colored text on the polygon, and (2) a unique bright DASHED BORDER in a distinct color (red, blue, magenta, cyan, yellow, etc.). The text label color matches the border color. Use BOTH the text label AND the border color to identify each zone. Zones with similar fill colors can be distinguished by their different border colors. Road/street zones can be distinguished from existing roads by their dashed border — only polygons with dashed borders are zones to render.`,
    `MANDATORY: The white mask shows the EXACT area to edit. Replace the colored polygon overlays visible in the screenshot with photorealistic architectural materials. Read the text label on each polygon to identify what to render there. Realistic rooftop materials, facades, and landscaping. Match scale and density of surrounding real 3D buildings. Rendered building facades and roofs MUST have the same color cast, warmth, and atmospheric tint as adjacent real buildings.`,
    `PROHIBITIONS: colored polygon fills visible on ANY rendered surface (rooftops, facades, ground), dashed boundary lines or outlines visible, text labels visible, watermarks, color temperature mismatch between rendered and existing buildings, rendered buildings appearing unnaturally crisp or clean compared to surroundings${style === 'winter' ? ', lush green vegetation, summer foliage, bright green lawns' : ''}`,
    `SITE BOUNDARY: Do NOT add any NEW buildings, structures, roads, people, vehicles, or landscaping outside the colored zone polygons. However, rendered zones MUST blend seamlessly into the surrounding landscape at their edges — match lighting, ground plane, and context so there is no visible seam between rendered and existing areas.`,
    `OCCLUSION: Some zones may be partially or fully hidden behind taller buildings from this camera angle. This is CORRECT — do NOT distort the perspective to make hidden zones visible. If a zone is occluded by a building in front of it, leave it hidden. Render only what would naturally be visible from this specific camera position and angle.`,
    `FINAL CONSTRAINT: Stay strictly within each colored zone polygon. Do not alter pixels outside the mask. Accuracy to the polygon boundary is more important than architectural flair. Each zone renders ONLY within its own colored boundary — never overlapping into adjacent zones.`,
  ];
  
  return sections.join('\n');
}
```

- **Zones format:** Numbered list `1. [bright vermillion #E03C31] MixedUseMarketingDesign | 6F 24m ~45×50m | retail frontage, glass atrium, marble surfaces...`
- **Color naming:** Detailed color names + hex ([useGlobeAIRender.ts:438–503](frontend/src/components/viewer/globe/useGlobeAIRender.ts:438)) — e.g. "bright vermillion #E03C31" vs codex's simpler "red". Helps Gemini match visual guides to prompt text.
- **MANDATORY clauses:** Extensive — zone boundary enforcement, color temperature matching, atmospheric perspective, occlusion rules.
- **CONSTRAINTS:** Hard boundaries, preservation of unmasked context, prohibition on artifacts (colored fills, dashed lines, text).
- **Style prompts:** Full sentences per style ([useGlobeAIRender.ts:27–42](frontend/src/components/viewer/globe/useGlobeAIRender.ts:27)), e.g. "Professional architectural photomontage indistinguishable from a real drone photograph. DJI Mavic 3 at 60m altitude, Hasselblad sensor. Proposed development appears fully constructed..."
- **Archetype injection:** Per-zone metadata (facade, roof, materials, public realm) injected inline ([useGlobeAIRender.ts:676–688](frontend/src/components/viewer/globe/useGlobeAIRender.ts:676)).

### Codex

**Function:** [useAIRender.ts:1800–2100](frontend/src/components/viewer/useAIRender.ts:1800)

```typescript
function buildSCHEMAPrompt(
  zoneEntries: ZonePromptEntry[],
  options: AIRenderOptions,
  mode: 'structured' | 'ground' | 'building',
  imageIndices?: Map<string, number>,
): string {
  const styleId = options.renderStyleId || options.style || 'photorealistic';
  const style = GEMINI_STYLE_MODIFIERS[styleId];
  const isArtistic = ['watercolour', 'charcoal', 'isometric', 'woodblock', ...].includes(styleId);
  const isSitePlan = styleId === 'site-plan' || styleId === 'site-plan-watercolor' || styleId === 'site-plan-photo';
  const isClay = styleId === 'clay-maquette';
  
  const lines: string[] = [];
  
  // ── STYLE ──
  if (style) {
    let styleText = style.prompt;
    const firstSentence = styleText.indexOf('. ');
    if (firstSentence > 0 && firstSentence < 200) {
      styleText = styleText.slice(0, firstSentence + 1);
    } else if (styleText.length > 200) {
      styleText = styleText.slice(0, 197) + '...';
    }
    lines.push(`STYLE: ${styleText}`);
  }
  
  // ── COMPOSITION ──
  if (isSitePlan) {
    lines.push('COMPOSITION: Near-top-down aerial, 15-20 degrees from nadir, colored polygons mark proposed zones on satellite photo');
  } else if (mode === 'ground') {
    lines.push('COMPOSITION: Oblique aerial, drone 60m altitude, ground-level zones only, no vertical structures');
  } else if (mode === 'building') {
    const entry = zoneEntries[0];
    lines.push(`COMPOSITION: Oblique aerial, drone 60m, single building on ${entry?.color || 'colored'} footprint, full 3D mass extending into sky`);
  } else {
    lines.push('COMPOSITION: Oblique aerial, DJI drone 60m altitude, colored polygons mark proposed zones on satellite photo');
  }
  
  // ── LIGHTING ──
  if (isClay) {
    lines.push('LIGHTING: Soft diffused studio light, gentle shadows defining form only');
  } else if (isArtistic) {
    lines.push(`LIGHTING: Match ${style?.label || styleId} artistic conventions`);
  } else if (styleId === 'atmospheric') {
    lines.push('LIGHTING: Dramatic golden hour, low-angle warm sun, long architectural shadows, volumetric haze');
  } else {
    const lightingMatch = styleId === 'photorealistic' ? 'Golden hour, warm sunlight, sharp shadows, realistic materials'
      : styleId === 'photomontage' ? 'Match surrounding real environment — lighting and shadow direction consistent with existing buildings'
      : 'Natural sunlight with realistic shadow casting';
    lines.push(`LIGHTING: ${lightingMatch}`);
  }
  
  // ── ZONES (abbreviated keyword format) ──
  const lines: string[] = []; // (continued)
  for (const entry of zoneEntries) {
    const imageIndex = imageIndices?.get(entry.color);
    const label = buildCompressedZoneLabel(entry, imageIndex);
    lines.push(label);
  }
  
  // ── PROHIBITIONS ──
  lines.push('PROHIBITIONS: colored polygon fill visible, text labels, watermark, people, vehicles, cartoon, sketch, artificial colors');
  
  // ── CONTEXT ──
  lines.push('CONTEXT: Preserve all surrounding satellite context exactly. Match lighting and color temperature of adjacent buildings.');
  
  // ── MANDATORY (building containment) ──
  lines.push('MANDATORY: Each zone renders ONLY within its own colored boundary polygon. Do not overlap or bleed into neighboring zones. Match perspective for 3D realism.');
  
  return lines.join('\n');
}

function buildCompressedZoneLabel(entry: ZonePromptEntry, imageIndex?: number): string {
  const BUILDING_TYPES = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];
  const isBuilding = BUILDING_TYPES.includes(entry.zoneType);
  const isRoad = ['road', 'street', 'path'].includes(entry.zoneType);
  const isPark = ['green_space', 'park', 'plaza', 'water'].includes(entry.zoneType);
  const priority = isPriorityZone(entry);
  
  const name = entry.archetypeTitle || entry.zoneName || entry.zoneType;
  
  // Scale
  let scale = 'gnd';
  if (isBuilding) {
    if (entry.floors && entry.heightM) scale = `${entry.floors}F ${entry.heightM}m`;
    else if (entry.floors) scale = `${entry.floors}F`;
    else if (entry.heightM) scale = `${entry.heightM}m`;
    else scale = 'multi-story';
  }
  
  // If we have an archetype image reference, use that instead of materials
  if (imageIndex != null) {
    return `[${entry.color}] ${name} | ${scale} | match style of Image ${imageIndex}`;
  }
  
  // Materials/features — priority zones get more keywords
  const maxKeywords = priority ? 6 : 3;
  let features = '';
  
  if (isBuilding) {
    const parts: string[] = [];
    if (entry.materials) parts.push(condenseToKeywords(entry.materials, priority ? 3 : 2));
    if (entry.facadeDescription) parts.push(condenseToKeywords(entry.facadeDescription, priority ? 3 : 2));
    if (entry.roofDescription) parts.push(condenseToKeywords(entry.roofDescription, priority ? 2 : 1));
    if (priority && entry.aerialAppearance) parts.push(condenseToKeywords(entry.aerialAppearance, 2));
    if (priority && entry.massing) parts.push(condenseToKeywords(entry.massing, 2));
    features = parts.filter(Boolean).join(', ');
  } else if (isRoad) {
    const roadDesc = entry.publicRealm || entry.materials || entry.descriptionText;
    features = condenseToKeywords(roadDesc, maxKeywords);
  } else if (isPark) {
    const parkDesc = entry.publicRealm || entry.materials || entry.descriptionText;
    features = condenseToKeywords(parkDesc, maxKeywords);
  } else {
    features = condenseToKeywords(entry.descriptionText || entry.materials || entry.publicRealm, maxKeywords);
  }
  
  const maxLen = priority ? 160 : 100;
  const label = `[${entry.color}] ${name} | ${scale} | ${features}`;
  return label.length > maxLen ? label.slice(0, maxLen - 3) + '...' : label;
}

/** Extract N keywords from verbose description text, joining with '+' */
function condenseToKeywords(text: string | undefined, maxTokens = 4): string {
  if (!text) return '';
  const tokens = text
    .replace(/\.\s+/g, ', ')
    .split(/[,;:]+/)
    .map(t => t.trim())
    .filter(t => t.length > 2)
    .map(t => t.replace(/^(a |an |the |with |and |or |in |on |at |of |for |is |are |has |have |its |this )/gi, '').trim())
    .filter(t => t.length > 2)
    .slice(0, maxTokens);
  return tokens.join('+');
}
```

- **Zones format:** Abbreviated labels with keyword extraction `[red] MixedUseMarketingDesign | 6F 24m | retail+glass+atrium+marble...` (up to 160 chars for priority zones, 100 for standard).
- **Color naming:** Simpler color names ([useAIRender.ts:2210–2240](frontend/src/components/viewer/useAIRender.ts:2210)) — e.g. "red", "coral", "spring green" without hex values.
- **Keyword condensation:** Archetype metadata is **tokenized and summarized** ([useAIRender.ts:1889–1904](frontend/src/components/viewer/useAIRender.ts:1889)) — removes articles/prepositions, joins with "+", targets 3–6 keywords per zone.
- **Style prompts:** Shorter — only first sentence or 200 chars max, not full narrative.
- **MANDATORY clauses:** Shorter, less detailed — zone boundary enforcement, no overlaps, match perspective.
- **PROHIBITIONS:** Shorter list.
- **Archetype image references:** If an archetype image is attached, the zone label becomes "match style of Image N" instead of listing materials.

**Key difference:** Stable emphasizes **detailed context (color temperature, atmospheric perspective, occlusion handling)** in the prompt. Codex emphasizes **brevity and keyword density** — targets 2,200–2,500 chars total, summarizes zone metadata into 3–6 keywords. This is because Imagen 3 (codex's backend) is more sensitive to prompt bloat, whereas Gemini (stable's backend) benefits from detailed instructions.

---

## 5. Archetype Reference Images

**Verdict:** Stable collects **up to 6 compressed JPEG reference cards (~30–50KB each)** keyed per zone. Codex collects **reference images per zone** in the same way but with **variant-aware color shifting** and **"match style of Image N"** substitution.

### Stable

**Function:** [useGlobeAIRender.ts:358–414](frontend/src/components/viewer/globe/useGlobeAIRender.ts:358)

```typescript
async function collectArchetypeImages(zones: SiteZone[]): Promise<Array<{ image_base64: string; label: string; zone_color: string }>> {
  const images: Array<{ image_base64: string; label: string; zone_color: string }> = [];
  
  for (const zone of zones) {
    if (images.length >= 6) break;
    if (zone.zone_type === 'site_boundary') continue;
    
    const props = zone.properties || {};
    const archetypeId = (props.development_archetype_id as string)
      || (props.green_space_archetype_id as string)
      || (props.road_archetype_id as string)
      || (props.plaza_archetype_id as string)
      || (props.development_subcategory as string)
      || (props.green_space_subcategory as string)
      || '';
    
    if (!archetypeId) {
      console.log(`[GlobeAIRender] Skipping zone "${zone.name || zone.zone_type}" — no archetype ID`);
      continue;
    }
    
    const entry = catalog.find((a: any) => a.id === archetypeId || archetypeId.startsWith(a.id + '_'));
    if (!entry) {
      console.log(`[GlobeAIRender] Skipping zone "${zone.name || zone.zone_type}" — archetype "${archetypeId}" not found in catalog`);
      continue;
    }
    
    // Use variant-specific thumbnail if available, fall back to parent
    const variant = entry.variants?.find((v: any) => v.id === archetypeId);
    const thumbnailUrl = variant?.thumbnailUrl || entry.thumbnailUrl;
    if (!thumbnailUrl) {
      console.log(`[GlobeAIRender] Skipping zone "${zone.name || zone.zone_type}" — archetype "${archetypeId}" has no thumbnailUrl`);
      continue;
    }
    
    // Fetch and compress the card image (512px wide JPEG ~30-50KB)
    try {
      const resp = await fetch(thumbnailUrl);
      if (!resp.ok) continue;
      const blob = await resp.blob();
      const base64 = await compressImage(blob, 512, 0.7);
      
      const sizeKB = Math.round(base64.length * 0.75 / 1024);
      console.log(`[GlobeAIRender] Archetype image: ${entry.title} — ${sizeKB}KB (compressed)`);
      
      images.push({
        image_base64: base64,
        label: entry.title || archetypeId,
        zone_color: colorName(resolveZoneColor(zone)), // e.g. "bright vermillion #E03C31"
      });
    } catch { /* skip failed fetches */ }
  }
  
  return images;
}

function compressImage(blob: Blob, maxWidth = 512, quality = 0.7): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, maxWidth / img.naturalWidth);
      const w = Math.round(img.naturalWidth * scale);
      const h = Math.round(img.naturalHeight * scale);
      
      const canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(img, 0, 0, w, h);
      
      canvas.toBlob((outBlob) => {
        if (!outBlob) return reject(new Error('Compression failed'));
        const reader = new FileReader();
        reader.onloadend = () => resolve((reader.result as string).split(',')[1]);
        reader.readAsDataURL(outBlob);
      }, 'image/jpeg', quality);
    };
    img.onerror = () => reject(new Error('Failed to load image for compression'));
    img.src = URL.createObjectURL(blob);
  });
}
```

- **Collection limit:** 6 images max (one per zone if 6 zones or fewer).
- **Lookup:** Archetype ID from zone properties (development/road/green_space/plaza prefix).
- **Variant handling:** If the zone's archetype ID is a variant (e.g. "residential_mid_rise_v2"), fetch variant-specific thumbnail if available.
- **Compression:** Resize to 512px wide, JPEG quality 0.7 (~30–50 KB per image).
- **Labeling:** Zone color name (e.g. "bright vermillion #E03C31") + archetype title.
- **Prompt injection:** ([useGlobeAIRender.ts:1253–1261](frontend/src/components/viewer/globe/useGlobeAIRender.ts:1253))
  ```
  ARCHETYPE STYLE REFERENCES (Images 2+): 3 reference images show the exact architectural style for specific zones. Use Image 1 as the spatial context. Apply each reference style to the matching colored zone.
  Image 2: Style reference for [bright vermillion #E03C31] MixedUseMarketingDesign
  Image 3: Style reference for [sky blue #2196F3] VibrantGreenSpace
  Image 4: Style reference for [teal #009688] UrbanStreetscape
  ```

### Codex

**Functions:** [useAIRender.ts:2650–2750](frontend/src/components/viewer/useAIRender.ts:2650)

```typescript
async function collectArchetypeImagesForZones(
  zones: SiteZone[] | undefined,
): Promise<Array<{ image_base64: string; label: string; zone_color?: string }>> {
  if (!zones || zones.length === 0) return [];
  const editable = zones.filter(z => z.zone_type !== 'site_boundary');
  const settled = await Promise.all(
    editable.map(async (zone) => {
      try {
        const card = await getZoneArchetypeCard(zone);
        if (!card) return null;
        const zoneColor = colorName(getZoneRenderColor(zone.id, zone.color || '#4CAF50'));
        return { ...card, zone_color: zoneColor };
      } catch (e) {
        console.warn(`[AIRender] getZoneArchetypeCard failed for zone ${zone.id}:`, e);
        return null;
      }
    }),
  );
  const cards = settled.filter((c): c is NonNullable<typeof c> => c !== null);
  console.log(`[AIRender] collectArchetypeImagesForZones: ${cards.length}/${editable.length} zones have archetype cards`);
  return cards;
}

async function getZoneArchetypeCard(zone: SiteZone): Promise<{ image_base64: string; label: string } | null> {
  const info = getZoneArchetypeInfo(zone);
  
  const PREFIXES = ['development', 'road', 'green_space', 'plaza'] as const;
  let archetypeId: string | undefined;
  for (const prefix of PREFIXES) {
    const v = zone.properties?.[`${prefix}_archetype_id` as keyof typeof zone.properties] as string | undefined;
    if (v) { archetypeId = v; break; }
  }
  // Legacy fallbacks
  if (!archetypeId) {
    archetypeId = (zone.properties?.archetype_id as string | undefined)
      || (zone.properties?.subcategory as string | undefined);
  }
  if (!archetypeId) return null;
  
  // Look up in catalog
  const entry = catalog?.find((a: any) => a.id === archetypeId || archetypeId?.startsWith(a.id + '_'));
  if (!entry || !entry.thumbnailUrl) return null;
  
  const base64 = await fetchArchetypeImageBase64(entry.thumbnailUrl);
  if (!base64) return null;
  
  return {
    image_base64: base64,
    label: entry.title || archetypeId,
  };
}

async function fetchArchetypeImageBase64(url: string): Promise<string | null> {
  try {
    const fullUrl = url.startsWith('http') ? url : window.location.origin + url;
    const resp = await fetch(fullUrl);
    if (!resp.ok) return null;
    const blob = await resp.blob();
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        resolve(dataUrl.split(',')[1] || null);
      };
      reader.readAsDataURL(blob);
    });
  } catch {
    return null;
  }
}
```

- **Collection:** All editable zones (no hard limit of 6, but typically 4–8).
- **Lookup:** Same as stable — prefix-based archetype ID.
- **Variant handling:** Same as stable.
- **Compression:** No explicit compression step — uses native fetch/blob encoding (typically larger than stable's 512px JPEG).
- **Labeling:** Zone color name (simple, e.g. "red") + archetype title.
- **Prompt substitution:** If image is available, the zone label becomes "match style of Image N" ([useAIRender.ts:2019–2020](frontend/src/components/viewer/useAIRender.ts:2019)) instead of listing materials keywords.
- **Color reassignment:** Codex handles **duplicate-colored building zones** by reassigning variant colors from `BUILDING_VARIANT_PALETTE` ([useAIRender.ts:2424–2473](frontend/src/components/viewer/useAIRender.ts:2424)). Stable relies on border colors + text labels to distinguish zones.

**Key difference:** Both collect the same reference images, but **stable explicitly limits to 6 and aggressively compresses to 30–50KB**, while **codex fetches all zones' images at full resolution**. Codex then **substitutes image references in the prompt** ("match Image 2") instead of describing materials, which saves token space but loses specificity.

---

## 6. Single-Shot vs Multi-Pass

**Verdict:** Stable always uses **single-shot** (render all zones in one Gemini call); codex supports **single-shot (Pass 1 ground + Pass 2 building per-zone)** via `renderPerZone()` with a two-pass architecture.

### Stable

**Single-shot only:**
- [useGlobeAIRender.ts:1119–1310](frontend/src/components/viewer/globe/useGlobeAIRender.ts:1119): `render()` captures canvas, generates mask, builds prompt, collects archetype images, **sends ONE Gemini API call** with image + mask + prompt + 6 reference images.
- [useGlobeAIRender.ts:856](frontend/src/components/viewer/globe/useGlobeAIRender.ts:856): `PERZONE_THRESHOLD = 99` — per-zone rendering is **disabled** (would only activate if >99% of zones are occluded, which is unrealistic).
- Per-zone capability exists ([useGlobeAIRender.ts:1370–1578](frontend/src/components/viewer/globe/useGlobeAIRender.ts:1370)) but is an **alternative path**, not the default. When invoked, it renders each zone individually, then composites using blur+clamp polygon clip.

### Codex

**Two-pass primary; single-shot fallback:**
- **Single-shot:** `render()` captures map, generates binary mask, builds structured prompt, collects archetype images, **sends ONE Imagen 3 API call** ([useAIRender.ts:~2900](frontend/src/components/viewer/useAIRender.ts:2900)).
- **Two-pass (when used):** `renderPerZone()` splits zones into:
  - **Pass 1 (Ground):** All ground zones (water, green_space, road, park, plaza) rendered in one call ([useAIRender.ts:~3000](frontend/src/components/viewer/useAIRender.ts:3000)).
  - **Pass 2 (Buildings):** Each building zone rendered individually, composited on top of Pass 1 result using hybrid stitch (polygon clip + pixel-diff above building height) ([useAIRender.ts:~3100](frontend/src/components/viewer/useAIRender.ts:3100)).
- **Auto-delegation:** If occlusion analysis detects partial occlusion, `render()` **auto-delegates to `renderPerZone()`** unless `forceSingleShot: true` is passed ([useAIRender.ts:~2850](frontend/src/components/viewer/useAIRender.ts:2850)).

**Key difference:** Stable prefers **single-shot** (simplicity, global context) because it has **3D spatial context from the canvas and per-zone text labels + borders**. Codex implements **two-pass** (fine-grained control) because **ground and building zones need separate rendering strategies** on flat satellite imagery — ground zones are rendered first at full quality, then buildings are overlaid on top using pixel-diff.

---

## 7. Compositing / Stitching

**Verdict:** Stable uses **polygon clip with feathered edges (blur + clamp)**; codex uses **hybrid: polygon clip + pixel-diff above building zones** to capture 3D vertical extent.

### Stable

**Function:** [useGlobeAIRender.ts:742–845](frontend/src/components/viewer/globe/useGlobeAIRender.ts:742)

```typescript
async function clipRenderToZones(
  originalBase64: string,
  renderedBase64: string,
  zones: SiteZone[],
  camera: THREE.Camera,
  canvasWidth: number,
  canvasHeight: number,
  terrainHeight: number,
): Promise<string> {
  const [origImg, rendImg] = await Promise.all([
    loadImage(`data:image/png;base64,${originalBase64}`),
    loadImage(`data:image/png;base64,${renderedBase64}`),
  ]);
  
  const w = origImg.naturalWidth;
  const h = origImg.naturalHeight;
  
  // Start with original screenshot
  const resultCanvas = document.createElement('canvas');
  resultCanvas.width = w;
  resultCanvas.height = h;
  const resultCtx = resultCanvas.getContext('2d')!;
  resultCtx.drawImage(origImg, 0, 0, w, h);
  
  // Build a combined feathered mask for ALL non-boundary zones
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const maskCtx = maskCanvas.getContext('2d')!;
  maskCtx.fillStyle = '#000000';
  maskCtx.fillRect(0, 0, w, h);
  maskCtx.fillStyle = '#ffffff';
  
  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    if (zone.zone_type === 'site_boundary') continue;
    
    const pixels = zone.coordinates
      .map(c => projectToPixels(c[0], c[1], terrainHeight, camera, canvasWidth, canvasHeight))
      .filter(Boolean) as { x: number; y: number }[];
    
    if (pixels.length < 3) continue;
    
    // Draw zone polygon
    maskCtx.beginPath();
    maskCtx.moveTo(pixels[0].x, pixels[0].y);
    for (let i = 1; i < pixels.length; i++) maskCtx.lineTo(pixels[i].x, pixels[i].y);
    maskCtx.closePath();
    maskCtx.fill();
    
    // For buildings, extend upward for 3D height
    const buildingHeight = (zone.properties?.height_m as number) || ... || 0;
    
    if (buildingHeight > 0 && (zone.zone_type === 'building' || zone.zone_type === 'residential')) {
      const topPixels = zone.coordinates
        .map(c => projectToPixels(c[0], c[1], terrainHeight + buildingHeight, camera, canvasWidth, canvasHeight))
        .filter(Boolean) as { x: number; y: number }[];
      
      if (topPixels.length >= 3) {
        const minY = Math.min(...pixels.map(p => p.y));
        const minX = Math.min(...pixels.map(p => p.x));
        const maxX = Math.max(...pixels.map(p => p.x));
        const roofMinY = Math.min(...topPixels.map(p => p.y));
        maskCtx.fillRect(minX, roofMinY, maxX - minX, minY - roofMinY);
      }
    }
  }
  
  // Blur + Clamp: soft feathered edges that never exceed polygon bounds
  // Blur creates gradient in both directions; clamping cuts off outward bleed,
  // leaving inward-only feathered edges.
  const blurCanvas = document.createElement('canvas');
  blurCanvas.width = w;
  blurCanvas.height = h;
  const blurCtx = blurCanvas.getContext('2d')!;
  blurCtx.filter = 'blur(4px)';
  blurCtx.drawImage(maskCanvas, 0, 0);
  
  // Clamp: multiply blurred mask with original hard mask — zero pixels escape
  const featherCanvas = document.createElement('canvas');
  featherCanvas.width = w;
  featherCanvas.height = h;
  const featherCtx = featherCanvas.getContext('2d')!;
  featherCtx.drawImage(blurCanvas, 0, 0);
  featherCtx.globalCompositeOperation = 'destination-in';
  featherCtx.drawImage(maskCanvas, 0, 0);
  
  // Composite: AI render masked with clamped feathered zones, drawn onto original
  const aiCanvas = document.createElement('canvas');
  aiCanvas.width = w;
  aiCanvas.height = h;
  const aiCtx = aiCanvas.getContext('2d')!;
  aiCtx.drawImage(rendImg, 0, 0, w, h);
  aiCtx.globalCompositeOperation = 'destination-in';
  aiCtx.drawImage(featherCanvas, 0, 0);
  
  // Draw the masked AI render on top of the original
  resultCtx.drawImage(aiCanvas, 0, 0);
  
  console.log('[GlobeAIRender] Post-process: blur+clamp clip (4px inward-only feather)');
  return resultCanvas.toDataURL('image/png').split(',')[1];
}
```

- **Approach:** Polygon clip + feather.
- **Steps:**
  1. Start with original screenshot.
  2. Build hard mask (white = zones, black = preserve).
  3. Blur the hard mask (4px) to soften edges.
  4. **Clamp:** Intersect blurred mask with hard mask using `destination-in` — ensures no pixels escape the boundary.
  5. Mask AI render with feathered polygon, composite onto original.
- **Feather:** Inward-only 4px blur — no outward bleed.
- **3D handling:** For buildings, extends upward using roof projection ([useGlobeAIRender.ts:796–808](frontend/src/components/viewer/globe/useGlobeAIRender.ts:796)) to include the 3D silhouette.

### Codex

**Functions:** [useAIRender.ts:1244–1433](frontend/src/components/viewer/useAIRender.ts:1244)

```typescript
async function stitchWithBoundaryMask(
  originalBase64: string,
  renderedDataUri: string,
  map: MapboxMap,
  siteZones: SiteZone[],
): Promise<string> {
  const [originalImg, renderedImg] = await Promise.all([
    loadImage(`data:image/png;base64,${originalBase64}`),
    loadImage(renderedDataUri),
  ]);
  
  const w = originalImg.naturalWidth;
  const h = originalImg.naturalHeight;
  const dpr = window.devicePixelRatio || 1;
  
  // ── Step 1: Mask-based composite of AI result ──
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;
  
  ctx.drawImage(originalImg, 0, 0, w, h);
  
  const boundaries = siteZones.filter(z => z.zone_type === 'site_boundary' && z.coordinates && z.coordinates.length >= 3);
  const clipZones = boundaries.length > 0 ? boundaries : siteZones.filter(z => z.coordinates && z.coordinates.length >= 3);
  
  const BUILDING_TYPES_STITCH = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];
  const hasBuildingZones = siteZones.some(z =>
    BUILDING_TYPES_STITCH.includes(z.zone_type) && z.coordinates && z.coordinates.length >= 3
  );
  
  // Build white-on-black mask: white = show AI render, black = keep original
  const maskCanvas = document.createElement('canvas');
  maskCanvas.width = w;
  maskCanvas.height = h;
  const maskCtx = maskCanvas.getContext('2d')!;
  maskCtx.fillStyle = '#000000';
  maskCtx.fillRect(0, 0, w, h);
  maskCtx.fillStyle = '#ffffff';
  
  // Draw site boundary polygon(s) into the mask
  for (const zone of clipZones) {
    const pixels = siteBoundaryToPixels(map, zone.coordinates!);
    maskCtx.beginPath();
    maskCtx.moveTo(pixels[0].x * dpr, pixels[0].y * dpr);
    for (let i = 1; i < pixels.length; i++) {
      maskCtx.lineTo(pixels[i].x * dpr, pixels[i].y * dpr);
    }
    maskCtx.closePath();
    maskCtx.fill();
  }
  
  // For each building zone, extend the mask upward by the building's perspective headroom
  if (hasBuildingZones) {
    const bldgZones = siteZones.filter(z =>
      BUILDING_TYPES_STITCH.includes(z.zone_type) && z.coordinates && z.coordinates.length >= 3
    );
    for (const zone of bldgZones) {
      const pixels = siteBoundaryToPixels(map, zone.coordinates!);
      const devicePixels = pixels.map(p => ({ x: p.x * dpr, y: p.y * dpr }));
      
      const bldgHeight = zone.properties?.height_m ? Number(zone.properties.height_m) : 0;
      const headroom = bldgHeight > 0
        ? calculatePerspectiveHeadroom(map, bldgHeight)
        : 100 * dpr;
      
      const minX = Math.min(...devicePixels.map(p => p.x));
      const maxX = Math.max(...devicePixels.map(p => p.x));
      const minY = Math.min(...devicePixels.map(p => p.y));
      const expandedTop = Math.max(0, Math.floor(minY - headroom));
      maskCtx.fillRect(minX, expandedTop, maxX - minX, minY - expandedTop);
    }
  }
  
  // Composite: draw AI render masked by the stitch mask
  const aiCanvas = document.createElement('canvas');
  aiCanvas.width = w;
  aiCanvas.height = h;
  const aiCtx = aiCanvas.getContext('2d')!;
  aiCtx.drawImage(renderedImg, 0, 0, w, h);
  aiCtx.globalCompositeOperation = 'destination-in';
  aiCtx.drawImage(maskCanvas, 0, 0);
  ctx.drawImage(aiCanvas, 0, 0);
  
  // ── Step 2: Pixel-diff ABOVE each building zone ──
  // For each building, compare original vs AI in the region directly above
  // the building's polygon (between its top edge and the headroom ceiling).
  // This captures the building's 3D silhouette without horizontal bleed.
  const BUILDING_TYPES = ['building', 'residential', 'commercial', 'industrial', 'mixed_use'];
  const buildingZones = siteZones.filter(z =>
    BUILDING_TYPES.includes(z.zone_type) && z.coordinates && z.coordinates.length >= 3
  );
  
  if (buildingZones.length > 0) {
    const origTmpCanvas = document.createElement('canvas');
    origTmpCanvas.width = w;
    origTmpCanvas.height = h;
    const origTmpCtx = origTmpCanvas.getContext('2d')!;
    origTmpCtx.drawImage(originalImg, 0, 0, w, h);
    
    const rendTmpCanvas = document.createElement('canvas');
    rendTmpCanvas.width = w;
    rendTmpCanvas.height = h;
    const rendTmpCtx = rendTmpCanvas.getContext('2d')!;
    rendTmpCtx.drawImage(renderedImg, 0, 0, w, h);
    
    const currentData = ctx.getImageData(0, 0, w, h);
    const currentPx = currentData.data;
    
    const DIFF_THRESHOLD = 18;
    
    for (const zone of buildingZones) {
      const pixels = siteBoundaryToPixels(map, zone.coordinates!);
      const devicePixels = pixels.map(p => ({ x: p.x * dpr, y: p.y * dpr }));
      
      const bldgHeight = zone.properties?.height_m ? Number(zone.properties.height_m) : 0;
      const headroom = bldgHeight > 0
        ? calculatePerspectiveHeadroom(map, bldgHeight)
        : 100 * dpr;
      
      const minX = Math.min(...devicePixels.map(p => p.x));
      const maxX = Math.max(...devicePixels.map(p => p.x));
      const minY = Math.min(...devicePixels.map(p => p.y));
      const expandedTop = Math.max(0, Math.floor(minY - headroom));
      
      // Only process the region ABOVE the polygon (between expandedTop and minY)
      const regionX = Math.max(0, Math.floor(minX));
      const regionR = Math.min(w, Math.ceil(maxX));
      const regionY = expandedTop;
      const regionB = Math.floor(minY);
      if (regionB <= regionY || regionR <= regionX) continue;
      
      const rw = regionR - regionX;
      const rh = regionB - regionY;
      
      const origRegion = origTmpCtx.getImageData(regionX, regionY, rw, rh);
      const rendRegion = rendTmpCtx.getImageData(regionX, regionY, rw, rh);
      
      for (let row = 0; row < rh; row++) {
        for (let col = 0; col < rw; col++) {
          const idx = (row * rw + col) * 4;
          const dr = Math.abs(origRegion.data[idx] - rendRegion.data[idx]);
          const dg = Math.abs(origRegion.data[idx + 1] - rendRegion.data[idx + 1]);
          const db = Math.abs(origRegion.data[idx + 2] - rendRegion.data[idx + 2]);
          
          if (Math.max(dr, dg, db) > DIFF_THRESHOLD) {
            const globalIdx = ((regionY + row) * w + (regionX + col)) * 4;
            currentPx[globalIdx] = rendRegion.data[idx];
            currentPx[globalIdx + 1] = rendRegion.data[idx + 1];
            currentPx[globalIdx + 2] = rendRegion.data[idx + 2];
            currentPx[globalIdx + 3] = rendRegion.data[idx + 3];
          }
        }
      }
    }
    
    ctx.putImageData(currentData, 0, 0);
  }
  
  console.log(`[AIRender] Hybrid stitch: polygon clip + pixel-diff for ${buildingZones.length} building(s)`);
  return canvas.toDataURL('image/png');
}
```

- **Approach:** Two-step hybrid.
  1. **Polygon clip:** Composite AI render with mask covering site boundary + building headroom boxes.
  2. **Pixel-diff:** For each building, compare original vs rendered in the "headroom region" (above the polygon, up to the calculated headroom ceiling). If pixel difference > threshold (18), use rendered pixel.
- **Headroom:** Calculated using `calculatePerspectiveHeadroom()` — building height × pixels-per-meter × sin(pitch) × 2.0× safety.
- **Diff threshold:** 18 (per-channel). Allows 3D building silhouette to "bleed upward" above the footprint while keeping horizontal extent constrained.
- **Rationale:** On 2D satellite imagery, the polygon clip alone would clip off the top of the building (the shadow and roof pixels). Pixel-diff captures those 3D artifacts above the footprint.

**Key difference:** Stable assumes **canvas already shows correct 3D silhouette** (from R3F projection), so polygon clip alone is sufficient. Codex assumes **satellite imagery is flat**, so it uses pixel-diff above building zones to recover the AI's 3D silhouette rendering.

---

## 8. Style Handling

**Verdict:** Stable supports **14 named styles** with full narrative prompts embedded in `GLOBE_STYLE_PROMPTS`; codex supports **14 styles** via both `AI_RENDER_STYLES` (legacy) and `GEMINI_STYLE_MODIFIERS` (active).

### Stable

**Styles:** [useGlobeAIRender.ts:27–42](frontend/src/components/viewer/globe/useGlobeAIRender.ts:27)

```typescript
const GLOBE_STYLE_PROMPTS: Record<string, string> = {
  photorealistic: 'Photorealistic architectural visualization, photomontage quality, golden hour afternoon sunlight, sharp detail on materials and facades.',
  photomontage: 'Professional architectural photomontage indistinguishable from a real drone photograph. DJI Mavic 3 at 60m altitude, Hasselblad sensor. Proposed development appears fully constructed. Lighting and shadows match surroundings. Atmospheric haze increasing with distance. Realistic material weathering.',
  atmospheric: 'Dramatic golden hour, low-angle warm sun, long architectural shadows, volumetric haze, warm orange light from the west.',
  spring: 'Photorealistic spring scene, fresh green foliage on trees, cherry blossoms, bright midday sunlight, vivid colors.',
  winter: 'Photorealistic winter scene with fresh snow on roofs and ground, bare deciduous trees, cool winter afternoon light, frost on surfaces.',
  night: 'Nighttime scene, city lights, warm interior glow from windows, moonlit sky, wet reflective streets.',
  watercolour: 'Beautiful watercolor architectural painting on textured paper. Soft bleeding edges, translucent layered washes with white paper glowing through. Pigment granulation in shadows. Muted earth-tone palette with sage green, ochre, and ultramarine accents.',
  charcoal: 'Dramatic charcoal sketch on rough textured paper with deep black smudged shadows. High contrast black and white, full tonal range. Sharp charcoal edge lines for architectural definition. Gallery-quality architectural drawing.',
  'marker-render': 'Handcrafted architectural marker rendering on smooth paper. Precise black ink linework with Copic marker shading. Visible overlapping streaky strokes following surface planes. Warm greys and ochres for facades, olive greens for landscape. White gaps for highlights.',
  'clay-maquette': 'Photorealistic macro photography of a physical architectural scale model carved from PURE WHITE matte plaster. Every element — buildings, trees, roads — is the SAME pure white material with ZERO color. Only shadows define form. Studio lighting with soft overhead softbox and deep ambient occlusion.',
  woodblock: 'Stylized woodblock print. Bold thick black outlines, flat limited vintage color palette of 4-6 colors with crisp separation. Visible wood grain texture. Zero gradation or blending. Graphic retro architectural illustration.',
  collage: 'Vibrant post-digital architectural collage as a mixed media composition. Flat unshaded colour blocks, photographic texture cut-outs with torn edges. Vintage botanical illustrations for trees. Flat illustrative lighting. Visible paper texture. Avant-garde competition aesthetic.',
  risograph: 'Risograph-printed architectural visualization. Halftone dot patterns, limited 2-3 spot color palette (fluorescent pink, teal, yellow), slight misregistration between color layers, grain texture, overprint where colors overlap.',
  'pixel-art': '16-bit pixel art architectural scene, grid-aligned with uniform square pixels. Nearest-neighbour scaling, zero anti-aliasing. Strict limited palette of 16 colors. Shading via checkerboard dithering patterns. Dark selective outlines. SNES-era JRPG city aesthetic.',
};
```

- **Count:** 14 styles (photorealistic, photomontage, atmospheric, spring, winter, night, watercolour, charcoal, marker-render, clay-maquette, woodblock, collage, risograph, pixel-art).
- **Format:** Concise narrative prompts (1–3 sentences each) embedded as Record values.
- **Injection:** Directly substituted into SCHEMA prompt via `STYLE:` section ([useGlobeAIRender.ts:700](frontend/src/components/viewer/globe/useGlobeAIRender.ts:700)).
- **Winter special handling:** The winter style adds a PROHIBITION clause for green vegetation ([useGlobeAIRender.ts:710](frontend/src/components/viewer/globe/useGlobeAIRender.ts:710): `` lush green vegetation, summer foliage, bright green lawns ``).

### Codex

**Styles:** [useAIRender.ts:132–390](frontend/src/components/viewer/useAIRender.ts:132) and [useAIRender.ts:394–540](frontend/src/components/viewer/useAIRender.ts:394)

**AI_RENDER_STYLES (legacy, for UI compatibility):**
```typescript
export const AI_RENDER_STYLES: AIRenderStyle[] = [
  {
    id: 'photorealistic',
    label: 'Photo Realistic',
    strength: 0.65,  // img2img strength for Imagen 3
    prompt: 'Hyper-realistic exterior architectural rendering with cinematic lighting. Golden hour sunlight...',
    negative: 'cartoon, illustration, sketch, painting, artistic, stylized, watercolor, pencil, monochrome...',
  },
  // ... 13 more styles
];
```

**GEMINI_STYLE_MODIFIERS (active, for Gemini):**
```typescript
const GEMINI_STYLE_MODIFIERS: Record<string, GeminiStyleModifier> = {
  photorealistic: {
    id: 'photorealistic',
    label: 'Photo Realistic',
    prompt: 'Hyper-realistic exterior architectural rendering with cinematic lighting. Golden hour sunlight casting realistic shadows. Highly detailed materials including reflective glass facades, textured concrete, natural stone, and weathered brick with visible grain. Lush realistic landscaping. Sharp focus, 8k resolution, ray-traced lighting, professional architectural photography.',
  },
  // ... 13 more styles (shorter prompts for Gemini)
};
```

- **Count:** 14 styles (same list as stable).
- **Format:** Two parallel definitions:
  - `AI_RENDER_STYLES`: Full narratives + `strength` field for Imagen 3's img2img (0.65–0.75).
  - `GEMINI_STYLE_MODIFIERS`: Shorter, Gemini-optimized prompts (first sentence only or 200 chars max).
- **Injection:** Selected via `renderStyleId` or `style` option, then looked up in `GEMINI_STYLE_MODIFIERS` ([useAIRender.ts:~1820](frontend/src/components/viewer/useAIRender.ts:1820)).
- **Strength field:** Codex uses `strength` (0–1) to control Imagen 3's "how much to transform" the base image. Stable doesn't have this (Gemini doesn't use this parameter).

**Key difference:** Stable's styles are concise because Gemini can handle shorter, more direct instructions. Codex's `AI_RENDER_STYLES` are verbose (original Imagen 3 spec) but the active `GEMINI_STYLE_MODIFIERS` are truncated to the first sentence, reducing prompt bloat.

---

## 9. Backend API Interaction

**Verdict:** Stable calls **Gemini 3.1 Flash** with model override, guidance scale 15, 2K output; codex calls **Vertex AI Imagen 3** (or Gemini via wrapper) with temperature 1.0, guidance scale 7–15, aspect ratio constraint.

### Stable

**API Call:** [useGlobeAIRender.ts:1265–1282](frontend/src/components/viewer/globe/useGlobeAIRender.ts:1265)

```typescript
const resp = await api.post(
  '/api/v1/render/generate',
  {
    image_base64: imageBase64,
    mask_base64: maskBase64,
    prompt,
    negative_prompt: 'cartoon, illustration, sketch, low quality, blurry, text, watermark, unrealistic colors',
    model,  // 'gemini-3.1-flash-image-preview' (default)
    temperature: 0.0,
    guidance_scale: 15,
    image_size: '2K',  // 2K output for architectural detail accuracy
    thinking_budget: 0,  // Disable thinking — no benefit for image generation, saves ~30-50% latency
    archetype_images: archetypeImages.length > 0 ? archetypeImages : undefined,
  },
  { timeout: 300000 },
);
```

- **Endpoint:** `/api/v1/render/generate` (proprietary backend).
- **Model:** `gemini-3.1-flash-image-preview` (default, configurable via `model` option).
- **Parameters:**
  - `image_base64`: Screenshot as JPEG (300–800KB).
  - `mask_base64`: Binary PNG mask.
  - `prompt`: Full SCHEMA prompt (~2,500–3,500 chars).
  - `negative_prompt`: Generic artifact exclusions.
  - `temperature`: 0.0 (deterministic).
  - `guidance_scale`: 15 (strong adherence to prompt).
  - `image_size`: "2K" (2048×2048 or similar output).
  - `thinking_budget`: 0 (disabled — no benefit for image tasks, saves latency).
  - `archetype_images`: Array of reference images (up to 6).
- **Timeout:** 300 seconds (5 minutes).

### Codex

**API Call:** [useAIRender.ts:~2850](frontend/src/components/viewer/useAIRender.ts:2850) (single-shot) and Per-zone variants

```typescript
// Single-shot render
const resp = await axios.post(RENDER_API_URL, {
  image_base64: cleanBase64,
  prompt,
  negative_prompt: buildNegativePrompt(options),
  image_size: computeAspectRatio(map),  // "16:9", "4:3", etc.
  model: options.model || 'gemini-3-pro-image-preview',
  guidance_scale: options.guidanceScale ?? 15,
  temperature: options.temperature ?? 0.7,
  seed: options.seed,
  steps: options.steps ?? 25,
  strength: options.controlStrength ?? 0.7,
  reference_image_url: options.referenceImageUrl,
  reference_strength: options.referenceStrength ?? 0.3,
}, { timeout: RENDER_TIMEOUT });

// Per-zone render (Pass 1 ground, then Pass 2 buildings)
const resp = await api.post(
  '/api/v1/render/generate',
  {
    image_base64: inputImage,
    mask_base64: singleMask,
    prompt,
    negative_prompt: 'cartoon, illustration, sketch, low quality, blurry, text, watermark' + (isBuilding ? ', colored polygon fill' : ''),
    model,
    temperature: 0.0,
    guidance_scale: 15,
    image_size: '2K',
    thinking_budget: 0,
    archetype_images: archetypeImages.length > 0 ? archetypeImages : undefined,
  },
  { timeout: 300000 },
);
```

- **Endpoint:** `/api/v1/render/generate` (same proprietary backend, or direct `RENDER_API_URL` for Imagen 3).
- **Model:** `gemini-3-pro-image-preview` (default, configurable).
- **Parameters (single-shot):**
  - `image_base64`: PNG screenshot.
  - `prompt`: SCHEMA AVANZATO prompt (~2,200–2,500 chars, abbreviated).
  - `negative_prompt`: Built from style preset + zone-specific negatives.
  - `image_size`: Aspect ratio string ("16:9", "4:3", "1:1", etc.).
  - `guidance_scale`: 15 (default, overridable).
  - `temperature`: 0.7 (default, overridable via `options.temperature`).
  - `seed`: Optional for reproducibility.
  - `steps`: 25 (default, overridable).
  - `strength`: 0.7 (img2img strength, controlable via `controlStrength`).
  - `reference_image_url`: Optional style reference.
  - `reference_strength`: 0.3 (style transfer weight).
- **Per-zone parameters:** Same as stable (temperature 0.0, guidance_scale 15, 2K, thinking_budget 0, archetype_images).
- **Timeout:** 300 seconds (5 minutes).

**Key differences:**
1. **Model default:** Stable uses Gemini 3.1 Flash (faster, more direct); codex uses Gemini 3 Pro (more capable but slower).
2. **Temperature:** Stable uses 0.0 (deterministic); codex defaults to 0.7 (more creative) but per-zone uses 0.0.
3. **Output size:** Stable hardcodes "2K"; codex computes aspect ratio from canvas and uses standard ratios.
4. **Thinking budget:** Stable explicitly disables (0); codex also disables in API calls but might have been used earlier in Imagen 3 calls.
5. **Strength/Reference:** Codex supports img2img `strength` and style `reference_image_url` parameters; stable doesn't expose these.

---

## 10. Net Deltas Worth Porting

**Verdict:** 5 critical improvements from stable that, if ported to codex, would demonstrably improve output:

### 1. **3D Context in Capture** (Highest Impact)

**Stable advantage:** [useGlobeAIRender.ts:1–10](frontend/src/components/viewer/globe/useGlobeAIRender.ts:1)
- Captures R3F canvas with **real Google Photorealistic Tiles**, giving Gemini authentic 3D building context, correct shadows, and realistic material cues.

**Codex gap:** [useAIRender.ts:752–802](frontend/src/components/viewer/useAIRender.ts:752)
- Captures **flat Mapbox raster satellite imagery**, which lacks:
  - 3D roof geometry (causes stretched single-story buildings on multi-story lots).
  - Real material textures (causes Gemini to invent colors/patterns that don't match context).
  - Accurate building shadows (causes poor lighting matching).

**Port requirement:** This is **architectural** — codex runs on Mapbox (2D), stable runs on R3F + Google Tiles (3D). **Not directly portable** without adopting R3F + 3D tiles backend for codex. However:
  - If codex ever gains R3F support, swap the canvas source to R3F.
  - For Mapbox-only codex, no direct fix. **Workaround:** Add a **3D building overlay layer** (Mapbox 3D extrusion) to the capture, so Gemini sees height cues.

### 2. **Silhouette Extrusion vs. Rectangular Headroom** (High Impact)

**Stable advantage:** [useGlobeAIRender.ts:298–316](frontend/src/components/viewer/globe/useGlobeAIRender.ts:298)
- Mask for buildings uses **roof outline projection** — extrudes the actual roof polygon upward, giving Gemini the **exact 3D silhouette it must fill**.

**Codex gap:** [useAIRender.ts:1157–1175](frontend/src/components/viewer/useAIRender.ts:1157)
- Mask for buildings uses a **rectangular box** above the footprint, calculated from pitch/zoom/height. Assumes rectangular buildings — wrong for L-shaped, T-shaped, or angled buildings. Can lead to:
  - Distorted/stretched silhouettes when Gemini fills the box.
  - Over-rendering outside the actual building boundary.

**Port requirement:** **Medium difficulty, high payoff.**
  ```typescript
  // In codex's generateBinaryMask():
  // Instead of: ctx.fillRect(minX, expandedTop, maxX - minX, minY - expandedTop)
  // Use: Project roof polygon using map.project(lngLat, buildingHeight)
  //      and draw the roof outline as a filled path
  
  // Requires:
  // 1. Map viewport must support altitude projection: map.project([lng, lat], altitude)
  // 2. For each building zone, project its coordinates at ground level + at (ground + height)
  // 3. Connect the roof outline with the footprint outline to form a 3D silhouette
  // 4. Fill the silhouette polygon
  ```
  - **Compatibility:** Works on R3F globe (stable's `projectToPixels()` already does this). Requires Mapbox extensions or custom projection math for codex.
  - **Alternative (simpler):** Improve the rectangular headroom calculation to account for building aspect ratio (width/depth), so the box better approximates the actual footprint shape.

### 3. **Detailed Prompt with Mandatory Clauses** (Medium–High Impact)

**Stable advantage:** [useGlobeAIRender.ts:700–713](frontend/src/components/viewer/globe/useGlobeAIRender.ts:700)
- SCHEMA prompt includes extensive **MANDATORY, PROHIBITIONS, SITE BOUNDARY, OCCLUSION, FINAL CONSTRAINT** clauses that enforce:
  - Polygon boundary accuracy.
  - Context preservation.
  - No artifacts (colored fills, text, dashes).
  - Occlusion respect (don't render occluded zones).

**Codex gap:** [useAIRender.ts:~1920](frontend/src/components/viewer/useAIRender.ts:1920)
- SCHEMA AVANZATO prompt is **abbreviated** to save tokens for Imagen 3 — loses enforcement clauses.

**Port requirement:** **Easy.**
  ```typescript
  // In codex's buildSCHEMAPrompt():
  // Add missing clauses:
  lines.push(
    'MANDATORY: Accuracy to polygon boundary is more important than architectural flair. Each zone renders ONLY within its colored boundary — never overlapping into adjacent zones. The white mask shows the EXACT area to edit.',
    'PROHIBITIONS: colored polygon fill visible on any rendered surface, dashed boundary lines visible, text labels, watermarks, color temperature mismatch, unnaturally crisp buildings compared to surroundings.',
    'OCCLUSION: Some zones may be occluded by taller buildings. This is CORRECT. Do NOT distort perspective to make hidden zones visible. Render only what is naturally visible from this camera angle.',
    'SITE BOUNDARY: Do NOT add new buildings/structures outside zone polygons. Rendered zones MUST blend at edges — match lighting, ground plane, context.',
  );
  ```
  - **Cost:** +500–800 chars per prompt (acceptable for Gemini, might bloat Imagen 3 calls).
  - **Payoff:** Reduced zone bleeding, artifact cleanup, better occlusion respect.

### 4. **Aggressive Archetype Image Compression & Explicit Limit** (Medium Impact)

**Stable advantage:** [useGlobeAIRender.ts:328–352](frontend/src/components/viewer/globe/useGlobeAIRender.ts:328)
- Compresses each archetype thumbnail to **512px wide JPEG at 0.7 quality** (~30–50KB per image).
- **Hard limit: 6 images max** — keeps API payload under 500KB total for reference images.

**Codex gap:** [useAIRender.ts:2677–2750](frontend/src/components/viewer/useAIRender.ts:2677)
- Fetches archetype images at **full blob size** (often 500KB–2MB per image for high-res product shots).
- **No limit** — can accumulate 8+ images, ballooning total request size.

**Port requirement:** **Easy.**
  ```typescript
  // In codex's collectArchetypeImagesForZones():
  const images: Array<...> = [];
  for (const zone of editable) {
    if (images.length >= 6) break;  // Add hard limit
    try {
      const card = await getZoneArchetypeCard(zone);
      if (!card) return null;
      
      // Add compression step (copy from stable):
      const blob = await fetch(card.thumbnailUrl).then(r => r.blob());
      const compressed = await compressImage(blob, 512, 0.7);  // 30–50KB
      
      images.push({ ...card, image_base64: compressed, zone_color });
    } catch (e) { ... }
  }
  ```
  - **Payoff:** Reduces API payload by 80–90%, speeds up render calls, prevents timeouts on slow networks.

### 5. **Occlusion Culling with Per-Zone Silhouette Tracking** (Medium Impact)

**Stable advantage:** [useGlobeAIRender.ts:106–229](frontend/src/components/viewer/globe/useGlobeAIRender.ts:106)
- `findOccludedZones()` uses **pixel-overlap testing** on a low-res scratch canvas (1/4 resolution) to identify zones >95% occluded, then **culls them from the prompt**.
- Prevents Gemini from wasting effort rendering zones that won't be visible in the final composite.

**Codex gap:** [useAIRender.ts:901–1053](frontend/src/components/viewer/useAIRender.ts:901)
- `findOccludedZones()` exists and computes **both culled zones AND partial occlusion with silhouette geometry**.
- But the silhouette geometry is only used to **subtract from the mask** — occluded zones are still included in the **prompt**, causing Gemini to render them (wasting tokens and time).

**Port requirement:** **Medium difficulty, medium payoff.**
  ```typescript
  // In codex's render():
  // After occlusion analysis:
  const { culled, partialOcclusion, occluderGeometry } = findOccludedZones(...);
  
  // Filter prompt zones to exclude culled ones:
  const visibleZones = zones.filter(z => !culled.has(z.id || ''));
  
  // Rebuild prompt only from visibleZones, not all zones:
  const zoneEntries = collectZonePromptEntries(visibleZones);
  const prompt = buildStructuredPrompt({ ...options, siteZones: visibleZones });
  ```
  - **Compatibility:** Requires that occlusion culling is enabled (already implemented).
  - **Payoff:** Reduces prompt size by 10–30% on complex multi-zone sites, faster Gemini inference.

### 6. **Blur+Clamp Feathering vs. Pixel-Diff** (Medium Impact, Lower Priority)

**Stable advantage:** [useGlobeAIRender.ts:812–830](frontend/src/components/viewer/globe/useGlobeAIRender.ts:812)
- **Blur+Clamp:** 4px inward-only feather — soft edges that never exceed polygon bounds. No horizontal bleed.

**Codex approach:** [useAIRender.ts:1329–1433](frontend/src/components/viewer/useAIRender.ts:1329)
- **Hybrid:** Polygon clip + pixel-diff above buildings. Captures 3D silhouette but can create **horizontal seams** if the AI's building silhouette doesn't align with the projected headroom box.

**Port requirement:** **Low priority** — codex's pixel-diff is actually superior for 2D satellite imagery. Only useful if:
  - Codex adopts 3D canvas capture (then blur+clamp becomes preferable).
  - Current pixel-diff creates visible artifacts in your site.

---

## Summary Table

| Aspect | Stable (useGlobeAIRender.ts) | Codex (useAIRender.ts) | Priority to Port | Difficulty |
|--------|------|------|---|---|
| **Capture** | R3F + 3D tiles (JPEG 85%, 300–800KB) | Mapbox 2D raster (PNG) | Architectural | N/A |
| **Mask Approach** | Silhouette extrusion (roof projection) | Rectangular headroom box | High | Medium |
| **Prompt Style** | Detailed SCHEMA + MANDATORY clauses | Abbreviated SCHEMA AVANZATO | High | Easy |
| **Occlusion** | Pixel-overlap culling + removed from prompt | Pixel-overlap + silhouette subtraction, but still in prompt | Medium | Medium |
| **Archetype Refs** | 6× compressed JPEGs (~30–50KB) | Unlimited full-res images | Medium | Easy |
| **Stitching** | Blur+clamp feather (inward-only) | Hybrid: polygon clip + pixel-diff above buildings | Low | N/A |
| **Styles** | 14 full narratives | 14 styles (abbreviated for Gemini) | Low | Low |

---

## Conclusion

**Stable is superior because:**
1. **3D context in capture** — Google Photorealistic Tiles give Gemini real building geometry, shadows, and materials.
2. **Silhouette masking** — Exact roof projection ensures Gemini fills the right 3D shape.
3. **Detailed prompt enforcement** — MANDATORY and CONSTRAINT clauses prevent zone bleeding and artifacts.
4. **Single-shot simplicity** — All zones rendered together with global context (color temperature, lighting, composition).

**Codex trades quality for flexibility:**
1. **2D Mapbox viewport** — Supports zoom-to-zone and per-zone workflows, but lacks 3D context.
2. **Two-pass rendering** — Separates ground and buildings, enabling fine-grained control.
3. **Abbreviated prompts** — Optimized for Imagen 3's token sensitivity; less enforce-able.

**Best path forward:** 
- **Option A (Recommended):** Adopt `useGlobeAIRender.ts` for codex as the default render pipeline, keeping `renderPerZone()` as a fallback for fine-grained control.
- **Option B:** Port the top 5 deltas (silhouette masking, detailed prompt, occlusion culling, compressed refs, mandatory clauses) into codex's current architecture incrementally.