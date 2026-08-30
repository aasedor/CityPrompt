# Amsterdam Hofje Medieval — RLASM v6.1 keeper

This package publishes the source-locked `amsterdam_hofje / hofje_medieval /
variant 0` forward test completed on 2026-08-30. The candidate began with
only the three exact catalogue photographs in `references/catalogue/`; no
prebuilt model or prior candidate was used.

The accepted candidate is `rlasm-amsterdam-hofje-medieval-v023`. It passed the
builder pixel gate and a separate holistic independent review with zero P0 and
zero P1 blockers. The reviewer opened all three locked sources, all sixteen
full-resolution renders, and both 1080 x 1920 phone boards at original
resolution.

## Published contents

- `prework-manifest.json` records the measured plan, bay and floor schedule,
  roof graph, elevation grammar, materials, contacts, openings, cameras, and
  occupied program.
- `references/` contains the exact catalogue sources, SHA-256 source lock,
  rectified identity derivative, and thirteen source-conditioned material
  roles with prompt and provenance records.
- `scripts/` contains the deterministic source preparation, Blender build, and
  phone-board assembly scripts.
- `renders/` contains the complete sixteen-view 1280 x 960 evidence set.
- `phone/` contains the two accepted 1080 x 1920 proof boards.
- `review/` contains technical preflight, builder review, independent holistic
  review, and final keeper lifecycle state.
- `KEEPER.json` records the canonical lifecycle promotion; `keeper-manifest.json`
  binds the compact repository package to the externally stored model hashes.
- `discrepancy-ledger.json` preserves the finite correction history through
  v023. Rejected render candidates remain in ignored local artifact storage.

The accepted `.blend` and `.glb` are retained as external heavyweight
artifacts. Their exact SHA-256 hashes and validation results are recorded in
`keeper-manifest.json`; the repository includes the reproducible build script,
source-specific material sheets, exact sources, and complete visual evidence.

## Final decision

- Builder: PASS, P0=0, P1=0, P2=4.
- Independent holistic review: PASS, P0=0, P1=0, P2=4.
- Keeper eligible: yes.
- Generic material fallbacks: 0.
- Mounted perspective photographs: 0.

The accepted P2 debt is limited to stylized court foliage, faceted fine
profiles, minor secondary-elevation finish, and coarse kitchen props/board
alignment. None is a keeper blocker under the independent source-locked review.
