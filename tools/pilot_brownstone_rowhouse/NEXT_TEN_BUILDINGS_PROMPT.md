# Prompt: ten new exact 3D buildings for City Prompt (RLASM v6.1, clay)

Work on branch `claude/branch-review-qmf8b9` of aasedor/CityPrompt (it already
carries the pilot tool in `tools/pilot_brownstone_rowhouse/`; read its README,
`family_brownstone.py`, `build.py` and `lock_sources.py` first). Read
`docs/RLASM_LATEST_METHOD.md`, `docs/HIGH_QUALITY_3D_BUILDING_MEMORY.md`,
`docs/ARCHETYPE_RUNTIME_INTEGRATION.md` and `docs/BUILDING_CATALOGUE_WORKFLOW.md`
before building anything. Follow CLAUDE.md: never json.dump the archetype
catalogues, pilot before scale, back up before destructive edits, tight commits.

Goal: ten new architectural-clay building candidates that do not yet exist as
exact 3D models in the student catalogue, each taken through RLASM phases A to G
with an independent review record, and preserved on the branch. Work
sequentially, one building at a time, committing and pushing after each one so
partial progress survives. Do not stop after the first building.

Environment setup (do this once):
- `uv venv --python /usr/bin/python3.11 <scratch>/venv311` then install
  `backend/requirements.txt` with uv, plus `bpy==4.2.0`. Cycles renders on CPU
  headless; expect about 15 minutes per 18-view roster at 1440 px.
- Catalogue reference images are Git LFS pointers locally. Hydrate only what
  you lock: `git lfs pull --include="frontend/public/archetypes/buildings/<id>/variant_0*"`.
- Google Drive is connected. The folder `snapshots` holds repository snapshots
  and external artefact folders (for example `CityPrompt-showcase-buildings`,
  `CityPrompt-priority-building-upgrades`). Search it for additional compatible
  views of the exact variant you lock. Never mix sibling variants.

The ten buildings, chosen from the catalogue gap analysis (empty or thin guide
groups and uses with no model). For each, pick a catalogue archetype whose
front, oblique and top views exist, lock all three, and build the exact variant:
1. Compact two-storey neighbourhood office (use: Office).
2. Indoor vertical farm or food-production building (guide group indoor_food,
   currently empty).
3. Fire station or emergency services building (Protective and Emergency Service).
4. Elementary school with gym (School Authority – School).
5. Second hotel or motel (guide group hotels has one entry).
6. Three-unit rowhouse building with individual grade entrances (for H-GO and
   M-G, which currently place nothing).
7. Heavy industrial facility with an outdoor yard (General Industrial – Heavy).
8. Utility or district energy building (guide group infrastructure).
9. Small place of worship (Place of Worship – Small; only Large exists).
10. Large-format supermarket with a parking court (Retail and Consumer Service).

Per building, mirror the pilot exactly:
- Phase A: `lock_sources.py`-style manifest with role, path, bytes, sha256,
  dimensions; catalogue_reference_nomination origin; excluded siblings listed.
- Phase B: measurement contract from pixels (bays, storeys, datums, roof,
  identity elements, programme, camera roster with the ten required baseline
  views plus family-specific contact views).
- Phases C to E: family module composed with `clay_core`, `geometry` and
  `assemblies` unchanged. Butt side carriers against front and rear carriers
  (inset by wall thickness); never let equal-height boxes overlap with visible
  coplanar faces; keep every vertex at z >= 0; furnish rooms behind glazing with
  low-power inspection lights.
- Phase F: quick 720 px / 8 spp subset render first, fix P0s, then the full
  1440 px / 32 spp roster, phone boards, builder pixel review at full resolution.
- Phase G: spawn a separate reviewer agent that sees only sources, renders and
  boards, using the brief pattern in the pilot (severity P0/P1/P2, four
  sections). Iterate as a new version if any P0 remains; at most three versions
  per building, then record the open blockers and move on.
- Preserve: Git LFS uploads are blocked from the cloud environment (reads
  work, writes return Forbidden), and Drive connector uploads need base64
  payloads inside tool calls, so neither is a sink for renders. Do exactly what
  the pilot did: keep the GLB in `tools/<family>/candidates/` as an ordinary
  blob with `git add -f` (it must stay under 1 MiB; if a model exceeds that,
  reduce furnishing detail or mortar-course density until it fits), and store
  the 18 renders and the phone boards as JPEGs under 950 KB each in
  `tools/<family>/evidence/<version>/{renders,boards}/`, with the build report,
  source entry, prework manifest, aperture audit and independent review record
  beside them. Zip the full-resolution PNGs plus the GLB and send that zip and
  the boards to the user with the file-sending tool after each building. Commit
  with a scoped message and push (plain git push works) after every building.

Do not: claim keeper approval; enrol anything in the catalogues or registries;
touch `buildingArchetypes.json`; publish; force-push; or run the frontend
publication preflight as a gate (trial entries fail it by design).

Finish with one report `docs/showcase/TEN_BUILDINGS_REPORT_<date>.md`: a table
of the ten candidates (archetype, variant, version, triangles, GLB bytes,
review verdict, open P0/P1), what was not completed and why, and the next
steps that need the user (runtime acceptance on localhost:5174, zoning use
programs, activation quotes). Send the phone boards of each building to the
user as they complete.
