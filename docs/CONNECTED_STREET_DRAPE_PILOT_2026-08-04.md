# Connected street drape pilot — 2026-08-04

## Workflow fit

This pilot validates the public-realm portion of the intended Generate to 3D
workflow:

1. Buildings compile from City Prompt LEGO families.
2. A connected street network is rendered as one north-up AI material atlas,
   registered back to authoritative site coordinates, and clipped by the saved
   road polygons.
3. Deterministic 3D curbs, markings, roundabout planting, trees, lights,
   furniture, vehicles, and other street-family elements remain above the flat
   material skin.

The existing park system follows the same hybrid separation: a flat per-park
ground surface plus deterministic 3D park kits. The reference park pilot supplied
by Andrew on 2026-08-04 is the quality target for paths and planting beds; its
missing trees and furniture belong in the 3D kit layer rather than the raster.

**Non-negotiable coordination rule:** buildings, streets, pathways, parks, and
residual landscape are one site design. Provider limits may require separate
surface-class images, but they must never become independent designs. Every pass
must use the same authoritative geometry, site coordinate frame, building
entrances, circulation graph, archetype selections, grade/context capture, and
edge relationships. Separate hard masks provide control; a shared site contract
provides coherence.

## Pilot parcel and call ledger

- Project: `fc279bd0-8549-4607-811b-59606a2e6534`
- Authoritative boundary: 178.38 × 154.63 m
- Street polygons: 15
- Image calls used: 3 of the allowed 5
  - Gemini street-atlas candidate
  - GPT Image 2 street-atlas candidate
  - One Direct 3D photorealistic validation render
- Generated QA assets remain outside the source tree at:
  `C:\Users\andre\OneDrive\Documents\Playground\artifacts\connected-street-drape-pilot-2026-08-04`

## Result

GPT Image 2 was the better atlas provider for this geometry-locked task.
Gemini produced richer local asphalt weathering but changed street geometry and
introduced non-ground objects. GPT preserved the connected network, right-angle
junctions, compact roundabout, and site registration much more closely.

The reviewed GPT atlas was uploaded once and attached to all 15 roads through a
shared geographic UV contract. Procedural asphalt and sidewalk bands are hidden
when that atlas is current, while the useful 3D detail layers remain. The live
Google Tiles review showed continuous intersections and a materially more
credible public realm. The final Direct 3D render retained realistic streets,
curbs, crossings, the roundabout, landscape, and the LEGO building layout.

## Source changes

- `scripts/_pilot_connected_street_drape_ab.py` creates the authoritative
  diagram, hard mask, five-call ledger, provider A/B outputs, registration, and
  clipped QA previews.
- `streetNetworkGroundTexture.ts` owns atlas placement, staleness signatures,
  authenticated loading, one-document upload, and road metadata persistence.
- `GlobeZoneLayer.tsx` maps the shared atlas across individual road meshes.
- `GlobeStreetDetailLayer.tsx` keeps 3D street details but does not cover an
  active atlas with procedural flatwork.
- The development-only Generate to 3D control imports a reviewed atlas for live
  validation without spending another image call.

## Remaining work to reach the product workflow

### Implemented on the pilot branch

- The normal **Generate to 3D** action now freezes authoritative zone
  revisions, generates missing/stale drapes, reloads the revisions written by
  those image jobs, and only then compiles LEGO buildings plus park/street 3D
  kits. The old Render-panel upgrade is no longer required for this workflow.
- The complete active street network uses one GPT Image atlas call regardless
  of polygon count. Parks currently use one geometry-locked Gemini call each.
- Current drapes are signature-checked and reused on retry, preventing a
  failed Community 3D compile from automatically spending the same image calls
  again.
- The signed-in live trial on project
  `482d8897-af45-4d74-b46d-55d2b3dfcfa5` completed one street atlas, one park
  drape, and the subsequent 2/2 ground-system compile without the previous 409
  source-revision failure.

### Still required

1. Move the browser-orchestrated drape sequence into a durable backend job so
   it survives navigation and can expose provider cancellation/recovery.
2. Generate coordinated public-realm inputs from the whole site: buildings and
   their entrances, streets, parks, residual landscape, Google Tiles context, and
   archetype references. Keep separate hard masks per surface class even if one
   coordinated context image is used.
3. Persist an atomic public-realm revision so a partially updated network can
   never mix old and new atlases.
4. Extract or retain semantic placement zones for the 3D kit layer. Trees,
   benches, lights, shelters, play/sports equipment, and pavilions must be
   weighted by archetype and blocked from carriageways, paths, entrances, and
   building clearances.
5. Add geometry and visual QA gates before accepting a paid output: network
   connectivity, mask leakage, registration drift, invented objects, road/park
   area coverage, and comparison against archetype imagery.
6. Extend the same coordinated drape contract to the residual area inside the
   site boundary so empty space is intentionally landscaped instead of receiving
   a generic procedural fill.
