# Building Orientation Research

**Goal**: Let users specify which direction a building faces (e.g., "Brownstone facing east") and have that propagate through aerial renders, street views, and 3D massing.

**Date**: 2026-03-31

---

## 1. Current State of Orientation in the Codebase

### 1.1 What Already Exists

The codebase already has substantial rotation/orientation infrastructure:

#### A. Polygon Rotation on the Map (fully working)

**File**: `frontend/src/components/viewer/SitePlannerMap.tsx`

- A **rotation handle** (amber circle with dashed line) appears when a building zone is selected.
- Users drag the handle to rotate the zone polygon around its centroid.
- A **north indicator** ("N" label in red) is placed due north of the centroid for reference.
- During rotation, a tooltip shows the delta angle (e.g., "+45 deg").
- On mouseup, rotated coordinates are persisted via `onZoneUpdated`.
- Only shown for `building` and `residential` zone types (line ~680).

Key code paths:
```
SitePlannerMap.tsx:622   computeRotationHandlePos()
SitePlannerMap.tsx:920   zone-rotation-handle source + 3 layers (line, handle circle, north label)
SitePlannerMap.tsx:1120  mousedown on rotation handle -> starts rotation drag
SitePlannerMap.tsx:1306  mousemove with type='rotate' -> rotates all vertices
SitePlannerMap.tsx:1368  mouseup -> persists new coordinates
SitePlannerMap.tsx:1795  Rotation overlay tooltip (shows +/- degrees)
```

#### B. Building `rotation_degrees` Field (exists but unused in renders)

**File**: `frontend/src/types/index.ts:50`

```typescript
export interface Building {
  // ...
  rotation_degrees?: number;  // <-- exists on the Building model
}
```

**File**: `frontend/src/store/undoActions.ts:212`

```typescript
export function createBuildingRotationAction(
  projectId: string,
  buildingId: string,
  prevDeg: number,
  newDeg: number,
  queryClient: QueryClient,
): UndoableAction { ... }
```

This field exists in the data model and has undo support, but is **not referenced** in the render prompt builders.

#### C. Layout Preview Orientation (AI-generated, read-only)

**File**: `frontend/src/types/index.ts:162-163`

```typescript
export interface LayoutOption {
  // ...
  orientation_deg?: number;       // e.g. 135
  orientation_mode?: string;      // e.g. 'site_orientation'
}
```

**File**: `frontend/src/components/viewer/LayoutPreviewPanel.tsx:36,252,468`

- The AI layout generator can return `orientation_deg` and `orientation_mode` per layout option.
- Displayed as a read-only badge: "Primary orientation: 135 deg SE".
- `formatOrientation()` converts degrees to cardinal direction labels (N, NE, E, SE, etc.).
- This is **display-only** -- the user cannot edit it.

#### D. Layout Building `rotation_deg` (per-building in layout)

**File**: `frontend/src/types/index.ts:140`

```typescript
export interface LayoutBuildingData {
  rotation_deg: number;   // individual building rotation within layout
  // ...
}
```

**File**: `frontend/src/components/viewer/massingUtils.ts:46`

```typescript
function buildRectFootprint(centerLat, centerLng, widthM, depthM, rotationDeg) {
  // Rotates the 4-corner rectangle by rotationDeg
}
```

This rotation is used to place layout buildings at various angles, but it describes **geometric rotation** (which way the rectangle is oriented), not **facade facing direction**.

#### E. Face Bearings (4-face rendering, hardcoded)

**File**: `frontend/src/components/viewer/useAIRender.ts:331-336`

```typescript
const FACE_BEARINGS = [
  { label: 'front', bearing: 0 },    // North
  { label: 'right', bearing: 90 },   // East
  { label: 'rear',  bearing: 180 },  // South
  { label: 'left',  bearing: 270 },  // West
];
```

The 4-face render system captures the map at 4 bearings and renders each face. Currently **hardcoded**: "front" always means bearing 0 (looking south at the north face). The building's actual facing direction is never consulted.

### 1.2 What Does NOT Exist

1. **No `facing_direction` property** on SiteZone or SiteZoneProperties.
2. **No UI in ZonePropertiesPanel** for setting building orientation/facing.
3. **No orientation data flows into render prompts** -- neither `buildBuildingPrompt()` (aerial) nor `buildStreetViewPrompt()` (street view) reference any facing direction.
4. **No compass rose picker component**.
5. **The rotation handle rotates the polygon shape** but does not record a semantic "front facade direction".

### 1.3 The Semantic Gap

The fundamental gap is the difference between:

- **Geometric rotation**: which way the polygon is oriented on the map (already works via drag handle)
- **Facade facing direction**: which side of the building is the "front" (entrance, main facade, street-facing side)

A building polygon can be geometrically oriented at any angle, but without knowing which edge is the "front", the render prompts cannot say "the brownstone entrance faces east" or "the main facade faces the park".

---

## 2. How Other Tools Handle Building Orientation

### 2.1 Revit: True North vs. Project North

Revit separates **True North** (real-world compass) from **Project North** (drawing convenience). Building orientation is set via `Manage > Position > Rotate True North`. The ViewCube includes a compass ring that shows cardinal directions relative to the model. Key insight: Revit treats orientation as a **site-level** property (rotating the whole project relative to north), not a per-building property.

### 2.2 SketchUp

SketchUp defines north as the green axis (+Y). Building orientation is implicit in how the user draws geometry. The `Solar North` extension lets users rotate the north direction for shadow studies. Key insight: orientation is about **sun/shadow analysis**, not facade labeling.

### 2.3 DesignBuilder

DesignBuilder has a `Site Orientation` field that is an angle relative to North (e.g., entering 45 rotates the building 45 degrees clockwise). This approach keeps the x/y axes aligned with the building for easier editing.

### 2.4 Chief Architect

Recommends drawing structures orthogonally (at 0/90/180/270) and rotating the plot lines instead. Distinguishes clearly between rotating a structure vs. rotating a view.

### 2.5 Sefaira (Energy Analysis)

Uses Revit's True North to determine building orientation for energy analysis. The massing can also be oriented in the web app directly.

### 2.6 Key Takeaway from Industry

Professional tools generally handle orientation at the **site/project level** (rotate everything relative to north) rather than per-building. Per-building "facing" is implicit in the geometry. However, for SiteForge's AI-prompt-driven workflow, we need **explicit semantic facing** because the AI needs to know "which facade faces which direction" to generate correct imagery.

---

## 3. Three UX Approaches

### 3.1 Approach A: Rotation Handle on the Map (Enhanced)

**Description**: Enhance the existing rotation handle to also set a "front facade" indicator.

```
                    N (red)
                    |
                    |
        +-----------+-----------+
        |                       |
        |     [Building]        |
        |                       |
        +-----------+-----------+
                    |
                    o-----> (amber rotation handle)
                    |
              FRONT (arrow indicator)

When user drags the rotation handle:
  - Polygon rotates (existing behavior)
  - "Front" marker stays on the same edge
  - After release, front direction is computed from the
    first edge of the polygon relative to north
```

**Interaction**:
1. Select a building zone -- rotation handle + north label appear (existing).
2. NEW: A **front-facade arrow** (green/blue) appears on the first edge of the polygon.
3. User drags the rotation handle to rotate the polygon -- the front arrow rotates with it.
4. NEW: Double-click the front arrow to reassign which edge is the front (cycles through edges).
5. On release, compute `facing_direction_deg` from the outward normal of the front edge.

**Pros**:
- Builds on existing rotation handle infrastructure.
- Spatial -- user sees the orientation directly on the map.
- No additional panel clutter.

**Cons**:
- Requires understanding that rotation handle = facade direction (not obvious).
- Double-click to change front edge is discoverable only by power users.
- Doesn't work well for irregular (non-rectangular) polygons.

**Effort**: Medium (extend existing rotation handle code).

### 3.2 Approach B: Compass Rose Picker in Properties Panel

**Description**: A visual compass rose widget in ZonePropertiesPanel that lets users click a cardinal/intercardinal direction to set the building's front-facing direction.

```
  Zone Properties Panel
  +------------------------------------------+
  |  Name: Brownstone Rowhouse               |
  |  Type: Building                          |
  |  Floors: 4        Height: 12m            |
  |                                          |
  |  Front Facing Direction:                 |
  |                                          |
  |              N                           |
  |          NW  |  NE                       |
  |            \ | /                         |
  |       W ----*---- E                      |
  |            / | \                         |
  |          SW  |  SE                       |
  |              S                           |
  |                                          |
  |  [Currently: EAST]                       |
  |                                          |
  |  (click a direction to set where the     |
  |   main entrance/facade faces)            |
  +------------------------------------------+

  Clicking "E" highlights it and sets:
    zone.properties.facing_direction = 'E'
    zone.properties.facing_direction_deg = 90
```

**Interaction**:
1. Open ZonePropertiesPanel for a building zone.
2. Below the floors/height controls, a compass rose widget appears.
3. Click one of 8 directions (N, NE, E, SE, S, SW, W, NW).
4. The selected direction highlights with a filled indicator.
5. Optional: A small compass overlay appears on the map zone.

**Pros**:
- Very discoverable -- clearly labeled "Front Facing Direction".
- Works for any polygon shape (direction is semantic, not geometric).
- Familiar UI metaphor (compass rose).
- Easy to implement (8 clickable segments + state).

**Cons**:
- Limited to 8 directions (45-degree increments).
- Requires opening the properties panel.
- Disconnected from the map -- user doesn't see the direction on the zone.

**Effort**: Low-Medium (new component, straightforward state management).

### 3.3 Approach C: Dropdown with Cardinal Directions

**Description**: A simple dropdown/select in ZonePropertiesPanel.

```
  Zone Properties Panel
  +------------------------------------------+
  |  Name: Brownstone Rowhouse               |
  |  Type: Building                          |
  |  Floors: 4        Height: 12m            |
  |                                          |
  |  Front Faces:  [ East (E)          v ]   |
  |                                          |
  |  Options:                                |
  |    North (N)        - 0 deg              |
  |    Northeast (NE)   - 45 deg             |
  |    East (E)         - 90 deg             |
  |    Southeast (SE)   - 135 deg            |
  |    South (S)        - 180 deg            |
  |    Southwest (SW)   - 225 deg            |
  |    West (W)         - 270 deg            |
  |    Northwest (NW)   - 315 deg            |
  |    Street-facing    - auto (inferred)    |
  |    Custom...        - enter degrees      |
  +------------------------------------------+
```

**Interaction**:
1. Open ZonePropertiesPanel for a building zone.
2. A dropdown labeled "Front Faces" appears below the height/floors controls.
3. Select a cardinal direction or "Street-facing" (auto-detect nearest road).
4. "Custom..." opens a numeric input for arbitrary degrees.

**Pros**:
- Simplest implementation.
- "Street-facing" auto mode is very powerful (detect nearest road zone and face it).
- Supports arbitrary angles via "Custom" option.
- Compact -- fits in existing panel layout.

**Cons**:
- Less visual/spatial than compass rose.
- Dropdown is utilitarian, not engaging.
- "Street-facing" auto-detect adds complexity.

**Effort**: Low (standard select component + optional auto-detect).

---

## 4. Impact Analysis

### 4.1 Aerial Render Prompt

**Current**: `buildBuildingPrompt()` in `useAIRender.ts:1046` describes the building archetype, materials, and style but never mentions which direction the facade faces.

**With orientation**: The prompt should include a sentence like:
```
"The main entrance and primary facade of this brownstone faces east (toward the right
side of the aerial image when viewed from above with north at top)."
```

**Implementation**:
1. Read `zone.properties.facing_direction_deg` (or `facing_direction` cardinal string).
2. Convert to a relative compass reference based on the current map bearing.
3. Append to the narrative in `buildBuildingPrompt()`.

**Code change** in `useAIRender.ts`:
```typescript
// After line 1070 (buildingNarrative)
const facingDeg = zone.properties?.facing_direction_deg as number | undefined;
if (facingDeg !== undefined) {
  const compassDir = degreesToCardinal(facingDeg);
  parts.push(
    `The building's main entrance and primary facade faces ${compassDir}. ` +
    `Orient the building so the most detailed, street-facing elevation faces ${compassDir}.`
  );
}
```

**4-Face Render Impact** (`FACE_BEARINGS` at line 331):
The "front" face bearing should be offset by the building's facing direction:
```typescript
// Instead of hardcoded front=0, use:
const frontBearing = facingDeg ?? 0;
const FACE_BEARINGS = [
  { label: 'front', bearing: frontBearing },
  { label: 'right', bearing: (frontBearing + 90) % 360 },
  { label: 'rear',  bearing: (frontBearing + 180) % 360 },
  { label: 'left',  bearing: (frontBearing + 270) % 360 },
];
```

### 4.2 Street View Prompt

**Current**: `buildStreetViewPrompt()` in `useStreetViewRender.ts:876` describes each visible zone with its archetype metadata and relative position (LEFT/CENTER/RIGHT) but never mentions which facade of the building the pegman is looking at.

**With orientation**: The prompt should indicate facade visibility:
```
"You are looking at the FRONT facade (main entrance) of the Brownstone Rowhouse"
vs.
"You are looking at the REAR facade (back wall/service side) of the Brownstone Rowhouse"
```

**Implementation**:
1. For each visible building zone, compute the angle from the pegman to the zone centroid.
2. Compare that angle to the building's `facing_direction_deg`.
3. Determine which face the pegman sees: front (within +/-45 deg of facing), left, right, or rear.
4. Inject this into the zone description in `describeZoneForStreetView()`.

**Code change** in `useStreetViewRender.ts`:
```typescript
function getVisibleFace(
  pegmanPos: [number, number],
  zoneCentroid: [number, number],
  facingDeg: number,
): 'front' | 'right' | 'rear' | 'left' {
  const bearingToZone = bearing(pegmanPos, zoneCentroid);
  const relative = ((bearingToZone - facingDeg) % 360 + 360) % 360;
  // The pegman sees the OPPOSITE face from their bearing to the building
  const viewFace = (relative + 180) % 360;
  if (viewFace >= 315 || viewFace < 45) return 'front';
  if (viewFace >= 45 && viewFace < 135) return 'right';
  if (viewFace >= 135 && viewFace < 225) return 'rear';
  return 'left';
}
```

Then in the prompt:
```
"[FRONT FACADE] Brownstone Rowhouse (4 stories) -- red brick facade with limestone
trim, arched entry, cast-iron railings..."
vs.
"[REAR FACADE] Brownstone Rowhouse (4 stories) -- plain brick wall, fire escapes,
utility connections..."
```

### 4.3 Clay Massing Model (3D)

**Current**: `generateClayRender()` in `useStreetViewRender.ts:1446` creates gray extruded boxes from zone polygons. Buildings are uniform gray with no facade differentiation.

**With orientation**: The clay model could visually indicate the front face:
1. **Minimal**: Render the front face in a slightly different shade (e.g., lighter gray or faint blue tint).
2. **Enhanced**: Add a small colored dot/line on the front face of each building box.

**Implementation** (minimal approach):
```typescript
// In the building extrusion material setup:
// Use a multi-material approach where one face gets a slightly different color
const frontFaceMaterial = new THREE.MeshStandardMaterial({
  color: 0xb0b0b0,  // slightly lighter than 0x9e9e9e
  roughness: 0.7,
});
```

This is **low priority** -- the clay model is a spatial guide, not a design tool.

### 4.4 Map Visualization

A small arrow or marker on the map showing the front-facing direction would provide immediate visual feedback:

```
         N
         |
    +----+----+
    |         |  --> E (front arrow)
    |  Zone   |
    |         |
    +----+----+
```

**Implementation**: Add a new GeoJSON feature to the `zone-rotation-handle` source (or a new source) that draws a small arrow from the zone centroid pointing in the facing direction. Use a symbol layer with a rotated arrow icon.

---

## 5. Data Model Changes

### 5.1 SiteZoneProperties (frontend type)

**File**: `frontend/src/types/index.ts:115`

Add:
```typescript
export interface SiteZoneProperties {
  // ... existing fields ...
  facing_direction?: 'N' | 'NE' | 'E' | 'SE' | 'S' | 'SW' | 'W' | 'NW' | 'street';
  facing_direction_deg?: number;  // 0-359, 0=north, 90=east
}
```

### 5.2 Backend / Database

The `site_zones` table stores properties as a JSONB column, so no schema migration is needed. The new fields will be stored as part of the JSON blob.

### 5.3 Utility Functions

Create a shared utility (e.g., `frontend/src/utils/orientation.ts`):

```typescript
export const CARDINAL_DIRECTIONS = [
  { label: 'North',     short: 'N',  deg: 0 },
  { label: 'Northeast', short: 'NE', deg: 45 },
  { label: 'East',      short: 'E',  deg: 90 },
  { label: 'Southeast', short: 'SE', deg: 135 },
  { label: 'South',     short: 'S',  deg: 180 },
  { label: 'Southwest', short: 'SW', deg: 225 },
  { label: 'West',      short: 'W',  deg: 270 },
  { label: 'Northwest', short: 'NW', deg: 315 },
] as const;

export function degreesToCardinal(deg: number): string {
  const normalized = ((deg % 360) + 360) % 360;
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  return directions[Math.round(normalized / 45) % 8];
}

export function cardinalToDegrees(dir: string): number {
  const map: Record<string, number> = {
    N: 0, NE: 45, E: 90, SE: 135, S: 180, SW: 225, W: 270, NW: 315,
  };
  return map[dir] ?? 0;
}

/**
 * Auto-detect facing direction: find the nearest road/street zone
 * and return the bearing from the building centroid to the nearest
 * point on that road.
 */
export function inferStreetFacingDirection(
  buildingCentroid: [number, number],
  allZones: SiteZone[],
): number | null {
  const roadTypes = new Set(['road', 'street', 'path', 'pedestrian']);
  const roads = allZones.filter(z => roadTypes.has(z.zone_type));
  if (roads.length === 0) return null;
  // Find nearest road centroid
  let nearest = Infinity;
  let nearestBearing = 0;
  for (const road of roads) {
    const centroid = computeCentroid(road.coordinates);
    const dist = haversine(buildingCentroid, centroid);
    if (dist < nearest) {
      nearest = dist;
      nearestBearing = bearing(buildingCentroid, centroid);
    }
  }
  // Snap to nearest 45-degree increment
  return Math.round(nearestBearing / 45) * 45 % 360;
}
```

---

## 6. Recommended Implementation Plan

### Phase 1: Dropdown + Prompt Integration (MVP)

**Effort**: 1-2 days

1. Add `facing_direction` and `facing_direction_deg` to `SiteZoneProperties` type.
2. Add a dropdown in `ZonePropertiesPanel.tsx` (Approach C) with 8 cardinal directions + "Street-facing (auto)" + "Custom".
3. Wire the dropdown to persist via `onUpdate`.
4. Inject facing direction into `buildBuildingPrompt()` in `useAIRender.ts`.
5. Inject visible-face detection into `buildStreetViewPrompt()` in `useStreetViewRender.ts`.

**Files to modify**:
- `frontend/src/types/index.ts` -- add fields to SiteZoneProperties
- `frontend/src/components/viewer/ZonePropertiesPanel.tsx` -- add dropdown UI
- `frontend/src/components/viewer/useAIRender.ts` -- enhance buildBuildingPrompt
- `frontend/src/components/viewer/useStreetViewRender.ts` -- enhance street view descriptions
- NEW: `frontend/src/utils/orientation.ts` -- shared utility functions

### Phase 2: Compass Rose + Map Indicator

**Effort**: 1-2 days

1. Replace the dropdown with a visual compass rose component (Approach B).
2. Add a facing-direction arrow on the map (small arrow symbol on the zone).
3. Wire the compass rose to update both `facing_direction` and the map arrow.

**Files to modify**:
- NEW: `frontend/src/components/viewer/CompassRosePicker.tsx`
- `frontend/src/components/viewer/SitePlannerMap.tsx` -- add facing arrow layer
- `frontend/src/components/viewer/ZonePropertiesPanel.tsx` -- replace dropdown with compass rose

### Phase 3: Enhanced Map Handle + Clay Model

**Effort**: 1 day

1. Add a front-face indicator to the existing rotation handle visualization.
2. Color the front face of buildings slightly differently in the clay massing model.
3. Offset `FACE_BEARINGS` by the facing direction for 4-face renders.

**Files to modify**:
- `frontend/src/components/viewer/SitePlannerMap.tsx` -- front-face indicator
- `frontend/src/components/viewer/useStreetViewRender.ts` -- clay render front face tint
- `frontend/src/components/viewer/useAIRender.ts` -- dynamic FACE_BEARINGS

---

## 7. Recommendation

**Start with Phase 1 (Dropdown + Prompt Integration)** because:

1. It delivers the core value immediately -- renders will respect building orientation.
2. The dropdown is the simplest UX to implement and test.
3. The "Street-facing (auto)" option is uniquely powerful for SiteForge (no other tool has this).
4. The `formatOrientation()` function already exists in `LayoutPreviewPanel.tsx` and can be reused.
5. The `createBuildingRotationAction` undo infrastructure in `undoActions.ts` can be adapted for facing direction changes.

**Phase 2** (compass rose) adds polish but is not essential for the core feature. It can be added later based on user feedback.

**Phase 3** (map handle + clay model) is the least critical and can be deferred.

---

## 8. Relevant File Index

| File | Role |
|------|------|
| `frontend/src/types/index.ts:115` | `SiteZoneProperties` -- add `facing_direction`, `facing_direction_deg` |
| `frontend/src/types/index.ts:502` | `SiteZone` interface |
| `frontend/src/types/index.ts:50` | `Building.rotation_degrees` (existing, unused in renders) |
| `frontend/src/types/index.ts:140` | `LayoutBuildingData.rotation_deg` (geometric rotation) |
| `frontend/src/types/index.ts:162` | `LayoutOption.orientation_deg` (AI-generated, read-only) |
| `frontend/src/components/viewer/ZonePropertiesPanel.tsx` | Properties panel -- add facing direction UI |
| `frontend/src/components/viewer/SitePlannerMap.tsx:622` | Rotation handle computation |
| `frontend/src/components/viewer/SitePlannerMap.tsx:920` | Rotation handle map layers |
| `frontend/src/components/viewer/SitePlannerMap.tsx:1306` | Rotation drag logic |
| `frontend/src/components/viewer/useAIRender.ts:331` | `FACE_BEARINGS` -- hardcoded front=0 |
| `frontend/src/components/viewer/useAIRender.ts:1046` | `buildBuildingPrompt()` -- inject facing direction here |
| `frontend/src/components/viewer/useAIRender.ts:1449` | `getActiveFaceLabel()` -- should respect facing direction |
| `frontend/src/components/viewer/useStreetViewRender.ts:723` | `describeZoneForStreetView()` -- add face visibility |
| `frontend/src/components/viewer/useStreetViewRender.ts:876` | `buildStreetViewPrompt()` -- inject face context |
| `frontend/src/components/viewer/useStreetViewRender.ts:1446` | `generateClayRender()` -- optional front-face tinting |
| `frontend/src/components/viewer/LayoutPreviewPanel.tsx:468` | `formatOrientation()` -- reusable utility |
| `frontend/src/components/viewer/massingUtils.ts:46` | `buildRectFootprint()` -- geometric rotation |
| `frontend/src/components/viewer/collectArchetypeRenderInputs.ts` | Facade detail metadata |
| `frontend/src/store/undoActions.ts:212` | `createBuildingRotationAction()` -- adapt for facing direction |
| `frontend/src/utils/coordTransform.ts:127` | `getRotatedRectCorners()` -- rotation math utility |

---

## 9. Open Questions

1. **Should facing direction auto-populate from the rotation handle?** When the user drags the rotation handle, should the "front" always be inferred as the first edge of the polygon? This would link geometric rotation to semantic facing, which is convenient but potentially confusing.

2. **Should "Street-facing" be the default?** For most urban buildings, the main facade faces the nearest street. Making this the default would reduce manual work but could be wrong for corner lots or park-facing buildings.

3. **How should facing direction interact with the 4-face render system?** Currently the 4-face render captures N/E/S/W views. Should it instead capture front/right/rear/left views relative to the facing direction? This would produce more useful results but changes the camera behavior.

4. **Should parks and open spaces also have an orientation?** Some park designs have a clear primary axis or entrance direction. This research focuses on buildings, but the same system could apply to parks.

5. **How does facing direction interact with multi-building zones?** A development_area zone may contain multiple buildings (via layout preview). Should each sub-building get its own facing direction, or should the zone have a single orientation that all buildings inherit?

---

## 10. Deep Research: AI-Specific Orientation Control Strategies (April 2026)

This section covers external research into how to make AI image generation models (specifically Google Gemini) respect building orientation/facing direction in aerial oblique renders.

### 10.1 The Core Problem

Diffusion models are biased toward the most photogenic/canonical view of any building type. When prompted to render a "brownstone rowhouse," Gemini will always produce the Instagram-worthy front stoop view, regardless of camera angle. This is because:

- Training data overwhelmingly contains "hero shot" front facade images
- The model has no concept of 3D geometry or viewing angle
- Text prompts describing orientation compete with the model's prior that "brownstone = front stoop"
- Google has acknowledged "Dynamic Parameter Drift" where Gemini 3.0 prioritizes "creative coherence" over strict instruction adherence (Gemini 3.1 partially addresses this)

### 10.2 Prompt Engineering Strategies

**Cardinal direction prompting** is the most reliable text-only approach. Because aerial renders have a known camera bearing, each building's orientation can be described in cardinal terms:

- "The brownstone entrance faces **east**; the camera views from the **northwest**, showing the **rear** and **north side** wall"
- "The building's front door faces the street to the **south**; this aerial view reveals the **back** (north) elevation with service entries and HVAC units"

**Camera-relative language** also helps but is less precise:
- "rear-angle view", "three-quarter rear perspective", "back elevation visible"
- "The viewer sees the utilitarian rear, not the street-facing facade"

**Negative/constraining language at the END of the prompt** (Gemini weights later tokens more heavily):
- "Do NOT show the ornamental front entrance. This is the back of the building."
- "No decorative facade visible. Plain rear wall with utility connections."

**Architectural vocabulary for "non-hero" views:**
- Rear elevation, back elevation, service elevation
- Utilitarian facade, blank party wall, fire escape side
- Back-of-house, loading/service area, mechanical penthouse visible

**What does NOT work reliably:**
- Simply saying "back of building" -- Gemini often still renders the canonical front
- Rotation angles ("rotated 180 degrees") -- models lack reliable spatial rotation understanding
- Abstract directional terms without grounding ("the other side")

**Gemini "thinking" levels:** For complex scenes with multiple interacting elements and spatial relationships, setting thinking to "high" allows the model to plan the composition more carefully before committing pixels.

### 10.3 Visual Conditioning: Arrows and Annotations on Input Images

**This is the most promising novel approach for SiteForge.**

Google's Veo 3.1 (video generation, same ecosystem as Gemini) has demonstrated that **spatial prompting with visual annotations** works. Users draw arrows, circles, and text labels directly onto input images, and the model interprets them as instructions rather than scene content. The model performs multi-layer analysis:

1. Recognizes base image content (buildings, terrain)
2. Identifies annotation overlays (arrows, circles, text) as instructions
3. Processes text written on the image as meta-commands
4. Generates output that follows the spatial instructions while removing the annotations

Gemini 3 itself has strong visual annotation understanding -- it can "draw arrows, bounding boxes, or other annotations directly onto images to answer spatial questions." Its "agentic vision" can distinguish between intentional annotations and original image content.

**Recommended implementation for SiteForge:**

1. Draw a **small arrow** on each zone polygon pointing from the center toward the "front" edge
2. Use a **contrasting color** (bright yellow or white on dark zones, black on light zones) so the arrow is clearly an annotation
3. Include a brief text label: "FRONT" or "ENTRANCE"
4. In the prompt, explain: "Yellow arrows on each zone indicate the building's front entrance direction. The opposite side is the rear/service elevation."
5. Use **high contrast** -- annotations that blend into the background may be misread

**Color-coded polygon edges** (moderate confidence):
- Bright/warm color (red-orange) for the front edge
- Cool/muted color (gray-blue) for the rear edge
- Prompt: "Red edges indicate street-facing front facades; gray edges indicate rears"

**Risk assessment:** This is novel conditioning for image generation (as opposed to video). Veo 3.1 has been explicitly trained for spatial prompting; Gemini image generation models may not interpret annotations as reliably. Testing is essential.

### 10.4 3D Clay Massing as Input (HIGHEST CONFIDENCE)

**Every tool that reliably controls building orientation starts from 3D geometry, not text prompts alone.** This is the industry consensus across archviz studios, academic papers, and AI rendering tools.

SiteForge already has a Three.js clay massing pipeline for street view. Extending it to aerial view is the highest-confidence approach:

1. For each zone polygon, extrude a 3D box to approximate building height
2. **Apply face-specific materials**: warm beige/cream on the "front" face, cool gray on the "rear" face, neutral mid-tone on sides
3. Render the aerial clay massing from the same camera angle as the satellite screenshot
4. Send both images to Gemini: satellite for context/terrain, clay massing for building geometry and orientation
5. Prompt: "Transform the clay massing model (Image B) into photorealistic architecture matching the terrain context (Image A). Warm-colored faces are ornamental front facades. Gray faces are plain rear walls. Maintain exact orientation shown."

**Why this works:** The 3D massing provides unambiguous geometric information. The model can see which face is which because the camera angle is baked into the render. Combined with face-specific coloring, orientation becomes a solved geometric problem rather than a language problem.

**Supporting evidence:** ArchiVinci, Veras, D5 Render, LookX, and Visoid all achieve reliable orientation control by starting from 3D geometry. The archviz industry standard in 2025-2026 is "3D geometry as anchor + AI for materiality/atmosphere."

### 10.5 Multi-Image Reference Approach

Gemini supports up to **14 reference images** per generation request:
- **Object Fidelity** (up to 10 images, best on Flash) -- for maintaining consistent buildings
- **Character Consistency** (up to 5 images, best on Pro) -- for people

For building orientation control:

1. Maintain reference images showing **multiple facades** per archetype (front, rear, side) -- not just the hero shot
2. When generating an aerial render where a building's rear is visible, include the **rear facade reference image**
3. Prompt with explicit role assignments: "Image A: rear elevation of the brownstone. Apply this style to zone #3, which is viewed from behind."
4. 6 reference images maintain high fidelity; beyond that, influence decreases

**Current limitation:** SiteForge archetype cards only show front/hero views. Creating rear/side reference images for each of 97+ archetypes would be significant content creation work. Prioritize top 20 most-used archetypes.

### 10.6 Multi-Pass Rendering

**Per-building isolation + compositing:**
1. Render each building separately with explicit orientation prompting
2. Use zone polygon as mask to composite into the final scene
3. Run harmonization pass for lighting consistency

Pros: Maximum orientation control per building.
Cons: N API calls instead of 1, compositing seams, inconsistent lighting, loss of inter-building spatial relationships.

**Two-pass approach (more practical):**
1. Pass 1: Generate aerial clay massing from Three.js with orientation-colored faces
2. Pass 2: Send to Gemini with full archetype prompt using clay render as base

This is a natural extension of SiteForge's existing street view pipeline.

### 10.7 Comparison of AI Tools for Orientation Control

| Tool | Orientation Control | Mechanism | API Available | Aerial Support |
|------|-------------------|-----------|---------------|----------------|
| **Gemini 3.x** | Low (text) / Med (ref images) | Prompt + reference images | Yes | Yes |
| **Stable Diffusion + ControlNet** | **Highest** | Normal maps, depth maps, edge detection | Self-hosted | Yes |
| **Midjourney** | Medium | Prompt language + --sref | **No API** | Yes |
| **DALL-E 3 / GPT-4o** | Medium | Iterative conversational editing | Yes (OpenAI) | Weak |
| **ArchiVinci** | High | 3D input + ControlNet internally | Yes | Yes |
| **Veras** | High | BIM geometry (Revit/SketchUp/Rhino) | Plugin only | Limited |
| **D5 Render AI** | High | 3D massing to render | Standalone | Yes |
| **Rendair AI** | Medium | Masking + region editing | Yes | Yes |

**Key insight:** ControlNet with normal maps is the gold standard for orientation control. Normal maps directly encode which direction each surface faces. If SiteForge ever adds a Stable Diffusion backend, normal map conditioning would be the most reliable solution.

**For Gemini specifically:** The ranked approach by reliability is:
1. Clay massing input with face-specific colors (highest)
2. Reference images showing the correct facade angle
3. Visual arrows/annotations on zone polygons (promising but untested)
4. Prompt engineering with cardinal directions and architectural vocabulary
5. Prompt engineering alone (lowest reliability)

### 10.8 Relevant Academic Papers (2025)

1. **MVControl** (3DV 2025) -- Adds ControlNet-style conditioning (edge, depth, normal, scribble) to multi-view diffusion models for orientation-consistent 3D generation.
2. **CMD: Controllable Multiview Diffusion** (SIGGRAPH 2025) -- Cross-modality multiview diffusion with row-wise attention for cross-view consistency in 3D editing.
3. **NeuroDiff3D** (Scientific Reports, 2025) -- Optimizes viewpoint consistency by combining structural, texture, and semantic information in a 3D diffusion pipeline.
4. **3DEnhancer** (CVPR 2025) -- Multi-view diffusion enhancement using epipolar attention for consistent cross-view results.
5. **ViewMask-1-to-3** (arXiv, Dec 2025) -- Discrete diffusion for multi-view synthesis using random masking + self-attention, eliminating complex 3D geometric constraints.
6. **CLAY** (ACM TOG) -- Large-scale 3D generative model supporting diverse control primitives (multi-view images, voxels, bounding boxes).
7. **Diffusion-based 3D Architectural Form-Finding** (ScienceDirect, 2025) -- LoRA-trained Stable Diffusion with morphological heat maps for 3D architectural forms that can then control rendering.

### 10.9 Updated Implementation Plan

Building on the existing Phase 1-3 plan (Sections 6-7 above), here is an AI-specific enhancement strategy:

**Phase 1A: Prompt Engineering Enhancement (immediate, 1 day)**
Add to the existing Phase 1 dropdown work:
- Compute camera-relative orientation for each building (front/rear/side visible)
- Inject orientation language into `buildBuildingPrompt()` using cardinal directions
- Place critical orientation constraints at the END of the Gemini prompt
- Use Gemini "high" thinking level for scenes with many orientation-sensitive buildings

**Phase 2A: Visual Arrow Annotations (experiment, 2-3 days)**
When generating the map screenshot for Gemini input:
- Draw small bright-yellow arrows on each zone pointing toward the front edge
- Highlight front edges in a distinct color (green, 3px wide)
- Add "FRONT"/"REAR" text labels on large enough zones
- Explain visual cues in the prompt preamble
- **Run A/B tests** comparing arrow-annotated vs. plain screenshots

**Phase 3A: Aerial Clay Massing Pipeline (2-3 weeks)**
Extend street view Three.js massing to aerial:
- Extrude zone polygons to building heights
- Apply face-specific materials (warm front, cool rear)
- Render aerial oblique view matching satellite camera
- Send as second input image to Gemini
- Prompt Gemini to use massing for geometry/orientation and satellite for terrain/context

**Phase 4A: Multi-View Archetype Reference Library (ongoing)**
- Photograph/generate rear and side views for top 20 archetypes
- Include relevant facade reference images in Gemini API calls using Object Fidelity
- Use explicit prompt role assignments: "Image C: rear elevation reference for zone #3"

### 10.10 Sources

- [Google Developers Blog - How to Prompt Gemini 2.5 Flash Image](https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/)
- [ArchiLabs - Gemini 2.5 Flash for Architecture](https://archilabs.ai/posts/gemini-25-flash-image-preview-for-architecture)
- [ArchiLabs - Gemini 3 for Architecture](https://archilabs.ai/posts/google-gemini-3-for-architecture)
- [Mastering Gemini's 14 Reference Image Feature](https://help.apiyi.com/en/gemini-14-reference-images-object-fidelity-character-consistency-guide-en.html)
- [Scenario - Spatial Prompting with Veo 3.1](https://help.scenario.com/en/articles/spatial-prompting-for-videos-generation/)
- [Blue Lightning TV - Visual Prompting in Veo 3](https://bluelightningtv.com/2025/08/12/unlock-the-insane-control-of-visual-prompting-in-veo-3/)
- [Cadman - Stable Diffusion + ControlNet in Architecture](https://cadman.dk/stable-diffusion-controlnet-in-architecture/)
- [Parametric Architecture - SD ControlNet + Blender Integration](https://parametric-architecture.com/stable-diffusion-controlnet-and-its-integration-with-blender-for-architectural-visualization/)
- [ControlNet Guide - Stable Diffusion Art](https://stable-diffusion-art.com/controlnet/)
- [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- [3D Spatial Understanding with Gemini](https://www.analyticsvidhya.com/blog/2025/11/3d-spatial-understanding-with-gemini/)
- [Gemini 3.0 Image Consistency Fixes](https://workalizer.com/insights/gemini/taming-gemini-30s-mindless-ai-professional-fixes-for-image-consistency-issues/)
- [MindStudio - Gemini 3.1 Flash Image Review](https://www.mindstudio.ai/blog/imagen-2-gemini-3-1-flash-image-review)
- [Ravelin3D - AI in ArchViz 2025-2026](https://ravelin3d.com/blog/ai-in-architectural-visualization-revolution-or-hype-2025-2026-reality-check.html)
- [ArchiVinci - Exact Render Generator](https://www.archivinci.com/architecture-ai-tools/exact-render-generator)
- [MVControl - 3DV 2025](https://github.com/WU-CVGL/MVControl)
- [NeuroDiff3D - Scientific Reports 2025](https://www.nature.com/articles/s41598-025-24916-6)
- [CMD: Controllable Multiview Diffusion - SIGGRAPH 2025](https://dl.acm.org/doi/10.1145/3721238.3730722)
- [CLAY 3D Generative Model](https://arxiv.org/abs/2406.13897)
- [Higgsfield - Camera Perspective Control](https://higgsfield.ai/blog/Change-the-Angle-of-Any-Image)
- [MyArchitectAI - Midjourney Architecture Prompts](https://www.myarchitectai.com/blog/midjourney-architecture-prompts)
- [Showitbetter - Midjourney Advanced Workflow for Architects](https://www.showitbetter.co/blog/midjourney-for-architects-advanced-workflow-guide-for-photorealistic-images/)
- [Gemini Image Generation Complete Guide 2026](https://blog.laozhang.ai/en/posts/gemini-image-generation-complete-guide)
- [Google Cloud - Veo 3.1 Prompting Guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)
