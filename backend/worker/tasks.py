from worker.celery_app import celery
from core.config import supabase_admin
import time

@celery.task(name="worker.tasks.run_ocr_task", bind=True, max_retries=3)
def run_ocr_task(self, submission_id: str):
    try:
        print(f"[OCR] Starting → submission {submission_id}")

        supabase_admin.table("submissions")\
            .update({"status": "processing"})\
            .eq("id", submission_id).execute()

        # ── Real OCR pipeline ──────────────────────────────────────
        from worker.ocr.pipeline import run_ocr
        results = run_ocr(submission_id)
        for result in results:
            run_grading_task.delay(result["grade_id"])
        # ──────────────────────────────────────────────────────────

        supabase_admin.table("submissions")\
            .update({"status": "ocr_complete"})\
            .eq("id", submission_id).execute()

        print(f"[OCR] Done → {len(results)} questions extracted")

    except Exception as exc:
        print(f"[OCR] Error → {exc}")
        raise self.retry(exc=exc, countdown=30)


@celery.task(name="worker.tasks.run_grading_task", bind=True, max_retries=3)
def run_grading_task(self, grade_id: str):
    try:
        print(f"[GRADING] Starting → grade {grade_id}")

        # ── Real LangGraph agent ───────────────────────────────────
        from worker.grading.graph import run_grading_graph
        run_grading_graph(grade_id)
        # ──────────────────────────────────────────────────────────

        print(f"[GRADING] Done → grade {grade_id}")

    except Exception as exc:
        print(f"[GRADING] Error → {exc}")
        raise self.retry(exc=exc, countdown=30)