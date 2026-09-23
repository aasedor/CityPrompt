# Generate 3D Site Landscape — local prototype

Initiative: `codex/site-landscape`, based on the local lightweight-tree pilot.
This is a student ideation feature, not construction or landscape-design compliance.

**Current behavior supersedes the original cutout design below:**
[the live continuous-base pilot](SITE_LANDSCAPE_BASE_PILOT_2026-09-20.md) uses
GPT Image 2.5 Flare at 26 app credits. Custom artwork is a continuous ground base
beneath the separately rendered objects. Tree placement still respects plots and
routes. A six-metre inward band blends to colours sampled from surrounding tiles.
The three bounded real calls, current saved result and remaining ground-height gap
are recorded there. Older simulated-only and pending-live statements below describe
the earlier implementation, not the current verification status.

## Student workflow

Open **1 Site → Review site boundary → Finish your site**. Choose
**Neighbourhood gardens**, **Natural landscape**, or **Urban landscape**, then
**Generate 3D Site Landscape**. The top-down preview is free for these presets.
**Apply landscape** installs the ground treatment, tree groups and low shrubs.
**Discard** preserves the existing landscape. **Remove landscape** and Apply
participate in the existing Undo/Redo history. Saved landscapes reopen with the project.

The optional **Custom ground treatment** accepts a brief and displays the current
image-model token cost (13 tokens in this verification). Generation spends those
tokens on the preview, not on Apply. It uses the existing budgeted render endpoint
implementation and file storage. Custom artwork is a flat surface: a pool concept
can appear in its materials, but physical depth, walls and structures need an
appropriate 3D archetype. The three free presets provide actual 3D trees and shrubs.

Currently supported: an active **prepared site** boundary with authored objects.
Following natural terrain is deliberately unavailable for this surface feature.
Existing prepared-site edge grading and level-pad limitations remain.

## Shared implementation

### Development and surrounding context

Custom generation now requires an actual 3D scene reference in addition to the
parcel template. The capture automatically frames the complete boundary with
at least 35 m of neighbourhood margin (20% of the larger parcel dimension for
larger sites), faces north, waits for current tiles/ground and hides editor
overlays. It restores the previous camera and controls, including on failure.
The reference shows authored buildings, streets and parks within their Google
3D context. Insufficient visible context blocks generation before a paid call.

The image provider receives two distinct inputs: the **LANDSCAPE PLAN** controls
output extent, orientation and protected areas; the **NEIGHBOURHOOD APPEARANCE
REFERENCE** informs paving hues, restrained grass colours, planting character,
material scale and transitions at site edges. The prompt includes metric parcel
dimensions and counts of the authored object types. It explicitly avoids copying
temporary empty-site lawn, construction rubble, tile defects or baked shadows.
The existing hard mask still prevents painting outside the parcel or across
archetypes and access routes. Context pixels are reference evidence, never a
replacement texture pasted over the neighbourhood.

The preview request sends `context_image_base64` only for custom generation.
The server validates/resizes the image before calling the budgeted renderer and
stores its SHA-256 and scene identity in `surface_context`. Missing context is a
422 response with no provider call. The render adapter labels this input as
appearance context, not an archetype or a previous render that controls geometry.

Browser continuation: actual Currie reference captured from an initially zoomed
view, sent through the preview endpoint to a simulated provider, inspected, then
discarded. HTTP 200, 3,001,008 encoded reference bytes, exact camera restoration,
no browser errors. Evidence: `landscape-neighbourhood-reference.png`,
`landscape-context-guide.png`, `landscape-context-verification.json` in the same
external artifact directory. An initial unavailable road-ground state blocked
the call; reload and a settled Design view recovered without source changes or
relaxing capture checks. Live AI material/planting quality remains unverified.

Compiled objects must also be represented by visible pixels in the reference.
The capture temporarily shows hidden building models and restores their original
visibility. A second browser check started with models hidden, intercepted the
outbound preview with a deliberate 409 to prevent generation, and confirmed a
complete reference, exact camera restoration and restored hidden-model setting.
The expected 409 console entry belongs only to that simulated rejection.
Final continuation checks: 63 backend tests, 38 frontend tests, TypeScript and
changed-file ESLint passed. Evidence: `landscape-context-inventory-verification.json`.

### Geometry, persistence and capture

- Backend `services/site_landscape.py` reuses the residual-landscape solver.
  The exact irregular boundary minus authored plots and buffered access corridors
  defines the eligible surface. Trees retain full canopy clearance; planted beds
  are clipped to that same remainder. Presets share one deterministic recipe.
- Frontend `features/siteLandscape/siteLandscape.ts` obtains the current building
  approaches and park connections from the existing shared route resolvers.
  Corridors protect the complete route width plus a margin, including its ends.
- `POST /api/v1/site-landscape/{boundary_id}/preview` checks the complete scene's
  revision set. Preview does not change any zone. A signed, expiring preview binds
  the boundary, geometry and object properties. Apply rechecks the scene under the
  project's write lock and rejects changes made since generation.
- Apply modifies only the boundary's `community_3d_landscape` and mode properties.
  Object edits invalidate the landscape; entrance/route/variant changes do so too.
  A stale landscape is not rendered as current; students can regenerate it.
- The prepared ground material owns the texture; no clickable overlay covers
  objects. Custom images are clipped on the server, feathered inward, and clipped
  again to eligible regions when composing the client texture. North-up artwork
  is flipped once into the existing geographic texture coordinate convention.
- Protected artwork is fetched through the authenticated API. Expiring download
  tickets are removed before this fetch; deployment URLs resolve to the API's
  configured origin. Signed previews bypass the response helper that normally
  decorates asset URLs, because changing the payload invalidates its signature.
- Export rejects custom textures that are loading or failed. Late image responses
  cannot replace a newer texture after editing or navigation.

## Verification evidence

Disposable Currie project: `7e1e9037-b98c-4d18-8502-839160315869`.
Irregular prepared parcel, eight homes, one street and one existing rustic park.
Protected reference projects were not modified.

- 37 focused backend tests passed: site landscape, residual landscape, site-zone
  utilities. Includes protected holes/routes, clipping, expiry/tampering, changed
  context, browser number serialization, nonfinite inputs and mocked provider/storage.
- 31 focused frontend tests passed: landscape protection/capture, residual texture,
  asset access, and signed-preview response preservation. TypeScript and changed-file
  ESLint passed.
- Browser: all three presets preview; discarded previews preserve the saved recipe;
  Apply, Undo/Redo, Remove/Undo and reload work. The 10 non-boundary objects retain
  exactly their original coordinates and properties.
- Custom path: a deterministic simulated provider image passed through the actual
  preview endpoint, clipping, object storage, signed Apply, authenticated texture
  loading, reload and exact export. No image-generation credits were spent.
  Live provider output quality, prompt adherence and a real pool concept are
  **NOT TESTED**. Do not treat the synthetic colour blocks as design artwork.
- Final gardens export: 3.289 seconds on this local run; custom simulated export:
  2.814 seconds. No browser page/console errors or grounding issues in the successful
  custom run. These are observed runs, not performance guarantees.
- Initial test configuration pointed at an asset folder missing the park's GLBs.
  Correcting it to the established external public directory restored the pavilion,
  equipment and trees without changing source or park data. HTTP status alone is
  insufficient: Vite can return HTML with status 200 for missing asset paths.

External evidence (not source assets): `C:/dev-artifacts/CityPrompt/` files
`landscape-final-oblique.png`, `landscape-final-top.png`,
`landscape-export-preview.png`, `landscape-exact-view.png` (downloaded PNG), `landscape-verification.json`,
`landscape-final-recovery.json`, `landscape-custom-verification.json`, and
`landscape-custom-export-simulated.png`.

## Local restart and remaining work

The original server remains on 5174/8000. Automatic approval review rejected
restarting that process, so verification used a separate server on **5175/8001**.
The external `landscape-server.py` harness uses the isolated classroom database
and disables paid providers. Its optional simulated-image switch was used only
for integration verification and is off after testing.

Frontend environment for this worktree:

```powershell
$env:CITYPROMPT_PUBLIC_DIR = 'C:/dev-artifacts/CityPrompt/student-design-transformation/public'
$env:VITE_ENV_DIR = 'C:/Users/andre/OneDrive/Documents/CityPrompt/frontend'
$env:API_PROXY_TARGET = 'http://127.0.0.1:8001'
npm run dev -- --host 127.0.0.1 --port 5175 --strictPort
```

Before publishing: review the gardens result with the user and run one bounded
live custom-image pilot in a provider-enabled environment. Record image fidelity,
token charge and failure recovery. Natural-terrain surfaces and generated physical
amenities are future features. This delivery does not approve new catalogue assets
or publish this branch or its inherited tree pilot.
