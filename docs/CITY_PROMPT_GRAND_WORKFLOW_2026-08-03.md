# City Prompt Grand Workflow

Date: 2026-08-03

Branch: `codex/city-prompt-grand-workflow`

## Product workflow

City Prompt now has one primary path from site selection to a durable image or
video output:

1. **Site** — draw one active Site Boundary.
2. **Plan** — understand the site with Site DNA, then draw or generate
   buildings, parks, and streets.
3. **3D** — use **Generate to 3D** once to compile the entire current plan.
4. **Render** — create a still image or video from that exact compiled scene.

The four-step workflow is shown consistently in both the globe and plan views.
Later steps remain unavailable until their required project state exists. If a
user edits a polygon or changes its archetype after compiling, the workflow
honestly returns to step 3 instead of rendering stale geometry.

## 1. Site Boundary and Site DNA

A project has at most one active Site Boundary. Migration `027` adds
`is_active_boundary`, marks the newest existing boundary active, and adds a
partial unique index that enforces the invariant at the database layer. The API
also owns activation, deactivation, deletion, and containment validation so
multiple browser sessions cannot create ambiguous site state.

Drawing the boundary immediately:

- establishes the only parcel used by planning, compilation, and rendering;
- clips the source Google photogrammetry inside the parcel so existing trees,
  buildings, and other captured features do not protrude through the proposal;
- creates a constructed site surface over the cleared area, sampled against the
  local grade to avoid a floating slab or severe edge discontinuities; and
- opens the canonical Site DNA panel for parcel and policy analysis.

The Site Boundary is a preparation and analysis object. It is not itself a
building, park, or street, and it is excluded from physical scene compilation.
Buildings, parks, and streets must be covered by the active boundary.

## 2. Manual planning and Master Planner

The same project state supports both authoring paths:

- **Manual:** draw a building, park, or street polygon and choose an archetype
  and variant.
- **Master Planner:** open Site DNA, generate and review planning scenarios, and
  apply the selected scenario to populate the boundary.

Generated public-realm labels are resolved to executable City Prompt
archetypes, not display-only text. The public-realm coordinator also receives
the surrounding scene context so connected streets and parks can form one
coherent network.

## 3. Generate to 3D

**Generate to 3D** is the single scene-compilation command. It plans the LEGO
building families first, then performs one bounded full-scene compilation:

- buildings use the authored LEGO family when available;
- buildings without a completed family preserve their exact authored envelope
  through deterministic massing rather than disappearing;
- parks and streets compile into Public Realm LEGO base surfaces and placement
  recipes;
- public-realm props such as trees, benches, lights, crossings, and street
  furniture are materialized only from a valid compiled recipe; and
- unallocated land inside the boundary compiles into a boundary-bound residual
  landscaping layer.

The workflow state verifies every physical polygon's source fingerprint and 3D
representation fingerprint. It also verifies the public-realm schema and the
residual landscape's boundary ID and source hash. A scene is renderable only
when all of those claims describe the current plan.

The default park and street base-skin generation is deterministic and
credit-free. The previously developed AI park-material drape controls remain
available behind `VITE_ENABLE_RENDER_PANEL_COMMUNITY_3D_TOOLS=true`. They are
not invoked automatically because a paid generative API call needs an explicit
product-level budget and approval policy. This does not affect deterministic
base skins, coordinated placement, or 3D props.

## 4. Still and video rendering

The primary still-image path is Direct 3D Render. The classic colored-polygon
render path is hidden by default because it does not represent the compiled
scene. It can be restored temporarily with
`VITE_ENABLE_CLASSIC_POLYGON_RENDER=true` for recovery or comparison work.

Still and video requests are bound to a canonical SHA-256 scene revision. The
revision contains the sorted per-zone Community 3D claims and residual
landscape claim. The backend validates video claims during the zero-cost
preflight and validates them again under the project lock immediately before
provider capacity or credits are reserved. A changed scene returns HTTP 409 and
is explicitly marked unbilled.

Saved stills and video attempts retain the scene revision in durable project
metadata. This makes it possible to tell which compiled design produced an
output and prevents a prepared video request from silently rendering a later
edit.

## Main state transition

```text
No active boundary
  -> draw Site Boundary
Active boundary, no physical zones
  -> draw manually or apply a Master Planner scenario
Current 2D plan
  -> Generate to 3D
Current compiled scene
  -> Render or Video Render
Edit boundary, zone geometry, archetype, or representation
  -> scene becomes stale -> Generate to 3D again
```

## Deployment and feature flags

Run the database migration before deploying the application:

```bash
cd backend
alembic upgrade head
```

The migration chain now includes the historical core-schema baseline, so the
same command provisions both a brand-new PostGIS database and an existing City
Prompt database. Existing installations at revision 027 are unaffected.

The production-default workflow requires no new frontend feature flags. These
flags only expose superseded or advanced surfaces:

| Flag | Default | Purpose |
| --- | --- | --- |
| `VITE_ENABLE_LEGACY_SITE_BOUNDARY_TOOLS` | `false` | Restore the old boundary-level community-generation controls. |
| `VITE_ENABLE_RENDER_PANEL_COMMUNITY_3D_TOOLS` | `false` | Restore internal Community 3D and optional AI material controls inside Render. |
| `VITE_ENABLE_CLASSIC_POLYGON_RENDER` | `false` | Restore the legacy colored-polygon image pipeline. |

## Verification checklist

1. Create or open a project and draw a Site Boundary.
2. Confirm source tiles are cleared inside the parcel and the prepared surface
   appears immediately.
3. Generate Site DNA and review a scenario without creating physical geometry.
4. Add at least one building, park, and street manually or apply a Master
   Planner scenario.
5. Confirm Render and Video Render remain disabled.
6. Select Generate to 3D and wait for the bounded full-scene build to finish.
7. Confirm buildings, base skins, public-realm props, and residual landscaping
   are visible and the workflow advances to Render.
8. Create a still and a video preflight.
9. Edit one physical polygon and confirm both rendering paths require a new
   Generate to 3D run.
10. Recompile and confirm the new outputs receive a different scene revision.

## Contributor handoff

After checking out this branch, install the existing frontend and backend
dependencies, run migration `027`, and use the repository's normal local setup
commands. The most important implementation entry points are:

- `frontend/src/features/workflow/cityPromptWorkflow.ts`
- `frontend/src/features/projects/ProjectViewPage.tsx`
- `frontend/src/features/legoAssembly/LegoBuilderPanel.tsx`
- `frontend/src/components/viewer/globe/GlobeZoneLayer.tsx`
- `frontend/src/components/viewer/globe/GlobeAIRenderPanel.tsx`
- `frontend/src/components/viewer/VideoGeneratePanel.tsx`
- `backend/app/api/v1/site_zones.py`
- `backend/app/api/v1/direct_3d_render.py`
- `backend/app/api/v1/video.py`
- `backend/app/services/scene_revision.py`

Large generated experiments from the July recovery workspace were intentionally
not copied or staged. The integration branch includes the reviewed source
checkpoints for planning, authored LEGO form preservation, coordinated public
realm generation, archetype hero images, and deterministic video capture. See
`docs/WORKSPACE_RECOVERY_2026-07-19.md` before reorganizing preserved generated
output.

## Known follow-on work

- Add an explicit paid-generation budget/approval experience before enabling AI
  material drapes by default.
- Continue promoting high-quality authored LEGO families; deterministic exact-
  envelope massing remains the safe fallback.
- Expand end-to-end browser coverage for provider-backed still and video jobs;
  automated tests intentionally do not spend external API credits.
- Re-baseline the inherited frontend performance budget after route-level code
  splitting. CI reports the current map/Three.js/catalogue bundle overage as an
  advisory while continuing to require a successful production build.
