# Catalogue contributor guide

This is the handoff for expanding City Prompt's building, park/plaza and
street/pathway catalogue. Start from the latest `origin/main` in
[aasedor/CityPrompt](https://github.com/aasedor/CityPrompt). Use a separate named
branch or worktree for each initiative.

## Prompt to give your coding assistant

> Read AGENTS.md, CLAUDE.md and docs/CATALOGUE_CONTRIBUTOR_GUIDE.md. Help expand
> City Prompt's catalogue according to this guide. Begin by inventorying runtime
> assets, existing candidates and missing files, then propose a gap table and one
> representative pilot. Do not recreate existing candidates, start paid generation
> or publish unapproved families. Continue unpaid investigation and validation
> while identifying the files, approvals and budget needed.

## Product vision

City Prompt helps university urban-planning students “build the city you want to
live in.” The January 2027 class has 60 students working in groups of about eight
on community master plans for real sites. Site context and elevation matter:
proposals appear in Google's 3D tiles environment.

The primary desktop/tablet workflow is **pick, place and reshape**:

1. Choose a building, park/plaza or street/pathway.
2. Place it, then resize, rotate or reshape it.
3. Automatic 3D updates save its current representation.
4. Frame a view and render images or videos for a presentation.

Catalogue assets do not require a separate Generate to 3D step. Keep choices and
controls intuitive and uncluttered. Planning guidance should help students explain
how to realize their vision, rather than prohibit ambitious designs. Interactive
walkthroughs are a future aspiration, not a prerequisite for catalogue expansion.

## Goal

Provide **at least two visually distinct, usable choices per agreed subcategory**,
not every conceivable archetype. Agree the subcategory list after reviewing the
taxonomy and prior research. A cosmetic recolour alone is not a distinct choice.

Use existing Calgary classifications. Buildings should be understandable by form
and relevant land-use references; streets should reference the City Street Manual;
parks and plazas should use appropriate City guidance. Review previous research
first. Verify new municipal claims against official sources and distinguish current
rules, historical district names and draft guidance. Catalogue classifications do
not establish development permission on a particular parcel.

## Investigate before generating

Read these sources and their machine-readable companions:

- [Agent rules](../AGENTS.md) and [repository architecture/workflow](../CLAUDE.md).
- [Current RLASM method](RLASM_LATEST_METHOD.md).
- [RLASM repository policy](RLASM_REPOSITORY_POLICY.md).
- [Building quality memory](HIGH_QUALITY_3D_BUILDING_MEMORY.md).
- [Four-family expansion handoff](CATALOGUE_EXPANSION_HANDOFF_2026-08-19.md).
- [Ten-family Wave 2 review](CATALOGUE_EXPANSION_WAVE2_REVIEW_2026-08-19.md).
- [Catalogue foundation](CATALOGUE_FOUNDATION_2026_09_05.md).
- [Desktop/tablet catalogue layout](CATALOGUE_LAYOUT_2026_09_05.md).
- [Local setup](LOCAL_SETUP_GUIDE.md).

Use the `rlasm-expert` skill if available. If unavailable, identify that gap and
consult the authoritative repository documentation; do not invent a replacement
building method. Search subsequent documentation and Git history for newer work,
Calgary research, park experiments and street experiments.

Inspect the [asset registry](../frontend/src/features/pickPlace/assetRegistry.ts),
[placement adapter](../frontend/src/features/pickPlace/catalogue.ts), runtime
references, compiler contracts, grounding and reshape behavior.

Create a gap table with columns for domain/subcategory, runtime choices, existing
candidates, missing files, proposed two choices, and approval/validation status.
Prioritize completing good existing candidates over recreating them.

**GitHub may not contain all local work.** Some candidate models and review images
exist only on Andrew's computer. Request an artifact handoff instead of duplicating
them. Do not transfer secrets or local `.env` files. The expansion waves above
remain candidates until explicit human visual approval; this guide does not grant
that approval.

## Asset requirements

### Buildings

- RLASM v6.1 is the active method. Sticker/V98 experiments are historical evidence.
- Match the established semi-realistic Architectural Clay appearance and preserve
  reference-specific architectural identity.
- Set native dimensions and sensible height/floor ranges for each building type.
- Widened residential plots should repeat appropriate whole buildings, rather than
  stretch one house into a block-long building.
- Respect each asset's supported reshape strategy and source-locked details.

### Parks and plazas

- Investigate the neighbourhood park pilot, basketball court and prior experiments.
- Adapt layouts to small, typical and large plots. Do not uniformly stretch
  playgrounds, courts, furniture or trees.
- Keep components inside the footprint, maintain practical dimensions and provide
  coherent paths, entrances and usable spaces.
- Integrate with nearby streets and building access using the existing connection
  system. Do not invent connections to inaccessible edges.

### Streets and pathways

- Use coherent cross-sections and route-based placement.
- Preserve meaningful lane, sidewalk and pathway dimensions.
- Check intersections, endpoints, elevation and park connections.
- Avoid disconnected or overlapping surfaces; identify draft guidance as draft.

### All assets

- Ground correctly against Google tiles: no floating or buried geometry.
- Look attractive in the actual 3D scene before AI rendering.
- Preserve identity, dimensions and positions across camera views, including
  close-ups, cropped objects and partially hidden objects.
- Supply required thumbnails, metadata, stable identifiers, dimensions and runtime
  references. Existing saved projects must retain their asset identities.
- Keep polygon counts, texture sizes and loading costs suitable for a neighbourhood
  containing many objects. Assess actual runtime cost before scaling up.
- Do not weaken render safeguards to make an asset pass. AI beautification does not
  prove that the underlying 3D model is correct.

## Pilot and approval process

1. Present the inventory, gap table and prioritized first batch.
2. Select one representative archetype and follow the documented dry-run/pilot
   sequence. Define finite batch sizes and checkpoints before generation.
3. Test it through the student UI on a genuinely empty site.
4. Check minimum, typical and maximum supported sizes, rotation, grounding,
   save/reload and integration with nearby buildings, parks and streets.
5. Capture close-up, aerial and partially occluded views of the actual 3D scene.
6. Present the pilot and evidence for human visual approval.
7. Expand only after approval, in bounded batches with the same checks.

Do not assume a paid API budget, credentials or an inherited spending allowance.
Obtain an explicit spending limit before paid calls. Continue inventory, planning
and unpaid validation in the meantime.

## Engineering and delivery

Follow AGENTS.md and CLAUDE.md. Keep building families, park batches, street batches
and unrelated app/compiler work in separate initiatives. Preserve pre-existing
changes. If assets need compiler work, identify and validate that prerequisite
before mass-producing them.

Keep heavyweight experiments and QA output outside tracked source folders. Follow
the repository's Git LFS/artifact policy. Never stage generated directories
wholesale; promote only reviewed deliverables. Synchronize metadata and
machine-readable companions, and regenerate affected manifests.

Run the relevant compiler, backend or frontend tests and asset validation commands
specified in the repository. Verify source changes separately from ignored output.
Commit coherent batches and prepare reviewable PRs. Do not merge to main or deploy
without explicit approval.

Each handoff should include the inventory/gap table, expansion plan, reviewed pilot,
screenshots, size and grounding checks, runtime-cost evidence, validation results,
limitations and continuation instructions. Clearly separate **candidate**,
**human-approved**, and **runtime catalogue** assets.
