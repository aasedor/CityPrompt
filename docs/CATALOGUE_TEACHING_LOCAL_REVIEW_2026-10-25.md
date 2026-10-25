# Undergraduate catalogue teaching — local review

Date: 2026-10-25. Branch: `codex/teaching-catalogue-20261025`.
Base: `44930bc3f2f7322c5d04ea670e92ad7fec9ee78a`.

## What changed

The catalogue now has visible ways to explore by use, architectural style or
planning idea. Selected topics explain their defining features and main idea
in a few undergraduate-level sentences, with expandable primary-source links.
Expanded cards separate building use from style and planning connections.

The authored audit covers 196 exact local choices. It supplies 42 design/style
definitions and six introductory planning topics: New Urbanism,
transit-oriented development, Garden City, green infrastructure, Complete
Streets and car-oriented layouts. Each domain offers topics with actual
matching components; a component does not certify a whole neighbourhood.
The default test environment exposes 195 choices; the existing local
development configuration exposes 196. The overlay does not activate choices.

Of 29 previously unlabelled buildings, 25 have usable style classifications.
Four are among eight disputed entries and remain held. Their cards say
“Style to be confirmed”; changed model revisions also withhold the old lesson.
No registry, model, reference image, placement contract, seed or backend
implementation changed. The separate Prairie School and Postmodern library
review candidates remain inactive.

Four existing court-only designs lacked browsing metadata on the base branch.
Their presentation entries now use their existing authored labels and
descriptions. This corrects the pre-existing catalogue coverage test failure.

## Student browser trial

Tested the actual app at `http://localhost:5174` through Edge, with backend
`http://127.0.0.1:8002` and the existing hydrated asset directory. The preview
serves this isolated branch. The main and student-fix source checkouts were
not modified. Project: `7f4bdfde-a41e-444c-8132-0e86733d417b`
(court-only athletic park student pilot).

| Trial | Observed result |
| --- | --- |
| Buildings → Architectural style → Neoclassical | One matching office; short definition and RIBA source link shown. |
| Expand building details | Use and architectural lesson appeared without starting placement. |
| Neoclassical + New Urbanism | Clear zero-match state; Clear filters restored all 97 buildings and cleared both topics. |
| Keyboard style selection, then Tab | Selected Neoclassical and moved focus to the planning selector. |
| Choose Neoclassical Office, then Escape | Existing 33 × 36 m preview opened and cancelled; no drawing added. |
| Streets → Planning idea → New Urbanism | Eight drawable components and two optional fixed review segments; whole-plan limitation visible. |
| Phone-width responsive check | Observed 357 CSS-pixel viewport and page width both 357; controls stacked, lesson wrapped, results reachable by scrolling. Override reset afterwards. |
| Search Inglewood, expand card | Held style and short uncertainty explanation; no tentative style taught as fact. |
| Captured browser warning/error logs | Empty list at the end of the trial. This is not a complete network or model-fidelity audit. |

Two old browser-tab bindings timed out before the trial. A fresh tab in the
same browser worked. One exact-label automation selector failed; the current
accessible selector worked. Neither failure was an app error. Screenshot
storage outside the browser tool's permitted directory was refused; its
documented temporary directory worked, and the resulting JPEG files were
copied into the external review folder. No app media export gate was used.

Screenshots are labelled `SCREENSHOT-*`; they are UI captures, not AI render
originals. They include desktop style browsing, the phone-width controls and
planning lesson, and the held reference/card explanation. No image/video
generation or credit purchase was needed for this phase.

## Verification and review

- 68 tests passed across nine relevant frontend teaching, palette, card,
  presentation and facet files. The initial narrow baseline was 35/36, with
  only the four missing court presentation records failing.
- `npm run type-check` passed after the final production edits.
- Four generator tests passed, including five altered-contract subcases and
  a regression check for Git line-ending conversion of locked inputs.
  The changed-revision failure was observed before the evidence fix.
- Startup delivery audit: 186 audited choices, 578 distinct image/model
  dependencies, zero failures. This checker has a different scope from the
  catalogue's displayed choice count.
- `buildingArchetypes.json` is byte-for-byte unchanged: Git blob
  `94cdad41c2ca974b1bee4032b56b10aa1d8164a9` matches the base.
- Fresh whole-branch code review found one important generator issue and one
  reproducibility issue. Both were fixed and independently re-reviewed with
  no remaining findings. The old audit can no longer be rebound to an updated
  model inventory. Immutable reviewed inputs and rebuilding instructions are
  checked in under `tools/catalogue_teaching/`.

## Remaining limits

This is a local teaching implementation, not a deployment or a claim that all
models have passed a fresh visual audit. The eight reference conflicts still
need source/model reconciliation. The two new RLASM candidates still need
human visual approval and a separate runtime integration initiative. The
source branch has not been pushed. Generated screenshots, logs and delivery
receipts stay outside the source tree at
`C:/dev-artifacts/CityPrompt/teaching-catalogue-20261025`.

## Delivered review evidence

[Teaching screenshots and review note](https://drive.google.com/drive/folders/1E8yvPqqSn_UH2e90UHupp0GMR2RIvg4i):
five original JPEG UI screenshots plus the review note, verified by Drive
file size and parent folder readback. Project ID and the absence of new
generation jobs are recorded in the local delivery manifest.

[Earlier RLASM model batch](https://drive.google.com/drive/folders/1Pch-m8DWJQWI1GEnpz8AauMT0wHmJhEB):
Prairie School and Postmodern library reference originals, exact 3D source
views, comparisons, model handoff and review evidence.
