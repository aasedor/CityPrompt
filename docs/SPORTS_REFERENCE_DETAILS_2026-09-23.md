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
passes. The final scale-up will use a fresh `final/` folder and narrower paved
seating alcoves to keep the complete original planted bed edges intact.

Browser trials, terrain integration and catalogue activation remain deferred
by the user's earlier instruction. The v1 outputs remain preserved. New
reference-detail packages use `_v2` IDs and do not replace runtime assets.
