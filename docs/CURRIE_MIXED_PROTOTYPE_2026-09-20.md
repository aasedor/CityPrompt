# Irregular Currie mixed-scene prototype — 20 September 2026

## Result

On disposable project `7e1e9037-b98c-4d18-8502-839160315869`, ordinary
desktop controls produced and reopened a mixed scene on the vacant Currie field:
the previously drawn irregular site between the straight east road and winding
west road, a bent 10 m tree-lined street, one Calgary Modern Infill House, and a
40 × 35 m neighbourhood park. The protected original project
`f5bffc94-def9-4c43-942e-9ae7411872e9` was not edited. This was an
existing-variant prototype, not a new catalogue entry or asset approval.

The house uses the `infill_flat_roof_minimal` architectural-clay model on a
12 × 16 m native plot. The picker initially faced it toward the authored street.
The building and park compiled and stayed present after reload. The saved
building entrance resolves to the street sidewalk; **Review entrances** reports
two concept steps, a 0.20 m fall to model base, 1.80 m clear walking width, and
at most 0.06 m foundation support height. A first plot-guide point made a
plan-connected route but produced an `entrance_approach_obstructed` ground
warning. Moving the guide point slightly toward the visible front-step side,
saving, and running Review entrances again cleared that warning. This scene
used the approximate plot guide, so exact native-step alignment is not claimed.

The park's automatic access solver reports a connected 2.2 m path from the
street sidewalk to its internal network. The saved park has no manually locked
entrance; that is expected for this automatic route. The fixed 40 × 35 m layout
shows one play pocket and one pavilion and omits swings. Reload retained the
street's public-road connection flag, both compiled objects, the house entrance,
and the park. There were no current 3D grounding issues or browser page errors.
The free exact 3D preview opened and its PNG downloaded successfully; no paid
AI image was requested and the balance remained 4,122 tokens.

## Practical classroom disposition

This is a working desktop authoring and exact-export prototype for a prepared
site. Its broad, plain brown pad and exposed edge are conspicuous in the wide
capture, and a single grey clay house appears small in a 4.3 ha field. The clay
asset returned HTTP 200 and no asset request failed; the grey material is not a
loading fallback. The wide image is useful as technical evidence but is not a
strong finished presentation. Students should compose closer views or fill the
site with a design before presenting it. Do not describe this one sparse scene
as a visually complete neighbourhood.

The explicit prepared level is 1102.226 m. Natural ground on this large parcel
still has partial measurement, so this run does not establish natural-ground
export. The northern public-road endpoint is proposed on the map; junction
grade, turning clearance, and the park gateway's low-view grade were not
quantitatively certified. The house route is concept geometry, not an
accessibility or construction assessment. A previous real AI image was visually
appealing but failed source-layout checks; continue to offer and verify exact
3D export as the faithful fallback.

## Reuse before catalogue scale-up

For each new building, street, or park variant, make one mixed scene on a
disposable realistic parcel using ordinary UI controls. After connection Save,
check the current 3D ground/entrance result as well as the plan solver; a
plan-connected line can still be obstructed. Reopen the project, confirm saved
variant identities and rendered objects, resolve the park's automatic or
manually locked path to a sidewalk, and download a free exact image. Inspect
both a close student camera and a wide context camera. Record visual limits
explicitly; do not copy this house's guide offsets to another model. The
[shared runtime checklist](ARCHETYPE_RUNTIME_INTEGRATION.md) remains the
acceptance contract, with separate RLASM 6.1 asset review and human activation.

## Evidence

External output directory:
`C:/dev-artifacts/CityPrompt/grounding-batch-a/currie-clear-route/`.
`prototype-entrance-review-connected.png` shows the saved approach review
(SHA-256 `FE12A1FCA0884080328B3E1A785AA5AFC52C69A466AF4EA1CF5755F1F21F1CCC`).
`prototype-mixed-reloaded-top.png` shows the four saved zones after reload
(`CA40C9A97CB71A35EEF6721EF8005C20E4E0F14D0D512FB3A01D68FE503254F9`).
`prototype-exact-preview.png` shows the free preview; the actual downloaded
image is `prototype-exact-download.png`
(`06CC4765923FA45E0C5361902EE12149165C5C52A7A32FADD55E23F6E403A4A8`).
`prototype-house-close-view.png` shows the clay model and street from a closer
camera. Local model/park GLBs returned HTTP 200 on reload, with no failed
asset responses or page errors. Source files were unchanged in this pilot.
