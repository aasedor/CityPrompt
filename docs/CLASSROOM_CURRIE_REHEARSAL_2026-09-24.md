# Currie classroom candidate rehearsal

Recorded 24 September UTC / 23 September Edmonton. Worktree:
`C:/dev/CityPrompt-sol-empty-lot-trial`, branch `codex/currie-student-trial`.
This is a local, assisted agent rehearsal. It is not a deployed release or
independent novice proof. The active release plan remains
[STUDENT_READY_RELEASE_PLAN_2026-09-23.md](STUDENT_READY_RELEASE_PLAN_2026-09-23.md).

## Exercise and evidence

Created a disposable student account and the project **Currie — Classroom
Candidate Rehearsal**, `fca9fd40-f29e-4e0d-900c-4644cdee0dfe`, through normal
browser authoring on frontend 5178 / API 8003. No proposal geometry was seeded by
API. Credentials remain in ignored local artifacts. Existing projects and assets
were preserved. This session made **zero paid generation calls**; the student
balance remains 1,000 test tokens. No push or deployment.

The exercise contains a nine-vertex irregular 27,527.5 m² prepared site between
the winding west road and straight east road, five buildings, three streets and
three parks: all nine exact starter variants. Main Street is curved; Local and
Market Streets form two T junctions. Local Street proposes a connection to the
existing east roadway. Two single infills, two bungalows and one Beltline mid-rise
provide building variety. The neighbourhood park, teaching garden and basketball
park retain their distinct programmes. The compact neighbourhood park reports its
adaptive layout rather than promising all full-size equipment.

Browser operations included building movement and rotation, overlap recovery,
Undo/Redo after bungalow creation, a Market-to-Local section change and Undo,
court deletion/replacement, route bending, endpoint snapping, residual landscape
generation/application, reopening, exact export and sharing/report review.
Debugging interrupted the exercise, so this is **not a 35-minute completion pass**.

The final scene had 12 saved zones. Read-only database snapshots before and after
reload were identical, including geometry and properties. The toolbar returned
in 0.915 seconds and the loading indicator was observed clear by 8.496 seconds;
the latter is an observation bound, not a cold-start or complete-ground guarantee.
Final free landscape: 14,664 m², 18 trees. Earlier building-entrance review found
five connected entrances, with conceptual steps/foundations where needed; this
does not establish accessible, step-free routes.

Two exact PNGs were downloaded through **regular Edge**, opened from Downloads
and visually inspected. They show the blue sky, preserved Google context,
connected junction, entry paths, street furniture and hardscape tree wells.

| Output | Result |
| --- | --- |
| Whole-site exact PNG | 1440 × 836, 2,729,504 bytes; preview observed by 5.676 seconds |
| Close exact PNG | 1440 × 836, 1,814,338 bytes; 3.794 seconds from export click to visible download link |
| Printable advisory report | HTML, 100,873 bytes; opened/read as an exported file |

Evidence, hashes and saved-scene snapshots are outside source control at
`C:/dev-artifacts/CityPrompt/classroom-release/currie-rehearsal-20260924/`.
The earlier `cityprompt-3d-view-1790219023184.png` exposed the broken junction and
is debugging evidence, **not an accepted final output**.

## Defects found and changes

- An empty geocoded project could lose its camera framing to coarse terrain.
  Preserve that project's owned camera and reject implausible raycast elevations
  for view pivots/drawing. Normal navigation remains enabled.
- An inline DRACO loader could be recreated/disposed during ordinary parent
  updates. The tile decoder now owns a stable loader and its cleanup, including
  React StrictMode. Browser occlusion also stalled queues during this rehearsal;
  do not attribute all observed earlier loading delay to the decoder.
- A sports park could overlap a street. Park preview, drag and save now use
  bounded nearest-fit placement, preserving size and orientation. Street-to-street
  overlap is explicit; buildings/parks remain obstacles. The overlapping court
  was replaced through the UI in a clear location northeast of the mid-rise.
- Bending Main Street could remove a real Local Street junction even while their
  polygons touched. Connected editing now checks actual renderable junction
  patches and clamps the gesture before breaking them. Section replacement also
  checks existing junctions. No neighbouring route is silently moved.
- The first guard passed road-only tests but failed in the live whole-site save:
  non-road zones inherited a default road width and hid a junction. The graph now
  rejects non-road zones. The regression includes buildings, parks and boundary.
  A subsequent browser bend saved a partial movement and retained both patches;
  saved readback verified this rather than relying on the drag preview.
- Exact export once correctly refused incomplete public-road ground measurements.
  Reload recovered the route. Add a maximum of two automatic retries after changed
  visible tile geometry settles; the export gate is unchanged. Retry policy is
  unit-tested; the subsequent successful browser captures used complete samples
  with zero automatic retries. The retry branch itself is not yet a live pass.
- Revoked project access was presented as a network problem. The error view now
  distinguishes 403/404 access/unavailability from a transient loading failure.

The common archetype integration checklist and template carry these rules for
future assets. No catalogue expansion or new generated models were introduced.

## Account and report checks

Owner in Edge; existing disposable `studio-smoke` account in a separate in-app
browser session. The original sign-ins were preserved. A wrong-account invitation
offered sign-in with the invited account and no acceptance action. A matching
view invitation was accepted: all 12 plan outlines and the owner's report were
visible, without geometry editing or report-response controls. Removing access
prevented reopening. Temporary invitations were removed; no emails were sent and
no public presentation link was enabled.

The owner requested and downloaded the free report. It correctly distinguished
11 proposal areas from buildings, four detached dwellings, incomplete floor-area
quantities and unavailable policy sources. It flagged the off-site road proposal
and park walking gaps of approximately 18, 21 and 7 metres. Those findings remain
visible. Park entrance/path resolution and the report's treatment of derived
access still need a focused check; this scene is not a full park-access pass.

Chrome was not available through the connected browser tools. The separate
in-app viewer check does **not** satisfy Chrome's native-download requirement.
Editor-role UI exercise and saved-media sharing are also still open (these exact
PNGs are local downloads, not saved AI media).

## Verification and next bounded work

Focused frontend verification: 134 tests across 13 files for placement, street
editing/graphs, terrain/camera, decoder ownership and capture/retry; another
16 tests across the Currie junction, park outlines and sharing modal. TypeScript
passed after the final access-message edit. New
decoder, connected-edit and retry modules passed focused ESLint. A temporary
local diagnostic test was removed; its earlier failed saved-junction assertion
led to the whole-site graph fix rather than being waived.

The revised access-error guidance was verified in the revoked viewer's browser.

Next: verify the park entrance/path workflow and editor-role
round trip; complete exact-variant review gaps and Chrome download when connected;
then rebuild one candidate from the frozen revision. Candidate `20260924-a`
predates these fixes and must not be mistaken for this tested source. Hosted
Linux/container acceptance, destination asset delivery, funded AI fidelity
comparison and independent novice observation remain separate release gates.
