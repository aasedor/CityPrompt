# Three-house flexibility pilot — 2026-09-28

## Scope

This pilot applies the RLASM 6.1 low-rise flexibility contract to three exact
building variants:

| Family | Approved native choice | New authored choice | Height pair |
| --- | --- | --- | --- |
| Post-war bungalow | 1 storey | 2 storeys | 6.36 m / 9.29 m |
| Edwardian Foursquare | 2 storeys | 1 storey | 7.66 m / 10.81 m |
| Halifax clapboard house | 2 storeys | 1 storey | 7.34 m / 10.48 m |

The original approved GLBs remain unchanged. Each alternate is a complete
assembly derived from the exact semantic authoring blend, with walls, openings,
roof, chimney and entrance resolved as one composition. The runtime selects the
whole assembly for the requested storey count; it does not repeat or scale
geometry vertically.

Each family also exposes one uniform horizontal scale control from 85% to 115%
in 5% steps. The scale applies to the selected complete assembly, leaves Z at
1.0, and does not reshape the surrounding placement parcel.

## Authorities and reproducibility

- Machine contract:
  `seed/model-library/rlasm-architectural-clay/house-flex-pilot-v001.json`
- Deterministic authoring operation:
  `tools/archetype_compiler/blender_house_storey_variant.py`
- Hash verifier and local installer: `scripts/house_flex_pilot.py`
- Generated neutral evidence remains outside the repository under
  `C:/dev-artifacts/CityPrompt/house-flex-pilot-2026-09-28`.

The machine contract records exact source and output hashes. Authoring blends
remain in the preserved external evidence paths; promoted runtime GLBs use Git
LFS.

## Review state

The three approved native assemblies retain their inherited independent review.
The three alternates have builder-reviewed front, front-corner and aerial
evidence and remain `BUILDER_PASS_VISUAL_REVIEW_PENDING` until an independent
holistic review. This pilot status does not imply catalogue-wide approval.

## Local application verification

The isolated browser pilot used ordinary student catalogue, placement and
building-edit controls against project
`e2f66297-5743-4e45-a5f6-9d99dba93d71`. It verified the following deliberately
different states, then reloaded the project and checked the saved server rows:

| Family | Tested choice | Footprint | Result after reload |
| --- | --- | --- | --- |
| Halifax clapboard house | 1 storey / 7.34 m | 85% | compiled |
| Post-war bungalow | 2 storeys / 9.29 m | 115% | compiled |
| Edwardian Foursquare | 1 storey / 7.66 m | 90% | compiled |

The final run returned no failed HTTP responses. Screenshots and the persisted
result record are under
`C:/dev-artifacts/CityPrompt/house-flex-pilot-2026-09-28/browser-three-house-evidence`.
This evidence is intentionally outside the repository.

The browser run also found and fixed two integration faults before acceptance:

- footprint-only scale changes now participate in the automatic 3D source key,
  and an obsolete in-flight failure yields to the queued newer edit;
- trusted native dimensions retain full manifest precision, preventing a 115%
  boundary target from changing fit classification between planning and save.
