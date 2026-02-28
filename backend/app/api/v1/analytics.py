"""
Cofounder-only analytics endpoints for deep platform insights.
"""

import asyncio
import time
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, case, cast, distinct, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_cofounder
from app.models.models import User, Project, Building, Document, ApiUsageLog
from app.schemas.schemas import (
    TimeSeriesResponse,
    TimeSeriesPoint,
    CreationTrendsResponse,
    GenerationStatsResponse,
    PlatformHealthResponse,
    TopUsersResponse,
    TopUserEntry,
    ProviderBalance,
    AnthropicTokenUsage,
    ServiceStatus,
    ApiBalanceResponse,
    OperationBreakdown,
    ApiUsageByProvider,
    DailyUsage,
    ApiUsageResponse,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_time_range(range_str: str) -> datetime:
    """Convert a range string like '7d' to a UTC start datetime."""
    now = datetime.now(timezone.utc)
    mapping = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = mapping.get(range_str, 30)
    return now - timedelta(days=days)


def get_granularity(range_str: str) -> str:
    """Return the appropriate date_trunc granularity for a given range."""
    if range_str == "7d":
        return "day"
    elif range_str == "30d":
        return "day"
    elif range_str == "90d":
        return "week"
    else:
        return "month"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/user-growth", response_model=TimeSeriesResponse)
async def user_growth(
    range: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    user: User = Depends(require_cofounder),
    db: AsyncSession = Depends(get_db),
):
    """Time series of user signups."""
    since = parse_time_range(range)
    granularity = get_granularity(range)

    result = await db.execute(
        select(
            func.date_trunc(granularity, User.created_at).label("period"),
            func.count().label("count"),
        )
        .where(User.created_at >= since)
        .group_by("period")
        .order_by("period")
    )
    rows = result.all()

    total = await db.execute(
        select(func.count()).select_from(User).where(User.created_at >= since)
    )

    return TimeSeriesResponse(
        data=[TimeSeriesPoint(period=r.period, count=r.count) for r in rows],
        total_in_range=total.scalar() or 0,
        range=range,
        granularity=granularity,
    )


@router.get("/active-users", response_model=TimeSeriesResponse)
async def active_users(
    range: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    user: User = Depends(require_cofounder),
    db: AsyncSession = Depends(get_db),
):
    """Time series of active users (by last_login_at)."""
    since = parse_time_range(range)
    granularity = get_granularity(range)

    result = await db.execute(
        select(
            func.date_trunc(granularity, User.last_login_at).label("period"),
            func.count(distinct(User.id)).label("count"),
        )
        .where(User.last_login_at >= since)
        .group_by("period")
        .order_by("period")
    )
    rows = result.all()

    total = await db.execute(
        select(func.count(distinct(User.id)))
        .select_from(User)
        .where(User.last_login_at >= since)
    )

    return TimeSeriesResponse(
        data=[TimeSeriesPoint(period=r.period, count=r.count) for r in rows],
        total_in_range=total.scalar() or 0,
        range=range,
        granularity=granularity,
    )


@router.get("/creation-trends", response_model=CreationTrendsResponse)
async def creation_trends(
    range: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    user: User = Depends(require_cofounder),
    db: AsyncSession = Depends(get_db),
):
    """Two time series: projects and buildings created over time."""
    since = parse_time_range(range)
    granularity = get_granularity(range)

    proj_result = await db.execute(
        select(
            func.date_trunc(granularity, Project.created_at).label("period"),
            func.count().label("count"),
        )
        .where(Project.created_at >= since)
        .group_by("period")
        .order_by("period")
    )
    proj_rows = proj_result.all()

    bldg_result = await db.execute(
        select(
            func.date_trunc(granularity, Building.created_at).label("period"),
            func.count().label("count"),
        )
        .where(Building.created_at >= since)
        .group_by("period")
        .order_by("period")
    )
    bldg_rows = bldg_result.all()

    return CreationTrendsResponse(
        projects=[TimeSeriesPoint(period=r.period, count=r.count) for r in proj_rows],
        buildings=[TimeSeriesPoint(period=r.period, count=r.count) for r in bldg_rows],
        range=range,
        granularity=granularity,
    )


@router.get("/generation-stats", response_model=GenerationStatsResponse)
async def generation_stats(
    range: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    user: User = Depends(require_cofounder),
    db: AsyncSession = Depends(get_db),
):
    """Per-engine success/failure counts and overall success rate."""
    since = parse_time_range(range)

    result = await db.execute(
        select(
            func.coalesce(Building.generation_engine, "unknown").label("engine"),
            Building.generation_status,
            func.count().label("count"),
        )
        .where(
            Building.created_at >= since,
            Building.generation_status.isnot(None),
            Building.generation_status != "idle",
        )
        .group_by("engine", Building.generation_status)
    )
    rows = result.all()

    by_engine: dict[str, dict[str, int]] = {}
    total_generations = 0
    total_completed = 0

    for row in rows:
        engine = row.engine
        status = row.generation_status
        count = row.count
        if engine not in by_engine:
            by_engine[engine] = {}
        by_engine[engine][status] = count
        total_generations += count
        if status == "completed":
            total_completed += count

    success_rate = round(total_completed / total_generations * 100, 1) if total_generations > 0 else 0.0

    return GenerationStatsResponse(
        by_engine=by_engine,
        total_generations=total_generations,
        success_rate=success_rate,
        range=range,
    )


@router.get("/platform-health", response_model=PlatformHealthResponse)
async def platform_health(
    user: User = Depends(require_cofounder),
    db: AsyncSession = Depends(get_db),
):
    """API metrics, queue depth, and document processing pipeline stats."""
    from app.main import _request_times, _request_count, _start_time

    times = list(_request_times)
    avg_ms = (sum(times) / len(times) * 1000) if times else 0
    p95_ms = sorted(times)[int(len(times) * 0.95)] * 1000 if len(times) > 1 else 0

    # Celery queue depth
    queue_info = {"active": 0, "reserved": 0, "scheduled": 0, "available": False}
    try:
        from app.tasks.worker import celery_app
        inspector = celery_app.control.inspect(timeout=1.0)
        active = inspector.active() or {}
        reserved = inspector.reserved() or {}
        scheduled = inspector.scheduled() or {}
        queue_info = {
            "active": sum(len(v) for v in active.values()),
            "reserved": sum(len(v) for v in reserved.values()),
            "scheduled": sum(len(v) for v in scheduled.values()),
            "available": True,
        }
    except Exception:
        pass

    # Document processing pipeline
    doc_result = await db.execute(
        select(
            Document.processing_status,
            func.count().label("count"),
        )
        .group_by(Document.processing_status)
    )
    doc_rows = doc_result.all()
    doc_pipeline = {row.processing_status: row.count for row in doc_rows}

    return PlatformHealthResponse(
        api={
            "total_requests": _request_count,
            "uptime_seconds": round(time.time() - _start_time, 1),
            "avg_response_ms": round(avg_ms, 2),
            "p95_response_ms": round(p95_ms, 2),
            "recent_samples": len(times),
        },
        queue=queue_info,
        documents=doc_pipeline,
    )


@router.get("/top-users", response_model=TopUsersResponse)
async def top_users(
    range: str = Query("30d", pattern="^(7d|30d|90d|1y)$"),
    user: User = Depends(require_cofounder),
    db: AsyncSession = Depends(get_db),
):
    """Top 10 users ranked by total activity (projects + buildings + documents)."""
    since = parse_time_range(range)

    # Subquery: count projects per user
    proj_sub = (
        select(
            Project.owner_id.label("user_id"),
            func.count(Project.id).label("project_count"),
        )
        .where(Project.created_at >= since)
        .group_by(Project.owner_id)
        .subquery()
    )

    # Subquery: count buildings per user (via project)
    bldg_sub = (
        select(
            Project.owner_id.label("user_id"),
            func.count(Building.id).label("building_count"),
        )
        .join(Building, Building.project_id == Project.id)
        .where(Building.created_at >= since)
        .group_by(Project.owner_id)
        .subquery()
    )

    # Subquery: count documents per user (via project)
    doc_sub = (
        select(
            Project.owner_id.label("user_id"),
            func.count(Document.id).label("document_count"),
        )
        .join(Document, Document.project_id == Project.id)
        .where(Document.uploaded_at >= since)
        .group_by(Project.owner_id)
        .subquery()
    )

    result = await db.execute(
        select(
            User.id,
            User.email,
            User.full_name,
            User.role,
            func.coalesce(proj_sub.c.project_count, 0).label("project_count"),
            func.coalesce(bldg_sub.c.building_count, 0).label("building_count"),
            func.coalesce(doc_sub.c.document_count, 0).label("document_count"),
            (
                func.coalesce(proj_sub.c.project_count, 0)
                + func.coalesce(bldg_sub.c.building_count, 0)
                + func.coalesce(doc_sub.c.document_count, 0)
            ).label("total_activity"),
        )
        .outerjoin(proj_sub, proj_sub.c.user_id == User.id)
        .outerjoin(bldg_sub, bldg_sub.c.user_id == User.id)
        .outerjoin(doc_sub, doc_sub.c.user_id == User.id)
        .order_by(
            (
                func.coalesce(proj_sub.c.project_count, 0)
                + func.coalesce(bldg_sub.c.building_count, 0)
                + func.coalesce(doc_sub.c.document_count, 0)
            ).desc()
        )
        .limit(10)
    )
    rows = result.all()

    return TopUsersResponse(
        users=[
            TopUserEntry(
                id=str(r.id),
                email=r.email,
                full_name=r.full_name,
                role=r.role,
                project_count=r.project_count,
                building_count=r.building_count,
                document_count=r.document_count,
                total_activity=r.total_activity,
            )
            for r in rows
        ],
        range=range,
    )


@router.get("/api-balances", response_model=ApiBalanceResponse)
async def api_balances(
    user: User = Depends(require_cofounder),
    db: AsyncSession = Depends(get_db),
):
    """Fetch current credit balances from all external API providers."""
    from app.core.config import get_settings
    cfg = get_settings()

    async def _fetch_meshy() -> ProviderBalance:
        if not cfg.meshy_api_key:
            return ProviderBalance(provider="meshy", configured=False, unit="credits")
        try:
            from app.generation.meshy_client import MeshyClient
            data = await MeshyClient().get_balance()
            return ProviderBalance(
                provider="meshy",
                balance=data.get("balance") or data.get("credits"),
                frozen=data.get("frozen"),
                unit="credits",
            )
        except Exception as exc:
            return ProviderBalance(provider="meshy", error=str(exc), unit="credits")

    async def _fetch_tripo() -> ProviderBalance:
        if not cfg.tripo_api_key:
            return ProviderBalance(provider="tripo", configured=False, unit="credits")
        try:
            from app.generation.tripo_client import TripoClient
            data = await TripoClient().get_balance()
            inner = data.get("data", data)
            return ProviderBalance(
                provider="tripo",
                balance=inner.get("balance") or inner.get("credits"),
                frozen=inner.get("frozen"),
                unit="credits",
            )
        except Exception as exc:
            return ProviderBalance(provider="tripo", error=str(exc), unit="credits")

    async def _fetch_stability() -> ProviderBalance:
        if not cfg.stability_api_key:
            return ProviderBalance(provider="stability", configured=False, unit="credits")
        try:
            from app.generation.stability_client import StabilityClient
            data = await StabilityClient().get_balance()
            return ProviderBalance(
                provider="stability",
                balance=data.get("credits"),
                frozen=data.get("frozen"),
                unit="credits",
            )
        except Exception as exc:
            return ProviderBalance(provider="stability", error=str(exc), unit="credits")

    meshy_bal, tripo_bal, stability_bal = await asyncio.gather(
        _fetch_meshy(), _fetch_tripo(), _fetch_stability()
    )

    # Anthropic token totals from usage logs (table may not exist yet)
    anthropic_configured = bool(cfg.anthropic_api_key)
    try:
        anthropic_result = await db.execute(
            select(
                func.coalesce(func.sum(ApiUsageLog.input_tokens), 0).label("total_input"),
                func.coalesce(func.sum(ApiUsageLog.output_tokens), 0).label("total_output"),
                func.count().label("total_calls"),
            )
            .where(ApiUsageLog.provider == "anthropic")
        )
        row = anthropic_result.one()
        anthropic_usage = AnthropicTokenUsage(
            total_input_tokens=int(row.total_input),
            total_output_tokens=int(row.total_output),
            total_calls=int(row.total_calls),
            configured=anthropic_configured,
        )
    except Exception:
        await db.rollback()
        anthropic_usage = AnthropicTokenUsage(configured=anthropic_configured)

    # Non-metered services
    services = [
        ServiceStatus(
            provider="mapbox",
            configured=bool(cfg.mapbox_access_token),
            description="Maps & satellite imagery",
        ),
        ServiceStatus(
            provider="google_oauth",
            configured=bool(cfg.google_client_id and cfg.google_client_secret),
            description="Google sign-in",
        ),
    ]

    return ApiBalanceResponse(
        meshy=meshy_bal,
        tripo=tripo_bal,
        stability=stability_bal,
        anthropic=anthropic_usage,
        services=services,
    )


@router.get("/api-usage", response_model=ApiUsageResponse)
async def api_usage(
    range: str = Query("30d", pattern="^(7d|30d|90d|1y|all)$"),
    user: User = Depends(require_cofounder),
    db: AsyncSession = Depends(get_db),
):
    """Aggregated API usage analytics by provider, operation, and day."""
    since = parse_time_range(range) if range != "all" else None

    try:
        # Per-provider, per-operation aggregation
        stmt = select(
            ApiUsageLog.provider,
            ApiUsageLog.operation,
            func.coalesce(func.sum(ApiUsageLog.credits_used), 0).label("total_credits"),
            func.count().label("call_count"),
            func.count().filter(ApiUsageLog.status == "success").label("success_count"),
        )
        if since:
            stmt = stmt.where(ApiUsageLog.created_at >= since)
        stmt = stmt.group_by(ApiUsageLog.provider, ApiUsageLog.operation).order_by(
            ApiUsageLog.provider, ApiUsageLog.operation
        )
        result = await db.execute(stmt)
        rows = result.all()
    except Exception:
        await db.rollback()
        return ApiUsageResponse(providers=[], daily=[], range=range)

    # Build provider-level aggregations
    provider_map: dict[str, dict] = {}
    for row in rows:
        p = row.provider
        if p not in provider_map:
            provider_map[p] = {
                "provider": p,
                "total_credits": 0.0,
                "total_calls": 0,
                "success_count": 0,
                "by_operation": [],
            }
        entry = provider_map[p]
        credits = float(row.total_credits)
        calls = int(row.call_count)
        successes = int(row.success_count)
        entry["total_credits"] += credits
        entry["total_calls"] += calls
        entry["success_count"] += successes
        entry["by_operation"].append(
            OperationBreakdown(
                operation=row.operation,
                total_credits=credits,
                call_count=calls,
                success_rate=round(successes / calls * 100, 1) if calls > 0 else 0.0,
            )
        )

    providers = []
    for info in provider_map.values():
        tc = info["total_calls"]
        providers.append(
            ApiUsageByProvider(
                provider=info["provider"],
                total_credits=round(info["total_credits"], 2),
                total_calls=tc,
                success_rate=round(info["success_count"] / tc * 100, 1) if tc > 0 else 0.0,
                by_operation=info["by_operation"],
            )
        )

    # Daily breakdown for chart
    try:
        daily_stmt = select(
            cast(ApiUsageLog.created_at, Date).label("day"),
            ApiUsageLog.provider,
            func.coalesce(func.sum(ApiUsageLog.credits_used), 0).label("credits"),
            func.count().label("calls"),
        )
        if since:
            daily_stmt = daily_stmt.where(ApiUsageLog.created_at >= since)
        daily_stmt = daily_stmt.group_by("day", ApiUsageLog.provider).order_by("day")
        daily_result = await db.execute(daily_stmt)
        daily_rows = daily_result.all()
    except Exception:
        await db.rollback()
        daily_rows = []

    daily = [
        DailyUsage(
            date=str(r.day),
            provider=r.provider,
            credits=float(r.credits),
            calls=int(r.calls),
        )
        for r in daily_rows
    ]

    return ApiUsageResponse(providers=providers, daily=daily, range=range)
