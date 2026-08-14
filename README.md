# 3D Interactive Development Visualization Platform

Transform architectural documents into immersive 3D visualizations for real estate and urban development projects.

## Overview

This platform accepts architectural documents (PDFs, CAD files, images, spreadsheets) and automatically generates interactive 3D models that stakeholders can explore through a web browser. It combines AI-powered document interpretation, procedural 3D generation, and geospatial integration.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                     │
│   React 18 · Three.js · Mapbox GL JS · Tailwind CSS     │
├─────────────────────────────────────────────────────────┤
│                   Application Layer                      │
│   FastAPI · Celery Workers · Claude API · OpenCV         │
├─────────────────────────────────────────────────────────┤
│                      Data Layer                          │
│   PostgreSQL/PostGIS · Redis · S3 Storage · CDN          │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker 24.0+ & Docker Compose v2
- Node.js 20 LTS+
- Python 3.11+
- Git 2.40+

### 1. Clone & Configure

```bash
git clone <repo-url>
cd 3d-development-platform
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 2. Start with Docker Compose

```bash
docker compose up -d
```

This starts PostgreSQL, Redis, the backend API, Celery workers, and the frontend dev server.

### Recommended Windows local launcher

For day-to-day development, including linked Git worktrees, start the local
stack with:

```powershell
.\scripts\start-local-city-prompt.ps1
```

The launcher starts Docker Desktop when necessary, reuses the existing local
PostgreSQL/Redis/MinIO containers so accounts and projects are preserved,
restarts the API from the current worktree so major edits cannot leave stale
code running, starts the frontend when necessary, and waits for both health
checks. This prevents the misleading empty HTTP 500 login error that appears
when Vite is running without the API. Pass `-KeepBackend` only when you
deliberately want to retain the currently running worktree API.

### 3. Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Celery Worker:**
```bash
cd backend
celery -A app.tasks.worker worker --loglevel=info
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 4. Access

- **Frontend (Docker Compose)**: http://localhost:5175
- **Frontend (npm run dev)**: http://localhost:5174
- **API Docs**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc


### 5. Configure Stability AI (Render Previews)

1. Add your key to `.env`:
   ```bash
   STABILITY_API_KEY=your-stability-key
   ```
2. Restart backend and Celery after updating environment variables.
3. Generate a building render preview from the UI, or call:
   - `POST /api/v1/buildings/{building_id}/render-preview`
4. Verify configuration and credits in cofounder analytics:
   - `GET /api/v1/analytics/api-balances`
## Project Structure

```
3d-development-platform/
├── frontend/                # React + Three.js client
│   ├── src/
│   │   ├── components/      # Reusable UI & 3D components
│   │   ├── features/        # Feature modules (projects, documents, buildings)
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API client layer
│   │   ├── store/           # Zustand state management
│   │   ├── types/           # TypeScript type definitions
│   │   └── utils/           # Utility functions
│   └── public/              # Static assets
├── backend/                 # Python FastAPI server
│   ├── app/
│   │   ├── api/             # API route handlers
│   │   ├── core/            # Configuration, security, logging
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic layer
│   │   ├── processing/      # Document extraction & analysis
│   │   ├── generation/      # 3D model generation
│   │   └── tasks/           # Celery async tasks
│   ├── tests/               # Test suite
│   └── migrations/          # Alembic DB migrations
├── infrastructure/          # Deployment configs
│   ├── docker/              # Dockerfiles
│   ├── k8s/                 # Kubernetes manifests
│   └── terraform/           # Infrastructure as code
└── docs/                    # Documentation
```

## Development Phases

| Phase | Duration | Focus |
|-------|----------|-------|
| **Phase 1: MVP** | 8-10 weeks | Basic upload, simple 3D extrusion, web viewer |
| **Phase 2: Enhanced** | 6-8 weeks | AI extraction, facade details, shadows |
| **Phase 3: Advanced** | 8-10 weeks | LOD, phasing, measurements, collaboration |
| **Phase 4: Production** | 4-6 weeks | Auth, mobile, testing, deployment |

## Tech Stack

**Frontend:** React 18, Three.js, React Three Fiber, Mapbox GL JS, Tailwind CSS, Zustand, React Query  
**Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Celery, PostgreSQL 15+, PostGIS, Redis  
**AI/ML:** Anthropic Claude API, OpenCV, Tesseract OCR  
**3D:** trimesh, pygltflib, glTF 2.0 (GLB)  
**Infrastructure:** Docker, Kubernetes, Terraform, S3, CloudFront

## License

Proprietary - All rights reserved.
