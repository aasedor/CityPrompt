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
database/storage only and creates private rows for an existing account.
It has no hosted installation or publication option.

### Private local programmes for multiple accounts — 29 October

The Brick, regular-tower and landmark installers resolve row IDs per account
before checking existing bindings. An account that already owns a legacy row
retains its ID. Other accounts receive a stable UUID5 derived from that legacy
ID and their normalized owner UUID, including when no legacy row is installed.
Repeated verification or installation selects the same private binding.

This is a per-account private local pilot. Model URLs, immutable object bytes,
source hashes and review requirements remain shared and unchanged. Existing
rows belonging to another account are preserved; a conflicting selected row or
object still rejects. Loopback database/storage and active-owner gates remain
required. This does not expose private rows to other users or authorize release
publication, catalogue activation, hosted installation or additional generation.

### Saved-zone target repair — 27 October

Ordinary browser edits to 15/25/40 storeys saved the requested count and height,
but automatic 3D and Retry rejected the recipe with the locked-footprint/height
409. Planning used the correct 54 × 44 m model target while final server
certification measured the 57 × 47 m reserved plot. The existing trusted target
resolver covered only the low-rise house programme, so the tower fell through
to polygon measurement. Earlier programme-only planning tests did not cross
this boundary.

The shared target resolver now recognizes the tower's exact asset, variant,
v006 source revision and native-footprint programme. It retains a unit scale and
the server-owned 54 × 44 m dimensions, ignoring client claims about native size.
Unbound identities/revisions and non-unit scales reject; module inventory,
source provenance, height and recipe equality checks remain required.

New regressions construct the ordinary 57 × 47 m saved zone and certify its
15/25/40-storey recipe through the same final validation used by
`place-community`. They reproduced the browser's exact 409 before the repair.
The 22 narrow tower/footprint tests and all 257 relevant assembly, placement-edge
and footprint tests pass after the repair. On 27 October, browser edits to
15, 25 and 40 storeys saved detailed geometry at 56.1, 86.1 and 131.1 m;
40 storeys survived a fresh tab/reload. Returning to the native 13 storeys
also saved successfully. Fixed-footprint resize corners were absent and
plot dimensions were disabled. Screenshots are retained outside Git in
`student-review-repairs-20261027`. This closes the local editing/reopening
check, not independent archetype visual approval or publication.

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
- The earlier `canonicalParkPlacement.test.ts` failure was an obsolete
  expectation: a flexible shade courtyard resolves its registered exact
  programme instead of the generic canonical placeholder. The 27 October
  catalogue sweep now verifies that registered identity explicitly.
- Integrated localhost browser editing/reopening at 15/25/40 now passes as
  recorded above. Exact capture and independent archetype visual review remain
  separate acceptance checks. No keeper approval is claimed; no other tower
  families scaled.
- Generated GLBs, installation receipts and plan readback stay outside Git.
  No render batch, paid generation, user-project mutation, deployment or push
  was performed by this subtask.

### Catalogue regression sweep — 27 October

The complete frontend run exposed eleven stale assertions in nine files; the
updated nine-file run passes all 55 tests. No catalogue records, approvals or
product behaviour were changed for these corrections. Coverage now verifies:

- `courtOnlyControls`: all four court-only designs can be chosen through their
  grouped parent cards, retaining the exact child placement IDs.
- `pickerHeroImages`: curated art still covers the earlier catalogue; the four
  court-only children retain their deliberate exact native preview fallbacks.
- `PlacementPalette` and `validationCatalogue`: grouped cards contain matching
  available variants and placements; ordinary cards still contain one. The
  second validation assertion now distinguishes rigid courts from flexible parks.
- `parkMatching`, `ZoningCatalogueCard` (two assertions) and
  `classroomStreetProgram`: 38 earlier native/flexible parks plus four exact
  courts and three released parks remain available. Court geometry alone does
  not establish land-use classification: the four courts remain under review,
  and earlier permitted/discretionary results stay unchanged.
- `canonicalParkPlacement`: registered flexible identity and programme remain
  exact; generic candidates still resolve to their canonical placeholder.
- `finalFiveBuildings`: each exact model retains its reviewed teaching styles,
  including the timber/structural transit pavilion and historic-industrial
  grocery, instead of imposing the legacy `contemporary_urban` tag on all five.
