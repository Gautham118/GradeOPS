from worker.celery_app import celery
from core.config import supabase_admin
import time

@celery.task(name="worker.tasks.run_ocr_task", bind=True, max_retries=3)
def run_ocr_task(self, submission_id: str):
    try:
        print(f"[OCR] Starting for submission {submission_id}")

        supabase_admin.table("submissions")\
            .update({"status": "processing"})\
            .eq("id", submission_id)\
            .execute()

        # Real OCR pipeline goes here on Day 5
        time.sleep(2)

        supabase_admin.table("submissions")\
            .update({"status": "ocr_complete"})\
            .eq("id", submission_id)\
            .execute()

        print(f"[OCR] Done for submission {submission_id}")

    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)


@celery.task(name="worker.tasks.run_grading_task", bind=True, max_retries=3)
def run_grading_task(self, grade_id: str):
    try:
        print(f"[GRADING] Starting for grade {grade_id}")

        # Real LangGraph agent goes here on Day 6
        time.sleep(1)

        supabase_admin.table("grades")\
            .update({
                "status": "pending_review",
                "ai_score": 7,
                "justification": "Stub grade — real grading coming Day 6"
            })\
            .eq("id", grade_id)\
            .execute()

        print(f"[GRADING] Done for grade {grade_id}")

    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)