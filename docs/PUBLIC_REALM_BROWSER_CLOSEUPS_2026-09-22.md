# Five public-realm browser close-ups — 2026-09-22

Completed the requested close-up browser screenshot and one AI render of each
new concept: Pickleball Social Garden, Community Futsal Park, Shaded Reading
Garden, Planted Shared Street and Garden Cycle Promenade. This review follows
the [park asset batch](SPORTS_GARDEN_ASSET_BATCH_2026-09-22.md) and
[street asset batch](PLANTED_STREET_ASSET_BATCH_2026-09-22.md).

## Evidence and scope

Output: `C:/dev-artifacts/CityPrompt/public-realm-browser-review-2026-09-22/`.
Open `index.html` directly, or use the locally served comparison gallery:
<http://127.0.0.1:5176/__review/batch3-closeups/index.html>.
`CityPrompt-five-closeup-comparisons.zip` contains the standalone gallery,
five exact 1200 x 750 WebGL captures, five 1586 x 992 provider images, ten full
browser screenshots, review notes, sanitized generation metadata and SHA-256
manifest. The images and heavy output remain outside Git.

Actual accepted GLBs were loaded with Three.js in a temporary Vite review page
on port 5176. Orthographic close-up cameras emphasize courts, pergolas,
furniture, planting and cycle markings. No model geometry was replaced by an
image. The clean canvas captures were supplied through the existing Classic
image-edit API to `gpt-image-2.5-flare`, high quality, requested 16:10, without
postprocessing. The same camera view is retained for each source/render pair.
The prompt asks to preserve geometry and refine surface appearance only.

These are isolated asset reviews, not site integration or Google Tiles tests.
No zone fingerprints or compiled-scene claims were manufactured. The Classic
route does not run the Direct 3D fidelity gate; renders are explicitly marked
illustrative. Terrain, placement, edits, Undo, reload, student picker activation
and district performance remain pending as documented in the asset reports.
No site zones, source models or production code were changed in this review.

## Visual comparison

| Concept | Observation |
| --- | --- |
| Pickleball | Court, pergola, seating and planted-bed arrangement retained. AI extends paving beyond the model edge and changes fine fence/gate detail. |
| Futsal | Goal, offset entrance, team pergola, seating and main markings retained. AI turns the neutral background into additional grass. |
| Reading garden | Both pergolas, benches, picnic table and planted-room pattern retained. AI increases planting density, adds flowers/soil openings and extends paving. |
| Shared street | Flush route, connected seating bays, tree beds and lights remain legible. AI adds paver texture and fuller planting. |
| Cycle promenade | Pedestrian/cycle separation, crossing, seating and opposing arrows retained. Bicycle symbols are redrawn and grass edges softened. |

Agent visual review: useful concept illustrations with the deviations above;
not an automated fidelity pass or human visual approval. Exact dimensions and
construction remain defined by the 3D source. Neutral studio backgrounds can
be interpreted as extra landscaping despite the prompt: a render is not
evidence of the model boundary.

## Save and credit verification

Exactly five successful calls, 26 credits each: **130 credits total**. Account
balance changed from **718 to 588**. All five returned images were saved with
style `asset-closeup-illustrative` in project
`54818ada-581f-4643-900a-78867b076c8c` (Currie Empty Lot — Sol Catalogue Trial).
Authenticated gallery GET returned 11 total images and matched all five new
saved IDs. Database audit rows independently reconciled all five charges.
Sanitized IDs, timestamps and charges are in the companion JSON and external
`credit-and-save-verification.json`. No additional paid retries were made.

The shared-street image generation and gallery save succeeded, but the later
account/model refresh returned HTTP 500. The temporary review page's broad
catch misleadingly labelled this as a render failure. Its raw error is retained
in metadata. The returned image and saved ID were checked before continuing;
the final authenticated account and gallery reads succeeded. Future reusable
review tooling should separate generation, save and account-refresh status so
a failed balance refresh cannot suggest a paid retry.

The browser comparison gallery decoded all ten images, reported no horizontal
overflow at 1264 x 1050, and returned HTTP 200 for all 22 image/download links.
`gallery-browser-check.json` and `gallery-browser.png` preserve that check.
No production TypeScript or backend changes: no production test suite rerun
was needed. Earlier console errors in the separate Currie tab are outside this
asset review; no global clean-console claim is made.

## Reproduction and next checkpoint

The ignored `artifacts/batch3-browser-review.html` preserves the viewer and
camera presets; its external archive is `review-viewer-source.html`. It has
explicit per-concept paid-render buttons and no generation on load. Preserve
completed outputs before reloading, because its duplicate-call guard is only
in memory. Reuse the existing images for further visual review.

Next: a separate bounded runtime integration initiative, starting with one
park and one street on vacant Currie land. Reuse shared terrain, native-size
components, access and edit/capture systems; complete exact-variant runtime
checklists before activating the five concepts in the student picker.
