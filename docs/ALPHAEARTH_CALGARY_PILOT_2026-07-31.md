# AlphaEarth annual-change pilot — Calgary University District

**Status:** one-site pilot completed with real Google/DeepMind AlphaEarth data.

## Outcome

The pilot demonstrates that annual AlphaEarth embeddings can produce a useful,
provenance-aware surface-change signal for Urban DNA. For the approximate
University District boundary, 10.51% of valid 80-metre analysis pixels exceeded
the declared `0.15` change heuristic between 2017 and 2025, versus 7.04% in the
surrounding 500-metre context ring.

This is evidence of stronger embedding change inside the pilot boundary, not a
claim about its cause. Construction, vegetation removal, water, disturbance,
and sensor/model effects require labeled validation before they can be named.

## Results

| Measure | Pilot site | 500 m context ring |
| --- | ---: | ---: |
| Valid pixels | 257 | 639 |
| Mean change | 0.0961 | 0.0931 |
| Median change | 0.0695 | 0.0750 |
| 90th percentile | 0.1529 | 0.1323 |
| 95th percentile | 0.2863 | 0.1944 |
| Pixels at or above 0.15 | **10.51%** | **7.04%** |

The generated heatmap was visually reviewed north-up. Most of the pilot site is
low-to-moderate change, with several isolated internal hotspots. The strongest
contiguous hotspot is immediately west/southwest of the approximate site
boundary. That spatial pattern is why the metric should be shown as a map and
not reduced to one unexplained score.

## Method

- Dataset: `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL`
- Years: 2017 and 2025
- Native dataset resolution: 10 metres
- Pilot analysis resolution: 80-metre built-in COG overview
- Vector dimensions: 64
- Measurement: `1 - cosine_similarity`
- Site geometry: approximate pilot polygon, not an authoritative legal boundary
- Context: 500-metre ring around the pilot polygon

The Cloud Storage COGs encode the embeddings as signed 8-bit values and store
the bands separately. The runner decodes the selected overview, re-normalizes
each valid 64-axis vector, and then calculates cosine similarity. AlphaEarth
embeddings are documented as linearly composable; re-normalization preserves a
consistent directional comparison after overview aggregation.

The 80-metre overview is an intentional bounded-pilot compromise. Direct native
10-metre range reads from the public 1.8 GB COGs were operationally slow in this
environment. The overview reduced the required live transfer to about 55 MB
across two annual files. Production 10-metre work should use Earth Engine,
managed extraction, or a regional block cache rather than repeated browser-like
COG requests.

## Artifacts

Generated, ignored output:

- `artifacts/alphaearth-pilot/calgary-university-district/result.json`
- `artifacts/alphaearth-pilot/calgary-university-district/change_score.tif`
- `artifacts/alphaearth-pilot/calgary-university-district/change_map.png`

A compact reviewed metric record is committed at
`tools/alphaearth_pilot/pilot_results/calgary_university_district_2017_2025.json`.
Large COG headers and overview payloads remain in ignored `artifacts/` cache and
must not be staged.

## Urban DNA fit

The runner emits an `environment.surface_change_2017_2025` field using the
existing Urban DNA value/confidence/source structure. Pilot confidence is 0.60
because the source and numerical comparison are sound but the boundary,
resolution, and threshold are not yet production validated.

Do not inject the raw embedding axes or an unlabeled change interpretation into
render prompts. Store the metric and raster as attributed evidence for the Site
Intelligence panel and planning agents.

## Decision and next gate

**Decision: continue, but do not integrate into the live Urban DNA task yet.**

The next bounded validation should contain three sites:

1. a known stable control;
2. a known major redevelopment; and
3. a vegetation- or flood-driven change site.

Validate the `0.15` threshold and compare 80-metre results with native
10-metre/Earth Engine extraction. Only then add a city-connector adapter and UI
layer. This avoids turning one visually plausible result into a false semantic
claim.

## Attribution and sources

Required attribution: “The AlphaEarth Foundations Satellite Embedding dataset
is produced by Google and Google DeepMind.”

- [Annual dataset catalog](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL)
- [Cloud Storage data structure](https://developers.google.com/earth-engine/guides/aef_on_gcs_readme)
- [Custom Satellite Embeddings announcement](https://mapsplatform.google.com/resources/blog/introducing-custom-satellite-embeddings-powered-by-alphaearth-foundations/)
