# Vacant Currie parcel — local grounding QA

This is the preferred **visually open-site** fixture for Batch A context and
grounding browser checks. It replaces the broad fictional Gold Standard site
for tests that require an apparently empty parcel. The Gold Standard remains a
frozen mixed-use benchmark; its prepared redevelopment scene is not evidence
that nothing existed under every proposed object.

- Local project: `f5bffc94-def9-4c43-942e-9ae7411872e9` at
  `http://127.0.0.1:5174/projects/f5bffc94-def9-4c43-942e-9ae7411872e9`.
- Existing-condition source: Google 3D Tiles at Currie, Calgary. The tested
  parcel is centred near `51.01652, -114.12461` (the project's broader Currie
  geocoder anchor is `51.0184836, -114.1237628`). The photographed block is bare ground;
  the public street and occupied buildings are visible beside it.
- Site outline: the eight-vertex boundary saved in the original 7 September
  twenty-building trial's `final-zone-inventory.json`, not the first broad
  rectangular attempt. That boundary excluded an unstable part of the Google
  visible surface and reached a settled scene in this browser check.
- Proposal: seven one- and two-storey reviewed residential representations
  (Craftsman bungalows, an Edwardian Foursquare, and modern infill homes), one
  neighbourhood park, and one six-metre internal yield street. These choices
  match the scale of the nearby residential context. The shortened street was
  authored wholly within the test block.

The fixture is a **disposable local copy**. The 20-building source project,
Salisbury hillside source, and frozen Gold Standard were not edited. Building
representations were copied from the documented local trial into new Building
records with new zone IDs; this is runtime QA setup, not evidence of a novice
student placement journey or a new RLASM review.

## Verification

The browser captured the site before proposal content at
`C:/dev-artifacts/CityPrompt/grounding-batch-a/vacant-currie-empty-oblique.png`
and `vacant-currie-empty-top.png`. After adding the proposal, it captured
`vacant-currie-proven-boundary-settled.png`,
`vacant-currie-proposal-top-settled.png`, and
`vacant-currie-reload-settled.png`. All were visually inspected. They show the
proposal within the open central block; the photographed curved road to the
west, public street to the east, and occupied structures remain outside the
proposal. The after-reload view retained all seven buildings, the park, and the
street. A clean reload produced no page errors or failed network requests.

An independent polygon check found all nine proposal zones covered by the
site polygon, with no positive-area overlap between any pair of proposal
zones. This checks authored geometry, not the precise survey footprint of
photogrammetry. The first broad rectangle failed the application's ground
quality gate; that failure is preserved in
`vacant-currie-ground-review.png`. The final fixture uses the previously
validated eight-vertex outline, and 3D loading settled without a ground
warning. It still requires pedestrian-level contact and controlled tile
refinement checks before the full grounding release gate can pass.

Google imagery establishes only that the parcel **appears open in the captured
context**. This check does not establish legal vacancy, development rights,
current construction status, a surveyed boundary, or bare-earth elevation.
No paid image or video generation was used. The project and screenshots are
local QA assets, not production seed content.
