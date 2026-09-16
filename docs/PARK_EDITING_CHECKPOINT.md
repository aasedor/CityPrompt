# Park placement and recessed ground checkpoint

Phase 6 interaction slice, not final grounding or visual-quality acceptance.

Canonical parks now use click placement and the existing move/rotate/outline
editor. Catalogue/variant identity still goes through the existing compiler;
placement descriptors do not certify or publish a detailed family. Fixed kits
start with their metric programme plus the existing reviewed edge clearance.
Unsupported parks retain the simplified-layout notice. Generic previews show
the footprint rather than incorrectly displaying a neighbourhood park.

The loaded skate assembly owns its ground. Its generic green fill is retained
as an invisible editing target; prepared site backing is cut around the park.
The existing world-coordinate Google mask also suppresses captured terrain
inside the loaded park, exposing the recessed bowls. No GLB, datum, bowl depth
or catalogue review gate changed. Registration is mounted-only and tied to the
zone revision/footprint; suspension, unmount and stale geometry restore fallback
ground. This is presently applied to the skate assembly, not every park family.

The selected skate park exposes a spectator-bench edge choice. The two bounded
positions keep the furniture outside the bowls and rails. It saves through the
existing project properties and undo queue. The source fingerprint includes
the alternate position; the missing/default value retains the old fingerprint,
so existing saved parks are not invalidated by this schema addition.

## Verification

Local student pilot `c5f73929-f949-41d2-ac7d-0340e09339e7`, skate zone
`8cd3aac9-1d09-4fa4-80e0-8634999094bb`: retained earlier green-bowl failure,
inspected corrected concrete bowls, changed bench to front, undo restored back,
redo restored front, and reloaded. Footprint unchanged. Evidence includes
`PHASE6-SKATE-MASK.png`, `PHASE6-SEATING-EDIT.png`, `PHASE6-SEATING-RELOAD.png`
and API state files `phase6-{after,undo,redo,reload}-seating.json`.

Separate prepared-site pilot `a71b743b-050a-41ac-9d4c-1768ccb2bd52`:
only the boundary was API-authored. Both parks were placed through the browser.

- Skate zone `4ae6d72b-6b74-4e72-b3cf-565b05ce8dc0`: canonical Professional
  Grade selection, 41.1 × 31.1 m parcel, reviewed `park_skate_archetype_v0`.
- Neighbourhood zone `d2475c40-f40b-45b5-b7fa-fe05bc45a849`: existing adaptive
  Rustic Timber & Gravel placement, 40 × 35 m, compact assembly with its status.

`PHASE6-BOTH-PARKS.png` and `PHASE6-BOTH-RELOAD.png` were visually inspected;
coordinates remain exactly equal after reload. The frozen Gold Standard park
camera was recaptured at 1600 × 1000 (`PHASE6-GOLD-PARK.png`) and compared with
the before image: the authored scene remains unchanged.

152 focused frontend tests across 10 suites, 15 backend residual/identity tests,
TypeScript and targeted ESLint pass. Browser fresh-session failed resource list
was empty; cumulative errors stayed at 444 through the final workflows (442
historical asset errors plus two transient errors during a multi-file HMR prop
change, absent after full reload). No image/video API spend.

## Open gates

Thin park-edge gaps against retained/sloping context and the broader prepared
site edge remain visible. The student pilot still reports a pre-existing
building foundation over 3 m. These are phase 7 release gates, not accepted
contacts. Furniture editing is bounded to skate seating; it is not a general
assembly authoring system. Full catalogue family visual review, entrances/path
editing across representative parks, final render fidelity and final novice
journey remain open. Heavy evidence stays outside Git under the mission's
documented local artifact root.
