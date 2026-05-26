from celery import Celery
from core.config import settings

celery = Celery(
    "gradeops",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_routes={
        "worker.tasks.run_ocr_task":     {"queue": "ocr"},
        "worker.tasks.run_grading_task": {"queue": "grading"},
    }
)