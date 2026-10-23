# People actions and simple Omni video — local acceptance

This initiative is local-only on `codex/people-video-local-20261022`, based on
`ca7814ad6`. It does not deploy, push binaries, change LFS policy or spend provider
credits. Existing parks/buildings, source assets and unrelated hydrated LFS
working differences are preserved.

## Trying it

Use the existing local preview at `http://127.0.0.1:5184`.
The disposable project is
`http://127.0.0.1:5184/projects/b5a05da9-df26-4b40-83be-1ccbaaba2293`.

1. Design → Add details → the prominent lime **People** tile. It has 23 characters,
   including 20 new athletic adult designs with varied hair, complexion, height,
   clothing shape and palette.
2. Place a person, stop placing and click them or select them under Placed items.
   The highlight and edit card identify the selected person. Choose **Person's
   action**; it saves automatically. Move/rotate/copy/delete work through the
   existing detail editor, with undo/redo and geographic save/reload.
3. Present → Video. Choose **Aerial**, **Street** or **Follow a person**, optionally
   add a prompt, click **Preview · free**, then **Generate video** after reviewing
   the quoted cost. Omni 1.1 is the only new-video model. Advanced retains route,
   length, quality, reference and photographic-guide controls. Photographic guides
   and finished videos each require explicit paid submission; there are no
   automatic paid retries.

## Saved actions

The fifteen IDs are standing, walking, running, sitting, talking, lying_down,
waving, using_phone, reading, waiting, looking_around, pointing, stretching,
dancing and cheering. `people_action` is optional on persisted people props;
legacy absence means standing without rewriting the old scene. Invalid actions
and actions on ordinary furniture are rejected.

The rig receives a static action pose during editing and still capture. Video
capture samples an absolute timeline; only walking/running advance from their
placement. It restores actors afterward and does no background actor animation
while editing. Per-person skeletons/materials remain isolated, cached geometry
and texture sources remain shared, and Earth-scale skinning precision is retained.

The backend binds authoritative saved actions to validated current project
details for still images, videos and photographic guides, even with custom-only
prompts. Instructions apply only to actors visible in the capture, preserving
their identity, pose, support and occlusion. Generic extra-crowd choices do not
erase authored people. Action revisions invalidate preview/admission. A newly
nonempty details collection cannot bypass revision checking by omitting the
revision; exact existing receipts remain recoverable after later edits.

## Asset evidence

`tools/people_pilot/community_provenance.json` records verified Quaternius CC0
source archives, builder inputs, dimensions, texture/skin checks and output hashes.
`community_delivery.json` locks all 40 new GLB/thumbnail files and their local ZIP.
The original 3 actors retain their asset/thumbnail hashes. Their descriptions were
updated to explain actions.

Heavyweight outputs are external:
`C:/dev-artifacts/CityPrompt/people-actions-2026-10-22/`.
The active runtime copies are under the existing external public directory at
`C:/dev-artifacts/CityPrompt/add-details-recovery-2026-10-12/public/street-kits/people-community-v1/`.
The finite 20 total 18,970,836 GLB bytes and 260,389 triangles; estimated decoded
asset bytes 29,547,366 exclude GPU allocation. Each has 65 bones, 16–19 primitives,
embedded 256² textures and a height between 1.624 and 1.896 m.

Passed asset checks: 40/40 exact-byte HTTP 200 responses; all 20 loaded by Three.js;
1,640 exported Walk/Idle pose samples; three shape-generation tests. Independent
review verified the forty archive members and hashes and inspected contact,
portrait and rear-walking boards. No P0/P1 remained.

## Executed application checks

- Frontend focused people, editing, catalogue, video, guide and capture suite:
  129 tests passed. Later route/panel regression checks passed 87 tests; final
  quality/route/panel checks passed 26 tests. A final combined 15-file regression run passed 89 tests. Suites overlap. Final type-check
  passed; scoped ESLint has zero errors and two inherited map-effect dependency
  warnings (`policyMap`, `cityPolicyMaps`).
- Fresh coordinator backend storage/action tests: 88 passed. Backend worker's
  broader image/video suite: 323 passed; complete registry/storage suite 76 passed.
  Disposable PostgreSQL recovery/guide/admission tests 38 passed; two optional
  external-storage tests skipped. Test suites overlap and are not additive.
- Production build passed using the existing hydrated external public directory.
  A build against the intentionally dehydrated source-public directory correctly
  refused missing historical recovered assets; no hydration guard was bypassed.
- Actual local browser: prominent 23-person category; original Maya placed, action
  changed to waving, rotated 15°, copied; new Ava placed. Reload retained all 3
  actors and their actions/angles. Deletion and Undo restored the person; backend
  readback confirmed exact saved actions. Automated tests also cover movement,
  redo, concurrent edits, read-only access and failed saves.
- Actual free aerial preview: 8 seconds, 192 deterministic H.264 frames at 1280×720;
  server admission ready with a US$1.01 estimate. No Generate or paid guide call.
- Actual free street preview: 4 seconds, 96 deterministic H.264 frames at
  1280×720; admission **Ready · Omni 1.1**, estimated US$1.01. The automatic route
  measured 6.4 m at 5.8 km/h, with a 1.7 m camera height. No paid submission.
  Screenshot: external `local/street-preview-ready.png`.
- Automatic street routes now use a short, level walking corridor and a bounded
  search that avoids authored building footprints and stays within a site when
  present. Manual routes keep their existing controls. Sparse people-only scenes
  use a lower edge-density threshold, while a substantial-colour guard rejects
  blank and two-plane frames at any angle. Architectural-scene thresholds are
  unchanged. This remains a heuristic, not proof of person visibility or a
  collision/pathfinding system; inspect the preview before paying.
- Actual WebGL model QA loaded all 23 actors, and all 15 action poses. At 3432×1173,
  the all-actor display (including floor/labels) used 417 draw calls, 299,224
  triangles, 395 geometry and 462 texture objects. A 120-frame synchronous
  render-plus-GPU-finish sample measured 5.7 ms median and 12.3 ms p95. This isolated
  desktop scene excludes Google tiles, browser composition and video encoding;
  it is not evidence of student-laptop/mobile frame rates.

Screenshots, UI measurements and API readback are in the external `local/` folder.
The browser-only QA harness is external public `people-action-qa.html`, not
production source or an advertised app screen.

## Remaining limits

These are stylized entourage, using two source anatomies and six hairstyles,
not twenty separately sculpted photoreal people. Shoulder/collar transitions
remain simple at close range. Walk/Idle are the two native clips; running uses
faster Walk and other actions use deterministic procedural poses/gestures.
There is no pathfinding, obstacle avoidance, automatic seat/door detection or
multi-person choreography. Students must provide suitable surfaces, seats and
clear movement paths. AI fidelity to these action directions still requires a
separately authorized paid-output trial; none was performed for this initiative.

No student-laptop/mobile benchmark was available. Opening the catalogue does not
load every GLB, and adding 20 catalogue choices does not auto-place 20 people.
No live availability is claimed. Hosted publication requires a portable,
approved asset source and established release checks; the new local ZIP alone
does not satisfy that gate.
