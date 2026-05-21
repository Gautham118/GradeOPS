from celery import Celery
from core.config import settings

celery = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery.conf.task_routes = {
    "worker.tasks.run_ocr_task": {"queue": "ocr"},
    "worker.tasks.run_grading_task": {"queue": "grading"},
}
