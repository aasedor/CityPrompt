# Hardscape tree wells

User direction: trees on paving belong in planted openings or tree wells.
The three supplied photos establish the visual references: a planted bed with
a low metal guard, a flush grate with an open trunk collar, and an open planted
pit. They are references, not specifications for engineering dimensions.

Worktree: `C:/dev/CityPrompt-sol-empty-lot-trial`, branch
`codex/hardscape-tree-wells`, based on main `42b262f0d0106757073524e9b980364758c06fdc`.
This change is local; the previous main release does not include it.

## Reusable implementation

- `treeWellGeometry.ts`: three lightweight metric styles, pale stone perimeter,
  charcoal metal and planting matching the meadow kit. Default footprint is
  1.8 x 1.8 m; grate collar radius is 0.36 m. Metal rings and bars have actual
  gaps above soil rather than a solid slab. Each style stays below 1,800 triangles.
- `GlobeTreeWells.tsx`: one instanced draw per style, including empty lists,
  changing instance counts and React StrictMode-safe geometry disposal. Horizontal
  well sizing is independent of tree/canopy height.
- Street furniture uses the actual band's surface classification. Grass bands
  retain planting; hardscape trees receive paired, street-aligned grates at the
  band's surface lift and interpolated terrain datum. All final trees receive
  wells even when a long street exceeds the independent planting-cell cap.
- Roundabout approach-sidewalk trees receive grates; the planted central island
  and existing woonerf planters retain their planting. Paved-plaza park scatter
  receives wells with the same per-tree ground offsets, independent of the legacy
  GLB tree flag. Existing path reserves exceed the well's diagonal footprint.
- `export_kit.cjs` exports the same three styles to the offline builder.
  `scene.py` identifies hardscape tree roots, adds the appropriate well and soil
  region, then partitions paving and joints around it. Protected sports/cycle
  surfaces and plot-edge violations reject generation. `verify.py` checks every
  tree's surface ownership and physically raycasts new openings in reimported GLBs.

The shared integration checklist and review template now require this rule for
all future archetypes, including building forecourts and site landscaping. This
is not a claim that every historical catalogue model has been audited.

## Revised local candidates

| Exact ID | Treatment | Triangles | GLB bytes | Route rays / tree roots checked |
| --- | --- | ---: | ---: | ---: |
| student_reading_garden_v1 | Four 1.8 m grates | 158,770 | 2,697,148 | 483 / 4 |
| student_pickleball_garden_v1 | Two 2.4 m planted wells; four existing beds | 165,094 | 4,149,848 | 105 / 6 |
| student_futsal_park_v1 | Two 2.4 m planted wells; four existing beds | 173,118 | 4,577,700 | 159 / 6 |

Assembly SHA-256:

- Reading: `ff5a5e756235d361e995b162e5528042558d1a4d5c30a80e69422f60042481e2`
- Pickleball: `bdb0f854fab104dba862b0f8f3426b09db8c29e35a6b2bad3c2769d08e00c48a`
- Futsal: `ddcf47fd7ac37fadab333f4601dc615c633e011271efd779d74fc0575bbfcacd`

The two recent street assemblies each already have four trees in soil beds;
their surface recipes passed the root ownership audit and their bytes are
unchanged. New park GLBs use revisioned development-only URLs to avoid stale
GLTF cache entries. Their soil-region recipes accompany them in
`publicRealmTrialAssets.json`; a regression test checks all eight full well
footprints after runtime ground reconstruction.

## Evidence and checks

All generated files remain outside tracked source under
`C:/dev-artifacts/CityPrompt/tree-wells-2026-09-23/`:

- `reading/`, `pickleball/`, `futsal/`: native modules, assembly, recipe, hashes,
  geometry-verification report, Blender native close/top/aerial views and pending
  runtime-review template. `manifest.json` indexes these exact packages.
- `shared-kit/kit.json`: shared runtime geometry exported for the builders.
- `browser-three-styles.png`, `browser-reading.png`, `browser-pickleball.png`,
  `browser-futsal.png`: actual WebGL component/native model previews, without
  Google Tiles. Screenshot hashes are in `browser-evidence.json`.
- Local hydrated copies live under the existing dev public directory's
  `public-realm-trials/tree-wells-2026-09-23/` path; no GLB is staged in Git.

Pilot sequence: export shared kit, dry-run reading recipe, build/reimport/verify
one reading garden, inspect its native close-up, then rebuild the bounded two
sports parks. All three passed hashes, native bounds, embedded-buffer checks,
material-aware clear-route rays and tree-root checks. Builder visual review
accepted the new wells and retained the existing kit style.

Frontend verification: 110 passing tests in tree-well geometry, street furniture,
street shared ground, local trial surfaces, park scatter and park ownership;
TypeScript and targeted ESLint passed. Grate ray tests prove the root collar and
gaps expose soil. The runtime manifest's reachable source graph matches the two
new modules; asset entries are unchanged. Full hydrated-asset inventory was not
rerun in this sparse source worktree.

Browser verification used the live `GlobeTreeWells` component in StrictMode and
all three revised native GLBs. Increasing/decreasing instance counts rendered
six/three wells correctly; close views showed visible soil, trim and open grates.
The temporary review harness initially warned when HMR recreated its React root;
its cleanup was corrected. This was a harness issue, not an application change.

No paid image calls. No new catalogue activation or publication.

## Remaining bounded check

The local app opened at sign-in. These checks therefore do not constitute a new
Currie Google Tiles scene, a student authoring exercise, or new save/reload/export
evidence. The exact-variant runtime templates retain NOT TESTED gates.
Reopen the disposable Currie five-concept project when its local service/session
is available and inspect close/aerial contacts with the revised local assets.
For generic sloping streets and plazas, inspect well-edge contact specifically:
the current surrounds are level details at measured centres, not corner-fitted
terrain meshes. Retain full clear routes and no pavement showing through soil.
