# Classroom building catalogue — 27 September 2026

The local student selection now contains **20 distinct building designs**:
the existing twelve plus eight exact RLASM 6.1 architectural-clay deliveries.
These eight reuse their reviewed models without geometry changes. They are local
pilots, not newly browser-approved or textured keepers. The user's latest
instruction is Astra construction first and Sol browser testing afterwards.

| Addition | Exact candidate | Native width × depth × height (m) |
| --- | --- | --- |
| Side-by-side duplex | calgary-side-by-side-duplex-clay-v004 | 13.34 × 21.472 × 9 |
| Plateau stacked duplex | montreal-plateau-duplex-clay-v004 | 12.649 × 19.32 × 8.105 |
| Brick courtyard entrance building | courtyard-brick-modern-clay-v004 | 25.582 × 13.382 × 12.275 |
| Post-war bungalow | calgary-inner-city-bungalow-clay-v005 | 10.898 × 16.05 × 6.36 |
| Edwardian Foursquare | toronto-edwardian-foursquare-clay-v004 | 11.07 × 17.93 × 10.81 |
| Rammed-earth infill | detached_contemporary_infill-clay-v003 | 13.375 × 19.60 × 10.15 |
| Blue-glass office tower | glass_tower_podium_modern-clay-v003 | 32.12 × 30.075 × 99 |
| Vancouver balcony podium tower | vancouverism-tower-podium-clay-v004 | 48.055 × 40.055 × 58.80 |

The Vancouver tower also has a finite authored-storey programme. Its unchanged
16-storey reviewed GLB remains the default. Students may choose 16–40 storeys;
the three-storey podium and roof/penthouse remain intact while a 3.2 m source
floor band repeats between them. The programme is recorded in
`seed/model-library/rlasm-architectural-clay/vancouverism-classic-storey-program-v001.json`.
Its reviewed footprint band is 51.1 × 43.1 m through 57.5 × 47.5 m. Local
student-controls browser checks passed at 25 storeys on the minimum footprint
and 40 storeys on the maximum footprint, including save and reopen.

Exact measured values, hashes, existing independent review identities and pending
runtime status are in `classroom_building_build_ledger_2026-09-27.json`.
The courtyard model is the source's entrance building, not a fabricated complete
housing block. The bungalow excludes the separate neighbouring infill visible in
its reference. Older Beltline models are excluded; the current v005 stays bound.

An independent Astra reviewer inspected source/model comparison boards, inventory
boards and individual contact views for reuse suitability. All eight exact GLB
hashes matched their earlier holistic clay reviews, with 214 available historical
evidence-file hashes matching. This fresh scoped review preserves those previous
approvals; it does not claim a new holistic keeper review. The report is
`classroom_building_reuse_review_2026-09-27.json`.

## Integration and reproducibility

`seed/classroom-buildings/selection.json` locks the finite eight. Three previously
external candidates were imported with the existing catalogue promotion tool's
local-trial preflight/apply sequence. Their GLBs use Git LFS and independent
reviews preserve their exact bytes. The other five already existed in the
canonical clay library. Original assets and existing project bindings were not
replaced.

Run `python scripts/classroom_buildings.py` for hydrated offline verification.
Use `--write-catalogue` to regenerate only building expansion cards and
`--stage-public <public directory>` to stage the 24 locked reference images.
`--install --owner-id <existing UUID>` uses configured loopback DB/storage only;
`--verify` reads bindings and actual stored bytes. Installation refuses competing
active bindings and mismatched stored objects. No credentials are committed.

All eight were additively installed and independently read back from the current
validation DB/bucket. Their picker cards retain reference photographs. New
placements contain one native-size model with sufficient plot clearance; larger
plots do not stretch it or duplicate it. Older saved repeating homes retain their
own edit contract. Sibling variants now have distinct discovery card keys.

## Evidence and limits

- 42 focused pytest checks passed: native one-model compilation, enlarged plots,
  undersized rejection and catalogue-promotion regression coverage.
- 11 focused Vitest checks passed: exact discovery, 20 distinct variants, sibling
  keys, native placement policy and preserved legacy lookup.
- TypeScript checking passed.
- All eight GLB bounds, hashes, texture-free containers, independent review
  bindings and 24 source hashes verified; DB/object readback passed.
- Browser, Walk, mixed-scene capture and current UI edit performance: **NOT TESTED**.
- Multiple door approaches, Foursquare performance (~10.3 MB GLB), tower camera
  framing and ground contact remain explicit Sol checks. Existing manual entrance
  controls remain available; no unmeasured automatic doorway was invented.

External evidence: `C:/dev-artifacts/CityPrompt/classroom-buildings-2026-09-27/`.
No student project changed, paid request made, push performed or hosted release
published. Availability in the local picker is separate from classroom acceptance.
