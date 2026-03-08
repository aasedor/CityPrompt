"""
API v1 router - aggregates all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1 import projects, documents, buildings, auth, oauth, context, shares, annotations, reports, activity, site_zones, admin, analytics, settings, files, model_library

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(oauth.router, prefix="/auth/oauth", tags=["OAuth2 Social Login"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(buildings.router, prefix="/buildings", tags=["Buildings"])
api_router.include_router(context.router, prefix="/context", tags=["Context"])
api_router.include_router(shares.router, prefix="/shares", tags=["Sharing"])
api_router.include_router(annotations.router, prefix="/annotations", tags=["Annotations"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(activity.router, prefix="/activity", tags=["Activity"])
api_router.include_router(site_zones.router, prefix="/site-zones", tags=["Site Zones"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Cofounder Analytics"])
api_router.include_router(settings.router, prefix="/settings", tags=["Platform Settings"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(model_library.router, prefix="/model-library", tags=["Model Library"])
