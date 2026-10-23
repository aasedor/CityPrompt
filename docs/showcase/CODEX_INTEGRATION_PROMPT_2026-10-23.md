# Codex prompt: review and implement the clay models in City Prompt

Copy everything below the line into Codex as its first message.

---

Take the 3D architectural-clay models on branch `claude/ten-new-buildings` of
https://github.com/aasedor/CityPrompt, review them, and implement the good ones in City Prompt so
students can place them from the picker. Read `CLAUDE.md` first and follow it.

**Where the models are.** Each model is a folder `tools/clay_<name>/`:

- `candidates/*.glb` is the model (one file, glTF 2.0, metres, built at grade).
- `sources.json` names the catalogue archetype and the three reference images it was built from.
- `README.md` says whether it passed its last review.
- `evidence/<version>/` holds that review and its renders.

There are buildings, parks and plazas, and streets and bridges. Start with the ones whose README
state line says `PASS_ZERO_P0_P1`. The others have known open problems listed in their README.

**For each model:**

1. **Review it yourself.** Load the GLB, look at it from the front, an oblique and above, and
   compare it with its three reference images under `frontend/public/archetypes/...`. Check it is
   the right building, sits on the ground at the right scale, and has no black holes or broken
   geometry. Skip any model you would not put in front of a student, and say why.
2. **Implement it** with the repository's existing process:
   - Buildings: `docs/BUILDING_CATALOGUE_WORKFLOW.md`, using `tools/catalogue_promotion.py` and
     `tools/seed_model_library.py`.
   - Parks and streets: the native park and street registries, `frontend/src/data/nativeParks.json`
     and `nativeStreetPilots.json`.
   - All three: the checks in `docs/ARCHETYPE_RUNTIME_INTEGRATION.md`. Every archetype already
     exists in the catalogues.
3. **Test it** on localhost:5174 like a student: place it, rotate it, save, reload, capture. Check
   it sits on the ground and there are no console errors. Run the repo's checks (type-check, tests,
   `python -m tools.catalogue_promotion check`).

Do one model end to end first, show me screenshots, then do the rest in batches.

**My approval.** I approve publishing the models that pass your review and testing. Record it in
the promotion package as: "Take the models you created, review them and then implement".

**Rules:**

- The models' branch is far from `main`, so do not merge it. Work on `codex/*` branches from
  `origin/main` and copy over only each model's folder.
- Don't change the GLBs. If a model is broken, skip it and tell me.
- Never parse-and-rewrite `buildingArchetypes.json` or the other archetype catalogues.
- Commit GLBs through Git LFS as the workflow requires.
- Open PRs to `main` and merge only when CI passes. Never force-push.

**Send me back:**

- Which models you implemented and which you skipped, and why.
- Screenshots of each implemented model in the app.
- The PR links.
