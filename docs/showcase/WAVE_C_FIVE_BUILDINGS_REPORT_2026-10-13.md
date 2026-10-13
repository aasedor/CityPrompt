# Wave C: five grand historic buildings, report, 2026-10-13

Five buildings that had never been attempted with the RLASM v6.1 process were built from
their locked catalogue views on branch `claude/ten-new-buildings`, each carried through
independent visual reviews under the stopping rule in
`docs/showcase/REWORK_STOPPING_RULE_2026-10-11.md` (stop at PASS_ZERO_P0_P1, or after two
consecutive reviews that do not lower the P0 + P1 count, or when the same finding survives
two targeted fixes; the best-reviewed version stays the candidate, and a tie keeps the
earlier version). Every version was rendered from the actual optimised GLB (18 views at
1440 px, 32 samples), reviewed by a separate agent that had not built it, and preserved
as JPEG evidence. Nothing here is enrolled, published or keeper-approved; each README
says `keeper_claimed=False` and `runtime_seed_allowed=False`.

## Results

| building | catalogue archetype / variant | family | outcome | candidate | triangles | GLB bytes | candidate review P0 / P1 / P2 |
|---|---|---|---|---|---|---|---|
| Scottish Baronial railway hotel | chateauesque_grand_railway_hotel / variant_0 | `tools/clay_baronial_railway_hotel` | **PASS_ZERO_P0_P1** at v006 | v006 | 83,012 | 4,172,400 | 0 / 0 / 7 |
| Belle Époque grand magasin | grand_magasin / variant_0 | `tools/clay_grand_magasin` | stopped, rule 2 (v005 and v006 held at 0 + 2) | v004 | 80,718 | 4,177,416 | 0 / 2 / 9 |
| Barcelona Modernista mercat | barcelona_mercat / variant_0 | `tools/clay_modernista_market_hall` | stopped, rule 2 (v004 and v005 did not lower 0 + 3) | v003 | 42,932 | 2,057,252 | 0 / 3 / 9 |
| Montreal Second Empire city hall | montreal_second_empire_civic / variant_0 | `tools/clay_second_empire_city_hall` | stopped, rule 2 (v005 rose to 0 + 6, v006 only tied the best) | v004 | 75,310 | 3,768,468 | 0 / 3 / 9 |
| Parisian corner block with a zinc dome | parisian_corner_with_dome / variant_0 | `tools/clay_zinc_dome_corner_block` | stopped, rule 2 (v005 and v006 held at 0 + 1) | v004 | 75,635 | 3,933,508 | 0 / 1 / 9 |

The candidate GLB of each family is the only file in its `candidates/` folder.

### Trajectory (P0 / P1 per independent review)

| building | v001 | v002 | v003 | v004 | v005 | v006 |
|---|---|---|---|---|---|---|
| railway hotel | 7 / 10 | 3 / 8 | 1 / 4 | 0 / 2 | 0 / 2 | **0 / 0** |
| grand magasin | 1 / 8 | 0 / 4 | 0 / 4 | 0 / 2 | 0 / 2 | 0 / 2 |
| mercat | 2 / 8 | 1 / 3 | 0 / 3 | 0 / 3 | 0 / 3 | (stopped) |
| city hall | 0 / 13 | 0 / 7 | 0 / 4 | 0 / 3 | 0 / 6 | 0 / 3 |
| zinc corner | 0 / 5 | 0 / 3 | 0 / 2 | 0 / 1 | 0 / 1 | 0 / 1 |

Every review after v001 confirmed in the pixels that the previous version's findings were
fixed; the counts held where reviewers then raised elements earlier reviewers had accepted.

## Open findings on the candidates that did not pass

These are copied in each family README under "Open blockers after vNNN", with the full
reviews in `evidence/vNNN/independent-review.md`.

- **Grand magasin v004 (0 / 2):** the glazed corner drum read as buried in the zinc mansard
  with posts spiking through the roof; the interior view was illegible. v005 fixed the
  interior and the drum backing, and v006 cut a terrace ring round the drum so its lower tier
  stands clear, with 16 continuous ribs on the court dome. v006's reviewer then asked for the
  stone attic storey both sources show between the cornice balustrade and the mansard, and
  for the gilded balcony fronts thinned to fit the 4 MiB cap to be restored.

- **Mercat v003 (0 / 3):** from inside, the hall ceiling was an opaque soffit with no
  lantern glazing visible; the lantern's corner posts stopped in mid-air over blank grey
  triangles; the quadrant pyramids' stained glass was a few huge saturated triangles instead
  of small muted leaded panes. All three were fixed in v004 and v005 (both evidence only),
  but those reviews raised three earlier-accepted elements instead: the tympanum glass
  (now a small-pane mosaic) and the roundels round the archivolt, the coat of arms cut by the
  gable rakes, and dark rake-end blocks on the gable piers.
- **City hall v004 (0 / 3):** one iron balcony per corner-pavilion face where the sources
  stack two; no rustication, grey stone base or quoins; flat-capped dormers where the
  sources show segmental hoods. v005 fixed all three but introduced quoin and hood defects;
  v006 added the pavilion attic storey, a shallow forecourt and continuous hoods and tied
  at 0 / 3, with the tower side window still cut by the mansard, the dormer hood caps
  overrunning their sides, and small black joints at part junctions.
- **Zinc corner v004 (0 / 1):** the chamfer balcony order (the full-width bracketed balcony
  sat at the first storey; the sources put it at the second). v005 fixed it; its reviewer
  then found the drum breaking the chamfer cornice on a corbel ring, which v001's reviewer
  had asked for (a reviewer disagreement, settled by the source pixels in v005's favour).
  v006 set the drum behind an unbroken cornice; its reviewer asked for a lower drum and a
  full-width stilted dome springing just above the cornice.

Because a tie keeps the earlier version, four of the later evidence versions are equal-count
alternatives that carry more fixes: grand magasin v006, zinc v006, city hall v006 and mercat v005. A human can
choose one of those instead; nothing else changes.

## Lessons worth carrying into the method

- **Coplanar faces render pure black in Cycles.** Almost every P0 in this wave was a pair of
  solids sharing a face plane: tower and passage reveals, quoin fronts against string
  courses, deck tops against carrier tops, court courses meeting at an inner corner. The
  fix is always to overlap by a few centimetres or to keep a visible gap, never to touch.
- **Do not cut windows into a concave panel.** The exact boolean dropped half of every
  crow-stepped gable. Building the gable as stacked rectangular step slabs fixed it.
- **The delivery step requires the lowest vertex at z = 0.** Sinking a wall 2 cm below
  grade to close a gap fails the build; stand it at grade on a slab instead.
- **The 4 MiB GLB cap binds at about 80,000 triangles.** Each wave C building reached it.
  Lighter window frames on faces seen only at distance, fewer arc segments and wider
  coursing and picket spacing recovered 100 to 750 KB without a visible loss in review.
- **Reviewers sample different elements each round.** Several stops came from reviewers
  raising elements that earlier reviewers had accepted. Recording those and comparing the
  source pixels directly (as for the zinc drum) kept the runs from looping.

## What to do next

1. Look at the railway hotel v006 renders and phone boards in
   `tools/clay_baronial_railway_hotel/evidence/v006/`. Keeper approval, runtime acceptance
   and publication are separate human checkpoints under
   `docs/ARCHETYPE_RUNTIME_INTEGRATION.md` and `docs/BUILDING_CATALOGUE_WORKFLOW.md`.
2. For the four that stopped, decide whether to accept the candidate with its open findings,
   switch to an equal-count later version, or reopen the building with a new stopping rule.
3. To try all twenty clay buildings in a browser, use
   `docs/showcase/CODEX_BROWSER_TRIAL_PROMPT_2026-10-13.md`.

## Evidence layout

Each family folder holds the generator (`family_*.py`, `build.py`), `sources.json`, a README
with the open blockers, `VERSIONS.md` with one row per version, the candidate GLB in
`candidates/`, and `evidence/vNNN/` per version with the build report, aperture audit,
manifest, 18 render JPEGs, four phone boards, the review brief and the independent review.
