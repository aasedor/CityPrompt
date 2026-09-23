# Planted street and garden cycle promenade — native 3D assets

Street initiative: `codex/planted-street-asset-batch`, based on park checkpoint
`6ef27c301`. First street checkpoint: `f5d97fb6f`. User requested new high-quality
parks/streets and actual 3D assets. This completes the two street concepts beside
the [three park packages](SPORTS_GARDEN_ASSET_BATCH_2026-09-22.md).

| Exact concept ID | Fixture | Cross-section | Triangles |
| --- | --- | --- | --- |
| student_planted_shared_street_v1 | 18 x 48 m | 5.5 m shared lane, two 3.75 m garden/furniture strips, two 2 m clear walks, two 0.5 m edges | 104,022 |
| student_garden_cycle_promenade_v1 | 16 x 48 m | 4 m garden, 3 m walk, 2 m planted separator, 3.5 m two-way cycle path, 3.5 m garden | 118,096 |

These are original concept sections, not reproductions of an official manual.
No speed-control, engineering, drainage capacity or accessibility certification
is claimed. The shared street has flush paving and open seating bays; the
promenade separates modes and supplies a flush cross-link. Cycle arrows use
right-hand travel, with bicycle stencils rotated along the direction of travel.
The crossing is a concept connection, not an approved traffic-control treatment.

## Deliverables and review

Root: `C:/dev-artifacts/CityPrompt/public-realm-batch3-2026-09-22/`.
Accepted packages: **shared-street-v2**, **promenade-v2**. Earlier `*-final`
folders are superseded experiments retained for comparison; trust this report
and its companion JSON rather than folder naming. Each accepted package has
assembly-preview.glb, reusable native-origin kit GLBs, complete surface/fixture
recipe, builder sources, aerial/top/detail images and pending runtime checklist.

The current meadow kit supplies actual tree branches/leaves, planting, slatted
timber furniture and charcoal metalwork. Metre-scale paving joints, drainage
slot graphics and bicycle symbols are geometry. No remote textures or paid
image calls. GLB assets are approximately 2.3 MB each; static details are merged
by material while kit geometry is shared. Mesh instances: 95 shared street,
109 promenade. No district-scale FPS benchmark is claimed.

Both dry runs passed. Shared-street pilot was reviewed before building the
promenade. All exports were reimported for render and verification. Agent
aerial/top/detail review passes the model concept; independent human visual
approval and student runtime acceptance remain open. Seating pads were extended
to meet sidewalks after the first review; cycle stencil direction was corrected
after the first promenade review. Old outputs remain preserved.

Verification passes self-contained GLB buffers, exact bytes/hashes, finite
complete-envelope geometry and material-aware route rays: 1,545 for the shared
street (including seating approaches), 1,026 for the promenade (including rest
bays and transverse link). No runtime/frontend production code changed, so
browser scene acceptance and frontend type-check are not claimed for this batch.

## Runtime handoff

Not in the student picker, seeded, published or pushed. Full assemblies are
straight, level inspection fixtures; reconstruct bands along the shared street
centreline/ground pipeline. Never bend, stretch or repeat the complete GLB.
Retain metric width, foliage envelopes and clear routes. Use network-owned
junction openings, crosswalks and ramps, and omit furniture near joins.

All per-candidate runtime gates remain NOT TESTED: straight/bent/reversed routes,
slopes, endpoints against surrounding roads, building/park approaches, edits,
Undo/Redo/reload, residual landscape and exact export. Test on disposable vacant
Currie land before classroom activation. Offline mesh checks do not prove
terrain support or novice usability. No changes to the protected Currie project.

Replay with Blender 5.2 using `--python-exit-code 1` and
`tools/public_realm_assets/build_streets.py -- --kind <shared|promenade>
--kit <kit.json> --output <fresh-directory> --dry-run`; remove `--dry-run` to
build, then run `verify.py -- <package>`. Exact hashes live in the companion JSON.
Generated binaries/images remain external, not ordinary Git blobs.

Combined five-concept delivery: `CityPrompt-five-concepts-3D.zip` (33,719,668
bytes; ZIP CRC check passed) and `five-concepts-overview.jpg` at the external
root. The ZIP includes the accepted park and street packages, local gallery and
overview. These files are local artifacts, not a remote shared backup.
