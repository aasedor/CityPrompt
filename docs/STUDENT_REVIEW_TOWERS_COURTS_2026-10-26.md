# Local student review: towers and court choices

Scope: student issues 7, 8 and the tower-height portion of 17. RLASM 6.1
remains the active method. This change does not activate or publish an asset.

## Court discovery

Court-only geometry now appears in the design-variant selector of Basketball
court, Tennis court, Pickleball court and Beach volleyball court. Existing
basketball and tennis/pickleball garden layouts share those cards. The grouped
card contains only registered, available variants. Placement objects, original
saved parent IDs, thumbnails, native footprints, classifications and geometry
remain unchanged. Search for “court only” opens the matching child variant.

## Finite Brick Podium tower pilot

Only the local development registry enables this programme. The production
registry retains the fixed 13-storey contract. The exact native v006 source
remains unchanged at 13 storeys / 50.1 m, SHA-256
`1ce717fb6f9246312cb359b4808e726088447f12d2c571954cb33a6a91dd0869`.

The local range is 13–40 storeys, with 15–40 recommended. Three bands are clipped
from that source, retaining source materials and XY coordinates:

| Role | Source height band | Occupied storeys | Behaviour |
| --- | --- | --- | --- |
| Lower assembly | 0–12.3 m | 3 | Complete two-storey podium, terrace furniture and first tower floor |
| Ordinary tower floor | 15.3–18.3 m | 1 | Repeat complete 3 m floors with balconies and glazing |
| Crown and roof | 42.3–50.1 m | 0 | One complete roof and mechanical penthouse |

Height is `12.3 + (storeys - 3) * 3 + 7.8` metres. The compiled target stays
54 × 44 m, separate from the 57 × 47 m placement plot. Every module scale is
exactly `[1,1,1]`. The offset shaft and crown retain their authored 2.5 m X
offset; the runtime does not recenter these modules independently.

`scripts/brick_podium_storeys.py` derives the finite three-module programme
from hash-locked source bytes. Its default external output is
`C:/dev-artifacts/CityPrompt/student-review-20261026/brick-podium-storeys-v001/`.
It refuses changed source bytes, changed bands, changed module bytes, existing
partial output and conflicting installed rows. Installation accepts loopback
database/storage only and creates private rows for one existing account.
It has no hosted installation or publication option.

The extractor now applies translated nodes to the source frame before slicing.
A real Blender regression reproduces the former disappearance of a translated
mesh and verifies its corrected bounds and unchanged horizontal offset.

## Verification and open acceptance

- 81 narrow frontend tests passed, including grouped discovery, exact variant
  placement/thumbnail, saved native identities, tower heights, controls and
  model availability preflight; TypeScript check passed.
- 24 backend tests passed for the Brick programme and existing Vancouver and
  revision-programme regressions. The Blender extraction regression passed.
- Three private local DB bindings and object-store hashes were verified after
  installation. Actual database planning selects unchanged assembled geometry
  for 13 storeys; 15/25/40 produce 56.1/86.1/131.1 m stacks with exactly one
  lower assembly, one roof and 12/22/37 complete floors. All scales equal one.
- The unrelated `canonicalParkPlacement.test.ts` flexible shade courtyard
  assertion fails because canonical drawing resolves its registered flexible
  asset instead of returning the canonical placeholder object. It was observed
  during adjacent verification and is outside this change.
- Integrated localhost browser inspection, ordinary UI save/reopen at
  15/25/40, exact capture and independent visual review remain for parent
  acceptance. No keeper approval is claimed; no other tower families scaled.
- Generated GLBs, installation receipts and plan readback stay outside Git.
  No render batch, paid generation, user-project mutation, deployment or push
  was performed by this subtask.
