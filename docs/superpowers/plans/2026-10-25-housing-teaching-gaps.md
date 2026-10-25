# Housing classification and missing-form implementation

**Goal:** Add two genuinely missing housing forms with basic, sourced teaching
classifications and independently reviewed RLASM 6.1 models.

**Architecture:** New finite housing builder reuses clay primitives, evidence
preparation and exact-source locking. Individual family modules own geometry;
research cards own form/style/era/planning labels. Heavy evidence stays external.

**Tech Stack:** Python 3.12, Blender 5.2, pytest, existing RLASM evidence tools.

**Spec:** docs/superpowers/specs/2026-10-25-housing-teaching-gaps-design.md

## Global Constraints

- RLASM v6.1 architectural clay; no textured keeper claim or runtime activation.
- Exact locked compatible source bytes, fixed native scale, complete elevations.
- Primary sources; approximate association dates, no invented construction year.
- No large ground rectangle; no change to current 196-choice classification audit.
- External artifacts: C:/dev-artifacts/CityPrompt/housing-teaching-20261025.
- No paid City Prompt generations, push, deployment or credit purchases.

## Review Focus

- Wartime cottage versus existing bungalow: steep roof/attic form is visibly distinct.
- Split-level actually has staggered occupied levels and connected stairs.
- Front/side/rear openings and roofs remain physically complete in exact GLB.
- Classification does not imply ownership, affordability or neighbourhood ideology.
- Failed attempts, untested runtime and activation status remain explicit.

### Task 1: Source contracts and teaching cards

**Files:** tools/housing_teaching/{contracts.py,test_contracts.py,cards.json,README.md}

**Interfaces:** Produces exact family specifications, fail-closed output/source
contracts and separately sourced teaching cards for the two builders.

- [x] Author sourced labels and generate one compatible reference board per house.
- [x] Write failing tests for missing roles, source identity drift, reused output,
      invented construction years and tenure assumptions.
- [x] Run pytest; expect failure before implementation, then implement contracts.
- [x] Run python -m pytest tools/housing_teaching/test_contracts.py; expect PASS.

### Task 2: Build and review the bounded models

**Files:** tools/housing_teaching/{build.py,family_victory.py,family_split.py}

**Interfaces:** Consumes Task 1 contracts and cards; produces exact GLB/render
packages, measurements, independent review records and hash-bound evidence cards.

- [x] Dry-run the source/camera contract; expect DRY_RUN_PASS.
- [x] Build Victory pilot, inspect all renders and phone boards, independently
      review; preserve failures and correct in new finite versions.
- [x] After zero P0/P1 pilot review build split-level, inspect and independently
      review all mandatory views. Keep unrun runtime checks NOT TESTED.
- [x] Verify output hash contracts with pytest and existing narrow compiler gates.

### Task 3: Delivery and final source review

**Files:** docs/HOUSING_TEACHING_REVIEW_2026-10-25.md,
docs/housing-teaching-cards.json; canonical human/machine evidence records.

**Interfaces:** Consumes exact approved review hashes; produces truthful batch
status, Drive receipts and local manifest. No student-catalogue activation.

- [x] Upload originals and review notes to dated Drive subfolder; metadata readback.
- [x] Run focused pytest, git diff --check/stat/status and independent final source
      review. Correct important findings with regression evidence.
- [x] Commit the coherent source unit; no push. Separate generated output in final.
