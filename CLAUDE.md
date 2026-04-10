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
- Temperature 0.0 for aerial renders (precision)
- Simple natural prompts beat complex structured ones for Gemini
- SCHEMA compressed prompts work for aerial, verbose depth-plane descriptions for street view
- Critical constraints go at the END of the prompt (Gemini weights later instructions more heavily)
- Street view: 200m view cone, 70° FOV, occlusion culling, Montage style produces best results

## Architecture

### Render Pipeline
1. User draws zones on map → assigns archetype per zone
2. Each archetype gets unique polygon color (archetypeShadeMap.ts)
3. Screenshot + mask generated from zone colors
4. Prompt built from archetype metadata + style + constraints
5. POST /api/v1/render → Gemini API (gemini-3.1-flash-image-preview)
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
