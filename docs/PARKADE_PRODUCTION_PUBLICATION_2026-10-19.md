# Five parkades: production publication

The user explicitly authorized the exact five reviewed parkades for the live
catalogue and deployment-version on 19 October 2026. This promotes bindings,
parent identities and source references; model bytes and saved IDs are unchanged.
The immutable model reviews remain architectural-clay passes, not engineering
certification or textured-keeper approval.

## Local verification

Earlier individual placement, move, rotation, deletion/Undo and reload checks,
model hashes and independent reviews are recorded in
`PARKADE_FAMILY_LOCAL_TRIAL_2026-10-17.md`. The additional disposable project is
`http://127.0.0.1:5184/projects/7bbf376c-62b6-4aea-8804-48193baebd88`.
It copies the preserved local QA geometry into the signed-in QA owner's project
using the normal project/zone and native-recipe APIs; originals were not edited.

All five loaded at minimum plots (64×40, 58×40.1, 64×44, 70×40, 68×52 m),
then plots enlarged by 10 m in each axis. Models retained native dimensions,
fixed floor counts, original 15° yaw, glazing and open decks. One enlarged
Courtyard plot initially crossed the test boundary and was correctly rejected;
the disposable boundary was enlarged before retrying. All plots were restored
to their minimum dimensions and the exact recipes reloaded successfully.
Classic also passed the ordinary inspector's enlarge/restore controls.

Free exact-view exports succeeded for the complete scene and a closer view with
cropped foreground parkades and partially occluded details. The latter includes
all five models; it is a mixed-scene capture check, not five independent paid AI
fidelity tests. Browser error log was empty. QA balance remained 628 tokens.
External evidence root:
`C:/dev-artifacts/CityPrompt/parkade-publication-2026-10-19/`:
`all-minimum-plots.png`, `all-large-plots.png`, `large-plots-source.png`,
`close-partial-source.png`, `close-partial-preview.png`, plot API readbacks.

## Rollback recorded before promotion

All three existing services ran commit
`3e73508bfcc1caed57540713592f9653d4dc138a` from
`aasedor/CityPrompt`, branch `deployment-version` in Walid's workspace.

| Service | Previous successful deployment |
| --- | --- |
| API `srv-d6ehtvk1hm7c73f5ho9g` | `dep-db9fqvijnfac73c5597g` |
| Worker `srv-d6ehtvk1hm7c73f5hob0` | `dep-db9fqsajnfac73c54ujg` |
| Frontend `srv-d6ehqtjh46gs73e28n50` | `dep-db9fqoijnfac73c54eq0` |

Use each existing service's successful deployment Rollback action if necessary,
API/worker first and frontend last. No database schema migration is introduced.
Keep additive model rows/objects so saved scenes can still resolve their assets.
Do not synchronize the historical Blueprint or create replacement resources.

## Limits and release status

Fixed native visual concepts: no editable floors, arbitrary stretching, working
doors, certified capacity/accessibility, vehicle swept-path proof, upper-floor
walking proof or automatic parkade driveways. Student-laptop/mobile and sloping
terrain tests remain unperformed. Existing desktop gallery measurements remain
the measured performance evidence; compressed size is not memory usage.

Passed before promotion: 54 targeted frontend tests, TypeScript checking,
241 backend tests (parkade identities, archetype resolution and LEGO assembly),
63 parkade/promotion tooling tests plus the added finite-release identity test.
Full hydrated canonical publication preflight passed for 63 buildings; all five
local database rows and stored GLB hashes were verified. Native backend contract
generation and catalogue JSON checks passed.

The production-profile Vite build (hosted HTTPS API and existing Claude-five
profile enabled) passed. Bundle budgets passed: 474.9 KiB initial JS,
8,431.9 KiB total JS against 8,448 KiB, largest chunk 2,413.3 KiB against 3,584,
189.7 KiB CSS against 192. Existing chunk-size and mixed-import warnings remain.

A clean `scripts/hosted_assets.py --fetch-lfs` rehearsal reproduced 161 choices,
524 distinct catalogue dependencies and 3,589 public files entirely from Git
and approved seed archives; full byte audit had zero failures. No developer
database or experimental public-tree assets supply that hosted package.
The global cleanup inventory initially included old unpinned files from the
external development public tree. It was regenerated from tracked public
files plus that verified hosted package, excluding those leftovers. The clean
inventory's `--check` passed with 5,319 required records and was independently
checked: zero unexpected paths, missing receipt assets or receipt hash mismatches.
Reproduce it with tracked `frontend/public` files plus the verified hosted package,
using `CITYPROMPT_PUBLIC_DIR` for that combined metadata tree. Historical
LFS pointers in this broad inventory do not establish hydrated legacy assets;
the active hosted catalogue has the separate full verification above.

Targeted ESLint also passed. Independent publication review found no remaining
P0/P1/P2 after the clean-inventory correction. Existing
247 parent records and all prior library entries remain unchanged. The caught
external-tree inventory issue is addressed before promotion.

Production verification remains pending at this preparation checkpoint.
