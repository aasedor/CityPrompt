# AlphaEarth annual change pilot

This bounded pilot compares Google/DeepMind AlphaEarth annual satellite
embeddings over one approximate Calgary site boundary. It produces:

- `result.json`: provenance-aware metrics shaped for Urban DNA ingestion;
- `change_score.tif`: georeferenced `1 - cosine_similarity` values; and
- `change_map.png`: a review image with the pilot site outlined in white.

It does **not** classify the cause of a change. The default `0.15` change
threshold is an explicit pilot heuristic that must be validated against known
imagery, permits, or labeled land-cover data before production use.

## Dataset and attribution

- Dataset: `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL`
- Source index: `gs://alphaearth_foundations/satellite_embedding/v1/annual/aef_index.parquet`
- Native resolution: 10 metres, 64 embedding axes
- Pilot analysis resolution: 80 metres (the third built-in COG overview)
- Default comparison: 2017 to 2025
- License: CC BY 4.0
- Required attribution: "The AlphaEarth Foundations Satellite Embedding
  dataset is produced by Google and Google DeepMind."

Official references:

- https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL
- https://developers.google.com/earth-engine/guides/aef_on_gcs_readme
- https://mapsplatform.google.com/resources/blog/introducing-custom-satellite-embeddings-powered-by-alphaearth-foundations/

## Run the pilot

From the repository root:

```powershell
python -m venv .venv-alphaearth
.venv-alphaearth\Scripts\python.exe -m pip install -r tools/alphaearth_pilot/requirements.txt

# Zero-COG-call validation; downloads the approximately 70 MB tile index once.
.venv-alphaearth\Scripts\python.exe -m tools.alphaearth_pilot.alphaearth_change --dry-run

# One-site pilot. Reads one contiguous 80m overview range from each public COG.
.venv-alphaearth\Scripts\python.exe -m tools.alphaearth_pilot.alphaearth_change
```

Use `--index PATH` to reuse an existing index and `--no-download-index` to
prohibit index downloads. Use `--cache-dir PATH` to reuse COG headers and
overview payloads and `--no-download-cogs` to require a completely offline
run. Generated output belongs under the ignored
`artifacts/` directory and should not be staged wholesale.

The 80-metre overview is an intentional transfer-bounded pilot setting. It can
show neighborhood-scale surface change but must not be described as parcel- or
building-level evidence. Native 10-metre analysis remains a production-access
and performance follow-up.

## Production gates

1. Validate the threshold on multiple known-change and known-stable sites.
2. Add semantic labels before claiming vegetation, construction, flooding, or
   another cause.
3. Replace the approximate pilot geometry with the project/site boundary.
4. Confirm commercial Google Cloud access, egress expectations, attribution,
   retention, and derived-output terms.
5. Add a city-connector adapter only after the pilot demonstrates useful lift.
