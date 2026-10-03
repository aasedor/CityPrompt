# Autumn street trio

Additive local pilots on `codex/catalogue-streets-autumn`, following the building
and park checkpoints. No existing saved asset binding is replaced.

| Choice | Exact variant | Width | Minimum route |
|---|---|---|---|
| London Cobbled Mews | student_london_cobbled_mews_v1 | 8 m | 30 m |
| Cherry Blossom Neighbourhood Street | student_cherry_blossom_street_v1 | 20 m | 40 m |
| Barcelona Shaded Promenade | student_barcelona_shaded_promenade_v1 | 36 m | 48 m |

Each uses a metric drawn-route program, prepared level terrain, and complete
fixed-size furniture modules. Maximum route length is 480 m. Ground ownership,
native module bounds, source photographs and hashes are recorded. Front-facing
source photographs are the picker heroes. Barcelona retains its broad promenade,
florist pavilions and shade trees; rectangular paving joints are a disclosed
adaptation from the reference hexagons.

Offline review inspected four views of each exported/reimported assembly:
aerial, top, detail and 1.65 m walking height. Rejected iterations remain outside
Git. Accepted deliveries: `mews-v003`, `cherry-v002`, `passeig-v002` under
`C:/dev-artifacts/CityPrompt/autumn-nine-2026-09-30/`.

Seed deliverables contain only exact required module GLBs, source recipe,
photographic hero, visual-review ledger and manifest. Binary files use LFS.
Generated scenes, screenshots and build logs remain outside source control.
Re-stage with `python scripts/autumn_streets.py --from-seed --public-root PATH`.

Verification covers source/dependency hashes, backend catalogue identity,
front/back mirrors, repeated and reversed routes, bent-route finite geometry,
ground coverage, and picker counts. Browser acceptance is **NOT TESTED**;
these are local validation candidates, not completed classroom approvals.

The finite nine-model batch now yields 63 selectable exact catalogue choices:
26 buildings, 21 parks and 16 streets. No push or publication performed.
