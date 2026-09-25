# Sports parks: reference-led amenity revision

The ten v1 courts reused the same pergola, terrace and benches. The user asked
for assets that better reflect the archetype images. Inspected the authoritative
catalogue heroes for basketball, tennis, beach volleyball, bocce/petanque and
pickleball, plus selected variants. New work is isolated on
`codex/sports-reference-details`, based on `8ba45ef8a`.

## Reference audit and intended revision

The existing pictures contain more specific amenities: player benches and
court floodlights in basketball; aluminium stands in the tennis professional
variant; solid-roof timber shelters in pickleball; seat walls, referee stands
and parasols in beach volleyball; cafe furniture, braced arbours and string
lights in bocce/petanque. These cues are encoded in
`tools/public_realm_assets/court_reference_profiles.py`, with per-sport observed
features and explicit adaptations. Every used source image is copied into its
new package with a byte hash.

There are no exact padel, badminton or netball images in this catalogue. Those
parks use clearly labelled related-sport adaptations. The single tennis court
remains a single court rather than claiming to reproduce the multi-court
reference program. Large background buildings, people and tropical palms are
not included. The existing native playing geometry and full reserves remain
unchanged.

Ten reusable amenity modules are authored in `sports_furniture.py`: player
bench, covered player bench, spectator bleachers, timber-topped seat wall,
cafe table/chairs, cafe parasol/table/chairs, referee stand, twin-head court
floodlight, braced vine pergola and festoon lights. `court_surroundings.py`
assigns different combinations to each sport. Only bocce retains a large
arbour; other types use player seating, smaller shelters, parasols or cafe
terraces. Hardscape tree wells stay in place.

| Sport | Distinct surrounding assets |
| --- | --- |
| Basketball | Simple player benches, twin-head floodlights, charcoal court finish |
| 3x3 basketball | Player benches, timber-topped seat walls and sport lighting |
| Tennis | Two covered player benches, low aluminium stand and sport lighting |
| Padel | One covered bench and one parasol cafe set around the glass enclosure |
| Volleyball | Team shelter, low stand, referee chair and sport lighting |
| Beach volleyball | Two parasol cafe sets, seat walls and referee chair |
| Badminton | One small shelter, cafe seating and player benches |
| Netball | Player benches, spectator stand and sport lighting |
| Bocce | Braced arbour, cafe tables/chairs, seat walls and string lights |
| Petanque | Open cafe terrace, seat walls and string lights; no repeated pergola |

## Reuse contract

`build_courts.py --reference-root <authoritative openspaces folder>` opts into
the v2 profiles. Without that flag, the v1 recipes remain available. The batch
runner accepts the same flag and still requires an explicit finite kind list,
a fresh output folder and a maximum of two workers. Five tests check the
unchanged sport dimensions and reference-lock behavior.

Each revised package exports its amenities individually in `modules/`, with
native metric origins, placement/yaw metadata, source-image hashes and separate
surface ownership. The reference review packager collects the ten unique
modules into an external `amenity-kit/` with an `index.json`. Use these modules
and placement recipes for new park archetypes; do not stretch the full park
assembly. Keep complete amenity envelopes outside sport reserves, preserve
ground contacts and leave the same tree-well exclusions in rebuilt paving.

Court lights and festoon bulbs are lightweight visible geometry, not an active
lighting simulation. These fixtures, shelter frames and seating are conceptual
assets; source resemblance does not certify structural or competition design.

## Pilot checkpoint

External output root:
`C:/dev-artifacts/CityPrompt/sports-reference-details-2026-09-23/`.

The first beach volleyball pilot passed its geometry checks and native aerial,
terrace-detail and court visual review. It now has two cafe parasols, four seat
walls and a physical referee stand. Added checks reimport the actual amenity
modules, compare their bounds, keep complete envelopes outside the court
reserve, check their contact points against owned paving and verify archived
reference-image hashes. The pilot passed 252 approach rays, 99 court-entry
rays, six tree-root checks and all three new module-envelope checks.

Five pure-Python tests pass, including preservation of court sizes and v1 IDs,
reference-byte changes and missing-reference rejection. Python compilation
passes. Pilot checkpoint `4073186bb` preceded the bounded ten-model scale-up
into a fresh `final/` folder. These packages use narrower paved seating alcoves
to keep the complete original planted bed edges intact. The first bocce detail
is preserved in `bocce-first-detail/`; its foliage was refined to sparse,
deterministic irregular leaves instead of a repeated roof pattern.

Browser trials, terrain integration and catalogue activation remain deferred
by the user's earlier instruction. The v1 outputs remain preserved. New
reference-detail packages use `_v2` IDs and do not replace runtime assets.

## Completed delivery and validation

All ten final v2 packages passed the generic and sports-specific geometry
verifiers and native visual review. Reviewed the individual revised amenities
in context, the full ten-model overview and the three-row reference/before/after
board. Final output is in the external root's `final/<sport>/` folders; the pilot
and first bocce detail remain separate from delivery.

- Ten complete assemblies, ten separate unchanged-dimension sport modules,
  placement recipes, 40 native images and per-variant pending runtime reviews.
- Ten unique reusable amenity GLBs in `amenity-kit/`, totaling **339,160 bytes**,
  with a hash/size/native-bounds index. This excludes whole-park assemblies.
- All 86 new amenity placements verified outside the complete sports reserves,
  with real module bounds and paved ground contacts. Existing approach widths,
  entrances, equipment heights, tree crowns and tree wells still pass.
- Twenty-one per-package reference-image locks verified against archived bytes.
  Each recipe distinguishes observed features from related-image adaptations.
- Complete assemblies range from 154,792 to 169,910 triangles, 118-126 mesh
  instances and approximately 4.23-5.04 MB. No new runtime dependency or image
  provider call was used.

The exact package/image hashes and profiles are recorded in
[the v2 delivery ledger](SPORTS_REFERENCE_DETAILS_2026-09-23.json). External
`final/manifest.json` also records all module hashes and exact archived source
hashes. `reference-before-after.png` shows tennis, beach volleyball and bocce;
the full native overview is `final/ten-sports-gardens.png`. The lightweight
kit index is `amenity-kit/index.json`.

The shared runtime checklist and review template now capture reference-image
fidelity and reusable amenity delivery for future archetypes. Source changes
and metadata are committed locally; native GLBs, reference copies and review
images stay outside Git. No browser checks, catalogue activation or push were
performed. The next integration trial should use these exact v2 packages.
