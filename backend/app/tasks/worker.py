"""
Celery worker configuration and task definitions.
"""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "dev_platform",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minute hard limit
    task_soft_time_limit=300,  # 5 minute soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    task_routes={
        "cityprompt.direct3d.render": {"queue": "direct3d"},
        "cityprompt.direct3d.maintain": {"queue": "direct3d-maintenance"},
        **({"process_document": {"queue": "classroom-documents"}} if settings.classroom_release else {}),
    },
    beat_schedule=({"recover-direct3d": {"task": "cityprompt.direct3d.maintain", "schedule": 30.0}}
                   if settings.direct_3d_jobs_enabled else {}),
)

# Import tasks so they register with Celery
import app.tasks.processing  # noqa: F401, E402
import app.tasks.render_preview  # noqa: F401, E402
import app.tasks.urban_dna  # noqa: F401, E402
import app.tasks.direct_3d  # noqa: F401, E402
