# People campus/fashion previews — local delivery

Ten picker portraits revised: Noah, Leo, Ava, Nina, Jules and Rhea gain more distinct casual silhouettes, shoes and accessories; Amara, Kai, Sana and Felix gain adult university-student outfits and warmer smiles. Thirteen other approved portraits remain identical. All 23 source GLBs, source thumbnails, dimensions, actions and stable IDs remain unchanged. This is picker imagery, not new backpack/clothing geometry or a guarantee of AI-render identity/wardrobe.

The fashion direction drew on [Vogue wide-leg denim](https://www.vogue.com/article/how-to-style-wide-leg-jeans-street-style), [Copenhagen street-style photography](https://www.vogue.com/slideshow/goddag-the-best-street-style-from-the-spring-2026-ready-to-wear-shows-in-copenhagen), [Who What Wear London street style](https://www.whowhatwear.com/fashion/street-style/london-fashion-week-street-style-trends-september-2026) and [Salomon's official sport footwear context](https://www.salomon.com/en-ca/lp/g/icons-speedcross). These inform broad visual directions, not copied branded garments or endorsements. Each new image has an individual exact prompt and existing fictional-person portrait reference.

Source changes: `peopleAppearancePreviews.json` selects versioned local WebPs; `appearance_styles.json` records the ten wardrobe briefs; `prepare_fashion_previews.mjs` verifies immutable inputs, snapshots baseline registries, prepares deterministic compact derivatives and records provenance. The thumbnail test now verifies the exact appearance-overlay URL and supports versioned previews rather than assuming v1 forever. No production TypeScript behavior changed in this initiative.

External output: `C:/dev-artifacts/CityPrompt/people-fashion-2026-10-23/` contains full prompt receipts, selected raw originals, prior manifest/style snapshots, source/reference/derivative hashes, contact sheets and browser evidence. Runtime ten new WebPs: `C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/public/street-kits/people-appearance-v2/`. All 23 selected WebPs total 269,604 download bytes; ten revised images total 133,850 bytes. These are compressed file sizes, not decoded/GPU memory or FPS claims.

Verification completed:

- Read-only HTTP verifier: 23/23 WebP responses, MIME/signatures/hashes/bytes; 23 unchanged GLBs and 23 unchanged source-thumbnail hashes.
- Actual local browser picker: all ten revised images decode 480×600. Searching `campus` returns exactly Amara, Kai, Sana and Felix. Proof: `campus-picker-local.png` and `browser-fashion-images.json` in the external output directory.
- 16 narrow tests in catalogue/thumbnail/placement-panel files; Node syntax check and diff check pass. Initial thumbnail test correctly failed because of its hard-coded v1 assumption, then passed with exact-overlay/version-aware validation.
- Independent reviewer: no actionable findings; exact ten changed/thirteen retained, original/provenance hashes verified, campus sheet reviewed, 14 independently selected tests pass. Generator error/idempotency paths reviewed statically.
- Prior walking initiative separately checkpointed at `708f7f551`; its saved local walking action survives reload, revision8, three original actors and all other fields intact.

Try locally: open `http://127.0.0.1:5184/projects/b5a05da9-df26-4b40-83be-1ccbaaba2293`, Add details → People, search `campus` (or a person's name). The browser is left on the campus previews. Local only; no push, hosted asset publication, deployment or paid app generation. Accessibility, seniors and family models requested afterwards are a separate scope and are not claimed as delivered here.
