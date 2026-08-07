# Park composition API validation: 50-image study

This bounded study used exactly 50 new image API calls: 25 Gemini and 25 GPT
Image references across 25 park compositions. All calls succeeded without a
retry. The images are qualitative training and validation evidence for the
deterministic park LEGO builder; they are not production drapes or sources of
regulation dimensions.

The study deliberately spans regulation modules, active recreation, civic and
academic spaces, productive landscapes, ecological systems and landform-led
parks. Every prompt requires the complete parcel, no people, no embedded large
buildings, standard modules rather than stretched facilities, archetype-owned
objects, and textured multi-material surfaces.

## Main findings

- The LEGO grammar should place entrances, accessible routes, service access,
  spectator/caregiver edges and equipment clearances before decorative scatter.
- Oversized sites should repeat complete standard modules. The paired
  basketball study correctly produced two separate courts and four hoops;
  the compact study correctly falls back to one half-court and one hoop.
- The object kit is as important as the surface. The images consistently add
  gates, nets, racks, fountains, bins, shade, maintenance access, drainage
  structures, boardwalks and family-specific equipment.
- Late ecological and specialty families need more object depth. Current live
  City Prompt trials are materially and spatially sparser than both their
  catalogue images and the API composition evidence.
- Generated topology cannot be copied blindly. One inclusive-play image added
  an unrelated basketball court and a person, pump-track loops became too
  tangled, bocce counts diverged and disc-golf safety could not be verified
  visually. The deterministic compiler remains authoritative.

## Recommended build order

1. Water/ecology kit: boardwalks, bridges, weirs, inlets/outlets, riprap,
   overlooks and maintenance gates.
2. Metric recreation kit: volleyball nets/posts/tapes, bocce sideboards and
   disc-golf tees/baskets.
3. Specialty kit: climbing blocks and landing zones, mini-golf sequence
   objects, amphitheater stage/terraces/rails.
4. Productive/campus kit: study furniture, canopies, research and garden
   operations objects, trellises and orchard supports.
5. Variant-specific finishing kit: senior fitness equipment, woodland memorial
   objects and ecological habitat micro-objects.

Meshy is best reserved for non-metric natural and furniture props such as
habitat logs, boulders, brush piles, potting benches and decorative obstacle
variants. Regulation sports equipment, accessible fitness geometry, bridges,
weirs and other clearance-critical objects should be built parametrically or
in Blender against metric proxies.

## Review files

- `provider-comparison-mobile-1.jpg` through
  `provider-comparison-mobile-5.jpg` contain five paired park studies each.
- `run.json` is the persisted call ledger proving 50 attempted and 50
  successful calls with no retry.
- `study_manifest.json` records the exact resolved prompts sent for all 25
  paired scenes.
- `tools/park_skin_compiler/park_composition_api_validation_50.json` contains
  the exact prompts, source-reference paths and 50-call cap.
- `tools/park_skin_compiler/park_composition_api_validation_50_assessment.json`
  contains the retain/reject rules, current LEGO comparison, P0/P1 object-kit
  backlog and the next one-at-a-time City Prompt verification batch.

Fresh browser renders were not substituted with API images. The open local
City Prompt tabs were logged out at review time, so the current comparison uses
the completed catalogue's existing one-at-a-time live trials. After sign-in,
the next verification is a fixed eight-family browser batch, one park at a
time, with no image drape.
