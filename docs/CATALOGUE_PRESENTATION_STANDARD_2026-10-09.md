# Catalogue presentation standard

The active picker has 148 exact choices: 69 buildings, 38 parks and 41 streets.
The presentation layer gives each choice a reviewed photographic hero, a
consistent name and short description, and curated search/style tags.

This pass generated 45 replacements, reused 7 existing photographs and retained
96 suitable images. All 148 selected URLs were fetched from the local app and
decoded successfully. See `CATALOGUE_PRESENTATION_AUDIT_2026-10-09.json` for the
exact selection, image hashes, generation briefs and style-correction evidence.

## Hero standard

- One realistic architectural or landscape photograph from a pedestrian view.
- Natural daylight and colour, readable subject, believable materials and context.
- Preserve the reference archetype's defining form, roof, programme and materials.
- No reference boards, collages, aerial diagrams, studio models or technical
  cross-sections as the main card image. Street cross-sections remain in the card.
- Existing suitable photographs can remain; lighting need not be identical.
- Hero images are illustrative catalogue views. The placed model and its saved
  geometry remain authoritative for a student's design.

`frontend/src/data/catalogueHeroImages.json` maps exact placement IDs to selected
URLs. `pickerHeroImages.ts` retains older review-choice mappings as fallbacks.
The selected new images have full-resolution WebP delivery copies at quality 90;
the original PNGs and generation evidence are retained outside the source tree.
New WebPs are stored using Git LFS under the three authoritative archetype roots.

## Text and tags

`frontend/src/data/cataloguePresentation.json` contains display-only names,
descriptions, style IDs and search tags for every active placement. Names use
consistent title casing; descriptions explain the design and useful constraints
without internal validation or compiler language. Useful programme terms,
including affordable housing and non-market housing, remain searchable.

The card, search and style filters use these exact-choice fields. Original
registry objects, generation tags, source images, variants, dimensions, zoning
classifications and saved properties remain unchanged. A corrected style must
also supersede stale parent appearance tags in search. Unclassified styles stay
unclassified rather than being guessed from a material or use.

## Adding future choices

1. Add an exact placement entry to both presentation manifests.
2. Reuse a suitable exact-archetype ground-level photograph if one exists.
   Otherwise generate and review a single photographic view using its locked
   references, preserving the model/source assets.
3. Keep original generations and contact sheets outside the source tree;
   promote only the reviewed web-delivery image.
4. Run the focused card, hero, presentation, facet and catalogue tests, TypeScript
   checks, and `scripts/tests/test_validation_bundle.py`.
5. Regenerate the runtime asset manifest and verify all selected image URLs load
   as real decoded images. The validation supplement derives required hero paths
   from the manifest; it no longer assumes a fixed count of twelve.

Local audit and generation evidence:
`C:/dev-artifacts/CityPrompt/catalogue-consistency-2026-10-09/`.
This work is local; publishing requires a separate requested push/deployment.
