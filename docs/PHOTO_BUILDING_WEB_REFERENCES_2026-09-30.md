# Web references for custom photo buildings

The Photos to 3D window now includes **Find more views online**. Students enter
a building name, choose an angle, and select photographs of the same building.
Up to four sources can combine uploaded photographs and Commons results.
Search is free; the existing 50-token reference preparation and 150-token model
generation remain separate, explicit actions.

## Implementation

- Wikimedia Commons search and image metadata APIs provide up to 12 results per
  search. The pilot uses name/title search, not automatic landmark recognition.
  Aerial, exterior, rear and side are search hints, not verified camera labels.
- Results include plain-text author, licence and source-page attribution. The
  student confirms the same building by selecting its photo. Only supported
  public-domain, CC0, CC BY and CC BY-SA records are offered.
- The server retains 48 recent candidates per building and signs each candidate
  against that building. Submitted IDs cannot replace the server's image URL
  or attribution, including through generic specification edits.
- Imports accept HTTPS images only from the two Commons media hosts, disallow
  redirects, bound download bytes and validate/normalize the actual image. All
  selected imports must succeed before tokens are reserved. Stored source bytes
  have SHA-256 hashes and provenance that survives reference/model generation.
- Existing project permissions apply. Search outages and no-result cases leave
  uploads available. Stale selections fail before a provider submission.
- The selected generated-view subset is retained and visible after reopening.
  Inputs are disabled while either paid stage is running, including after reload.
- The reference prompt reserves space for student notes within the existing
  Meshy client's 600-character cap. The stored brief retains the full input.

API documentation used:
[Commons search](https://www.mediawiki.org/wiki/API:Search),
[image metadata](https://www.mediawiki.org/wiki/API:Imageinfo),
[Meshy image preparation](https://docs.meshy.ai/en/api/image-to-image).

## Concert-hall trial

Disposable local project: `a4b28067-b47a-4daf-9faf-e9e505daa595`.
Building: `f465419b-4a10-49e1-91ce-60e117e18d6a`.
Local UI: `http://127.0.0.1:5183` (backend 8007).

One reference submission used the user's clear front photo and two real aerial
photographs by Carol M. Highsmith, marked public domain by Commons:

- [Aerial 2013633216](https://commons.wikimedia.org/wiki/File:Aerial_view_of_Walt_Disney_Concert_Hall_in_Los_Angeles,_California_LCCN2013633216.tif)
- [Aerial 2013633215](https://commons.wikimedia.org/wiki/File:Aerial_view_of_Walt_Disney_Concert_Hall_in_Los_Angeles,_California_LCCN2013633215.tif)

Generated views 0 and 1 were used. View 2 had a conspicuous missing roof section
and was deselected in the browser. One model submission completed and mounted
in the existing disposable project. The trial used 200 City Prompt tokens;
there were no additional paid retries. The previous model and state were saved
before replacement. The reference submission preceded the prompt-shortening
fix; that fix has automated coverage, not an additional paid visual trial.

The result contains substantially more roof, garden and side-wing structure
than the first attempt. Visual inspection still shows softened roof details,
flattened/merged metal sails, dark baked surface shading and approximate glazing.
It is a private AI preview, with no RLASM keeper or classroom catalogue approval.

## Verification and evidence

- Backend: 17 focused pytest cases passed across reference search and the existing
  photo-building workflow.
- Frontend: 5 focused Vitest cases passed; TypeScript type-check passed.
- Browser: search, angle selection, source selection plus upload, paid reference
  submission, exclusion of the damaged view, paid model submission and mounting
  were exercised through ordinary controls.
- Offline: eight actual-GLB views inspected, including both sides and roof.
- No new catalogue assets were published. No aerial/street AI presentation
  renders, terrain/entrance certification or storey/footprint scaling trials were
  part of this feature test.

Generated evidence, source images, exact model and prior-state record are outside
Git at `C:/dev-artifacts/CityPrompt/landmark-reference-pilot-2026-09-30/`.
`trial.json` contains the model hash, source provenance, reference hashes and
generation state; screenshots and GLB renders sit beside it.
