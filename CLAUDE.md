# SiteForge — AI-Powered Architectural Site Planning

## What This Is

SiteForge lets architects draw zones on a map, assign building archetypes, and generate photomontage-quality AI renders. Frontend is React/TypeScript/Vite with Three.js and Mapbox. Backend is Python FastAPI with PostgreSQL/PostGIS.

## Quick Commands

```bash
# Frontend (port 5174)
cd frontend && npm run dev

# Backend (port 8000)
cd backend && uvicorn app.main:app --reload --port 8000

# Tests
cd frontend && npm run test        # Vitest
cd backend && pytest                # Pytest

# Type check & lint
cd frontend && npm run type-check && npm run lint
```

## Critical Rules

### NEVER json.dump buildingArchetypes.json
`json.dump()` corrupts `thumbnailUrl` paths (underscores → hyphens). When adding archetypes, use TEXT-LEVEL insertion — splice new entries as raw text before the closing `]`. Never parse-modify-dump.

### Test locally before pushing
Always verify on localhost:5174 before committing. Check that cards load, renders work, no console errors.

### Two remotes must stay in sync
- `origin` → aasedor/2D-Maps
- `beeman` → beemanbesh/2D-Maps2
Check both with `git log origin/master --oneline -5` and `git log beeman/master --oneline -5` before pushing. Never force push without checking what's on both remotes.

### Render prompt guidelines
- Do NOT send temperature on Gemini 3 image calls (official guidance: keep the
  default; the old temp-0.0 rule and the guidance_scale knob are retired —
  guidance_scale was silently overriding temp to 0.75). Send aspect_ratio +
  image_size explicitly instead.
- Simple natural prompts beat complex structured ones for Gemini
- SCHEMA compressed prompts work for aerial, verbose depth-plane descriptions for street view
- Critical constraints go at the END of the prompt (Gemini weights later instructions more heavily)
- Street view: 200m view cone, 70° FOV, occlusion culling, Montage style produces best results

## Collaboration Patterns (the working rhythm)

Default operating style for non-trivial work in this repo. Preserved from the 2026-04-18 session where a full catalog overhaul + 2,000+ Gemini calls landed with zero rollbacks.

1. **Pilot → confirm → scale.** Never fire a $50+ full-catalog run without a cheap smoke test first: dry-run (0 API calls) → 1-archetype pilot (~$0.25, <1 min) → show output → green light → execute. Applied for Collegiate Gothic, Neighborhood Park, Haussmann Boulevard before every catalog-wide run.
2. **Show images inline for visual verification.** Don't just report "4/4 succeeded" — read the generated JPGs back so the user sees the actual output. Quality issues (e.g. 75° perspective creep on a 90° nadir) are invisible in a success count.
3. **Offer 2–3 options with tradeoffs.** When decisions exist, present A/B/C with cost, time, risk. Don't silently pick.
4. **Validate after every bulk change.** For catalog edits: JSON still parses, thumbnailUrl count unchanged, no duplicate archetype IDs, known-good entries untouched. For bulk deletes: verify targets gone AND non-targets still intact.
5. **Backup before destructive edits.** Every catalog splice / recategorization / bulk migration saves a `.bak` or `.bak-<operation>` file. Enables one-line rollback.
6. **Scope commits tightly.** Never bundle unrelated work. If a commit accidentally sweeps in pre-staged files, flag it immediately and offer `git reset --soft HEAD~1` to split.
7. **Check existing research first.** `docs/*-RESEARCH-AndrewDesk.md` and `docs/*_AUDIT_REPORT*.md` files may already have answers. Align to them before inventing new structures.
8. **Diagnose root cause, not symptoms.** When something breaks, fix the underlying logic (e.g. id-collision check in the orphan detector), not a one-off patch.
9. **Parallel only when genuinely safe.** Background tasks writing to different folders with no race conditions = OK. Otherwise chain sequentially.
10. **When a data change doesn't show in UI, check which field the consumer actually reads.** The UI picker filters by `developmentType`, not `buildingSubcategory` — updating the wrong field silently fails.

## Architecture

### Render Pipeline
1. User draws zones on map → assigns archetype per zone
2. Each archetype gets unique polygon color (archetypeShadeMap.ts)
3. Screenshot + mask generated from zone colors
4. Prompt built from archetype metadata + style + constraints
5. POST /api/v1/render → Gemini API (gemini-3.1-flash-image — GA id; the -preview alias is deprecated)
6. Post-processing (sharpen, contrast, color) → composite onto map

### Aerial Render
`frontend/src/components/viewer/useAIRender.ts` (134 KB) — prompt building, mask generation, stitching

### Street View Render
`frontend/src/components/viewer/useStreetViewRender.ts` (87 KB) — Three.js clay massing model, SCHEMA-style prompts (Geometric Lockdown, Numerical Inventory, depth planes), multi-image archetype routing, entourage overlay

### Key Data Files
- `frontend/src/data/buildingArchetypes.json` (841 KB) — 97 building archetypes
- `frontend/src/data/streetPathArchetypes.json` — 36 street types
- `frontend/src/data/openSpaceArchetypes.json` — parks & plazas
- `frontend/src/data/archetypeShadeMap.ts` — unique color per archetype
- Archetype images: `frontend/public/archetypes/{buildings|openspaces|streets}/{slug}/`

### State Management (Zustand)
- `useAuthStore` — user, login, permissions
- `useViewerStore` — selected zones, editing state
- `useGenerationStore` — render jobs, queue, progress
- `useUndoRedo` — undo/redo stack

### Backend Structure
- `backend/app/api/v1/render.py` — Gemini API proxy
- `backend/app/api/v1/site_zones.py` (93 KB) — zone CRUD
- `backend/app/core/config.py` — all env config (API keys, DB, Redis)
- `backend/app/models/models.py` — SQLAlchemy ORM
- `backend/app/schemas/schemas.py` — Pydantic validation

## Tech Stack Summary

**Frontend:** React 18 · TypeScript 5.6 · Vite 6 · Three.js · @react-three/fiber · Mapbox GL · Zustand · TanStack Query · Tailwind CSS · Recharts · Sentry

**Backend:** FastAPI · SQLAlchemy 2 + asyncpg · PostgreSQL + PostGIS · Redis · Celery · Google GenAI SDK · Anthropic SDK · Pillow · OpenCV

**Infra:** Docker Compose · MinIO (S3) · Alembic migrations

## File Size Warning

Several key files are very large. Read specific line ranges instead of whole files:
- `useAIRender.ts` — 134 KB
- `useStreetViewRender.ts` — 87 KB
- `ZonePropertiesPanel.tsx` — 147 KB
- `SiteZonesGroup.tsx` — 113 KB
- `site_zones.py` — 93 KB
- `schemas.py` — 67 KB
- `buildingArchetypes.json` — 841 KB
