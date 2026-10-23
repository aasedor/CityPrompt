# People render trials — local, 23 October 2026

Status: **3/3 videos completed; 1/3 AI images completed; 2 AI images pending provider availability.** This is a local trial, not a production deployment or complete appearance-fidelity approval.

## Scope and environment

The user authorized three image and three video renders to compare realistic picker photographs, actual People GLBs and AI results. One Sunburst 2.5 guide counts as image 1; it was reviewed and used with Omni video 1. After OpenAI rejected image 2 twice with HTTP 429 (both attempts marked billed=false), image retries stopped. Image 3 was not submitted. Videos 2 and 3 used direct Omni 1.1 video editing without a photographic guide; they are not controlled guide-versus-no-guide comparisons because the subjects differ.

Source base: `1267752c8`; initiative branch `codex/people-render-trials-20261023`. Active checkout: `C:/Users/andre/.codex/worktrees/add-details-recovery/CityPrompt`. App `http://127.0.0.1:5184`, API 8012, existing local repair database; dedicated disposable projects owned by Andrew local trial. No production changes, push, credit purchase or account switching. Existing local async-image feature enabled for the trial API/worker; no secrets committed.

External evidence: `C:/dev-artifacts/CityPrompt/people-render-trials-2026-10-23`. The `review/` directory contains only intentional images/videos and an HTML comparison page, served on localhost at `http://127.0.0.1:65185/`. Private job state and signed media URLs stay outside that directory. `media-inventory.json` records media SHA-256 and sizes; `paid-ledger.json` records logical slots, successful jobs and failed requests.

## Actual outputs

| Scene / project | Image | Omni video | Result |
| --- | --- | --- | --- |
| Campus outfits / `2e64bcfc-4cc8-4dbd-a7e4-d9096d0fd4e1` | `622e579c-7d80-4e55-a5dd-cc0d0d71e1c1`, Sunburst 2.5, completed | `bd0fb9e9-745b-492c-8c2a-9cfe01d6789a`, complete | Main garment colours and accessories recognizable. Rhea's skirt shape loosens during motion. Faces interpreted. Sofia partly cropped; Felix outside source framing, so neither is fully assessed. |
| Mobility / `7dc25ed3-cf07-4f3a-9622-15c3ded92930` | Failed `3fa5b928-d832-4b09-aef5-e45fd1ee3376`; one deliberate retry `2e2c5018-fdf3-49b5-a1a8-99fcfcbd5bc4` also HTTP 429, billed=false | `ad3f8071-bd28-4197-a651-83d27bdd0aa0`, complete | Manual/powered wheelchairs and cane remain recognizable. Ava's appearance and jacket change substantially; Mateo's trousers change colour. Fine guide-dog harness fidelity not established. Partial match; exact appearance fails. |
| Families / `2257ef4b-4b47-44de-beef-ab48806465ed` | Not submitted after repeated provider rejection | `0b03efd5-60f4-4bad-a0b9-3002ad291756`, complete | Child, stroller/infant and rollator retained. Several faces, clothing colours and garment details change, including Noah's top and Eli's jacket. Partial appearance match. |

All videos identify `gemini-omni-1.1-flash` and decode to **4.0 seconds, 1280×720, 24 fps, 96 frames**. App UI reports saved to project. The side-by-side derived videos put original 3D on the left, AI on the right; originals remain unchanged. Four evenly spaced frames per result were inspected, and all three comparison files played in the browser with no media errors. The Sunburst still was visually inspected. Runtime GLB/photo comparison boards use the actual delivered picker photos and actual GLB thumbnails.

The near-static mobility/family camera routes are approximately 0.3 m at 0.3 km/h; campus about 1.7 m at 1.5 km/h. These are short appearance checks, not brisk walking, crowd-motion, mobile or student-laptop benchmarks. Inclusive models retain their disclosed fixed poses; AI movement is an interpretation. Only the selected visible subjects were assessed here; this does not establish all 31 models' AI identity fidelity or every action.

Successful work used one 26-token image plus three 50-token videos (176 app tokens); the two image failures were marked unbilled. Each video UI output estimate was $1.0136; input charges are extra and estimates are not invoices or billing caps. Provider usage receipts are saved. No extra successful paid generations were made.

## Camera correction discovered during free previews

A manual street route always aimed seven metres above the site centre. In a close people-only scene this aimed above the subjects and could yield blank/all-sky captures. The rejected free source recordings are retained separately. `manualStreetFocusHeight` now uses a 1.05 m focus for manual people-only scenes. Building zones and any saved building inventory retain the prior 7 m framing, including zone-less GLBs with their own footprints. Automatic route framing is unchanged.

Changed production files: `GlobeSitePlannerMap.tsx`, `streetRenderProfile.ts`. Tests: `streetRenderProfile.test.ts` adds a full-body projection regression and a zone-less saved-building regression. Independent reviewer identified the saved-building edge case; it was corrected and re-reviewed with no remaining actionable finding.

Verification executed after the fix: four narrow Vitest files (`streetRenderProfile`, `videoRouteControls`, `VideoGeneratePanel`, `peopleCapture`), **40 tests passed**; `npm run type-check` passed; scoped ESLint **0 errors**, two pre-existing policyMap/cityPolicyMaps hook warnings; scoped `git diff --check` passed. Browser source capture shows full-height people after the change. No backend source was changed. No full production build/deployment was attempted.

## Remaining work

Resolve OpenAI HTTP 429 before the remaining two images. The provider response's detailed rate/quota reason was not retained by the existing guide service, so it cannot honestly be diagnosed as expired key, exhausted balance or a particular rate limit. User notified; no automatic paid retry.

The rendering pipeline works for the three completed videos, but **exact picker-to-video appearance is not validated**. A future bounded pilot should use explicit character appearance references and per-person clothing/identity constraints, then review aids and faces against both picker and GLB. Do not spend more credits or call these results exact matches without another measured trial.

226 inherited hydrated LFS differences remain excluded from staging. All generated assets, original recordings, rejected previews and AI outputs remain external/ignored; this source checkpoint contains only the camera change, tests and this report.
