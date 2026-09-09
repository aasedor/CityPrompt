# Sports parks catalogue pilot — 2026-09-08

Three new metric sports assemblies are available locally under **Parks → Play &
sport amenities**. They use the existing adaptive park renderer, shared trees,
benches, terrain-following lawn and connected circulation. Existing cinema,
garden and concert assets are unchanged. These are planning models, not certified
competition venues or engineered grading/accessibility designs.

| Option | Playing area | Fixed module, including reserve | Minimum park |
| --- | --- | --- | --- |
| Regulation basketball park | 28 × 15 m | 36 × 23 m | 52 × 39 m |
| Twin tennis courts | Two courts, each 23.77 × 10.97 m | Each 38 × 20 m | 54 × 60 m |
| Full-size soccer park | 105 × 68 m | 117 × 80 m | 133 × 96 m |

Basketball has two hoops, coloured keys, perimeter fencing and an open gate.
Tennis has doubles/singles/service markings, sagging nets, separate fenced
enclosures and gates. Soccer has mowing stripes, full-size goals, goal nets,
penalty/goal areas, centre and penalty arcs, and corner flags. Furniture and
trees sit outside the playing modules. Three small GLBs contain approximately
12.7k, 13.2k and 4k triangles respectively, with 8/5/5 material meshes.

## Dimension references

- [FIBA Venue Guide](https://www.venueguide.fiba.basketball/vanue-design):
  28 × 15 m court and at least 2 m clear boundary space. Our larger module
  reserves room for hoop supports and fences beyond that clearance.
- [ITF court definitions](https://www.itftennis.com/en/about-us/organisation/tennis-glossary/)
  and [ITF Facilities Guide](https://itf.uberflip.com/i/1255985-facilities-guide/11):
  doubles playing dimensions and run-back/side-run guidance. Our 38 × 20 m
  module exceeds the guide's 36.57 × 18.29 m international minimum envelope;
  it is not the larger preferred international envelope.
- [IFAB Law 1](https://www.theifab.com/laws/latest/the-field-of-play/):
  permissible pitch dimensions and 7.32 × 2.44 m goal opening. The chosen
  105 × 68 m pitch is within the international range. A six-metre perimeter
  reserve is a City Prompt planning choice, not a universal IFAB run-off rule.

## Reshape and terrain contract

`frontend/src/data/sportsParkDimensions.json` is shared by the mesh builder
and layout. A larger simple plot adds complete modules up to finite caps
(4 basketball, 6 tennis, 2 soccer), or more surrounding landscape. Rotation
preserves the same module dimensions. Narrow/unsuitable shapes report that
the programme cannot fit; equipment is never cropped or squeezed.

Each gate has an approach connecting to the park loop. Lawns and paths follow
the sampled terrain; courts/pitches remain planar on local pads. Existing pad
metadata reports grading review when the height difference exceeds 0.8 m.
Steep sites still need designed grading and gate transitions. This initiative
does not solve the shared-boundary terrain readiness issue recorded in the
skyscraper trial, and does not establish a fully accessible route on slopes.

## Build, installation and review

Run Blender 5.2 with `tools/park_trio/build_sports.py`, passing `--sport`
(`basketball`, `tennis` or `soccer`) and a new external `--output-dir`. Add
`--dry-run` for the zero-call preflight. The builder refuses existing output,
reimports each exported GLB, checks its ground and physical envelope, writes a
hash/size/mesh manifest, and renders a preview from the delivered geometry.
No paid image/video generation was used.

Runtime GLBs and manifests: `frontend/public/landscape-pilots/sports-parks-v1/`.
Catalogue previews: authoritative `frontend/public/archetypes/openspaces/`
folders `sports-basketball-regulation`, `sports-twin-tennis`, and
`sports-soccer-full-size`. Binary deliverables use existing Git LFS rules.
Experimental outputs and full browser captures remain outside Git at
`C:/dev-artifacts/CityPrompt/sports-parks-2026-09-08/`.

Actual student-flow trial:
http://127.0.0.1:5177/projects/fb2cdeca-8ae1-4aea-bfa7-ab1d695443ea

- Created a fresh Currie project through the UI and placed all three through
  the normal catalogue and canvas clicks, on open land.
- Resized tennis to 58 × 64 m and rotated it 5 degrees through the reshape panel.
- Reloaded and checked saved objects and `3D saved`; no uncaught browser errors.
- Corrected soccer's initial invalid parent ID to the authoritative athletics
  precinct parent/variant. Repaired only that new test zone through the local API.
  Regression tests now check each parent/variant against the authoritative JSON.
- Assigned ordered depth-tested drawing to thin sports surfaces and markings
  after seeing pad/paint flicker at the first camera position. No depth testing
  was disabled; camera-specific precision should remain part of future trials.
- Checked flat assembly previews; minimum, enlarged, rotated and constrained
  layouts, catalogue routing, gate connections, type-check and touched-file lint.

The parks remain pilot catalogue entries. No production publication or push to
main was performed. Pre-existing local tower catalogue changes and PNG filter
differences remain separate from this sports initiative.

## Follow-up browser trial

Tested the same project through normal catalogue, canvas and reshape controls:

- Minimum basketball width of 20 m correctly disables Apply. A modest enlargement
  saves; a 96 m expansion into the adjacent tennis park reports overlap and keeps
  the previous saved shape.
- A fresh 96 × 43 m basketball park on clear land produces two complete courts.
  Deleted that temporary copy and a newly placed tennis copy through the UI.
- Deleted and recreated the soccer park through the catalogue. After reload the
  API contains exactly three sports zones, all compiled; deleted copies stay gone.
- Reproduced grey court surfaces from another camera angle. The earlier drawing
  order adjustment was insufficient: the supporting pad cap competed with each
  sports GLB's own slab. Removed only the duplicate sports cap, retaining terrain
  skirts and normal depth testing. Same-camera screenshots and subsequent
  overhead/30-degree oblique views show the playing surfaces correctly.
- Rounded Place another defaults to millimetres and 0.001 degrees to eliminate
  floating-point tails in copied size inputs; added a callback regression test.
- Four focused Vitest files pass (47 tests); TypeScript and touched-file ESLint
  pass. Browser reports no uncaught errors. No paid render calls were made.

Evidence remains outside Git: `retest-new-double-court.png` (before),
`retest-pad-fixed.png` (same camera after), and `retest-final-3d.png` under the
external artifact directory above. This trial does not certify steep-slope
grading or every camera distance.

## Close-up and flexible plot follow-up

The normal reshape UI saved basketball at 58 × 45 m (previously 52 × 39 m),
retaining one 28 × 15 m playing court. Added tests for each sport growing by
six metres independently in width/depth: module dimensions and counts remain
unchanged. Surrounding lawn and circulation adapt. Perimeter seating now grows
with width, bounded to two through six benches on each of two edges, outside
the sports modules. Very large plots can still add complete courts.

Validation: 42 focused layout/sports tests, type-check and touched-file lint pass.
Close-up browser evidence: `basketball-detail.png` and `tennis-detail.png` in
the external sports artifact directory. This session also attempted paid
photorealistic soccer and basketball/tennis views; both returned provider HTTP
500 errors with no images. The app retained the reservations because provider
billing was uncertain. These failures do not demonstrate image fidelity.
The final watercolour attempt also returned HTTP 500 (194.6 seconds). Stopped
after three attempts, with zero AI images produced. Provider request IDs:
`req_e2cbfc8e3a79417a8bc28faecd004ccd`,
`req_8bb3eaa943a14f809e03e399d7078cbf`,
`req_85d1268dc4e344109bf484acecd1fb9b`.
