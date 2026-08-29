# RLASM v5 — identity-corrected new three

This phone-viewable package supersedes the fire-station entry in
`rlasm-new-three-material-corrected-2026-08-29`.

The station and hospital candidates are unchanged. The Second Empire fire
station advances from v12 to v14 because the v12 crest was a role-specific but
still-oblique crop of the locked facade image. v14 uses a source-conditioned,
front-elevation carved relief sticker registered inside the physical crest
carrier at its native aspect ratio.

## Start here

- [Three-building phone index](rlasm-v5-three-new-buildings-phone-index.png)
- [Fire-station v14 phone comparison](10-second-empire-fire-station-rlasm-v14-phone-comparison.png)
- [Fire-station v14 registered orthographic crest](10-second-empire-fire-station-rlasm-v14-registered-orthographic-crest.png)
- [Fire-station v14 straight-on crest proof](10-second-empire-fire-station-rlasm-v14-facade_close.png)
- [Locked source facade](10-second-empire-fire-station-rlasm-v14-locked-source-facade.png)

## Fire-station v14 evidence

- Exact locked facade, 60-degree and topology sources are recorded by bytes and
  SHA-256 in the [prework manifest](10-second-empire-fire-station-rlasm-v14-prework-manifest.json).
- The exact ImageGen prompt, input roles/hashes, raw output, deterministic
  export-padding crop, registered hash, carrier, UV dimensions and review view
  are recorded in [crest provenance](10-second-empire-fire-station-rlasm-v14-crest-provenance.json).
- The full build contains 11 reviewed renders, one registered identity and zero
  generic fallbacks; see [builder evidence](10-second-empire-fire-station-rlasm-v14-builder-evidence.json).
- The builder identity review passes centering, full-edge visibility,
  perspective-fragment rejection and identity-hash verification; see
  [builder review](10-second-empire-fire-station-rlasm-v14-builder-review.json).

Useful views:

- [front](10-second-empire-fire-station-rlasm-v14-front.png)
- [front corner](10-second-empire-fire-station-rlasm-v14-front_corner.png)
- [aerial](10-second-empire-fire-station-rlasm-v14-aerial.png)
- [glass close](10-second-empire-fire-station-rlasm-v14-glass_close.png)
- [roof/cupola close](10-second-empire-fire-station-rlasm-v14-architecture_close.png)
- [locked source board](10-second-empire-fire-station-rlasm-v14-locked-source-board.png)

## Method update

- [RLASM latest method v5](RLASM_LATEST_METHOD_V5.md)
- [RLASM proven build recipe v5](RLASM_PROVEN_BUILD_RECIPE_V5.md)

The new reusable rule is: when an exact emblem exists only in an oblique
reference, create a source-conditioned orthographic identity derivative rather
than projecting the oblique crop. Preserve prompt and hashes, remove only
export padding, retain native aspect, mount it to a real physical datum, and
prove all four registered edges in a straight-on close view.

## Status

Builder material, envelope and identity review: **pass**.

Keeper status: **false** until a separate reviewer records zero P0 blockers.
