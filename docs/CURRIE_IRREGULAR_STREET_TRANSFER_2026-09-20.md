# Currie irregular-site street transfer pilot — 20 September 2026

This is a bounded runtime rehearsal of an **existing** street variant, not a new
asset approval. The browser pilot used only disposable project
`7e1e9037-b98c-4d18-8502-839160315869` at the vacant CFB Currie parcel.
The protected original `f5bffc94-def9-4c43-942e-9ae7411872e9` was not
edited. Runtime source before this evidence record: `c7222f9c2`.

## Authored parcel and street

The first rectangular test was removed through the UI. The replacement site
was drawn through the ordinary Site tool with 12 corners: its eastern boundary
follows the straight road, while its western boundary bends alongside the
curving road. The browser reports about **4.3 ha** and a **309 × 179 m**
footprint. This is a visual development-site approximation with road setbacks,
not a surveyed property line or cadastral claim. It covers vacant land between
the roadways without including the occupied blocks beside them.

The Design picker placed `narrow_residential_street_v0` / Classic Tree-Lined,
then the selected street panel retained that exact variant on reload. Its
`narrow-residential-street-v1` fixed section totals 10 m: 1.2 m sidewalk,
0.6 m planting, 1.4 m flexible parking, 3.6 m unmarked yield carriageway,
then the symmetric bands. The saved street is
`a88e2fc4-c1cd-4e24-a64b-38d6a97ac1dc`; the site is
`987a7d31-ef62-4bd6-b163-1eb63342044a`. First-pass recipe hash:
`4266eb792fc730ad7f004f4d4af3a2b88556fc1afb8408f8823b98120c267912`.
The catalogue and capability fingerprints are
`a551ee6abadcaac9102cb8eedd036ca4aacbf2914e0d193449f58e67ea7b56c8`
and `9843e8af0dce72a2f2d7e9b74ec11c9f79bd6ada205f53d88b77c3abe01e0315`.

The north endpoint was dragged through the UI from inside the parcel to the
visible public road, with **Connect to a public road** selected. The PUT
returned 200. The saved north latitude changed from `51.0175081822135` to
`51.0178935449673`, with `connect_to_public_road: true`. Undo restored the
earlier endpoint and recipe hash; Redo restored the connection and final hash.
A full reload retained the 12-corner site, street variant, compiled state and
endpoint. Present correctly calls this a **proposed** public-road connection
and asks for a map check; the endpoint visually reaches the mapped road in the
overhead view. This does not certify junction grading or vehicle turns.

## Gate record

| Gate | Result | Evidence and limit |
| --- | --- | --- |
| C1 exact identity | PASS for runtime ID | Picker, selected panel and readback agree on exact variant; catalogue reference imagery was not approved against the model. |
| C2 dimensions | PASS for this fixed section | UI shows ordered metric bands summing to 10 m; supported bends/reversed sections were not tested. |
| C3 ground | PASS prepared; FAIL natural full-site | Natural mode reported uncertain ground and paused exports. Explicit Clear site for redevelopment made the street visible and free exact capture available. |
| C4 freshness | PASS for endpoint and bend edits | Undo/Redo changed endpoint and recipe hash; the bent compiled recipe survived reload. Pending tile/result races were not exercised. |
| C5 circulation | PROPOSED, not certified | Northern endpoint visually meets a real mapped road and Present explains its provisional state. Junction surface, vertical grade and turning clearance need a low-view review. |
| C6 editing | PASS for tested actions | Site draw, street placement, direct re-selection over prepared ground, endpoint and bend-point drag, Undo, Redo and reload used normal desktop controls. |
| C7 recovery | PASS for chosen mode; other failures NOT TESTED | Natural warning preserved editability; explicit prepared mode restored exact export. Interrupted/failed saves were not induced. |
| C8 visibility/capture | PASS for exact export; visual review OPEN | Overhead, low/side views and free exact preview show the street and parcel. Cars, two tree rows and thin traditional lamp posts are visible at ground view. The large level pad has a conspicuous edge; junction grade and catalogue-reference comparison remain open. No AI image was generated. |
| C9 student use | PASS desktop pointer path | No API-authored geometry or developer offsets were used. Keyboard/touch-specific authoring was not tested. |
| S1 section | PASS for this 10 m straight run | Fixed band widths and symmetric order shown in selected panel; reverse/asymmetric cases remain open. |
| S2 network | PARTIAL | An endpoint reaches the northern public road in plan. A three-point bent route saves and survives reload. Intersection pavement, crossings and T-junction behavior remain unverified. |
| S3 shared grade | PARTIAL | The prepared-site renderer uses the site's level for contained street surfaces; the saved street's older `terrain_elevation_m` is not the rendered prepared level. Physical off-site transition remains unmeasured. |
| S4 clearance/identity | PARTIAL | Live low view shows parked cars, two tree rows and thin lamp posts. Junction clearance, walkable width and exact reference match remain unmeasured. |

The site prepared elevation is `1102.22638251786 m`; the street retains
`1099.3195671846 m` in its saved terrain field. The street renderer takes the
prepared site level before that field for a contained street and uses the
shared `preparedStreetElevation` transition when the marked road extends beyond
the boundary. That transition keeps inside stations on the prepared level and
blends toward measured terrain over the first 10 m outside. The stored
difference alone is therefore not proof of a sunken road. It is a reminder to
check the rendered off-site transition rather than inferring physical contact
from stored point elevations.

The prepared pad's broad plain surface and bright exposed boundary are visible
in the exact preview. This large-parcel appearance needs design review before
using this scene as a polished classroom example. On natural ground, the site
remains only partly measured; do not claim natural-mode capture readiness or
flatten the site silently. The catalogue description also mentions parked cars
and ornamental lamps. The follow-up low view established both in the live 3D
scene, but did not compare their exact design against the catalogue reference.
Exact appearance approval stays open.

## Evidence and next bounded checks

External evidence is in
`C:/dev-artifacts/CityPrompt/grounding-batch-a/currie-clear-route/`.
`irregular-boundary-saved.png` (SHA-256
`d00c993752e032f9b40d70e2a2ac62d912a67c6d85cc4460977013f29b3cc418`)
shows the authored corners. `irregular-street-natural.png`
(`446f140225164fd0ba0919a9d68154f222e16158cd6046d3c7b8a8ea6a12be0f`)
shows the natural-ground warning. `irregular-street-connected-settled.png`
(`afde042638e90d770b834e7f01064de8c8fc42c5ec9030c6346d11c19adf9a53`)
shows the plan endpoint; `irregular-present-connection.png`
(`971b2e34fa1580576fb121b86f187f54e581c9fc362eb0c775701468801d04e8`)
shows the provisional-access notice. The post-reload exact preview is
`irregular-connected-exact-preview.png`
(`d1c7fe8aaaeac1d32270f03335df69f2661aa21f100d2e7ff637042936fc23e40`).
`irregular-street-zones.json` is the first-pass read-only saved-zone snapshot
(`3f8ee0c974323d8b38af4b533ecf831fde202ed6aee09725a76e498dd172fa0e`).
No paid render was requested and the token balance remained 4,122.

The focused prepared-ground/site/reference suite passed **20/20**, and the
street-extension/capture/readiness suite passed **4/4**. These tests were run
with `CITYPROMPT_PUBLIC_DIR` set to the authoritative
`C:/Users/andre/OneDrive/Documents/CityPrompt/frontend/public` because this
isolated source worktree intentionally has no heavy `public/archetypes` copy.
The first reference-file run without that asset root failed on a missing local
PNG path; the authoritative file exists and the configured run passed. The
browser reported no page errors after reload.

The second pass inspected the northern junction at low angle and found no
obvious floating street surface, but did not measure its grade or turning
clearance. `junction-review-low-close.png` and
`junction-review-ground-along.png` show the off-site approach, the site edge,
two tree rows, parked cars and slender lamps. The broad flat pad and bright
exposed edge remain conspicuous in `junction-review-ground-unobstructed.png`.

After reload, clicking the street over the prepared surface selected **SITE
BOUNDARY**. The shared globe zone handler now defers boundary-surface selection
to the canvas's smallest-containing-zone picker. A browser recheck selected the
street directly, selected the site elsewhere, and reselected the street. This
applies to future authored zones over prepared boundaries as well as this
variant. Evidence: `selection-recheck.png`.

The street panel's existing **Add bend point** control inserted a third route
point. Dragging it west through the ordinary white handle saved successfully
(PUT 200). On reload, three handles, `connect_to_public_road: true`, and the
compiled state remained. The centreline is now
`[[-114.12462745111789,51.01789354496727],[-114.12499257622368,51.01658486279298],[-114.12462186740842,51.01540902927948]]`.
The updated recipe hash is
`c0af80b84bcc8e8d6da26b9a2a28f5fcba682c6222689dcfd1598e2c91d8b280`.
Evidence: `bend-point-added.png`, `bent-route-saved.png`, and
`bent-route-reloaded.png` in the same external directory. The first-pass
snapshot and hash above are historical, not the current saved street state.

The next finite pilot should pair a pedestrian approach with this bent street,
measure the northern grade/clearance and test recovery while ground updates.
The prepared-pad edge also needs a design decision before this large bare parcel
is used as a polished classroom example. This existing-variant pilot does not
satisfy separate new-variant catalogue entry or publication gates.
