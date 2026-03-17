# Viewpoint Street Render — Claude Code Instructions

## What this adds

Two new files that let users drop a pin anywhere on the 3D massing map,
fly to a street-level camera at that point, and generate a photorealistic
render of that specific viewpoint using FLUX.1 Depth.

The result is a panel on the right side of the map (the existing aerial
render panel stays on the left) showing a list of saved viewpoints.
Each one can be previewed, renamed, rendered, and downloaded independently.

---

## Files to add tonight

Add these two new files to the SAME folder as the existing map component
(same place you put useAIRender.ts and AIRenderPanel.tsx earlier):

| File | What it does |
|---|---|
| `useViewpointPicker.ts` | Hook — manages pins on the map, fly-to preview, direction arrow |
| `ViewpointRenderPanel.tsx` | UI panel — viewpoint list, style picker, render button |

Then REPLACE the existing map component with the new version:

| File | Action |
|---|---|
| `MapboxTiltedAerialReplacement.tsx` | Replace existing file |

---

## Step by step for Claude Code

Paste this message into Claude Code:

---

I have three new files to add to the project for a street-level viewpoint
render feature. Please:

1. Add useViewpointPicker.ts and ViewpointRenderPanel.tsx to the same
   folder as the existing map component and the other render files

2. Replace MapboxTiltedAerialReplacement.tsx with the new version

3. Run tsc --noEmit to check for TypeScript errors and fix any found

4. Confirm the following are all in the same folder:
   - useAIRender.ts
   - useViewpointPicker.ts
   - AIRenderPanel.tsx
   - ViewpointRenderPanel.tsx
   - MapboxTiltedAerialReplacement.tsx

5. Confirm done

---

## How the feature works (for your reference)

1. User opens the app — two panels are now visible:
   - Bottom LEFT  → aerial massing render (existing)
   - Bottom RIGHT → street viewpoint render (new)

2. User clicks "+ Add viewpoint pin" in the right panel

3. The cursor changes to a crosshair

4. User clicks anywhere on their development site on the map

5. A pin drops with a yellow direction arrow showing which way the camera faces

6. The map automatically flies to street level at that point (62° pitch,
   zoom 18.5) so the user can see exactly what the render will look like

7. The direction arrow on the pin can be dragged left/right to rotate the
   camera bearing before rendering

8. User picks a style and clicks "Render [viewpoint name]"

9. The AI generates a street-level photorealistic render — same FLUX.1
   Depth pipeline as the aerial render but with street-level prompts

10. Result appears in the panel with a Save button

11. User can add multiple viewpoints — each saves its own render result

12. "↑ Aerial" button in the panel header returns to the massing view

---

## Key differences from the aerial render

The street render uses different prompts — it drops "aerial oblique view"
and uses "street level architectural photography, eye level perspective,
pedestrian scale, activated ground floor" instead.

lockPitchForCapture is set to FALSE for street renders — the map is
already at street pitch when the user hits render, so no pitch adjustment
is needed before screenshotting.

Street renders do NOT create a map overlay (unlike aerial renders which
pin the image to geographic bounds). Street renders are standalone
presentation images — they appear in the panel and can be downloaded.

---

## Troubleshooting

If the pin does not appear after clicking:
→ Check browser console for Mapbox marker errors
→ Ensure mapboxgl CSS is imported

If the camera does not fly to street level after placing a pin:
→ The map needs maxPitch set to at least 70 — this is already set in
  MapboxTiltedAerialReplacement.tsx but worth confirming

If TypeScript errors reference Viewpoint type not found:
→ Ensure useViewpointPicker.ts is in the same folder and the import
  path in ViewpointRenderPanel.tsx matches
