# CityPrompt animated people and photographic video pilot

Local pilot on `codex/people-video-pilot`, based on `85ef6c174`, with implementation saved as `683517d0d471c550fc72c1ac5f6bd09cccb94a07`. Three rigged adults can be placed through Add Details, edited with the existing tools and animated during deterministic video capture. Four-second Omni edits turn the stylized characters into photographic people. Architectural and identity fidelity remain approximate; these are concept films rather than exact design records.

## Characters and source authority

| Character | Runtime ID | Idle width × depth × height, m | Triangles | GLB bytes |
|---|---|---:|---:|---:|
| Maya, rust overshirt | `people-pilot-commuter` | 0.685 × 0.710 × 1.693 | 13,828 | 1,096,500 |
| Eli, navy overshirt | `people-pilot-neighbour` | 0.791 × 0.740 × 1.786 | 11,397 | 796,312 |
| Sofia, sage coat | `people-pilot-creative` | 0.670 × 0.694 × 1.653 | 13,562 | 1,077,976 |

The [provenance manifest](../../tools/people_pilot/character_provenance.json) binds exact GLB, source archive and license hashes, measured dimensions, materials and animation tracks. The [build instructions](../../tools/people_pilot/README.md) preserve the recipe. Anatomy, hair and motion derive from the official free Quaternius Universal Base Characters and Universal Animation Library Standard archives under CC0; the simple clothing and palettes are pilot derivatives. Native characters are deliberately stylized, without cloth simulation.

Assets use metres, +Y up, +Z forward and an authored foot datum. Each has a 65-bone rig, eight materials, `Idle` and `Walk`. No global CityPrompt scale, asset-storage policy or LFS rule changed. Six intentional runtime GLB/thumbnail files use the existing street-kit LFS rules. Source archives, Blender files, generated portraits and video experiments stay outside the repository.

## Runtime and capture

- People are optional in Add Details and load when placed. Normal editing holds an idle pose, with no continuous actor animation loop.
- Existing selection, lime highlighting, movement, rotation, duplication, deletion, undo/redo and persistence are reused. Geometry and textures are shared; each placed person owns its skeleton and cloned material state.
- Video capture optionally animates people forward at 1.2 m/s from their saved positions. A clear level path is required; no route planning, obstacle avoidance or interaction simulation is claimed.
- Follow a person uses a 1.6 m camera and tracks the primary actor. This pilot stages the primary actor first; arbitrary multi-actor directing is not implemented.
- Four seconds means 96 source frames at 24 fps; the existing eight-second path remains 192 frames. Warmup and final capture use the same absolute timeline. Capture failure and completion restore actor/camera state.
- Optional PNG/JPEG appearance references are bounded to 8 MiB and 4096 pixels per edge. They have a separate identity role from the source video, are included in replay hashes, stored privately and redacted from shared responses. There are no automatic paid retries.

The first free source exposed severe skeletal deformation in Earth-centred coordinates. Actor-owned mesh-local palettes now remove large world coordinates before Float32 skinning, with matching CPU skinning for selection and bounds. Absolute poses invalidate owned skinned bounds. Independent review checked 288 frames and 2,552,544 vertex samples across the exact three GLBs; only floating-point roundoff remained outside recomputed bounds.

Ground contact uses the native sidewalk surface rather than the site's base altitude. Measured native sole errors at sampled times were below 0.34 mm. Existing global shadow bias can still make the stylized source appear slightly detached; the pilot does not change global shadows. Blender re-import samples have between-frame sole residuals of −2.04 to +6.48 mm.

## Paid trials and visual findings

Every provider call was manually submitted through the app after its free source and preflight checks. The user authorized at most ten four-second trials. Five completed identity-guided calls survived the computer shutdown; the ensemble source was interrupted before a sixth reservation or provider call. The saved ledger was reconciled with the local database before resuming. One further ensemble call completed after recovery: **six completed calls, four unused, no retries or purchases**. Each source and output has 96 decoded frames at 24 fps, 1920 × 1080. This delivery size does not establish native 1080p model synthesis. The admission cost estimate is not an actual provider bill.

| Take | Purpose | Measured output | Visual result |
|---|---|---|---|
| 1 | Maya, simple photographic prompt | 4.000 s, 96 frames, 1920 × 1080 | Convincing fabric, person and light; changes the open verge and distant buildings. |
| 2 | More explicit Maya identity | 4.000 s, 96 frames, 1920 × 1080 | Stable outfit but approximate face/hair; adds hedging and changes the verge. |
| 3 | Preserve Maya's green verge and horizon | 4.000 s, 96 frames, 1920 × 1080 | Preferred balance of photographic subject and source composition. Awnings/furniture change and background pedestrians are invented. |
| 4 | Eli with his own portrait | 4.000 s, 96 frames, 1920 × 1080 | Distinct photographic adult; significant redesign of planting beds, benches, lamps and horizon. |
| 5 | Sofia with her own portrait | 4.000 s, 96 frames, 1920 × 1080 | Coherent bob, coat and subject; altered planting/furniture, invented pedestrians, some faceted trees retained. |
| 6 | Three authored walkers, video only | 4.000 s, 96 frames, 1920 × 1080 | Strong photographic ensemble with three distinct roles; Sofia turns away, Eli's trousers/facing change, extra distant people appear, and architecture/planting are rewritten. Cinematic interpretation, not a fidelity keeper. |

Take 6 is attempt `b30d3681-7e7f-4729-bb1d-e89efb202bf4`. Its source SHA-256 is `30b2cf5dc0457b4e9144f76cf930a2c7931666181843d07851a250e7fb62804f`; output SHA-256 is `58a904195d01b942b0c64909bb1915c7ff82b6c426852309dde984f0bc0a5efd`. All six attempts, exact prompts, source/output hashes, decoded media and provider token receipts are recorded in [pilot_results.json](../../tools/people_pilot/pilot_results.json). Takes 1–5 used the matching generated portrait; take 6 used video alone. The restored Edge session required an extra extension permission to upload a portrait, so that permission was left unchanged and the optional portrait omitted.

The photographic portraits were generated specifically for this pilot. No real person's likeness or the Blender-town creator's character was copied. The Blender-town example informed the workflow—rigged source motion plus a separate photographic identity—not an objective claim of outperforming it.

All six source/result pairs have been played to their ends in the browser and sampled at eight output frames each. Independent reviewers inspected forty output samples for takes 1–5 with matching references/source endpoints, then all eight matched source/output pairs for take 6. No obvious sampled body fusion or extra limbs were found in take 6. Its source has three independently placed native people, but the edit reverses a secondary walk, changes Eli's clothing and adds distant people. Photographic appearance is demonstrated; exact face likeness, exact architecture, unchanged actor direction and a large controlled crowd are not validated. Still-frame review does not establish absence of foot sliding or flawless temporal motion. Maya take 3 remains the preferred single-person composition baseline; take 6 is the strongest ensemble presentation with these disclosed fidelity limits.

## Executed verification

| Check | Result |
|---|---|
| Focused frontend suite: people, video panel/quality/routes and existing detail placement | 52 passed in nine files |
| Backend: people video, Omni, media, replay/recovery, scene revision, privacy, existing animation/providers and project details | 188 passed; six existing datetime deprecation warnings |
| TypeScript | `npm run type-check` passed |
| Scoped ESLint | Zero errors; two existing policy-map effect-dependency warnings in GlobeSitePlannerMap |
| Configured Vite production build | Passed using the local runtime profile, external output and `copyPublicDir:false` |
| Exact local asset HTTP responses | All three HTTP 200, valid GLB header/length and matching SHA-256 |
| Post-shutdown media integrity | All six exact source/result pairs recovered, SHA-256 matched and ffprobe confirmed 96 decoded frames / 24 fps / four seconds |
| Character animation | 246 Blender re-import pose samples; 14 deterministic runtime tests including Earth-coordinate skinning, raycasting and fresh bounds |
| Browser editing | Actual mesh click selected/highlighted Maya; move saved; undo/redo worked; a copy increased three placements to four and undo restored three; rotation/deletion and undo also checked; reload preserved all three |
| Existing scene | Six authored buildings, a native street, planting and furniture loaded; all character captures completed without changing real user scenes |

The measured three-person 1440p-to-1080p free source recorded 1,171 draw calls, 4,164,278 triangles, 880 geometries and 807 textures for the **whole scene**, including Google context. CPU render-submission time was 22.6 ms median and 25.1 ms p95. GPU work, encoding and object/GPU memory overhead are additional. These are desktop capture measurements, not student-laptop or mobile FPS benchmarks. The three decoded character mesh estimates total about 4.57 MB before object/GPU overhead.

## Local recovery and trying the pilot

The interrupted shutdown left Docker's Secrets Engine socket unusable. The failed Docker processes were stopped with its CLI; the socket's containing directory was renamed intact, then Docker and the existing database/Redis/MinIO containers restarted. No volumes, containers, database rows or media were deleted. The recovery is recorded in the external QA folder; the corresponding [Docker issue](https://github.com/docker/for-win/issues/15064) documents the same directory-level workaround. The API health and Vite's 156-choice/514-dependency catalogue check passed after restart.

The existing Edge local test session was preserved. A new disposable **People film studio · Three neighbours** scene was seeded under that already-signed-in local test account, without changing credentials, membership or existing projects.

The resumed free source was revised to put Sofia on the clear sidewalk behind Maya. The external seed helper initially flushed without committing; its missing transaction commit was corrected and a new session verified saved revision 2 before the final free capture. This was fixture setup, not an application persistence defect. Two rejected free staging captures made no provider calls.

- App: `http://127.0.0.1:5184/projects/302b7c87-0900-514c-aef3-48c78d1ddc2f`
- Add Details → People contains Maya, Eli and Sofia.
- Video → 4 seconds → Follow a person → High Quality. Native people animate only for capture; optional references guide appearance.
- Comparison player: `http://127.0.0.1:18121/#take-6`, with all six source/result pairs and MP4 downloads. The ensemble source/result both reached the end without a media error in the restored browser.
- Exact receipts, sources, outputs, screenshots and budget ledger: `C:/dev-artifacts/CityPrompt/people-video-pilot-2026-10-21/`.

Production, deployment branch and provider configuration were not changed. Pre-existing hydrated building/model files remain separate from the source changes. This is a local pilot for human review before any publication decision. The source, provenance and report are small tracked deliverables; video media, receipts, generated portraits, screenshots and editable character sources remain external generated output.
