# Phase 1: Complete Backend APIs (Schemas, Routers, and main.py Integration)

Establish the core REST API endpoints needed for GradeOps, enabling the instructor to upload exams and rubric configurations, submit PDF submissions, and allow TAs to fetch the grading queue and perform Human-in-the-Loop overrides/approvals.

## User Review Required

> [!IMPORTANT]
> The database tables must already be migrated using the SQL scripts under `supabase/migrations/` and the storage buckets (`exam-pdfs`, `answer-crops`) must exist. Please make sure that migrations `001` through `006` are executed in your Supabase SQL Editor and the storage buckets are created before testing.

> [!WARNING]
> We will stub the Celery task triggers (`run_ocr_task.delay(submission_id)`) initially so that the endpoint does not crash if Celery or Redis are not running. The actual Celery tasks will be completed in Phase 2.

## Open Questions

> [!NOTE]
> Has the Supabase schema migrations been executed already? If not, we will need to run the SQL scripts in `supabase/migrations` via the Supabase dashboard SQL editor.

## Proposed Changes

We will modify the stubs in `backend/schemas/` and `backend/routers/` to implement proper logic and hook them up to Supabase through `supabase_anon`.

---

### Schemas

#### [MODIFY] [exam.py](file:///d:/GradeOPS/GradeOPS/backend/schemas/exam.py)
Update schemas to specify the exact shape of Pydantic models for exams:
- `ExamCreate`: contains title, subject, and `rubric_json` (containing questions structure).
- `ExamOut`: adds `id`, `created_by`, `created_at`.

#### [MODIFY] [submission.py](file:///d:/GradeOPS/GradeOPS/backend/schemas/submission.py)
Define `SubmissionOut` schema with all fields matching the `submissions` table:
- `id`, `exam_id`, `student_name`, `pdf_path`, `status`, `uploaded_by`, `created_at`.

#### [MODIFY] [grade.py](file:///d:/GradeOPS/GradeOPS/backend/schemas/grade.py)
Provide proper fields for `GradeOut` and the `TAOverride` request schema.

---

### Routers

#### [MODIFY] [exams.py](file:///d:/GradeOPS/GradeOPS/backend/routers/exams.py)
Implement `POST /exams` (instructor only), `GET /exams` (any authenticated user), and `GET /exams/{id}` (any authenticated user).

#### [MODIFY] [submissions.py](file:///d:/GradeOPS/GradeOPS/backend/submissions.py)
Implement `POST /submissions/bulk` to handle uploaded files:
1. Accept multipart upload of files.
2. Upload bytes to Supabase `exam-pdfs/{exam_id}/{uuid}.pdf` bucket.
3. Record each submission with status `uploaded`.
4. Trigger OCR task stub.
Implement `GET /submissions` to list submissions for an exam.

#### [MODIFY] [grades.py](file:///d:/GradeOPS/GradeOPS/backend/routers/grades.py)
Implement `GET /grades` (paginated filters by `exam_id` and `status`) and `PATCH /grades/{id}` (TA override actions).

---

## Verification Plan

### Automated Tests
- Run a manual test script that simulates:
  1. Authenticating as an instructor/TA.
  2. Calling the API endpoints using `curl` or `requests` in Python.
- Check the Uvicorn reload logs to ensure no syntax/import errors.

### Manual Verification
- We can inspect the Supabase dashboard to verify exams and submissions tables are populated upon API request.
