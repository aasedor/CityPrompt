# Roads, RLASM repair and tower activations — 2026-09-09

This integration adds the three initiatives selected by the user. It preserves
the other dirty worktrees and the unpublished catalogue waves.

## Included

- Procedural road network: new hand-drawn roads retain semantic centrelines,
  snap compatible endpoints, and display derived junction surfaces in both map
  views. The read-only, authorized API derives topology without changing parent
  zone IDs or history. Catalogue street sections keep their existing contracts.
  See [the road contract and remaining milestones](PROCEDURAL_ROAD_NETWORK.md).
- One-click RLASM repair: Generate to 3D recognizes a backend-certified linked
  source-locked model and repairs missing duplicated zone markers. The client
  accepts that detailed representation instead of falsely reporting a missing
  LEGO family. Uncertified Meshy responses remain rejected.
- Three tower activations: blue glass office v003, Vancouver balcony/podium
  v004, and twisting glass sky-garden v005. The exact independently reviewed GLBs
  are in Git LFS, with their unchanged independent review records. User approval
  is bound to each model hash in the canonical library manifest. No geometry or
  RLASM method changes were made.

## Verification

The isolated integration app ran at `http://127.0.0.1:5174`, using backend 8003,
the existing local test database and local object storage. Paid media providers
were disabled. This was not a production deployment.

- Road/API/source/concurrency checks: 45 tests passed; six offline junction
  cases were rendered and visually inspected. An authenticated live trial
  returned a deterministic, warning-free T-junction with three edges and one
  intersection, then displayed the derived surfaces in the globe.
- One-click repair: 181 backend tests and 55 frontend tests passed.
- Full frontend run: 1,649 tests passed before activation; the remaining test
  correctly rejected trial-labelled catalogue entries. After activation, the
  publication and road suites passed all five tests. Type-check, touched-file
  lint and Python formatting at the repository's 120-column setting passed.
- All nine published building packages passed hydrated catalogue validation.
  Installed storage/database readback verified the exact hashes of all three
  towers. Their saved recipes each contain one native model at scale `[1,1,1]`.
- All three catalogue cards were visible. Plot trials used blue 36×34/60×55 m,
  Vancouver 52×44/80×70 m, and twisting 49×49/75×75 m, with rotations of 15°, 20°
  and 25° respectively. Below-minimum Vancouver dimensions were rejected.
  Reload retained three linked detailed buildings. Overview, low-angle partial
  occlusion and close cropped Direct 3D captures retained all three instance
  IDs with nonzero visible pixels and no grounding warnings or browser errors.

Measured capture metadata and exact model bindings are in
[the trial record](TOWER_ACTIVATION_TRIAL_2026-09-09.json). Screenshots, complete
capture bundles, test logs and the local trial scripts are outside Git at
`C:/dev-artifacts/CityPrompt/roads-rlasm-towers-2026-09-09/`.

Tower trial project: `9b77dbcd-b21b-4dbf-a425-216db44ed183`.
Road trial project: `8f1a8be5-576d-4dad-b8f6-cf149242f1c3`.

## Still to fix before broad catalogue expansion

The [earlier handoff](CATALOGUE_EXPANSION_FIX_HANDOFF_2026-09-09.md) remains
applicable: rough-ground readiness can hide otherwise valid buildings;
residual landscaping conflicts and per-house doors still need work. These
activations certify the tested native tower models, not every terrain condition.
The road feature is an initial planning-surface implementation; detailed street
band trimming, live hover indicators, migration of old roads and parcel clipping
of junction additions remain separate work.

The first local run used an absolute `VITE_API_URL` on a separate port. Recipe
verification then rejected absolute ticketed model URLs against stored relative
URLs. The normal same-origin proxy passed. Deployments with a separate API origin
need an explicit, trusted-origin URL canonicalization fix; do not weaken asset
identity checks or treat arbitrary external URLs as equivalent.

To install these assets in another environment, hydrate Git LFS, run
`python -m tools.catalogue_promotion check`, then use the existing
`tools/seed_model_library.py --rlasm-clay-only --candidate ...` workflow with the
three exact candidates. Run a dry run first and `--verify` afterward. Repository
activation does not itself install database rows or object-storage files in a
hosted environment.
