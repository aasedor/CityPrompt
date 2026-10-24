# Court-only sports — local student pilot

Four separate court-only choices let students combine and repeat sports facilities
without inheriting a complete park's landscaping and amenities. In the local app,
open **Parks** and search **court only**, or browse **Play & sport amenities**.
The existing complete parks and their saved revisions are preserved.

| Court | Playing rectangle | Complete native reserve |
| --- | --- | --- |
| Basketball | 15 × 28 m | 21 × 36 m |
| Tennis | 10.97 × 23.77 m | 18.3 × 36.6 m |
| Pickleball | 6.096 × 13.4112 m | 10.4 × 19.6 m |
| Beach volleyball | 8 × 16 m | 14 × 22 m |

Each model contains the playing surface, markings, hoops or net, and clear playing
reserve. There are no fences, lights, trees, benches or garden surrounds. Court
dimensions and the plot are fixed: use Move, Rotation and Place another. Width
and depth fields are disabled, white resize vertices are absent, and irrelevant
park parcel-enlargement controls are hidden.

## Evidence

Student project: `7f4bdfde-a41e-444c-8132-0e86733d417b` at
`http://localhost:5174/projects/7f4bdfde-a41e-444c-8132-0e86733d417b`.

Normal UI placement created two basketball courts, one tennis court, two
pickleball courts and one beach volleyball court rotated 90 degrees. Repeat,
drag Move, Undo/Redo and walking were exercised. A read-only persistence audit
confirmed six exact native assembly recipes, no fallback models, zero plot
overlaps and zero plots outside the boundary. The saved state hash was identical
before and after reload:
`f512a511191708a0b1951238ec0ab5096b4d4dc16e848b286e005373bc359070`.
Credits stayed at 476; no paid generation jobs were submitted.

Verification: 81 narrow frontend tests, 55 backend native park contract tests,
eight specification/registrar Python tests, and TypeScript checking passed.
All four GLBs were reimported and independently checked for native bounds,
equipment height, continuous ground, allowed materials and open perimeter.
Basketball was built and visually inspected before the remaining three.
All four aerial source renders were visually reviewed. A fresh read-only code
review found no actionable Critical, Important or Minor source findings.

The browser test found and corrected two integration problems: the new assets
needed entries in the student discovery roster, and the fixed-court edit panel
inherited contradictory parcel-enlargement instructions. Both have regression
coverage. Local preview assets were isolated from another worktree's runtime
overlay; six already-existing missing native assets were restored by verified
hash without changing their catalogue identities.

## Review files and provenance

[Google Drive batch folder](https://drive.google.com/drive/folders/1Se0cecqfyroERvsjQr8SmixJMtXasyr2)
contains original 1400 × 1050 PNG source renders (aerial, top and eye height per
court) and separately labelled app screenshots. These are exact 3D source
renders, not AI photographic outputs. No videos were generated for this feature
pilot. The local delivery manifest records file IDs, hashes, byte sizes and
metadata verification in `artifacts/court-only-sports-20261024/`.

Source packages are in `seed/classroom-parks/court-only-*-v001/`; each retains
the actual GLB, recipe, reviewed preview and geometry report. Generated build
logs, extra renders, runtime overlay and QA account/project remain ignored local
evidence. Registration validates the complete finite batch before writes and
preserves existing IDs and bytes. Re-run the registrar only with the same reviewed
packages; changed content needs new immutable IDs.

## Scope decisions

- Keep these as local pilots; production discovery withholds them while retaining
  saved identity lookup. Production storage/deployment acceptance awaits an
  explicitly authorized release.
- Use source-based playing dimensions with clear reserves for planning. These
  models do not establish competition certification or construction detailing.
- The registrar is a single-operator local tool. It preflights validation failures
  and rolls back ordinary write exceptions; it is not a crash-safe transaction
  across multiple files or a concurrent registration service.

No deferred minor code findings were reported. The independent reviewer left
browser acceptance and delivery to the executing agent; those are recorded above
and in the delivery manifest. The broader existing camera/context loading issue
can still require Top View / Focus Plan after a fresh project load; court geometry
and saved bindings remained intact.

Dimension references: [FIBA venue guide](https://www.venueguide.fiba.basketball/vanue-design),
[LTA court dimensions](https://www.lta.org.uk/support-centre/venue-support/facilities-and-funding/facilities-support/what-are-the-lta-recommended-court-dimensions/),
[USA Pickleball official rulebook](https://usapickleball.org/docs/2025-USA-Pickleball-Rulebook.pdf),
[FIVB beach volleyball rules 2025–2028](https://www.fivb.com/wp-content/uploads/2025/02/FIVB-BeachVolleyball_Rules2025_2028-EN-v01.pdf).
