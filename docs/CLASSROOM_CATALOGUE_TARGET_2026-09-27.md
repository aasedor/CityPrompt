# Student catalogue target: 20 buildings, 15 parks, 10 streets

## Build checkpoint

The Astra build phase now exposes **20 buildings, 15 parks and 10 streets** in
the local student picker. Eight building, seven park and three street additions
have exact assets staged and offline checks recorded. The new entries remain
pilots: current browser acceptance is **NOT TESTED**. See the three domain
catalogue documents, exact ledgers, `classroom_student_roster_2026-09-27.json`
and `CLASSROOM_45_SOL_HANDOFF_2026-09-27.md`. The count records available choices,
not 45 completed classroom approvals. No push or hosted publication occurred.

User direction, 27 September 2026: prioritize a useful, high-quality student
catalogue. Advanced resizing and video can follow. Fixed native building and
park layouts are sufficient; streets retain their advertised route controls.

## Starting point

Starting checkpoint: `a1ef001cd`, approved-validation checkout. The actual
student picker contains 12 building, 8 park and 7 street choices (27 total).
The earlier 13/9/8 inventory included three additional legacy starter entries
that are not exposed by this picker. They are candidates, not completed additions.
The target requires 8 further building, 7 park and 3 street choices, subject to
the same quality and runtime checks as the existing set.

The existing 27 do not all have complete student acceptance. Use the exact
building reviews, `native_park_acceptance_2026-09-26.json` and
`native_street_acceptance_2026-09-27.json` for current evidence. Do not copy the
historical validation roster's approval flags into new entries.

## Quality and availability

- Buildings: RLASM v6.1; Halifax clapboard v003, SoHo v002 and Crystal Brewhouse
  v003 are the recent visual references. Review complete native geometry and
  measured entrances; keep architectural-clay and textured approval distinct.
- Parks: Botanical conservatory v013 is the composition and detail benchmark.
  Preserve each park's own identity, complete paths, planting and native equipment.
- Streets: Canal v005, BRT v004 and Bridge v003 are the recent visual references,
  using their current route integration. Drawing and saved geometry must agree.
- Each student choice needs verified assets, a visible searchable picker entry,
  native-scale placement, plausible access, ordinary editing and undo, save/reopen,
  aerial and walking views, and exact capture. Record remaining concept limitations.
- Count unique student choices. Extra layouts of the same park do not increase
  the park total. A missing asset or pending visual review does not count as ready.

## Bounded work

Keep domain changes in separate branches and verified commits. First park pilot:
Shaded Reading Garden, preserving its existing composition and improving sparse
planting. Integrate through the shared native park contract. Latest user direction:
complete offline builds and checks using Astra first; run the later browser
acceptance with Sol. Keep built, locally available, and browser-accepted states
distinct. Candidate park queue: Pickleball Social Garden,
Garden Tennis, Bocce Pergola Garden, Urban Pocket Park, Linear Greenway and
Inclusive Playground. Recover the best exact assets before deciding to rebuild.

Building and street queues require exact-source and runtime review before their
final selection. Existing reviewed models should be reused where they meet the
current standard. No quota is satisfied by adding an unreviewed picker card.

Availability in this initiative means the current local student app. Hosted
deployment, Git push and paid provider calls are separate actions; none has
been performed by this checkpoint.
