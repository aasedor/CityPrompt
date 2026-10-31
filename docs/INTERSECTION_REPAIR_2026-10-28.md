# Student intersection repair

The student stress pass reproduced a rejected greenway T-junction. The user
authorized fixes and emphasized intersections at multiple angles. Keep the
existing metric street sections and shared junction renderer; do not admit an
overlap unless a complete surface can be rendered. Preserve authored bearings
for oblique joins and use bounded endpoint corrections for imprecise gestures.

## Plan and acceptance

1. Reproduce the saved local greenway failure and add geometry tests covering
   T and X joins at 30, 45, 60, 75, 90, 105, 120, 135 and 150 degrees, reversed
   routes, near-end gestures and negative duplicate/short-approach cases.
2. Trace admission, snapping, graph detection and surface clipping together.
   Expand the existing shear-based renderer rather than bypassing validation.
   Keep incompatible specialist structures and overlapping parallels separate.
3. Clarify unavailable public-road snapping without disabling internal street
   connections. Add a genuine orthographic plan view if compatible with the
   shared globe capture/navigation pipeline; otherwise record its limitation.
4. Run focused Vitest coverage, type checking, lint, then browser-create angled
   junctions on a disposable local project. Inspect pavement, sidewalks and
   furniture near the junction, edit/reload, and free capture.
5. Review and checkpoint this roadway initiative separately. Then fix historic
   point picking and court-only discovery in separate coherent checkpoints.

No asset publication, push, deployment or paid rendering is authorized by this
repair. Existing source tree was clean at start. Use the current managed local
worktree and existing dependencies. Evidence stays outside the source tree.
