# Draft 4.B source reconciliation — 2026-09-30

Supplement to [the runtime checkpoint](STREET_MANUAL_CHECKPOINT_2026-09-30.md).
No runtime dimensions, saved variants, geometry hashes or publication status change
in this evidence-only checkpoint. The per-variant results and source hashes are in
[the review ledger](STREET_MANUAL_REVIEW_2026-09-30.json).

## What the supplied files contain

- **Street Manual Draft 4.B**, March 2026, 117 pages. Page 1 explicitly describes
  new material for section 1.9 and chapters 9/10. The other headings are placeholders
  for material circulated in 4.A. Section 4.4 on page 23 has no cross-section drawings.
- **Standard Intersection Drawings**, 41 pages: 12 numbered intersection designs,
  accompanied by swept-path and related checks. These contain valuable approach
  dimensions but not every component of the 13 standard mid-block sections.
- Main-manual page 40 explicitly excludes intersections involving High Activity
  Collector/Arterial approaches because cycle-track configurations are being refined.
  These omissions must not be filled with a generic junction claimed to be official.

## Findings from drawing images and tables

| Source | Finding | Effect on current pilot |
| --- | --- | --- |
| Drawing 11, PDF p37 | No-parking local: 16 m total, 6.5 m carriageway, two 3.25 m lanes, 1.8 m separate sidewalks | Partial corroboration. Remaining 4.75 m roadside allocation still needs its detailed section. |
| Drawing 11, PDF p37 | Other arms are 17 m with parking one side and 18 m with parking both sides | Separate variants; do not turn the base local into an 18 m street. |
| Drawings 10/12, PDF pp34/39 | Local industrial: 18 m total, two 4.5 m lanes, 1.6 m separate sidewalks | Partial corroboration, not full utility/frontage verification. |
| Drawing 8, PDF p30 | Collector with parking both sides: 23 m ROW, two 3.3 m lanes, two 2.1 m parking bands, 3 m pathway and 1.8 m sidewalk | Different parking programme from the 20 m no-parking pilot. |
| Drawing 10, PDF p34 | Industrial collector: 26 m total, two 3.5 m lanes, 4 m two-way turn lane, labelled 3 m pathways on both sides | Total/motor widths agree; opposite-side path conflicts with recorded 1.8 m sidewalk plus utility strip. Resolve using section sheet. |
| Manual p93, Table10.17 | Arterial one-way cycle track: general constrained minimum 2.5 m | Recorded High Activity Arterial is 2.2 m. Known unresolved discrepancy, not approved. |
| Manual p93, Table10.17 and notes | Collector cycle track minimum 2.2 m; general buffer minimum 1 m with 0.6 m allowed adjacent to parking | Read footnotes: the recorded 0.75 m parking buffer is not an automatic violation. A retrofit range does not prove the standard section. |
| Manual p90, Table10.15 note6 | High Activity local discussion assumes marked centreline | Current unmarked treatment needs source reconciliation. |

The cycle-track short-segment exception on p93 permits narrower tracks only under
specified conditions. It must not be used to approve a narrower continuous corridor.
Likewise enhanced retrofit widths are not mandatory replacements for all standard
sections. Numeric superscripts in extracted text are footnote markers: for example
`2.2` followed by notes `2,3` must not be parsed as a 2.223 m dimension.

## Intersection implementation implications

Page 40 requires curb ramps aligned with crossings and tactile indicators, and
specifies a 6 m bend-out offset for wheeling approaches. Page 41 says widths should
not transition at/through intersections and cross-sections should match across them.
Drawing notes restrict curve data to perfect 90-degree intersections. Do not reuse
those radii unquestioningly on a student's skewed or curved connection. Existing
shared junction code remains a conceptual system; these documents do not certify it.

## Next evidence required

Obtain **Draft 4.A section 4.4 standard cross-section sheets 1–13, including the
A/B/C parking and school variants**. Reconcile source conflicts before issuing new
geometry revisions, preserve old saved bindings, then test affected junctions and
close views. The 13 pilot entries remain incomplete, with no publication approval.

Rendered pages and text extracts are outside the repository at
`C:/dev-artifacts/CityPrompt/street-manual-2026-09-30/draft4b`.
This review did not modify the supplied PDFs, run paid renders or change user projects.
