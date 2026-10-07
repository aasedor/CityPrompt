# Five narrow pathways — local trial, 7 October 2026

Find these in **Streets**, searching **winding path**. Select a card, click route
points, and finish the route using the normal street drawing controls. These are
concept designs, not City of Calgary standard sections.

| Exact variant | Clear width | Finish |
| --- | --- | --- |
| garden_gravel_path_v1 | 1.5 m | Fine warm gravel |
| concrete_neighbourhood_walk_v1 | 1.8 m | Jointed concrete |
| brick_courtyard_path_v1 | 2 m | Running-bond brick |
| timber_garden_walk_v1 | 2 m | Transverse timber boards |
| asphalt_shared_path_v1 | 3 m | Fine dark asphalt |

All five are surface-only paths with zero vehicle lanes and no added furniture,
trees or curbs. Width stays fixed through bends. The maximum route length is
300 m; the UI minimum is 2 m except asphalt at 3 m. They use prepared level
ground. Slope and stair support is outside this batch.

Each card has a generated photographic inspiration image. The photograph's
surrounding planting and buildings are not part of the path model. Actual native
geometry uses lightweight procedural paving and fine aggregate details. Exact
image, source recipe, assembly and executable-program hashes are recorded in
[the evidence manifest](NARROW_PATHWAYS_2026-10-07.json). Source assembly here
means metric procedural JSON, not an external GLB.

## Implementation and pilot

The generator `tools/public_realm_assets/build_narrow_pathways.py` defaults to a
dry run and supports only a one-path pilot or the finite five-path batch. Run it
with `--output <external-directory> --count 1`, review the result, then add
`--install`; `--count 5` completes the reviewed batch. It preserves existing
catalogue records and refuses to replace an existing changed revision.

The gravel dry run, one-path installation and native browser review preceded
the other four. The local mixed scene includes the preceding five-building
batch, a planted shared lane and a shaded reading garden. All five paths were
drawn through ordinary UI controls. Read-only API checks confirmed their exact
identities and widths. No geometry was injected through developer APIs.

Two shared issues were reproduced and fixed:

- Parent trail/street defaults could replace a narrow path's real width with a
  wider road section. Exact native width and zero motor lanes now agree across
  catalogue, section, footprint and junction calculations.
- Boundary validation could send an already sampled curve back through the
  editing pipeline, losing the sparse bend controls. It now carries the
  translated editing controls. Concrete retained five handles through bend
  edit, Undo, Redo, save and reload. The earlier gravel test fixture retains
  its pre-fix sampled centreline; no retroactive handle-recovery claim is made.

## Verification

- 163 tests passed across eight focused frontend files: narrowPathways,
  streetBoundaryPlacement, streetPlacement, streetConnectionProblem,
  canonicalCatalogue, streetGraphIntersections, streetJunctionGeometry and
  nativeStreetProgram.
- 21 backend tests passed: test_narrow_pathways and
  test_native_street_candidate_contract.
- `npm run type-check` and native street registry parity passed.
- All old catalogue records remained equal to HEAD; exactly five were added
  to each frontend/backend registry and starter roster.
- All five hero URLs returned hydrated PNG bytes matching their locked hashes.
- All five persisted after browser reload. Concrete/gravel and gravel/shared
  lane joins were exercised; each exact path also passed an automated T-join.
- Timber was inspected at walking height with a short forward movement check.
  This does not establish complete route traversal or slope behaviour.
- The final browser console query returned no warnings/errors. QA balance
  remained 8,970 tokens; no paid City Prompt render was submitted.

Test project: <http://127.0.0.1:5181/projects/d7eb67d6-11a5-41ad-84d8-c48872fbb465>.
Screenshots and API readbacks are external local evidence under
`C:/dev-artifacts/CityPrompt/narrow-pathways-2026-10-07/`.
The compact manifest records their hashes. Credentials are excluded.

## Remaining review and delivery scope

This is a provisional local concept trial, not independent student acceptance
or human visual approval. The five exact-variant checklists are in
`docs/runtime-reviews/narrow-pathways-2026-10-07/`. Applicable unrun gates stay
NOT TESTED. Follow-up checks include touch/iPad drawing, failed/conflicting
saves, full walking traversal, natural slopes, and actual exported-file delivery.
The free capture action was invoked, but a downloaded image was not verified;
the supplied screenshots are browser captures. These checks remain open before
claiming the complete classroom runtime matrix.

The standalone brick, timber and asphalt routes are test strips, not a complete
circulation plan. Broader source work and existing dirty delivery scripts were
preserved. Intentional deliverables are source/registry changes, five Git LFS
hero images and these review records; heavyweight QA output remains outside
the repository. Nothing was pushed or deployed.
