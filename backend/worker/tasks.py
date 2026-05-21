from worker.celery_app import celery

@celery.task(name="worker.tasks.run_ocr_task")
def run_ocr_task(submission_id: str):
    # run_ocr_task (Celery task wrapper)
    pass

@celery.task(name="worker.tasks.run_grading_task")
def run_grading_task(grade_id: str):
    # run_grading_task (Celery task wrapper)
    pass
