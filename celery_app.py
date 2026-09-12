from celery import Celery
from app.core.config import settings
celery_app = Celery("job_platform", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_track_started = True
celery_app.conf.task_serializer = "json"
celery_app.conf.accept_content = ["json"]
