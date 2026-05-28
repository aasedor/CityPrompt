# Deployment Environment Checklist

Use this before any staging or production deploy. The current deployment target is controlled private beta first, public production later.

## Local 5175

- Frontend: `http://localhost:5175`
- Backend API: `http://localhost:8000`
- WebSocket: `ws://localhost:8000`
- Google OAuth callback: `http://localhost:8000/api/v1/auth/oauth/google/callback`
- Microsoft OAuth callback: `http://localhost:8000/api/v1/auth/oauth/microsoft/callback`

Local `.env` is intentionally ignored by git. If OAuth redirects to a tunnel or old host, restart the backend container after editing `.env`; Docker does not reload `env_file` values until the container is recreated.

## Render Production

API and worker must both have the same production safety contract:

- `APP_ENV=production`
- `APP_DEBUG=false` or unset
- `JWT_SECRET_KEY` generated or set to a strong value
- `ALLOWED_ORIGINS=https://cityprompt.ca,https://www.cityprompt.ca,https://threed-platform-frontend.onrender.com`
- `FRONTEND_URL=https://cityprompt.ca`
- `GOOGLE_REDIRECT_URI=https://threed-platform-api.onrender.com/api/v1/auth/oauth/google/callback`
- `MICROSOFT_REDIRECT_URI=https://threed-platform-api.onrender.com/api/v1/auth/oauth/microsoft/callback`
- `RENDER_GLOBAL_DAILY_TOKEN_CAP=5000` or another explicit beta cap

`https://cityprompt.ca` is the canonical production frontend. Keep `https://www.cityprompt.ca` and the old Render frontend host in `ALLOWED_ORIGINS` unless they are intentionally retired.

Production frontend build variables:

- `VITE_API_URL=https://threed-platform-api.onrender.com`
- `VITE_WS_URL=wss://threed-platform-api.onrender.com`
- `VITE_MAPBOX_TOKEN`
- `VITE_GOOGLE_MAPS_API_KEY`
- `VITE_SENTRY_DSN` when Sentry is enabled

Manual secrets to set in the Render dashboard:

- Object storage: `S3_ENDPOINT_URL`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`
- Render providers: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MESHY_API_KEY`
- OAuth: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`
- Maps and monitoring: `GOOGLE_MAPS_API_KEY`, `VITE_GOOGLE_MAPS_API_KEY`, `SENTRY_DSN`, `VITE_SENTRY_DSN`

## OAuth Provider Consoles

Google authorized redirect URIs:

- Local: `http://localhost:8000/api/v1/auth/oauth/google/callback`
- Production: `https://threed-platform-api.onrender.com/api/v1/auth/oauth/google/callback`

Microsoft authorized redirect URIs:

- Local: `http://localhost:8000/api/v1/auth/oauth/microsoft/callback`
- Production: `https://threed-platform-api.onrender.com/api/v1/auth/oauth/microsoft/callback`

## Pre-Deploy Smoke

- `python -m compileall backend/app`
- Production settings import with Render-like env.
- API starts and `/health` returns healthy.
- `node scripts/smoke-production-cors.mjs`
- Frontend build has all required `VITE_*` values.
- Login works with email/password and Google OAuth.
- Project opens on `localhost:5175`; map/globe loads; render gallery lists saved renders.

To test a different deployment target:

```bash
PRODUCTION_API_ORIGIN=https://threed-platform-api.onrender.com \
PRODUCTION_FRONTEND_ORIGINS=https://cityprompt.ca,https://www.cityprompt.ca \
node scripts/smoke-production-cors.mjs
```
