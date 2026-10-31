# Full catalogue browser review plan

> Execute this finite test plan in the current chat. No product implementation is proposed. Use systematic debugging and regression tests if a reproducible defect needs a source correction.

**Goal:** Build every selectable local building, street/path and park variant through the ordinary application controls and report actual working and failing cases.

**Architecture:** Freeze the current catalogue inventory and keep an external per-case ledger. Use disposable prepared-site QA projects on visible clear ground. Place through the catalogue, inspect actual geometry, exercise ordinary controls, save/reopen, and retain screenshots and saved-source readbacks. File/download audits supplement these trials; they cannot substitute for them.

**Tech Stack:** Local City Prompt at port 5174, browser CUA controls, read-only PostgreSQL verification, local evidence files, connected private Google Drive.

**Spec:** User request in this chat: check all buildings, streets and parks, build them in the program and see if they work. Practical acceptance: docs/CLASSROOM_READINESS_PLAN_2026-09-20.md and docs/ARCHETYPE_RUNTIME_INTEGRATION.md.

## Global constraints

- Inventory at source 0b5e2562e: 201 catalogue cards, 204 exact placements: 105 buildings, 46 parks, 53 streets/paths. Include court-only options hidden inside parent cards.
- Only disposable QA projects may be changed. Do not replace or delete real user designs.
- Ordinary browser authoring, no API-authored geometry. Read-only source/database checks are evidence only.
- No paid image/video generation, credit purchase, publication, push or deployment.
- Keep source fixes isolated and verified; preserve exact model and saved-source identity.
- Each case starts NOT TESTED. PASS requires an actual visible result; warnings, missing programmes, proxy blocks and unsupported controls stay explicit.
- Use dated evidence under C:/dev-artifacts/CityPrompt/full-catalogue-trials-20261028. Upload completed source screenshots and reviews to the existing private review Drive parent, with verified receipts.

## Review focus

- Detailed identity versus saved block/partial geometry.
- Embedded grey bases, floating/buried objects, visible ground gaps and obstructed approaches.
- Model default size, fixed-size restrictions and supported storey programmes.
- Streets: actual metric section, route completion, bends/junction behavior where advertised.
- Parks: complete default programme, native amenities and court-only options.
- Persistence, ordinary move/rotate controls, bounded retry/recovery, and no scene-wide crash.

## Tasks

- [x] Freeze exact selectable inventory and initialize 204-case ledger.
- [x] Create a clear-ground prepared QA site through normal controls and pilot one building, one park and one street.
- [x] Buildings: all 105 exact default choices; record screenshots and save/reopen for every case. Check supported tower storey options and shared edit controls separately.
- [x] Parks: all 46 exact placements, including grouped court-only options; inspect native amenities and default programme, edit restrictions and persistence.
- [x] Streets/paths: all 53 exact choices, valid route drawing and persistence; exercise representative bends and angle joins across section types and record unsupported programmes.
- [ ] Reproduce any failures, correct authorized shared defects with narrow regressions and retest affected cases. Do not silently substitute assets or mark unrun capabilities passed.
- [ ] Produce a final per-case report separating default-placement results, advertised-control results, limitations and untested cases; upload screenshots and notes, verify Drive readback and leave local app ready.

## Street expansion checkpoint

The user added long-route testing. All 43 repeatable editable routes passed
approximately 550 m in the browser; a six-control route reached1,737.92 m with
residential, shared-lane, arterial and path geometry reviewed. Old300/480/288 m
authoring caps and prepared-ground handle drift were reproduced and corrected.
Generated junctions at approximately 31/60/90/120/149 degrees and connected section
replacement passed save/reopen. X-to-T recovery now passes at a supported37 degree
angle; a near30 degree gesture still clamps and remains open. No fixed reference
scene or bridge span was stretched. See docs/LONG_STREET_BROWSER_REVIEW_2026-10-28.md.

The catalogue placement sweep is complete, not a blanket acceptance of every
capability: 44 cases have recorded visual issues and one park walk view fails.
Building floor finishing and park camera findings remain open in the external
ledger. Do not call the whole catalogue classroom-ready.
