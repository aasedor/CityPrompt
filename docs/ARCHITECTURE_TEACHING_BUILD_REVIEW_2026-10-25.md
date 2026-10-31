# Architecture teaching builds — offline review handoff

This first finite batch addresses two gaps from the undergraduate catalogue
audit: a distinct Prairie School house and a clear Postmodern civic example.
The latter is a student-catalogue coverage gap; inactive Postmodern recreation
centre source families already exist. See
[the audit](ARCHITECTURE_TEACHING_GAPS_2026-10-25.md) and
[plain-language card drafts](architecture-teaching-gap-cards.json).

Both designs are original generated references, not named historic buildings.
They use the RLASM 6.1 architectural-clay profile: physical source-specific
geometry, native dimensions, occupied rooms and zero bitmap textures. Green QA
ground is excluded from the GLBs. Only small native entrance landings are
included. There is no large rectangular site pad.

## Candidate evidence

| Candidate | Native envelope, metres | Exact GLB SHA-256 | Independent visual status |
| --- | --- | --- | --- |
| Prairie School house clay-v004 | 18.4 × 12.4 × 5.8 | `0d84ec0a10f478d3c57f97ff7de47be1a9c83dcfaf5caa189492bdf040df9b7a` | PASS architectural clay; zero P0/P1 |
| Postmodern neighbourhood library clay-v002 | 20.36 × 12.665 × 5.85 | `7fb72964e6da37efab1c3f3a024c33bceb445c52b7b4e2a7dce5b9012d9c534e` | PASS architectural clay; zero P0/P1 |

Each candidate has 14 full-resolution 1600×1200 renders from an exact GLB
reimport, source locks, two 1080×1920 comparison boards, editable Blender source,
builder scripts, opening audits, native entrance measurements and a separate
runtime-review template. Geometry and material were not replaced after export.
Deterministic delivery checks passed for both candidates. Thirty focused
source/evidence, RLASM method/delivery and quality-memory tests passed.

The Prairie source lock excludes two inconsistent rear proposals. Only its
compatible front, oblique and top views govern exact identity. The model's
rear and left are explicit architectural inferences. Roof pitch was calibrated
against normalized front-source rise rather than the image-generation prompt.
Prairie fine leadwork remains simplified. A stale evidence-layout sentence is
corrected by a separate erratum; reviewed files were not rewritten.

The library has its own three-view reference lock. Its third image is a high
aerial, despite the generator's "top roof plan" label. The source shows a rear
wing setback, portico centre +3m and apex 5.85m; those observed relationships
override the prompt. Rear/left openings and detailed shelf arrangements are
declared inferences. Library v001 failed builder review because the circular
carrier and frame reveals were coincident; v002 separates them by 35mm and
regenerates the complete camera roster. Earlier failed versions are preserved.
The independent reviewer opened all 14 views, the three sources, source board
and both phone boards afresh. Remaining P2 polish is slight circular faceting
in extreme close-up and a source-view label that would be clearer as "high
aerial". Existing provenance already records that view correctly.

## Runtime boundary and next local trial

No binding was installed in the app, and no seed, live catalogue or deployment
was changed. Both exact models support scale [1,1,1] and one authored storey.
Plot clearance values are concept assumptions, not planning requirements.
Do not infer tested placement or accessibility from an offline clay pass.

| Gate group | Status and reason |
| --- | --- |
| C1–C9: app identity, transforms, support, freshness, routes, edits/recovery, capture and controls | NOT TESTED; neither exact variant is installed |
| B1–B5: building placement, measured app entrance, entrance authoring, approach recovery and access review | NOT TESTED; offline measurements are supplied, app behavior unrun |
| S1–S4 and P1–P4 | N/A for these building assets; a future mixed scene still needs its own street/park evidence |
| Model Library storage, exact-byte readback and fresh installation | NOT TESTED |
| Student ordinary-control placement, rotation, neighbour/edge snap, Undo/Redo, reload and capture | NOT TESTED |
| Natural/prepared terrain, complete foundation support, shared landscape and entrance-route connection | NOT TESTED |
| Textured keeper approval and human catalogue activation | Not granted by this architectural-clay review |

A later finite local trial should install only reviewed exact bytes in a
disposable project, register the measured entrances, retain fixed native scale
and test the ordinary student flow on level, irregular and sloped sites. It
must establish complete support, usable approaches, collision/snap agreement,
save/reload and actual exported-file delivery before any student-ready claim.

## Durable delivery and source state

The [Google Drive review batch](https://drive.google.com/drive/folders/1Pch-m8DWJQWI1GEnpz8AauMT0wHmJhEB)
contains original reference images, unchanged extracts, exact GLB renders,
comparison boards, candidate packages and failure history. The external local
root is `C:/dev-artifacts/CityPrompt/teaching-gaps-20261025`; upload IDs, hashes
and metadata verification are recorded in `delivery-manifest.json`.

Built-in reference generation exposes output filenames, not provider job IDs;
the manifest records that limitation. There are no City Prompt paid-render job
IDs, purchased credits, requested videos or saved student-project polygons for
this offline batch. No source-capture image is labelled as an AI original.

The source initiative is isolated on
`codex/architecture-teaching-gaps-20261025`. Generated binaries remain outside
Git. The dirty primary checkout and running student-fix worktree were preserved.
