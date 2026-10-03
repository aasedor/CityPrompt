"""
API v1 router - aggregates all endpoint routers.
"""

from fastapi import APIRouter, Depends
from app.core.classroom_scope import require_classroom_scope

from app.api.v1 import (
    projects,
    reference_layers,
    student_reports,
    documents,
    buildings,
    auth,
    oauth,
    context,
    shares,
    annotations,
    reports,
    activity,
    site_zones,
    admin,
    analytics,
    settings,
    files,
    model_library,
    model_cache,
    master_plan_2d,
    render,
    direct_3d_render,
    render_attempts,
    feedback,
    elevation,
    geocoding,
    shapefiles,
    custom_style,
    urban_dna,
    lego_assembly,
    site_landscape,
    video,
)

api_router = APIRouter(dependencies=[Depends(require_classroom_scope)])

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
api_router.include_router(model_cache.router, prefix="/model-cache", tags=["Archetype Model Cache"])
api_router.include_router(lego_assembly.router, prefix="/lego-assembly", tags=["LEGO Assembly Experiment"])

api_router.include_router(master_plan_2d.router, prefix="/master-plan-2d", tags=["2D Master Plan"])
api_router.include_router(render.router, prefix="/render", tags=["AI Render"])
api_router.include_router(video.router, prefix="/video", tags=["Video Render"])
api_router.include_router(direct_3d_render.router, prefix="/render", tags=["Direct 3D Render"])
api_router.include_router(render_attempts.router, prefix="/render", tags=["Direct 3D Render"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Beta Feedback"])
api_router.include_router(elevation.router, prefix="/elevation", tags=["Elevation"])
api_router.include_router(geocoding.router, prefix="/geocoding", tags=["Geocoding"])
api_router.include_router(shapefiles.router, prefix="/shapefiles", tags=["Shapefile Import"])
api_router.include_router(custom_style.router, prefix="/custom-style", tags=["Custom Style"])
api_router.include_router(urban_dna.router, prefix="/urban-dna", tags=["Urban Intelligence DNA"])

api_router.include_router(reference_layers.router, prefix="/reference-layers", tags=["Reference layers"])
api_router.include_router(student_reports.router)

api_router.include_router(site_landscape.router, prefix="/site-landscape", tags=["Site Landscape"])
