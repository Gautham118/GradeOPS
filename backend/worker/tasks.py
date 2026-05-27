from worker.celery_app import celery
from core.config import supabase_admin
import time
import uuid

@celery.task(name="worker.tasks.run_ocr_task", bind=True, max_retries=3)
def run_ocr_task(self, submission_id: str):
    try:
        print(f"[OCR] Starting → submission {submission_id}")

        # Mark submission as processing
        supabase_admin.table("submissions")\
            .update({"status": "processing"})\
            .eq("id", submission_id)\
            .execute()

        # ── Real OCR pipeline goes here on Day 5 ──────────────────
        # from worker.ocr.pipeline import run_ocr
        # grade_ids = run_ocr(submission_id)
        # for grade_id in grade_ids:
        #     run_grading_task.delay(grade_id)
        # ──────────────────────────────────────────────────────────

        # STUB: simulate OCR work + create one fake grade record
        time.sleep(2)

        # Fetch submission to get exam_id
        sub = supabase_admin.table("submissions")\
            .select("exam_id")\
            .eq("id", submission_id)\
            .single()\
            .execute().data

        # Create a stub grade record (pending_review so it shows in TA dashboard)
        grade = supabase_admin.table("grades").insert({
            "submission_id": submission_id,
            "exam_id": sub["exam_id"],
            "question_id": "q1",
            "transcription": "STUB: handwritten answer transcription here",
            "crop_url": None,
            "ai_score": None,
            "max_marks": 10,
            "status": "ocr_complete"
        }).execute().data[0]

        # Enqueue grading task
        run_grading_task.delay(grade["id"])

        # Mark submission as ocr_complete
        supabase_admin.table("submissions")\
            .update({"status": "ocr_complete"})\
            .eq("id", submission_id)\
            .execute()

        print(f"[OCR] Done → submission {submission_id}")

    except Exception as exc:
        print(f"[OCR] Error → {exc}")
        raise self.retry(exc=exc, countdown=30)


@celery.task(name="worker.tasks.run_grading_task", bind=True, max_retries=3)
def run_grading_task(self, grade_id: str):
    try:
        print(f"[GRADING] Starting → grade {grade_id}")

        # ── Real LangGraph agent goes here on Day 6 ───────────────
        # from worker.grading.graph import run_grading_graph
        # run_grading_graph(grade_id)
        # ──────────────────────────────────────────────────────────

        # STUB: simulate grading + write fake result
        time.sleep(1)

        supabase_admin.table("grades").update({
            "ai_score": 7,
            "breakdown": [
                {"condition": "States F = ma correctly",       "awarded": True,  "marks_given": 3, "reason": "Clearly stated."},
                {"condition": "Explains force-acceleration",   "awarded": True,  "marks_given": 4, "reason": "Well explained."},
                {"condition": "Gives a real world example",    "awarded": False, "marks_given": 0, "reason": "No example given."}
            ],
            "justification": "Student demonstrates solid understanding but omits a practical example.",
            "ai_model_used": "stub",
            "status": "pending_review"
        }).eq("id", grade_id).execute()

        print(f"[GRADING] Done → grade {grade_id}")

    except Exception as exc:
        print(f"[GRADING] Error → {exc}")
        raise self.retry(exc=exc, countdown=30)