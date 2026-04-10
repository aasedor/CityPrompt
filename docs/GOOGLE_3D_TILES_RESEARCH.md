# Google Photorealistic 3D Tiles Integration Research

> **Date:** 2026-03-31
> **Goal:** Evaluate integration paths for Google Photorealistic 3D Tiles into SiteForge's street-level view, currently powered by Mapbox GL JS + AI-generated renders via Vertex AI Imagen 3.

---

## Table of Contents

1. [Current SiteForge Architecture](#1-current-siteforge-architecture)
2. [Google 3D Tiles Overview](#2-google-3d-tiles-overview)
3. [Integration Path A: Native Google Maps JS API](#3-integration-path-a-native-google-maps-js-api)
4. [Integration Path B: Deck.gl with Tile3DLayer](#4-integration-path-b-deckgl-with-tile3dlayer)
5. [Integration Path C: Three.js with 3d-tiles-renderer](#5-integration-path-c-threejs-with-3d-tiles-renderer)
6. [Technical Challenges](#6-technical-challenges)
7. [Migration Strategy: Strangler Fig Pattern](#7-migration-strategy-strangler-fig-pattern)
8. [Pricing and Quotas](#8-pricing-and-quotas)
9. [Recommendation](#9-recommendation)
10. [Implementation Roadmap](#10-implementation-roadmap)

---

## 1. Current SiteForge Architecture

### Map Layer (Bird's Eye)
- **Renderer:** Mapbox GL JS v3.8.0 via direct `mapboxgl.Map` instantiation (not react-map-gl wrapper)
- **Component:** `SitePlannerMap.tsx` -- a 900+ line component handling zone drawing, polygon editing, drag/rotate, pegman placement, and massing overlay
- **Style:** Mapbox satellite or streets, with GeoJSON sources for site zones
- **3D:** Mapbox's built-in pitch/bearing (currently set to 60-degree pitch), plus fill-extrusion layers for massing

### Street View Layer
- **Renderer:** AI-generated imagery (Vertex AI Imagen 3), NOT real 3D geometry
- **Hook:** `useStreetViewRender.ts` -- computes view-cone geometry using THREE.js math (raycasting, polygon intersection), builds structured text prompts from archetype metadata, sends to backend render API
- **Panel:** `StreetViewPanel.tsx` -- compass UI, rotation controls, style picker (photorealistic, watercolour, charcoal, etc.), generates AI images on demand
- **Three.js usage:** Currently limited to math utilities (`THREE.Vector2`, `THREE.Raycaster`, etc.) for view-cone intersection -- no actual WebGL scene rendering

### Key Dependencies (package.json)
| Package | Version | Current Usage |
|---|---|---|
| `mapbox-gl` | ^3.8.0 | Primary map renderer |
| `react-map-gl` | ^7.1.7 | Listed but SitePlannerMap uses raw mapbox-gl |
| `three` | ^0.170.0 | Math only (view cone geometry) |
| `@react-three/fiber` | ^8.17.10 | Installed but no R3F Canvas found in main app |
| `@react-three/drei` | ^9.117.3 | Installed, unused in production views |
| `@react-three/postprocessing` | ^2.16.3 | Installed, unused |
| `3d-tiles-renderer` | ^0.4.22 | **Already installed** but no imports found |

**Critical finding:** The `3d-tiles-renderer` package (NASA-AMMOS/3DTilesRendererJS) is already in `package.json` at v0.4.22, along with the full React Three Fiber stack. This means Path C has zero new dependency overhead.

---

## 2. Google 3D Tiles Overview

### What They Are
Google Photorealistic 3D Tiles are textured meshes (not point clouds) covering 2,500+ cities worldwide, served in OGC 3D Tiles format (glTF). They provide photogrammetry-quality 3D geometry and imagery streamed progressively by level of detail.

### Root Tileset Endpoint
```
https://tile.googleapis.com/v1/3dtiles/root.json?key=YOUR_API_KEY
```

After June 9, 2025, `root.json` contains the root tile itself (one HTTP request to start traversing, down from two). The renderer handles all subsequent tile fetching automatically as the user navigates.

### Session Model
A single root tileset request creates a "session" valid for at least 3 hours of tile streaming. After that, a new root request is required.

### Attribution Requirement
All renderers MUST display Google's copyright attribution. The attribution data is embedded in the tile responses.

### EEA Restriction
Photorealistic 3D Tiles are unavailable for new projects with EU/EEA billing addresses after July 8, 2025. The native `<gmp-map-3d>` element is exempt because Google handles rendering internally.

---

## 3. Integration Path A: Native Google Maps JS API

### The `<gmp-map-3d>` Web Component

Google provides a custom HTML element for 3D map rendering:

```html
<gmp-map-3d
  center="49.2827,-123.1207,500"
  tilt="67.5"
  heading="0"
  range="1000"
  mode="hybrid"
></gmp-map-3d>
```

**Breaking change (Feb 2025):** `mode` is now mandatory -- either `"HYBRID"` or `"SATELLITE"`.

### Key Capabilities
- **glTF model placement:** `Model3DElement` supports adding custom `.glb` models to the scene
- **Mesh flattening:** `<gmp-flattener>` element flattens the photogrammetry mesh within a polygon path -- this is Google's built-in solution for site excavation
- **Camera animation:** `flyCameraTo()` and `flyCameraAround()` with altitude modes
- **Polygons/Polylines:** Native 3D overlay support
- **Cloud styling:** Map ID-based styling support

### FlattenerElement for Site Excavation
```html
<gmp-map-3d mode="satellite">
  <gmp-flattener>
    <!-- path defines the polygon to flatten -->
  </gmp-flattener>
  <gmp-model-3d
    src="proposed-building.glb"
    position="49.2827,-123.1207,0"
    altitude-mode="CLAMP_TO_GROUND"
  ></gmp-model-3d>
</gmp-map-3d>
```

### Pros
- Simplest integration (single web component)
- Built-in `<gmp-flattener>` solves site excavation natively
- Google handles rendering performance, tile management, attribution
- Works in EEA (rendering is server-side)
- Free during Preview (no SLA), then part of Maps JS API billing
- `Model3DElement` supports glTF with `CLAMP_TO_GROUND` altitude mode

### Cons
- **Black box rendering** -- no access to the WebGL context, depth buffer, or scene graph
- Cannot cast shadows from custom models onto Google terrain
- No postprocessing (depth of field, color grading, bloom)
- No custom shaders on tile geometry
- Cannot composite with existing Three.js scenes
- Limited camera control vs. full Three.js orbital controls
- 5MB model size recommendation (mobile constraint)
- **Not embeddable inside a React Three Fiber canvas**

### Verdict
Best for a quick "preview mode" but insufficient for architectural-quality visualization. The lack of shadow casting and postprocessing makes this unsuitable as the primary street-level renderer.

---

## 4. Integration Path B: Deck.gl with Tile3DLayer

### Setup
```javascript
import { Tile3DLayer } from '@deck.gl/geo-layers';
import { CesiumIonLoader } from '@loaders.gl/3d-tiles';

const tile3DLayer = new Tile3DLayer({
  id: 'google-3d-tiles',
  data: 'https://tile.googleapis.com/v1/3dtiles/root.json',
  loadOptions: {
    fetch: {
      headers: { 'X-GOOG-API-KEY': API_KEY }
    }
  },
  onTilesetLoad: (tileset) => {
    // Handle attribution from tileset.credits
  }
});
```

### TerrainExtension for 2D/3D Compositing
Deck.gl's `TerrainExtension` drapes 2D layers (GeoJSON polygons, icons, paths) onto the 3D tile surface via GPU reprojection. This lets you overlay site zone boundaries on top of photorealistic tiles.

### Pros
- Mature library with strong React support (`@deck.gl/react`)
- `TerrainExtension` enables draping 2D data layers onto 3D tiles
- Good performance for large datasets (100k+ features)
- Google officially lists deck.gl as a supported renderer
- Community demo with shadows and postprocessing exists (cheeaun/photorealistic-3d-deckgl)

### Cons
- Deck.gl's rendering pipeline is WebGL-based but not Three.js -- cannot easily share a scene graph with R3F
- Custom model placement requires ScenegraphLayer, which has limited material/lighting control
- Shadow casting onto tile geometry is not built-in
- Clipping/excavation of tiles not natively supported (no equivalent to FlattenerElement or ClippingPolygonCollection)
- Would require maintaining two separate rendering paradigms (Mapbox for 2D, deck.gl for 3D)
- PostProcessing would need custom WebGL work outside deck.gl's pipeline

### Verdict
Good middle ground if the primary need is data visualization on 3D tiles, but lacks the rendering control needed for architectural realism (shadows, clipping, DOF).

---

## 5. Integration Path C: Three.js with 3d-tiles-renderer

### Why This Path Is Ideal for SiteForge

The `3d-tiles-renderer` package (NASA-AMMOS/3DTilesRendererJS) is **already installed** at v0.4.22, and the full React Three Fiber stack (`@react-three/fiber`, `@react-three/drei`, `@react-three/postprocessing`) is present in `package.json`. This path requires zero new dependencies.

### Setup with React Three Fiber
```tsx
import { Canvas } from '@react-three/fiber';
import { TilesRenderer } from '3d-tiles-renderer';
import { GoogleCloudAuthPlugin } from '3d-tiles-renderer/plugins';

function GoogleTilesScene({ apiKey, center }) {
  const tilesRef = useRef<TilesRenderer>();

  useEffect(() => {
    const tiles = new TilesRenderer();
    tiles.registerPlugin(new GoogleCloudAuthPlugin({ apiToken: apiKey }));
    tiles.setLatLonToYUp(center.lat, center.lon);
    tilesRef.current = tiles;

    return () => tiles.dispose();
  }, [apiKey, center]);

  return (
    <Canvas
      gl={{ logarithmicDepthBuffer: true }}
      camera={{ fov: 50, near: 0.1, far: 1e7 }}
    >
      {tilesRef.current && (
        <primitive object={tilesRef.current.group} />
      )}
      <directionalLight castShadow position={[100, 200, 100]} />
      <EffectComposer>
        <DepthOfField focusDistance={0.01} focalLength={0.02} bokehScale={3} />
      </EffectComposer>
    </Canvas>
  );
}
```

### Key Features of 3d-tiles-renderer v0.4.x

| Feature | Version | Relevance |
|---|---|---|
| Google Cloud Auth Plugin | v0.3.x+ | Handles API key injection for all tile requests |
| ImageOverlayPlugin alpha masking | v0.4.19 | **Site excavation** -- cut holes in tiles using alpha masks |
| GeoJSON overlay plugin | v0.4.17 | Overlay site zone boundaries directly |
| WMTS/WMS/TMS imagery overlays | v0.4.17 | Additional map data layers |
| Frustum culling optimization | v0.3.20 | 45% fewer tiles drawn, 35% fewer downloaded for Google tiles |
| EastNorthUpFrame utilities | v0.4.x | Position and orient models on the ellipsoid surface |
| React Three Fiber support | v0.3.x+ | Official R3F bindings |
| Babylon.js support | v0.4.x | Not needed but shows maturity |

### Site Excavation via ImageOverlayPlugin
```typescript
import { ImageOverlayPlugin } from '3d-tiles-renderer/plugins';

// Alpha mask that cuts a hole where the development site is
const overlayPlugin = new ImageOverlayPlugin();
tilesRenderer.registerPlugin(overlayPlugin);

// Create a mask texture from the site polygon
const maskCanvas = createMaskFromPolygon(sitePolygon);
overlayPlugin.addOverlay({
  bounds: siteBounds,      // geographic bounds
  image: maskCanvas,
  mode: 'alphaOut',        // clip OUTSIDE the mask (keep the hole)
});
```

### Terrain Alignment via Raycasting
```typescript
import { WGS84_ELLIPSOID } from '3d-tiles-renderer';

function getTerrainElevation(lat: number, lon: number, tilesGroup: THREE.Group): number {
  // Get position above the surface
  const pos = new THREE.Vector3();
  const mat = new THREE.Matrix4();
  WGS84_ELLIPSOID.getEastNorthUpFrame(lat, lon, mat);
  pos.setFromMatrixPosition(mat);

  // Offset upward and raycast down
  const up = pos.clone().normalize();
  const origin = pos.clone().addScaledVector(up, 500);

  const raycaster = new THREE.Raycaster(origin, up.negate());
  raycaster.firstHitOnly = true;

  const hits = raycaster.intersectObject(tilesGroup, true);
  return hits.length > 0 ? hits[0].point.length() - WGS84_ELLIPSOID.radius.x : 0;
}
```

### Pros
- **Already installed** -- zero dependency additions
- Full Three.js scene graph access (shadows, custom materials, postprocessing)
- React Three Fiber integration for declarative scene composition
- ImageOverlayPlugin provides site excavation (alpha masking)
- Raycasting against tiles for terrain alignment
- `@react-three/postprocessing` enables depth of field, bloom, tone mapping
- Can share the scene with custom glTF architectural models
- Active maintenance by Garrett Johnson (Cesium Ecosystem Grant recipient)
- Logarithmic depth buffer support for earth-scale rendering
- 8 tiled data formats supported (3D Tiles, Quantized Mesh, TMS, WMTS, WMS, XYZ, DeepZoom, GeoJSON)

### Cons
- More complex setup than Path A
- Shadow casting onto Google tile geometry requires custom shader work (Google tiles use ShaderMaterial without shadow receive support)
- Must implement camera controls for globe navigation (or use drei's controls)
- Must handle Google attribution display manually
- Logarithmic depth buffer has performance implications
- Earth-scale scenes need careful near/far plane management

### Verdict
**Recommended path.** Maximum rendering control, zero new dependencies, and the ImageOverlayPlugin provides the critical site excavation feature. The R3F ecosystem enables rapid UI iteration with declarative components.

---

## 6. Technical Challenges

### 6.1 Site Excavation / Mesh Clipping

The goal is to remove existing buildings from Google tiles where the user places a new development.

| Approach | Tool | Mechanism | Quality |
|---|---|---|---|
| Google native | `<gmp-flattener>` | Flattens mesh to ground plane within polygon | Good -- leaves flat ground |
| CesiumJS | `ClippingPolygonCollection` | GPU-based polygon clip, added in v1.117 | Excellent -- clean edges, inverse mode |
| 3d-tiles-renderer | `ImageOverlayPlugin` (v0.4.19) | Alpha mask on tile textures | Good -- can cut shapes; some edge aliasing |
| Three.js manual | Stencil buffer / clipping planes | `renderer.clippingPlanes` with `THREE.Plane` | Flexible but only planar cuts, not polygon |

**Recommended approach for Path C:** Use `ImageOverlayPlugin` with `alphaOut` mode to mask the site footprint. For cleaner edges, generate the mask at 2x resolution with anti-aliased polygon rasterization. The mask can be derived directly from the site boundary zone polygon already stored in `siteZones`.

**Limitation:** The alpha mask approach operates on textures, not geometry. The mesh triangles remain but become transparent. For shadow analysis (e.g., will the new building shadow the neighbor?), the transparent mesh triangles may still participate in shadow maps unless explicitly excluded.

### 6.2 Shadow Casting

Casting shadows from custom architectural models onto Google terrain is a known difficulty because Google tiles use `ShaderMaterial` without built-in shadow receive support.

**Approaches:**

1. **Material replacement:** Replace Google tile `ShaderMaterial` with `MeshStandardMaterial`, copying textures. Technically possible but fragile -- Google can change their shader output between API versions.

2. **Shadow plane proxy:** Place an invisible `ShadowMaterial` plane at ground level beneath the custom model. The plane receives shadows from the model and composites them via alpha blending. Works well for flat sites but not for sloped terrain.

3. **Cascaded Shadow Maps (CSM) with three-geospatial:** The `@takram/three-atmosphere` package provides CSM integration that casts volumetric cloud shadows onto terrain. This same CSM infrastructure could be extended to cast model shadows.

4. **Screen-space shadow compositing:** Render the custom model's shadow in a separate pass using the depth buffer, then composite onto the final frame. This avoids modifying tile materials entirely.

**Recommended approach:** Start with the shadow plane proxy (simplest, works for flat urban sites). Upgrade to screen-space shadow compositing for sloped terrain in a later phase.

### 6.3 Depth of Field (Hiding Photogrammetry Artifacts)

At street level, Google photogrammetry exhibits texture stretching, mesh holes, and geometric simplification artifacts -- particularly on building facades not well-captured by overhead imagery.

**Solution:** `@react-three/postprocessing` DepthOfField effect:
```tsx
<EffectComposer>
  <DepthOfField
    focusDistance={0.01}    // focus on the custom model
    focalLength={0.02}      // shallow depth
    bokehScale={4}          // bokeh intensity
  />
  <ToneMapping />
  <Vignette darkness={0.3} />
</EffectComposer>
```

This blurs the photogrammetry beyond the focal plane, masking artifacts while keeping the proposed development sharp. The `BokehPass` (Three.js built-in) or PMNDRS `DepthOfField` (already available via `@react-three/postprocessing` in package.json) both work.

**Additional technique:** Fog (`<fog attach="fog" args={['#cce0ff', 200, 800]} />`) can further soften distant photogrammetry.

### 6.4 Terrain Alignment (Z-Axis Positioning)

Custom models must sit at the correct elevation on Google terrain, which has real-world topography.

**Approach:** Raycast from above the site centroid downward against loaded tiles:

1. Convert site centroid (lat/lon) to ECEF using `WGS84_ELLIPSOID.getCartographicToPosition()`
2. Create a downward ray from 500m above
3. Raycast against `tilesRenderer.group` with `firstHitOnly: true`
4. Position the model at the intersection point
5. Use `WGS84_ELLIPSOID.getEastNorthUpFrame()` to orient the model's up-axis correctly

**Important:** Set `tilesRenderer.loadSiblings = true` to ensure tiles are loaded even outside the camera frustum -- this is necessary for reliable raycasting at the site location before the camera has navigated there.

---

## 7. Migration Strategy: Strangler Fig Pattern

### Concept

The Strangler Fig Pattern enables gradual migration by running old and new systems in parallel, routing to each via a facade layer, and incrementally shifting features to the new system.

### Applied to SiteForge

```
Phase 1: COEXIST
  [Mapbox 2D Bird's Eye] ─── existing, unchanged
  [Three.js/R3F 3D Street View] ─── NEW, replaces AI-render-only modal

Phase 2: EXPAND
  [Mapbox 2D Bird's Eye] ─── existing
  [Three.js/R3F 3D Bird's Eye] ─── NEW, optional toggle
  [Three.js/R3F 3D Street View] ─── from Phase 1

Phase 3: MIGRATE (optional)
  [Three.js/R3F 3D Bird's Eye + Street View] ─── unified
  [Mapbox 2D] ─── deprecated or used as fallback only
```

### Facade: View Mode Abstraction

Create a `ViewMode` abstraction that the `ProjectViewPage` uses to switch between renderers:

```typescript
type ViewMode =
  | { type: 'mapbox-2d' }                          // Existing bird's eye
  | { type: 'three-3d-street'; position: LatLon; heading: number }  // New street view
  | { type: 'three-3d-aerial'; center: LatLon; zoom: number };      // Future aerial 3D

// In ProjectViewPage:
{viewMode.type === 'mapbox-2d' && <SitePlannerMap ... />}
{viewMode.type === 'three-3d-street' && <StreetView3DCanvas ... />}
```

### Why Not Replace Mapbox Immediately?

1. **Zone drawing** -- SitePlannerMap has 900+ lines of polygon editing, drag, rotate, undo/redo logic tightly coupled to Mapbox's event model and GeoJSON sources. Rewriting this in Three.js is a multi-week effort.
2. **Satellite imagery** -- Mapbox provides high-quality 2D satellite tiles essential for the bird's eye planning view. Google 3D tiles are optimized for oblique/3D viewing, not top-down 2D.
3. **Performance** -- 2D Mapbox is far lighter than streaming 3D tiles for the planning workflow where users need fast polygon editing, not photorealistic rendering.

### Phase 1 Implementation (Street View Only)

1. Keep `SitePlannerMap.tsx` unchanged for bird's eye planning
2. Replace the AI-render-only `StreetViewPanel` modal with an interactive 3D canvas
3. The 3D canvas loads Google Photorealistic Tiles via `3d-tiles-renderer`
4. User's proposed buildings appear as glTF models (generated or procedural) in the scene
5. The existing AI render styles (watercolour, charcoal, etc.) become screenshot-based postprocessing options applied to the 3D canvas output
6. The pegman drop interaction on SitePlannerMap transitions the user into the 3D street view

---

## 8. Pricing and Quotas

### Google Map Tiles API (Photorealistic 3D Tiles)

| Metric | Value |
|---|---|
| Free tier | 1,000 root tileset (session) requests/month |
| Daily quota | 10,000 root tileset requests |
| Session duration | 3+ hours of tile streaming per root request |
| Billed SKU | Enterprise tier (Photorealistic 3D Tiles) |
| Individual tile requests | Not billed (only root requests count) |
| Preview status | Currently in Preview (free, no SLA) as of March 2026 |

### Cost Estimation for SiteForge

Assuming each user session triggers one root tileset request:
- **1,000 sessions/month:** Free
- **10,000 sessions/month:** Estimated $50-200/month (Enterprise SKU pricing)
- **Individual tile fetches within a session:** Free (only root request is billed)

### Comparison: Current Vertex AI Imagen 3 Costs

Each AI-rendered street view currently costs per-image via Vertex AI. If users generate 5-10 renders per session, the 3D tiles approach could be **cheaper per session** while providing unlimited viewpoints within that session.

---

## 9. Recommendation

### Primary Path: C (Three.js + 3d-tiles-renderer)

**Rationale:**
1. **Zero new dependencies** -- `3d-tiles-renderer` v0.4.22, Three.js v0.170, and the full R3F stack are already installed
2. **Maximum rendering control** -- full access to the scene graph, materials, shadows, and postprocessing
3. **Site excavation** -- ImageOverlayPlugin (v0.4.19) alpha masking cuts holes in tiles
4. **Terrain alignment** -- raycasting against loaded tiles
5. **Postprocessing** -- `@react-three/postprocessing` already installed for DOF, bloom, tone mapping
6. **Dual-view architecture** -- Mapbox handles 2D planning, R3F handles 3D visualization
7. **AI render fusion** -- the existing Vertex AI pipeline can be retained as an optional "artistic style" layer, capturing the 3D canvas and applying AI style transfer

### Secondary Capability: Google `<gmp-map-3d>` for Quick Preview

Use `<gmp-map-3d>` as a lightweight "context preview" shown in a small inset panel while the user is in 2D planning mode. This gives immediate 3D context without the overhead of the full R3F scene. The `<gmp-flattener>` could flatten the site area even in this preview.

---

## 10. Implementation Roadmap

### Phase 1: Foundation (2-3 weeks)

- [ ] Create `StreetView3DCanvas.tsx` -- R3F Canvas with Google tiles via `3d-tiles-renderer`
- [ ] Implement `GoogleTilesProvider` component wrapping `TilesRenderer` + `GoogleCloudAuthPlugin`
- [ ] Add `VITE_GOOGLE_MAPS_API_KEY` environment variable
- [ ] Implement camera positioning from pegman lat/lon/heading (reuse view cone math from `useStreetViewRender.ts`)
- [ ] Handle Google attribution display (extract from tile credits)
- [ ] Add `logarithmicDepthBuffer: true` to R3F Canvas
- [ ] Wire pegman drop on SitePlannerMap to open `StreetView3DCanvas`

### Phase 2: Site Excavation + Model Placement (2-3 weeks)

- [ ] Implement `SiteExcavator` component using `ImageOverlayPlugin` to alpha-mask site boundary
- [ ] Create `ProposedBuilding` component that loads a glTF model and positions via raycast
- [ ] Implement terrain alignment using `WGS84_ELLIPSOID.getEastNorthUpFrame()` + raycasting
- [ ] Generate placeholder glTF massing models from zone properties (floor count, footprint)
- [ ] Add shadow plane proxy beneath proposed buildings

### Phase 3: Visual Quality (1-2 weeks)

- [ ] Add `EffectComposer` with `DepthOfField` for photogrammetry artifact hiding
- [ ] Implement atmospheric fog for distance fade
- [ ] Add `ToneMapping` and `Vignette` postprocessing
- [ ] Implement sun position calculation from site latitude/longitude + time of day
- [ ] Add orbit controls with heading/pitch matching pegman direction

### Phase 4: AI Style Fusion (1 week)

- [ ] Capture R3F canvas to image buffer
- [ ] Send canvas capture to Vertex AI with existing style prompts (watercolour, charcoal, etc.)
- [ ] Display AI-styled version alongside or overlaid on the 3D view
- [ ] Allow user to toggle between "3D Interactive" and "AI Rendered" modes

### Phase 5: Context Preview Inset (optional, 1 week)

- [ ] Add small `<gmp-map-3d>` inset panel in bird's eye view
- [ ] Sync camera position with SitePlannerMap center
- [ ] Use `<gmp-flattener>` to flatten site area in preview

---

## Appendix A: API Endpoints Reference

| Service | Endpoint | Auth |
|---|---|---|
| Map Tiles API (3D) | `https://tile.googleapis.com/v1/3dtiles/root.json?key=KEY` | API key (query param) |
| Map Tiles API (preview) | `https://tile.googleapis.com/v1/3dtiles/datasets/CgIYAQ/root?key=KEY` | API key |
| Maps JS API (3D) | `https://maps.googleapis.com/maps/api/js?key=KEY&v=beta&libraries=maps3d` | API key (script tag) |
| Individual tile fetches | Automatic (renderer follows tileset URLs) | `X-GOOG-API-KEY` header or query param |

## Appendix B: Key Library Versions

| Library | Minimum for Google Tiles | SiteForge Current |
|---|---|---|
| `3d-tiles-renderer` | v0.3.x (basic), v0.4.19+ (clipping) | **v0.4.22** |
| `three` | v0.150+ | **v0.170.0** |
| `@react-three/fiber` | v8.x | **v8.17.10** |
| CesiumJS (if used) | v1.124+ (best perf), v1.117+ (clipping polygons) | N/A |
| deck.gl (if used) | v8.9.13+ | N/A |

## Appendix C: Key References

- [Google Map Tiles API -- Photorealistic 3D Tiles Overview](https://developers.google.com/maps/documentation/tile/3d-tiles-overview)
- [Google Map Tiles API -- Work with a 3D Tiles Renderer](https://developers.google.com/maps/documentation/tile/use-renderer)
- [Google Maps JS API -- 3D Maps Overview](https://developers.google.com/maps/documentation/javascript/3d/overview)
- [Google Maps JS API -- Mesh Flattening](https://developers.google.com/maps/documentation/javascript/3d/mesh-flattening)
- [Google Maps JS API -- 3D Models](https://developers.google.com/maps/documentation/javascript/3d/models)
- [NASA-AMMOS/3DTilesRendererJS (GitHub)](https://github.com/NASA-AMMOS/3DTilesRendererJS)
- [CesiumJS -- Photorealistic 3D Tiles Quickstart](https://cesium.com/learn/cesiumjs-learn/cesiumjs-photorealistic-3d-tiles/)
- [CesiumJS -- Clipping Polygons Tutorial](https://cesium.com/learn/cesiumjs-learn/cesiumjs-clipping-polygons/)
- [Deck.gl -- Tile3DLayer API](https://deck.gl/docs/api-reference/geo-layers/tile-3d-layer)
- [Deck.gl -- Google 3D Tiles Example](https://deck.gl/examples/google-3d-tiles)
- [three.js Forum -- 3d-tiles-renderer Discussion](https://discourse.threejs.org/t/3d-tiles-renderer-a-3d-tiles-implementation-for-three-js-from-nasa-jpl/44136)
- [three.js Forum -- Shadow Analysis on Google 3D Tiles](https://discourse.threejs.org/t/shadow-analysis-on-google-3d-tiles/52623)
- [Google Map Tiles API -- Pricing](https://developers.google.com/maps/documentation/tile/usage-and-billing)
- [cheeaun/photorealistic-3d-deckgl (shadows + postprocessing demo)](https://github.com/cheeaun/photorealistic-3d-deckgl)
