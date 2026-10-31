# Long street and pathway browser review — 28 October 2026

The user asked to expand the different streets and verify that students can draw
long sections. This is a local authoring checkpoint; nothing was pushed,
published or deployed. No paid image or video calls were made.

## Outcome and changes

All 43 repeatable editable street/path choices were built at approximately 550 m,
saved and reopened through ordinary browser controls. The fixed-span bridge was
tested within its existing 260–480 m range. Nine fixed reference scenes were
placed at native size; they do not become extendable routes.

Several native street validators still capped routes at 300/480 m and the elevated
rail walking guard capped them at 288 m. Repeatable routes now share a 2,000 m
authoring limit in frontend/backend policy. Widths, native amenity scale,
station-count/straightness restrictions, source programmes and model hashes stay
unchanged. Historical recipes retain their old exact capability/catalogue locks;
those locks cannot approve an extended or modified recipe.

Prepared ground was another reproduced defect: editing sampled hidden original
tiles and displaced the white dots from the visible street ends. Handles and
pointer picking now use the prepared datum. A recorded X-to-T gesture also
revealed an unnecessary arm-count lock. A complete T or X may preserve the same
connection; removal of a working junction still rejects.

## Browser evidence

Disposable project: `8ef6fab3-ad0b-4225-89ff-46e28921e317`, local port 5174,
Edge desktop mouse/keyboard, Student stress tester. Original catalogue default
trials used a vacant prepared parcel. Long trials expanded this disposable site
to 640 × 680 m over surrounding map context; it is a synthetic stress-test parcel,
not a planning proposal or surveyed vacant land.

| Trial | Result |
| --- | --- |
| All 43 repeatable exact choices, approximately 550 m | PASS: full section, save/reopen, exact selected type |
| Residential six-point route, 1,665.38 m and four rounded bends | PASS |
| Endpoint extension to 1,737.92 m; Undo/Redo/reopen | PASS |
| Same extended route as planted shared lane, four-lane arterial and asphalt shared path | PASS: complete bends and native section widths |
| Residential crossings around 31° and 60° | PASS: complete generated junction and reload |
| Connected residential section replaced by 24 m cycle avenue | PASS: junction retained |
| Shared path crossings around 90°, 120° and 149° | PASS: complete route and reload |
| New near-road path endpoint | PASS: snaps to a complete T |
| T→X→T at approximately 37° | PASS after correction: no spur, saved/reopened |
| Existing X shortened near the 30° angular limit | OPEN: can clamp into a spur; not counted as a passing recovery |

The 2,000 m validator ceiling is covered by automated tests. This does not mean
every variant was drawn at 2,000 m in the browser. Straight-only transit programmes,
authored station limits, bridge span limits and fixed reference scenes retain
their restrictions. Natural/sloped terrain, public-road service access, touch
input and exhaustive pedestrian-height junction inspection are NOT TESTED in
this long-route batch. Public-road context lookup failed externally in one trial;
internal drawing remained available.

## Verification

- Full frontend suite: 470 files, 4,016 tests PASS.
- Backend street/recipe suite: 219 tests PASS.
- Focused junction/edit regression: 6 files, 82 tests PASS; the new X-to-T test
  first failed against the arm-count lock.
- TypeScript type-check PASS after completing required test fixture fields.
- Prepared handle regression first failed at 1,042 m versus the prepared 1,026 m
  datum, then passed; browser handles align with rendered route ends.

Evidence, originals and exact-variant runtime review records are outside Git:
`C:/dev-artifacts/CityPrompt/full-catalogue-trials-20261028`.
The cases ledger retains all 204 catalogue placements, including visual issues
and the failed park walk camera. Successful placement alone does not certify
every entrance, floor finish, walking view or supported size.

Private review folder:
https://drive.google.com/drive/folders/1C8FphiN9m8biRKuu7UNBUHfYJPp9YQKy
Upload receipts and metadata verification are recorded in the local delivery
manifest. Screenshot originals are labelled as 3D source screenshots, not AI
renders. Source changes form one street authoring/recovery initiative; all
generated screenshots, archives and test logs remain external.
