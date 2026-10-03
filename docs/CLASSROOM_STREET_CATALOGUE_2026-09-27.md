# Ten local classroom street choices

This checkpoint adds three native route types to the existing seven, bringing
the local student picker to **20 buildings, 15 parks and 10 streets**. The three
additions are built and staged local pilots. Browser acceptance is **NOT TESTED**;
the user requested Astra construction first and Sol browser testing afterwards.

| Addition | Exact variant | Width | Route length | Fixtures per source repeat |
| --- | --- | --- | --- | --- |
| Protected Cycle Avenue | student_cycle_avenue_v1 | 24 m | 48–480 m | 43 |
| Ruelle Verte Community Alley | student_green_alley_v1 | 11 m | 40–480 m | 30 |
| Playful School Street | student_school_street_v1 | 18 m | 48–480 m | 28 |

These reuse the preserved September 22 native compositions. Models, furniture,
planting and palette remain at native scale. Source-authored bicycle symbols,
arrows, play markings and planting-bed edging are recovered as hash-locked detail
meshes; the road surface and those details follow the drawn route. Rigid furniture
uses the existing individual-module placement contract. The preview assembly is
never stretched into a road. Existing saved street capability fingerprints are
preserved in the backend history.

## Offline verification

- All 23 delivered module files, three reference images, source recipes and
  program hashes verified. GLBs have no external dependencies.
- Recovered detail vertices match source assembly vertices within 0.000001 m.
- Source and actual frontend reconstruction were rendered from matched top,
  oblique and walking-height cameras. Astra inspected all nine image pairs.
  Fixture counts, distinctive markings, paving, planting and furniture agree.
  The runtime's existing 0.025 m ground lift remains intentional.
- 36 focused Vitest checks passed, including the 20/15/10 picker count,
  discoverability, exact fixture repetition, reversed routes, detail clipping,
  route limits, readiness and asset locking. Nine focused pytest checks passed,
  including all ten trusted street recipes and corruption rejection.
- TypeScript checking and production compilation passed. Production HTTP smoke
  served 31 compiled chunks and 26 separately staged street assets; the live
  local app served all 26 with exact byte matches. Backend health passed after
  restarting its cached registry. This is not a browser smoke test.
- Production compilation retains large-chunk warnings. Loading and interaction
  performance remain part of the later Sol pass.

Evidence and full-size comparison renders are outside Git at
`C:/dev-artifacts/CityPrompt/classroom-streets-2026-09-27/`.
Exact evidence hashes and limitations are in
`classroom_street_build_ledger_2026-09-27.json`.

## Reproducibility

With Git LFS files hydrated, `python scripts/classroom_streets.py` verifies the
finite delivery without changing anything. Use
`--public-root <public-dir> --manifest <outside-source-manifest.json>` to stage
verified assets, or `--write-catalogue` to regenerate only the three street
expansion cards. Existing street contracts and cards remain separate.
`python tools/public_realm_assets/sync_native_street_registry.py --check` checks
frontend/backend mirrors and trusted capability bindings.

`tools/public_realm_assets/extract_classroom_street_details.py` records the exact
authoring inputs when recovering source detail meshes. Reproduction of that
recovery needs the preserved source packages; normal installation uses the
locked recipes, modules and programs shipped in `seed/classroom-streets`.
Do not overwrite an active content revision. Introduce a new explicit revision
if a subsequent visual or runtime check requires geometry changes.

## Acceptance still required

Use prepared level terrain. These are reference-informed teaching concepts,
not traffic-engineering or accessibility certificates. Acute bends, joins,
partial repeat endings, slope rejection, real terrain, Walk, render preparation,
save/reopen and mixed-scene performance still require the Sol browser pass.
Do not copy earlier seven-street acceptance results to these three additions.

Local student availability is enabled; no hosted deployment, Git push, paid
provider request or modification to existing student projects occurred.
