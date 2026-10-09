# Final five neighbourhood buildings

Local work on `codex/final-five-neighbourhood-buildings`, based on `2bb671295`.
Requested batch: five original building families using RLASM 6.1.

| Catalogue name | Category | Intended teaching programme |
| --- | --- | --- |
| Brick Garden Courtyard | Homes over shops | Four floors, six shopfronts, homes, open passage and planted courtyard |
| Aspen Terrace Seniors Apartments | Apartments | Five floors of independent dwellings, shared lounge and garden terrace |
| Neighbourhood Health Centre | Civic | Two floors, clinic, pharmacy, covered drop-off and therapeutic garden |
| Sawtooth Neighbourhood Grocery | Shops | One floor, produce, grocery aisles, checkout and four narrow roof lights |
| Timber Wing Transit Pavilion | Infrastructure | Waiting hall, ticket machines, cafe and four timber V-columns |

## Representation and use

The realistic catalogue photographs are original generated reference images.
Models are source-specific architectural clay, with physical openings, furnished
interiors, simple source-derived colours and fixed native dimensions. They are
not textured photoreal models. Enlarge the placement plot or rotate the building;
the architecture itself is not stretched. Hidden room layouts and metric scale
are inferred educational designs, not surveyed buildings or code approvals.

Zoning matching uses the existing permitted/discretionary screening system and
the explicit programme for each building. Seniors housing means independent
dwellings, not assisted living. Health-care uses and the transit facility retain
explicit review notes where the district snapshot cannot resolve them; the cafe
component is not evidence that an entire station is permitted. Tracks and transit
operations are separate from this pavilion.

## Evidence and local trial

Immutable candidates, source hashes, full model reimport renders, phone boards,
independent reviews and failed versions are retained at
`C:/dev-artifacts/CityPrompt/final-five-2026-10-08/`.
Only independently passed candidates may enter the local trial catalogue.
Human publication approval and hosted rollout remain separate.

Trial project: `08988ff6-3b88-4def-9372-ca4803437d6e`, **Neighbourhood essentials ·
final five**, on a prepared vacant site near Range Road 284. Existing user
projects are unchanged. No paid image or video generations are part of this task.

Continuous held-key traversal requires manual follow-up:
the available browser automation sends key taps, not a sustained walking input.

## Exact candidates

| Building | Revision | GLB SHA-256 |
| --- | --- | --- |
| Courtyard | v006 | `4edb11725a41a638d9f31c34ce86a739f3d92088966d6ff143079e6d65c88271` |
| Seniors | v003 | `9721947c0cf2f0ec6813c57e068fb34bd18d07ecbef15ca809b0e549d9823165` |
| Health | v003 | `4824545b9a82581e470e73907337651db93ca0c3657a8bc8564685321af5c893` |
| Grocery | v004 | `3981963cf2543037cb472a7383f7a3466cdb157d416cc170e2ec06db7c46de5d` |
| Transit | v002 | `2aa8ac03a0f11f193b782cc2e7de8d64a214b55e25309a07e5f519dd9798581e` |

The primary entrance is measured relative to the centred native GLB. The current
shared connection API uses one primary entrance per placed building. Additional
shopfront, garden and service doors are modelled, but automatic connections to
every door are not claimed. Sloping-site approaches, uninterrupted stair walking
and hosted classroom performance remain follow-up trials.
The external `public-entrance-inventory.json` records 55 measured openings and
their inferred public/resident/service/interior roles. All five primary offsets
match the runtime roster; passage inner mouths are not extra street entrances.

## Reinstall locally

Use the existing backend environment and an existing local seed-owner account.
Set `MODEL_LIBRARY_SEED_OWNER_ID` to that account's UUID. From the repository root:

```powershell
python -m tools.final_five_buildings.install_local
python -m tools.final_five_buildings.install_local --apply
python -m tools.final_five_buildings.install_local --verify
```

The first command is a dry run. This installer refuses non-loopback database or
storage endpoints, accepts only the finite final-five roster, and uses the
normal local-trial seeder. Restart the backend after a catalogue revision.
Source images and GLBs use Git LFS. The local catalogue contains unpublished
trial entries; the publication gate deliberately rejects them until approval.

## Verification on 9 October

- All five exact candidates have independent architectural-clay passes with zero
  unresolved P0/P1 findings. Previous failed candidates remain external.
- All five were selected and placed through the browser catalogue on the prepared
  test site. Plots were enlarged without stretching the buildings. The seniors
  and grocery remain at 15 degrees; the other three face the test frontage.
- Each has a saved walking-height entrance screenshot showing the open door and
  interior. The complete scene was reloaded and retained all five. Read-only
  database verification confirms exact variant and model-dimension revisions.
- Current browser console errors: none. The backend restart briefly invalidated
  the browser session; normal sign-in restored the existing test account and site.
- Focused frontend tests: 4 files, 23 passed. TypeScript and catalogue JSON/native
  model-contract checks passed. Python source/promotion tests: 20 passed; backend
  trusted-identity test: 1 passed. The final tests require exactly five entries.
- Stored-byte verification passed for all five final GLBs. Whole local Model
  Library storage audit: 64/64 objects present, including preserved old trials.
- The runtime asset inventory was regenerated. Its release hydration report still
  identifies 3,305 unrelated missing/pointer assets in this checkout. This local
  five-model trial does not establish a complete hosted release package.

External evidence includes `final-project-readback.json`, `final-storage-audit.json`,
`final-five-runtime.png`, and each candidate's `evidence/runtime-final-trial.json`
and runtime checklist. Initial NOT_TESTED build records remain immutable; the
separate final trial records identify exactly which later checks were performed.
The trial is ready for local visual feedback. Continuous keyboard/stair walking,
all-door street connections, natural terrain and paid-render fidelity are explicit
follow-up checks, not implied passes.
