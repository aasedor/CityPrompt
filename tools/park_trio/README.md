# Three new park pilots

Originally a local development initiative, 2026-09-06. The user approved
publication on 2026-09-07. The three assemblies now appear in the normal picker;
their seven reviewed GLBs are tracked through Git LFS.

| Difficulty | Park | Exact source variant | Initial placement | Larger review plot |
| --- | --- | --- | --- | --- |
| Easy | Outdoor cinema lawn | `outdoor_cinema_lawn_v1` | 32 × 45 m | 50 × 75 m |
| Medium | Teaching demonstration garden | `research_garden_teaching_arboretum_variant_3` | 32 × 40 m | 42 × 50 m |
| Complex | Wave-canopy concert lawn | `concert_pavilion_lawn_v1` | 80 × 80 m | 90 × 110 m |

The reference sets are the matching ground, 60° and 90° images under
`frontend/public/archetypes/openspaces`. Source hashes and reviewed GLB hashes
are recorded in `candidates/*.json`. No new image/video API calls were used.

## Build and review

1. Read `CLAUDE.md` and the park findings/pilot documents. Inspect all three
   source views. Some generated references disagree; choose one coherent
   programme and document inferences rather than reproduce contradictory objects.
2. Prepare an **external** public directory with `prepare_public.ps1`, providing
   a hydrated runtime public directory. It reuses existing source images,
   neighbourhood trees/benches and ground textures with junctions. Existing
   candidate directories are preserved.
3. In Blender 5.2, run `build_assets.py` with `--dry-run`, then build one park:

   ```powershell
   & 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background `
     --python tools/park_trio/build_assets.py -- --park cinema `
     --source-root C:/path/to/hydrated/CityPrompt `
     --output-dir C:/external/park-review/public/landscape-pilots/park-trio-v3/cinema
   ```

   Repeat for `garden` and `concert` only after reviewing the preceding candidate.
   The builder refuses nonempty output directories. Revisions belong in new
   directories; update `PARK_TRIO_REVISION` and the launcher together. Rebuilding
   may produce different binary hashes; validate the new manifest, never copy an
   old approval or hash onto it. The current cinema/garden candidates predate
   the beam-construction performance refactor; their original bytes are preserved.
4. The complete three-park launcher verifies manifest hashes before starting:

   ```powershell
   ./tools/park_trio/serve.ps1 -PublicRoot C:/external/park-review/public `
     -SourceRoot C:/path/to/hydrated/CityPrompt -Port 5176
   ```

   It expects the existing isolated backend on port 8002. This command starts
   the frontend only, using the source checkout's existing frontend env.
5. Open `/park-trio.html` for the same renderer on flat or sloping synthetic
   terrain. Review minimum, standard, enlarged and rotated plots; test narrow
   and concave shapes. The latter must report a constraint, not crop equipment.
   For the first single-park build, start Vite with the launcher's env values
   directly and review only the built park; the complete launcher requires all 3.
6. Open a new local project. Draw a clear open-site boundary, choose **Parks**,
   place and reshape each pilot. The preview and saved assembly use the same
   identity. Wait for both **3D saved** and successful ground alignment. Test
   save/reload and **Check direct capture**. This last action is free.
7. Run the narrow layout, catalogue, access and automatic-3D tests, TypeScript
   checks, lint for touched components, and `git diff --check`. Commit only the
   intentional source and review manifests. Heavy outputs stay external.

## Assembly rules

- Native structures are never stretched. Cinema screen and booth, the garden
  shelter/beds/signs, and concert stage/seat units retain metric dimensions.
- Larger plots add whole furniture/bed units within finite limits. Small cinema
  plots omit the booth. Grass and connected routes adapt to available space.
- Garden circulation stays clear of beds; its central court is gravel. Blank
  interpretation panels avoid invented claims or culturally specific text.
- The complex canopy has a continuous shell and soffit, supporting columns,
  roof-following rear wall, side ramp, lighting and 64 audience seats. It uses
  an existing-terrain audience lawn. Artificial terraces are deferred.
- Fixed modules have level pads; lawn/paths follow the common sampled terrain
  triangulation. High pad/ground differences carry `gradingReviewRequired`
  metadata. This does not constitute engineered grading or verified accessibility.
- Exact parent + exact variant + `park_trio_layout` revision activate each
  assembly. Unflagged catalogue entries retain their prior behavior. The three
  placement cards are available in development and production without a flag.
- Derived street connections use authored sidewalks/path bands and the same
  internal loop. Hidden/offscreen objects must stay hidden in render guidance.

## Review before publication

See `docs/PARK_TRIO_PILOT_2026-09-06.md` for the original review and remaining
landscape refinements. The 2026-09-07 publication request explicitly covers these
three parks. Future revisions still require their own review before promotion.
