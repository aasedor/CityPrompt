# Teaching archetypes Wave 2 implementation plan

> **For agentic workers:** Use `superpowers:executing-plans` inline. RLASM requires a separate holistic visual verifier for each completed candidate.

**Goal:** Build three new original teaching archetypes under the RLASM 6.1 architectural-clay profile.

**Architecture:** New family-specific Blender constructors reuse audited low-level clay/evidence utilities. Exact generated source views govern each family. Assets remain external and unactivated.

**Tech Stack:** Blender 5.2/Python, built-in image generation, Pillow evidence layouts, focused pytest and Drive delivery.

**Spec:** `docs/superpowers/specs/2026-10-25-teaching-archetypes-wave2-design.md`.

## Global constraints

- Three original designs; Bauhaus workshop pilot, then De Stijl studio and Mughal-inspired pavilion.
- Native fixed scale, zero GLB images/textures, complete exact-GLB reimport evidence.
- No enclosing site pad, model activation, registry/placement changes, paid app renders, credit purchases, push or deployment.
- Preserve previous sources/candidates; output exclusively beneath `C:/dev-artifacts/CityPrompt/teaching-wave2-20261025`.
- Front/oblique/top compatible source lock; source pixels override prompts; explicit hidden-view inference.
- Independent holistic visual review, zero unresolved P0/P1 before offline pass.

## Review focus

- Glazed studio shows a recognisable workshop programme and a connected two-storey stair, not empty glass rooms.
- De Stijl planes are physically supported and close the weather envelope; colour alone does not establish identity.
- Pavilion arches are real clear openings, with supported roof/dome and visible inner arcade faces.
- Export/reimport retains materials, cut openings and bounds; QA ground/cameras/lights stay excluded.
- Whole-view cameras retain margin; close views prove their named contact/programme, and sources stay hash-bound.

### Task 1: Source lock and Bauhaus workshop pilot

**Files:** new `tools/teaching_style_wave2/{contracts.py,build.py,family_workshop.py,test_contracts.py,README.md}`; external reference and candidate packages.
**Interfaces:** `specification(make_cameras)` supplies IDs, locked source filenames, measured notes, palette and camera roster; `construct()` builds one exact family; `build.py --family workshop --version N --output <new>` refuses existing output and copies scripts/sources.

- [x] Generate/inspect one original compatible source board, preserve unchanged crops and provenance.
- [x] Write meaningful failing source/output contract tests, then implement bounded manifest checks.
- [x] Dry run, build full pilot, export/reimport, prepare complete evidence and inspect full-resolution pixels.
- [x] Obtain independent holistic review; address only finite blockers in preserved new versions; checkpoint source/memory after pass.

### Task 2: Remaining two exact families

**Files:** new `family_destijl.py`, `family_pavilion.py`; extend build choice; new teaching card drafts and batch review doc.
**Interfaces:** same specification/constructor contract as Task 1; reuse exact source/evidence gates.

- [ ] After pilot pass, generate and lock each family's own compatible sources.
- [ ] Construct original envelope, openings, programme and supports; dry run each.
- [ ] Build each candidate and complete its exact-GLB render/phone evidence set.
- [ ] Inspect and obtain separate holistic reviews; preserve failures and rerender all views after corrections.

### Task 3: Verification, source checkpoint and delivery

**Files:** batch review Markdown/card JSON, synchronized method/memory companions; external delivery manifest.

- [ ] Verify exact hashes/native contracts/texture counts, run focused source/evidence and RLASM compiler tests.
- [ ] Synchronize review findings and lifecycle boundaries in human/machine memory.
- [ ] Inspect staged diff/check/status and commit only the coherent source initiative.
- [ ] Upload originals, full render sets, comparisons and packages to the existing Drive parent; verify metadata/readback and local receipts; report review state and runtime limits.
