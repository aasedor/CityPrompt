# User generated building picker

Buildings → Object category → User generated lists the signed-in owner's
completed photo/Meshy/Tripo buildings. These are AI concept models, separate
from the reviewed catalogue. Reference thumbnails are explicitly labelled.
Failed, unfinished and repeated placed copies are excluded.

Choose & draw footprint uses the existing zone creation workflow. The server
checks source ownership, copies the stored GLB into the destination project,
links the building and saves history in the same database transaction. It
does not invoke generation or deduct credits. A failed copy rejects the save.
Source photos and generation task details are not copied. Rebuilding Community
3D preserves this saved model and includes its identity in scene freshness.

## Verification

- 52 focused frontend tests and TypeScript check passed.
- 207 backend model/compiler/landscape tests passed; after fixing a live
  timestamp refresh issue, 16 model/zone-save tests passed (overlapping suites).
- Browser: category discovery, both reference thumbnails, card selection and
  transition to footprint drawing passed on localhost:5183.
- Live API: owner-only listing, identical source/copy GLB SHA-256, save/reload,
  retry idempotency, rebuild preservation, foreign-source rejection, failed
  placement rollback and unchanged credit balance passed.
- No paid render was submitted. Full browser drawing and capture acceptance
  are not claimed by this picker check. The browser session also retained
  earlier park-revision errors; this work does not certify those park assets.

Local evidence and test scripts live outside Git at
`C:/dev-artifacts/CityPrompt/user-generated-picker-2026-09-30/`.
The local Catalogue Student account now has a private copy of the two-door
red stucco house in “My generated buildings”; its original pilot is unchanged.
That local database/storage copy is not a published catalogue asset.
