# Realistic People picker — local delivery

Local branch `codex/people-picker-realism-20261023`, based on `497cf0b68`.
The user approved Maya's photoreal pilot, then corrected the repeated generic
overshirts and requested different clothes and styles. The selected finite set
now includes dresses, shorts, athletic clothing, hoodies, knitwear, linen,
office tailoring, denim, outerwear and a polo. Maya and Clara retain reviewed
portraits; 21 other selected images use the varied-wardrobe direction.

## What changed

- Separate `peopleAppearancePreviews.json` maps 23 stable IDs to realistic
  name/style previews. Original `peopleCatalogue.json`, GLBs, model thumbnails,
  rigs, transforms, saved actions, backend and render prompts are unchanged.
- Picker cards use taller portrait framing, appearance names/styles, accurate
  accessible names and an AI appearance preview label. Style names are searchable.
  Original runtime labels continue to identify the existing 3D models.
- Preview URLs take precedence over original model captures in the existing
  lazy thumbnail path. Browsing requires no GLB decode. Other detail categories
  keep their existing previews and controls.

These are imagined appearances and wardrobes, not exact 3D captures or guaranteed
AI output identities. The new images are not automatically sent to image/video
providers as character references. That behavior was not part of the picker-only
request. The card explains that placed people use simplified 3D models.

## Assets and provenance

The image tool was built-in `image_gen`; no CityPrompt paid render/API key was
used. Selected generation records and originals are preserved outside the repository:
`C:/dev-artifacts/CityPrompt/people-picker-realism-2026-10-23/`.
`appearance-provenance.json` records prompt, raw output hash, unchanged model/
source-thumbnail hashes and each reviewed derivative. `appearance_styles.json`
records the chosen wardrobe brief per character. Earlier generic alternatives
are preserved in separate receipts and are excluded from the selected manifest.

Runtime files use the current external public directory:
`C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/public/street-kits/people-appearance-v1/`.
All 23 WebPs are 480×600, total **238,348 bytes**, maximum **14,332 bytes** each.
Only format/size optimization was applied to reviewed originals; no crop.
This is compressed download size, not decoded image memory or an FPS benchmark.

Portable local backup: external `people-appearance-v1-local.zip`, containing the
23 WebPs and detailed provenance. SHA-256:
`696222c7e3899086c1989e8afe11ef2298ed5d2829610b90a798b432b7277bff`.
Heavy assets remain outside Git. This is local availability, not a hosted release.
Production publication still needs the established approved storage/release path.

## Checks actually run

- Observed failing→passing tests for preview precedence without geometry loading,
  unchanged model URLs/rig data, honest labels, new style search and accessible
  card names. Final focused frontend run: **50 tests in 10 files passed**.
- `npm run type-check` passed; scoped ESLint and `git diff --check` passed.
- HTTP verifier: **23/23** valid WebP responses with exact manifest hashes and
  byte sizes; **23/23 GLBs and 23/23 original thumbnails unchanged**.
- Actual local browser: all 23 cards loaded and decoded at 480×600 while scrolling;
  search `summer dress` found Sofia, and choosing her selected the existing
  Sofia placement model. Stopped placement without adding scene data.
- Reload retained the three existing test people. API readback confirmed revision
  7, actions waving/standing/waving and original 15° rotations, with exact per-ID
  persisted values. No real user/live scenes were altered.
- Independent review verified hashes, selected visual samples, tests and type
  check. Two minor search/accessibility findings were fixed and independently
  rechecked (14 affected tests passed). No P0/P1 remained.
- Full-size generation outputs and the complete compact contact sheet were
  visually inspected for wardrobe variety, full bodies, shoes and obvious defects.

No new paid AI render was run. No production build, deployment, student-laptop
or mobile FPS claim is made for this picker-only update; the production code was
type-checked and tested. No push or deployment was performed.

## Trying it

Open `http://127.0.0.1:5184/projects/b5a05da9-df26-4b40-83be-1ccbaaba2293`,
then Design → Add details → People. The browser is left on this gallery.
The external folder includes `picker-live-local.png`, the 23-image browser decode
receipt `picker-browser-images.json`, and `people-appearance-contact-sheet.jpg`.

Recheck delivery with:
`python tools/people_pilot/verify_appearance_previews.py`.
