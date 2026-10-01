# Three climbable parks — local catalogue delivery

Date: 2026-10-01. Initiative: `codex/climbable-park-trio`.

The user approved Quarry Garden, Spiral Lookout Park and Cascade Water Garden,
with the existing catalogue's visual standard and reliable walking as requirements.
These are original, deterministic native assemblies. Their planting and furniture
reuse the established shared park kit; the circulation, terrain and stonework are
new. Aerial thumbnails show the actual exported models.

## Delivered models

| Park | Native size | Walkable change in level | Triangles | Seed package |
| --- | --- | --- | --- | --- |
| Quarry Garden | 60 × 68 m | Three flights down 4.5 m, with two terrace loops | 745,529 | `seed/classroom-parks/climbable-quarry-v006` |
| Spiral Lookout Park | 64 × 68 m | Continuous 3.5 m wide promenade to a 5.425 m summit | 587,510 | `seed/classroom-parks/climbable-spiral-v003` |
| Cascade Water Garden | 54 × 68 m | Paired stairs up 4.5 m and a crossover at the top | 714,401 | `seed/classroom-parks/climbable-cascade-v004` |

Each seed package includes the GLB, recipe, geometry check, exact-model walking
check, author visual review, thumbnail and inspected aerial/pedestrian images.
All binary deliverables use Git LFS. Superseded candidates and build experiments
remain outside source control under
`C:/dev-artifacts/CityPrompt/climbable-parks-2026-10-01`.

## Walking behavior

The visible paving and navigation triangles come from the same authored faces.
They are covered by the layout revision alongside the model hash. Only these
three parks opt in to the new movement constraints. Existing park movement is
preserved.

Movement is divided into short steps. The camera follows connected treads and
ramps; it cannot jump a retaining wall or cross a pool. It can slide along a path
edge, turn, and back away from furniture. Entry clicks on excluded areas recover
to a nearby walking surface. A **Return to park entrance** button restores the
park's real entrance in its saved position and rotation. **Exit walk** and Escape
remain available.

The exported-model verifier walked every authored route in both directions:
14,844 movement samples, no blocked route, maximum tread change 0.15 m, and less
than 0.000001 m difference between navigation and the GLB surface. It also swept
three torso heights across a 0.44 m width against stone, metal and timber meshes.
These are geometric checks of the authored routes, not an exhaustive claim about
every possible input sequence.

## Pilot and corrections

A quarry pilot was dry-run, built, visually reviewed and placed through the
ordinary catalogue on the vacant Currie test site before the remaining two parks
were built. Live keyboard walking descended and climbed 4.5 m. Strengthening the
clearance verifier then exposed railing across two side exits; the final quarry
opens those landings. The final revision is verified separately.

Other review corrections included the spiral entrance guard opening, fuller
planting within the 900,000 triangle ceiling, solid stair landing supports, and
separation of ground and paving planes. Rejected candidates were retained as
external evidence and are not catalogue choices.

## Verification scope

See `CLIMBABLE_PARKS_2026-10-01.json` for exact hashes, local browser evidence,
checks and limitations. Tests cover edge recovery, pools, furniture, ascending
and descending steps, ramps, saved rotations, entry/exit transitions and missing
models. Existing native park, catalogue, camera-ground and walking tests also run.
Backend tests check shared registry parity and native recipe identity, including
rotated placement, full footprint fit, excluded areas and stale revisions.

These are fixed native assemblies on prepared level sites. Water is static
geometry. Public street connections, natural/sloped terrain and paid imagery are
outside this delivery's live checks. Publication and independent human visual
approval remain separate from author review and local functionality checks.

## Reproduction

Run Blender with `tools/public_realm_assets/build_climbable_parks.py`, one kind
and a new output directory per invocation; use `--dry-run` first. The recipe
records source and kit hashes. Run
`node tools/public_realm_assets/verify_climbable.mjs <candidate-directory>`.
Review aerial and walking images, then use
`scripts/register_climbable_parks.py --package <candidate-directory> --dry-run`
and the same command without `--dry-run`. Registration requires an exact-model
walking pass including torso clearance and hashed author visual evidence.
Restart the local Vite preview after adding public files: public asset watching
is disabled in this repository.
