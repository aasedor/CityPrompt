# Tree detail editor trial — 8 October 2026

Extends the independent bench trial with three existing oak GLB shape variants
from `landscape-pilots/neighborhood-rustic-v5`. These are three shapes of oak,
not three species. Original model dimensions are retained (roughly 9–10 m tall
and 6 m crown width). No new generated assets or paid calls.

## Behaviour

Project toolbar → Edit details → Tree model → Add tree. Select the tree and drag,
use Move on plan or 0.5 m direction buttons; rotate, remove or undo before saving.
Trees and benches share one draft and one revision-protected save. Coordinates
belong to the project, independent of site boundaries or archetypes. The plan
shows tree crowns for context but permits overlapping crowns; trunks and bench
bases cannot stack. Normal 3D scene picking ignores individual added details.

The API stores `trees` alongside `benches` in existing project metadata. Tree
variants are allowlisted. Older requests omitting trees preserve saved trees;
an explicit empty list clears them. Existing bench-only records still load.

## Browser evidence

Project: **Bench detail editor · pilot**, ID
`099fdc75-8eb1-4849-b602-8eebecef296e` on localhost:5183.

Added one oak shape beside the community hall, one beside the residential street,
and one on open ground east of the park, all through the detail editor. Moved,
rotated and removed the third tree, undid removal, saved and reloaded. All three
trees and the three pre-existing independent benches persisted. Inspected all
three in 3D. A normal scene click on a tree selected the underlying site, not
the tree. Browser error log was empty at the end of the trial.

Screenshots saved outside the source tree:

- `C:/dev-artifacts/CityPrompt/bench-editor-2026-10-08/tree-trial-layout.png`
- `C:/dev-artifacts/CityPrompt/bench-editor-2026-10-08/tree-trial-hall-street.png`
- `C:/dev-artifacts/CityPrompt/bench-editor-2026-10-08/tree-trial-open-ground.png`

## Checks and scope

Five backend tests pass, including tree round-trip, legacy-write preservation,
explicit removal, permissions, revision conflicts and validation. Frontend tests
cover tree editing/undo, mixed-object persistence, geographic frame independence,
and retaining existing bench spacing when trees are added. Existing park layout
and student workflow tests also pass. TypeScript and focused ESLint pass.

This edits independently added trees. It does not yet expose trees embedded in
existing buildings, streets or parks. The three browser placements used level
prepared ground; steep terrain, large-scale planting, public shared viewers and
AI-render fidelity remain outside this bounded trial. The inherited terrain
sampling and model caching are reused. No hosted deployment or push performed.
