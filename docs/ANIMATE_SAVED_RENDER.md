# Animate a saved architectural render

An optional five-second, silent Kling film uses a selected **finished, full-resolution
saved render**. Open a saved image in Project Renders, Saved Renders, the projects
dashboard, or the aerial render gallery and choose **Animate this render**. The
dialog shows the image, dimensions, credit charge and provider estimate before
**Create 5-second clip** submits a generation. Completed clips play and download
as MP4s and are saved to the project's existing video gallery.

The default shot is a slow forward dolly. The application labels this as an
**animated still**: it does not assert that the resulting camera follows a 3D
route or that the model preserved exact building geometry. Review the details
before presenting. Existing eight-second route videos and their fidelity checks
are unchanged.

## Server setup

Set these in the backend environment and restart the API:

```dotenv
FAL_KEY=<your server-side fal key>
KLING_ANIMATION_ENABLED=true
KLING_ANIMATION_ENDPOINT=fal-ai/kling-video/v3/pro/image-to-video
KLING_ANIMATION_COST_PER_SECOND_USD=0.112
KLING_ANIMATION_CREDIT_COST=50
```

The optional feature defaults to disabled. No key is sent to the browser. It uses
the existing PostgreSQL project metadata and S3-compatible storage; no schema
migration or additional worker is required. `fal-client` is already a backend
dependency. Run the normal backend (`uvicorn app.main:app`) and Vite frontend
after setting the backend environment. The starter `CLASSROOM_RELEASE=true`
boundary continues to disable paid video POSTs, including this feature.

fal's [Pro image-to-video pricing](https://fal.ai/models/fal-ai/kling-video/v3/pro/image-to-video)
was checked on 2026-10-06: **US$0.112/second without audio, US$0.56 for this clip**.
The estimate and City Prompt credit charge are separate configurable settings.
This requires funded fal access; Google/educator credits are not assumed to pay
fal bills. When evaluating another compatible endpoint, check its schema and
pricing and update both settings. Each saved job retains its original endpoint,
prompts and settings for recovery.

The [verified input schema](https://fal.ai/models/fal-ai/kling-video/v3/pro/image-to-video/api)
is `start_image_url`, `duration: "5"`, `generate_audio: false`, `cfg_scale: 0.5`,
one prompt and one negative prompt. No seed, resolution, multi-shot, end image,
additional elements or unsupported camera parameters are sent.

## Storage, ownership and recovery

The dialog accepts an optional **Scene direction** of up to 400 characters,
such as “People stroll along the paths.” It is appended to the existing single
animation prompt; blank input retains the default. Keep directions brief and
focused on activity or movement. The submitted direction and complete provider
prompt are saved with the job and included in its idempotency check. Reopening
a saved job checks that job rather than generating a revised clip.

If a readiness or history read fails, **Check again** reruns only those unpaid
checks. Generation stays disabled until both succeed. An existing paid job can
still be recovered if a fresh submission would exceed the credit allowance.

- Requests identify the project and saved-render UUID. The backend checks current
  editor access, render membership and the exact project storage key. It reads
  the saved PNG/JPEG/WebP bytes without resizing. Gallery thumbnails and a Direct
  3D `authoritative_source` fallback cannot become animation inputs.
- The unchanged finished pixels are uploaded using the existing server-side fal
  client. Project ID, source render ID, source checksum/dimensions, prompts,
  endpoint and settings are retained in `video_pilot_attempts` project metadata.
- A UUID idempotency key reserves an attempt before submission. Credits are
  conditionally debited and a usage log is committed before the paid call. The
  existing bounded project/video trial allowances apply; failures count toward
  an installed trial allowance. Administrators retain the existing credit bypass.
- Queue submission uses the [documented REST queue API](https://fal.ai/docs/documentation/model-apis/inference/queue)
  with transport retries disabled. The Python client's submission helper retries
  POSTs; it is deliberately used only for upload and read-only queue recovery.
  The returned provider request ID is committed immediately, before polling.
- Close/reload is safe. Reopening the saved image finds its existing attempt and
  polls the retained provider request. **Check saved request** performs recovery
  without submitting or charging another generation. Only the original requester
  can recover; completed saved videos use existing project/shared-media access.
- Completed remote output is downloaded into
  `projects/<project>/video-render/<attempt>/kling-animation.mp4`. A leased poll
  prevents concurrent completion writes; expired leases allow restart recovery.
  Temporary queue/download/storage failures retain the receipt for another check.
- A timeout/crash before a receipt could be retained is an **unknown submission**.
  No automatic paid retry occurs. Check the fal queue/operator records before
  arranging another generation; a narrow unavoidable crash window exists between
  fal returning its receipt and PostgreSQL committing it.

API routes (all generation/recovery POSTs require authenticated editor access):

| Route | Purpose |
| --- | --- |
| `POST /api/v1/video/animate/preflight` | Free validation and cost preview; no fal calls |
| `POST /api/v1/video/animate` | Reserve and submit a saved render exactly once; returns a queued attempt |
| `POST /api/v1/video/projects/{project}/animations/{attempt}/recover` | Poll the original request and persist completed output |
| `GET /api/v1/video/projects/{project}` | Existing gallery, including saved-still animations |

Preflight needs `project_id`, `source_render_id`; submission also needs
`request_id`, `confirm_paid_submission: true`. No route points are supplied.

## Verification and limits

Provider calls are mocked in `test_kling_video.py` and `test_render_animation.py`.
They cover payload/cost, unchanged full-resolution bytes, forbidden inputs,
ownership, concurrent duplicate admission, credits/trial limits, durable receipt,
restart/lease recovery, lost receipts and storage failures. Existing route-video
tests remain part of the focused regression run. Frontend tests exercise the
saved-render action, cost, one submission, reload/recovery, playback/download,
blocked history checks and polling cleanup.

The local browser trial uses a disposable project and a deterministic **mock
playback fixture**, not a Kling-generated quality sample. It verifies UI/API/
PostgreSQL/storage/playback/download without paid generations. Screenshots and
runtime fixtures are kept outside the repository in
`C:/dev-artifacts/CityPrompt/animate-saved-render-2026-10-06/`.

The reference recording inspires calm motion and stable architectural detail.
Matching its visual quality still needs a separately authorized live Kling pilot
and human review. Source resolution/framing/lighting influence results. The
provider controls output resolution/aspect; this feature sends no resolution
override. Completion is fetched when this panel is open or recovered; there is
no new autonomous background downloader. Keep fal receipts available and reopen
jobs before the provider expires its hosted result. Video-to-video, 4K, multiple
shots and new drone/bicycle route controls remain outside this change.

### Checked on 2026-10-06

- Backend: **61 passed** across the new service/animation tests and existing
  video recovery, Seedance, Omni and scene-revision tests. PostgreSQL cases ran
  in automatically created disposable schemas; providers/storage were mocked.
- Frontend: **15 passed** across the animation dialog, SavedRenderCard,
  ProjectListPage and render-presentation tests. TypeScript type-check passed;
  new files passed focused ESLint/Ruff/Black checks.
- Browser: authenticated saved-image action, free preflight, one mocked paid
  submission, close/reload/reopen recovery, five-second playback and download
  verified at `http://127.0.0.1:5181`. The existing 5174 preview was occupied and
  preserved. Console errors: zero. Source bytes matched their stored checksum
  at **1774 × 887**; the downloaded MP4 matched the saved fixture checksum.
- Mock receipts: **1 upload, 1 submit, 3 polls, 1 output fetch**. Credits changed
  once (1000 → 950 in the disposable test account). Actual paid generations: **0**.
- `git diff --check` passed. Browser/runtime images, media, credentials and test
  fixtures remain outside the source tree and are not commit deliverables.

### Files affected

| Area | Files |
| --- | --- |
| New backend flow | `backend/app/api/v1/render_animation.py`, `backend/app/services/kling_video.py` |
| Existing infrastructure | `backend/app/api/v1/router.py`, `backend/app/api/v1/video.py`, `backend/app/core/config.py`, `backend/.env.example` |
| New UI | `frontend/src/components/viewer/AnimateRenderButton.tsx` |
| Saved-render/gallery integration | `frontend/src/features/projects/ProjectViewPage.tsx`, `frontend/src/features/projects/ProjectListPage.tsx`, `frontend/src/components/viewer/AIRenderPanel.tsx`, `frontend/src/components/viewer/VideoGeneratePanel.tsx`, `frontend/src/services/api.ts` |
| Focused tests | `backend/tests/test_kling_video.py`, `backend/tests/test_render_animation.py`, `frontend/src/components/viewer/AnimateRenderButton.test.tsx` |
| Setup/verification | `docs/ANIMATE_SAVED_RENDER.md` |
