# Seven usable native streets

Branch: `codex/seven-native-streets`, starting at park checkpoint `d34a9b9da`.
The eight native parks and Basketball Long remain on `codex/custom-render-prompts`.
No push, merge, publication or paid street render is authorized.

## Scope and milestones

Preserve Main Street (23 m), Market Street (18 m), Calgary Local and saved
fixed fixtures. Implement these exact five, in this order:

1. Quiet Residential, residential-v002, 18 × 48 m reference composition.
2. Planted Shared Lane, shared-v001, 14 × 40 m reference composition.
3. BRT Transit Mall, brt-v004, 40 × 100 m reference; explicit station programs.
4. Amsterdam Canal, canal-v005, 36 × 80 m reference; water/bank ownership.
5. Tied-Arch Gateway Bridge, bridge-v003; measured 84 m structural span,
   24 m endpoint section and 4.3 m deck, within a 36 × 100 m inspection fixture.

Use a shared, immutable native street contract, with specialist capabilities.
Preserve original assets and source recipes. Recover complete authored surfaces,
edging, furnishings and programs; never stretch or repeat whole preview GLBs.
Verify each native reference composition before scaling, then longer/reversed
routes, supported joins, recovery, persistence and exact export. Unsupported
specialist geometry must receive actionable rejection, retaining the saved design.

## Evidence and current state

External evidence and persistent detailed log:
`C:/dev-artifacts/CityPrompt/streets-runtime-2026-09-26/PROGRESS.md`.
The supplied review archive has SHA-256
`1234404b3738bf4c247d0d51968d36455503b12e4684e877712ab4cbfd7f63db`.
Five whole assemblies, 20 target modules and 15 specialist source scripts match
their recorded hashes. Main/Market baseline module bounds and the 44-family
capability catalogue are preserved. These are asset checks, not runtime passes.

First reproduced defect: drawing an 18 m diagonal Market route used a different
buffer from road editing, producing 17.548 m perpendicular width and 2.003 m
end-cap skew. Drawing, editing and street-view line preparation now share the
metric-normal helper. Existing saved polygons are not changed on load.

The shared foundation now also preserves unchanged saved family recipes through
catalogue additions, using finite historical capability locks and canonical
revalidation. It retains all native Main/Market components, removes long-route
cycle thinning, and checks complete module bounds with coupled tree/well clipping.
Repeated meshes use instancing, preserving source materials and transforms.
SHA-verified asset loading and expected-instance capture checks reject absent,
stale, corrupt or incompletely mounted street programs; Retry 3D update recovers
failed loads without accepting late errors for moved/deleted objects.

Verification: 39 focused frontend tests, 98 backend recipe tests, TypeScript and
production build passed. Fresh production browser at localhost:4181 reopened the
disposable eight-park/Market scene and exported its exact current view; no page
errors, only the ordinary elevation log. Evidence: `shared-baseline-top.png` and
`shared-baseline-export.png`. This is a bounded Market regression smoke, not a
pass for the five new streets or every Main/Market workflow. No paid calls.

## Residential integration checkpoint

Recovered Residential's complete source composition through a hash-locked adapter:
138 rigid placements per 48 m cycle, authored ground ownership, seating pads,
cross-link, physical bed edging, paving joints and drainage details. Route editing
preserves native sizes, accepts 48–480 m on prepared level ground, and rejects
short edits before changing saved geometry. Existing fixed rectangles keep their
assembly bindings. Registry/roster mirrors have a reproducible checked sync tool:
`tools/public_realm_assets/sync_native_street_registry.py`.

Production browser at 4181 verified catalogue drawing, automatic compilation,
reopening, Walk, moving, Undo/Redo, extension and short-edit recovery. It exposed
and resolved an incorrect prepared-ground gate on interior streets. Exact preview
capture passed; the browser cancelled the download click, so file export remains
an open check. Browser errors: none. No paid calls. Full matched-view comparison,
curve/junction matrix and fault injection remain pending; this is not a completed
street approval. Evidence: `residential-browser-checkpoint.json` in the external
evidence directory. Latest source tests also cover legacy rectangle preservation
and registry/roster parity.

## Shared Lane integration checkpoint

The exact shared-v001 delivery is now reconstructed through the same adapter,
with its own 14 m section, 118 placements, four walkway arbors, 0.48 × 0.24 m
brick units and complete ground program. The original 12 m service lane is not
substituted. The registry sync retains the pre-addition capability catalogue so
saved Residential/Main/Market recipes continue to validate.

44 focused frontend and 103 backend tests passed, along with TypeScript and a
production build. Fresh production browser checks passed catalogue drawing,
automatic compilation, Walk, exact street-view preview, reversal with extension,
Undo/Redo and reopening. No page errors or paid calls. Matched-view fidelity,
curve/junction matrix, asset failure injection and file download remain open.
Evidence: `shared-browser-checkpoint.json`. Candidate status remains pending.

At the Shared Lane checkpoint four route candidates were implemented. BRT, Canal and Bridge remained
fixed review fixtures while their specialist programs are implemented. Original
editable Blender files for all three match their recipe authoring hashes and
retain semantic components, recorded in `specialist-authoring-inventory.json`.
Next: BRT's complete explicit station and crossing program, separate from ordinary
repeatable transit segments. Do not count the five-street initiative complete.

## BRT integration checkpoint

The brt-v004 original is preserved. `extract_brt_runtime.py` recovers the complete
152-object station/crossing program and the original lettering/arrow module from
its hash-verified editable file. `verify_brt_extraction.py` checks both directions
of the mesh round-trip by material: maximum station vertex error 0.000003313 m,
ten materials retained; bus symbol error zero. Source and reconstructed aerial
and walking-height views were rendered from identical cameras and inspected in
`brt-matched-v1/`. Equipment, planting, paving, ramps, median and markings match.
`stage_brt_runtime.py` uses the shared immutable delivery workflow; staged bytes
stay outside tracked source and the original files are unchanged.

The local BRT candidate supports straight, prepared-level routes 100–480 m long,
40 m wide. Students add, move and remove stops explicitly; right-click selects
a distance for the Add station / stop control. Stop envelopes require 21 m before
and 33.5 m after the anchor, with 56.5 m between anchors. Invalid edits retain the
saved corridor. Draft roads and junctions must stay clear of the full station
reservation; the initial capability does not join another road through a stop.
Stations never appear automatically when extending a corridor. Rigid modules
remain unscaled; source-authored surfaces and openings follow the chosen stops.

Stop positions participate in automatic compilation, server source hashes and
mounted-scene capture identity. Existing fixed BRT fixtures remain bound to their
original assembly. This checkpoint also repairs a misplaced legacy-fixture guard
that referenced `strict` inside the fallback helper; dedicated regressions now
exercise both fixed-fixture paths.

Verification: 43 focused frontend tests, 116 backend tests, five staging/adapter
tests, TypeScript and the production build pass. In the disposable production
project, ordinary catalogue drawing (118 m), empty corridor, add stop, right-click,
overlap rejection, stop move, Undo/Redo, reopening, whole-route move, Walk and exact
street/aerial preview pass. No page errors or paid calls. The file download again
reports `Download was canceled` in the automation; file delivery is unresolved.
Endpoint joins, extended BRT routes, multi-stop browser checks and fault injection
remain open. See `brt-browser-checkpoint.json`; this is a candidate, not final
runtime approval or publication.

Current local selection: five route candidates and two fixed review fixtures
(Canal and Bridge). The seven-usable-street objective remains incomplete. Next:
Canal's water, banks, original arch crossing and basin termination; then the
Bridge's fixed structural span and correctly graded approaches. Preserve the
separate parked buildings/parks work and use no paid street generations.

## Canal integration checkpoint

The canal-v005 original is reconstructed once from its exact ground, crossing
and furnishing programs (8,483 meshes). Matched aerial and walking-height views
were inspected; material-separated round-trip error is at most 0.000009537 m.
Source files remain unchanged. Hash-verified extraction and staging also prepare
the fixed bridge span, but Bridge is not activated at this checkpoint.

Canal routes are straight, prepared-level, 36 m wide and 80–320 m long. Only the
open end extends, using native-size components and the source brick program.
The basin and original arch remain single instances. The corridor owns its ground
cutout; water stays at -2.05 m. Ordinary roads snap to the dry outer bank and cannot
create an asphalt junction across the channel. The outer 1.9 m walk provides a
connection apron; penetration into the inner bank is rejected.

Production browser checks passed catalogue drawing (243 m), short-route rejection,
resizing, Walk at the original arch, free exact street/aerial preview, a Market
bank connection and reopening. Rapid Undo/Redo initially exposed a real revision
race with automatic compilation. Zone history writes now share the project write
queue; a fresh rapid Undo/Redo and reopen preserve the 153 m result. The tests also
retain editing support for existing Calgary Local streets without adding them to
the finite new-street picker. Earlier failure screenshots remain in the evidence.

Verification: latest 33 targeted tests pass, earlier broader frontend checks pass,
109 backend tests, registry parity, TypeScript and production build pass. The new
bank-apron tolerance has unit coverage; browser recheck remains pending. Downloads
still report `Download was canceled` from agent-browser, while exact previews pass.
This remains an open delivery check. The shared specialist foundation includes
unactivated bridge approach/camera helpers. No paid calls or publication.

Evidence lives outside source in `streets-runtime-2026-09-26`, including
`canal-browser-checkpoint.json`, `canal-roundtrip.json`, `canal-matched-v1/`,
`canal-bank-snap-ready.png` and `canal-fast-redo-reopened.png`.
Current local selection is six route candidates plus the fixed Bridge review
fixture. Full acceptance, fault injection and the seven-usable-street goal remain
open; candidate activation is not completion approval.

## Fixed bridge integration checkpoint

Bridge v003 now uses the normal route catalogue and saved native contract. Its
1,672 structural meshes retain their exact source transforms/materials; only the
inspection water plane is excluded. The extracted GLB round-trip has zero vertex
error. The original 84 m arch and 100 m deck stay rigid, with 24 m deck width,
36 m support reservation and two minimum 80 m approaches. Routes support
260–480 m on prepared level ground. Matched original/reconstructed aerial and
walking views were inspected. Approaches use matching asphalt, marking, paving
and open railing programs, joining the 4.30/4.482 m source deck/walk elevations.

The production browser passed ordinary catalogue drawing, ground-endpoint Market
connection, a Market underpass with no at-grade junction, walking up the approach
onto the deck, walking under the span, direct deck entry, short-edit rejection,
extension, Undo/Redo, reopening and exact capture. Tall modules below the bridge
yield as whole occupied components to the source girder clearance; low market
stalls remain. A neighbouring bridge edit changes the capture clearance identity.
Native programs are no longer dropped by the historical 160-road detail budget.

The recurring PNG failure was traced to agent-browser's escaped Windows download
path. The same visible Download render control succeeds through Chromium with a
normal native path; no export-code workaround was required. Actual PNG:
`downloads-verified/cityprompt-3d-view-1790503133245.png`, 1,289,863 bytes,
SHA-256 `38f2671791faa92546d9a2b92c8b22dcfcadc8f8ef2f1ef369fcbdaaea65f3bc`.
The earlier automation failures remain recorded, superseded by this file receipt.

63 targeted frontend tests, 109 backend tests, registry parity, type-check and
production build pass. No paid street calls. Seven route candidates are locally
available; this is not final completion: the full finite matrix, including asset
fault recovery, duplicate/delete and ordinary-street joins/curves, remains open.
Bridge evidence: `bridge-first-ready.png`, `bridge-walk-forward.png`,
`bridge-walk-below.png`, `bridge-deck-entry-fixed.png`, `bridge-endpoint-connection.png`,
`bridge-short-edit-rejected.png`, `bridge-extended.png`, `bridge-redo.png`.

### Native source comparisons completed

`render_native_program_comparison.py` compares actual frontend output and original
source GLBs from matched top, oblique and pedestrian cameras. All twelve images
in `residential-matched-v1/` and `shared-matched-v1/` were inspected. The complete
native compositions agree, including beds, paving, arbors, planting and furniture.
The intentional runtime ground lift is 0.025 m. These close earlier source-fidelity
checks; they do not replace the remaining browser matrix or human visual approval.
