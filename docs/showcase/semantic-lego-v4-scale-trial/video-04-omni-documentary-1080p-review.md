# Omni documentary trial v004 — builder review

## Scope

This is a scoped source-video finishing trial, not a holistic RLASM keeper
review. The deterministic four-second City Prompt route clip is the geometry,
camera, material-identity, terrain, and context authority.

## Technical result

- Model: `gemini-omni-1.1-flash`
- Task: video edit
- Requested and returned: 1920×1080, 24 fps, 4.0 seconds
- Delivery: stored URI, downloaded once after the single successful generation
- Audio: effectively silent AAC stereo
- Fidelity: 71.4 average, 57.1 minimum, `review`
- Temporal consistency: 80.5

## Visible gains

- The three distinct whole-bay building assemblies and their open separations
  remain clearly legible.
- Roofs remain flat in character instead of becoming the hipped roofs seen in
  v001.
- The green storefront identity remains recognizable.
- The pale site apron is integrated into plausible public-realm surfaces.
- The result is calmer and more photographic, with coherent daylight and
  materially improved contact.

## Blockers

### P0

- Source-frame and camera registration drift progressively. The measured score
  falls from 82.0 at the first checkpoint to 57.1 at the final checkpoint.
- Roof construction and facade geometry are reinterpreted rather than copied
  exactly from the deterministic source.

### P1

- Parked cars and rooftop equipment are invented despite the no-new-objects
  instruction.
- Roof finish, parapets, storefront details, and surrounding site surfaces are
  materially changed.

## Decision

`visual_rework_required`. The stable-model and 1080p delivery changes pass
their scoped technical gate, but this output is not source-locked evidence and
cannot be promoted as a keeper.
