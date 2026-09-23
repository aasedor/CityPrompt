# Continuous site landscape base — live pilot

Local initiative: `codex/site-landscape` in `C:/dev/CityPrompt-grounding-edit-race`.
The user requested real image calls, selected GPT Image 2.5 as the landscaping
standard, and changed the design to a continuous base beneath the 3D objects.
They also requested feathering into the surrounding Google tiles.

## Current behavior

- Custom landscaping uses `gpt-image-2.5-flare`, high quality, one output and
  **26 app credits**. Free presets remain free. Other render workflows retain
  their existing model choices.
- The first image is a continuous parcel template at its physical aspect ratio.
  The second image shows the development and Google tiles for appearance only.
  A ground-specific final prompt overrides conflicting requests to draw buildings,
  roads, park layouts, shadows or interior object cutouts. Ordinary scene renders
  still use their existing design-preservation lock.
- New recipes store `surface_mode: site_base`. Artwork covers the parcel beneath
  the independently rendered buildings, street, park and connections. The same
  protected remainder still controls tree/planting placement. Old recipes keep
  their original cutout behavior.
- The capture samples adjacent context four metres outside the boundary. It uses
  the actual camera matrices and ignores proposal pixels and nearly empty pixels.
  This pilot obtained **251 colour samples**. A six-metre inward band smoothly
  blends the new ground into those local colours; the parcel mesh remains bounded.
  Only colour is transferred, not neighbouring roofs or other objects.
- Transparent provider pixels remain transparent. The original compositor had
  replaced their alpha, creating black gaps in the first GPT result; this is fixed.
- The displayed credit balance refreshes after generation, including failures.

## Three bounded paid calls

| Trial | Model | App credits | Observed duration | Result |
| --- | --- | ---: | ---: | --- |
| Original cutout comparison | Gemini 3.1 Flash Image | 13 | 39.0 s UI round trip | Layout aligned; large decorative planting islands |
| Same inputs | GPT Image 2.5 Flare | 26 | 26.3 s service round trip | Better landscape appearance, but shifted objects; rejected, never applied |
| Continuous base plus colour feathering | GPT Image 2.5 Flare | 26 | 25.8 s UI round trip | Ground only, applied under the existing neighbourhood |

These durations include different local request paths and are not benchmark claims.
The comparison GPT call invoked the app's landscape service with the exact saved
inputs and its normal billing/storage pipeline. The other two calls used the UI.
All three completed audit reservations. Balance: **4,122 → 4,057**, total **65**.
App credits are not an exact provider invoice. No retries or additional paid calls.
Paid providers are disabled again in the local QA harness.

## Verification

Disposable Currie project: `7e1e9037-b98c-4d18-8502-839160315869`, prepared irregular
4.3 ha boundary, eight homes, one street, one rustic park. All ten authored objects
retain their coordinates and properties. The continuous base is currently applied.

- UI Generate/Apply, Undo to the previous Gemini surface, Redo to the GPT base,
  reload, authenticated texture loading and exact PNG export passed.
- Exact export: **2.822 seconds**. No page errors or grounding issues in this run.
- Reloaded recipe matches after canonicalizing the optional expiring asset-ticket
  query string. The texture loader already removes tickets before authenticated fetch.
- 42 focused backend tests and 24 focused frontend tests passed; TypeScript and
  changed-file ESLint passed. Tests cover full-base coverage below objects, retained
  tree/access exclusions, provider alpha, context-colour blending, outside probes in
  both windings, GPT cost/model and the ground-only provider prompt.
- Existing protected projects were not changed. Nothing was pushed.

## Remaining visual limitation

Colour feathering is implemented. **Ground-height continuity is not solved by it.**
The saved prepared parcel has no measured retaining-edge profile. Its existing
white strip is a view through a gap in the ground geometry, confirmed by temporarily
changing the scene background to magenta and restoring it. Review ground reports
up to about 6.4 m of fill and 3.8 m of cut around the boundary relative to visible
tile surfaces. These are photogrammetry measurements, not a survey.

No site levels, objects or retaining profiles were changed for this image test.
Next useful improvement: a measured ground-edge transition that closes these gaps
without moving objects or replacing the colour blending with a large flat apron.
Do not describe the current result as a seamless terrain merge. Natural terrain
surfaces and physical pools/amenities remain outside this prototype.

## Evidence outside the source tree

`C:/dev-artifacts/CityPrompt/site-landscape-live-pilot/` preserves both original
comparison inputs, raw outputs, credit records, previews and Gemini screenshots.

`C:/dev-artifacts/CityPrompt/site-landscape-base-pilot/` contains the final input
template, context, edge samples in `preview-request.json`, raw provider output,
feathered preview, before/after zones, `gpt-oblique.png`, `gpt-exact-export.png`,
`final-verification.json`, and the reversible edge-gap diagnostic.

Do not rerun `call.cjs` or provider launchers without a newly bounded live trial.
Use the existing 5175/8001 test-server setup and external public asset directory
documented in `SITE_LANDSCAPE_2026-09-20.md`.
