# GradeOps 🎓

> AI-powered exam grading pipeline with Human-in-the-Loop review

GradeOps automates the grading of handwritten exam PDFs using Vision-Language Models and LLM-based rubric evaluation, with a real-time TA review dashboard for human oversight and correction.

Built as a portfolio project targeting **Data Science and ML Engineering** roles.

---

## Demo Flow

```
Instructor uploads handwritten exam PDFs
            ↓
Celery OCR worker transcribes each answer using Groq Vision API
            ↓
LangGraph grading agent scores each answer against the rubric
            ↓
Grades land in Supabase → Realtime pushes to TA dashboard
            ↓
TA reviews AI grade → Approve / Override / Flag with keyboard shortcuts
            ↓
Final grades locked in database
```

---

## Features

- **Bulk PDF upload** — instructors upload multiple handwritten answer sheets at once
- **Automated OCR** — Groq Vision API transcribes handwritten text from each answer crop
- **LangGraph grading agent** — 4-node graph evaluates partial credit per rubric condition
- **Plagiarism detection** — pgvector cosine similarity flags suspiciously similar answers
- **Real-time TA dashboard** — Supabase Realtime pushes grade cards as they complete
- **Keyboard-driven review** — `A` approve, `F` flag, `0-9` + `Enter` override score
- **Role-based access** — instructors create exams, TAs review grades

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | FastAPI + Uvicorn |
| Task Queue | Celery + Redis |
| OCR | Groq Vision API (meta-llama/llama-4-scout-17b) |
| Grading Agent | LangGraph + Groq (llama-3.3-70b-versatile) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Database | Supabase (PostgreSQL + pgvector) |
| Storage | Supabase Storage |
| Auth | Supabase Auth |
| Realtime | Supabase Realtime |

---

## Project Structure

```
gradeops/
├── backend/
│   ├── main.py                  # FastAPI app, CORS, router registration
│   ├── core/
│   │   ├── config.py            # Admin + anon Supabase clients and Pydantic settings
│   │   ├── auth.py              # JWT verification via HTTPBearer
│   │   └── deps.py              # require_role() dependency
│   ├── routers/
│   │   ├── exams.py             # POST /exams, GET /exams
│   │   ├── submissions.py       # POST /submissions/bulk
│   │   └── grades.py            # GET /grades, PATCH /grades/:id
│   ├── schemas/                 # Pydantic v2 request/response models
│   └── worker/
│       ├── celery_app.py        # Celery instance + task routing
│       ├── tasks.py             # run_ocr_task, run_grading_task
│       ├── ocr/
│       │   ├── pipeline.py      # PDF → crops → transcription → DB
│       │   ├── pdf_utils.py     # PyMuPDF page rendering
│       │   ├── crop_utils.py    # Heuristic question region detection
│       │   └── vision.py        # Groq Vision transcription
│       └── grading/
│           ├── graph.py         # LangGraph StateGraph definition
│           ├── nodes.py         # 4 grading nodes
│           ├── prompts.py       # LLM system prompts
│           └── embedder.py      # Embedding + pgvector similarity search
│
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Login.jsx        # Supabase Auth UI
│       │   ├── Dashboard.jsx    # Role-aware landing page
│       │   ├── ExamUpload.jsx   # 2-step exam + PDF upload wizard
│       │   └── ReviewQueue.jsx  # TA grading dashboard
│       ├── components/
│       │   ├── GradeCard.jsx    # Crop image + breakdown + action buttons
│       │   ├── RubricEditor.jsx # Dynamic rubric builder form
│       │   ├── KeyboardHints.jsx
│       │   └── ProtectedRoute.jsx
│       └── hooks/
│           ├── useSession.js
│           ├── useRole.js
│           └── useRealtimeGrades.js
│
└── supabase/
    └── migrations/              # 6 SQL migrations (run in order)
```

---

## Local Setup

### Prerequisites

- Python 3.11 (Anaconda recommended)
- Node.js 20+
- Redis (WSL on Windows: `sudo service redis-server start`)
- Supabase project (free tier works)
- Groq API key (free at console.groq.com)

### 1. Clone the repo

```bash
git clone https://github.com/Gautham118/GradeOPS.git
cd GradeOPS
```

### 2. Supabase setup

Create a free project at [supabase.com](https://supabase.com), then run the 6 migrations in order via the SQL editor:

```
supabase/migrations/001_create_profiles.sql
supabase/migrations/002_create_exams.sql
supabase/migrations/003_create_submissions.sql
supabase/migrations/004_create_grades.sql
supabase/migrations/005_rls_policies.sql
supabase/migrations/006_pgvector_embeddings.sql
```

Create two Storage buckets in the Supabase dashboard:
- `exam-pdfs` — Private
- `answer-crops` — Authenticated read

Add this RLS policy for the answer-crops bucket (SQL editor):

```sql
CREATE POLICY "Authenticated users can read answer crops"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'answer-crops');
```

### 3. Backend setup

```bash
cd backend
cp .env.example .env
# Fill in your Supabase + Groq credentials in .env
```

```bash
conda activate your-env
pip install fastapi uvicorn python-dotenv supabase python-jose[cryptography] \
            python-multipart pydantic-settings celery redis pymupdf pillow \
            groq langchain-groq langgraph sentence-transformers
```

### 4. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
# Fill in VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
```

### 5. Environment variables

**`backend/.env`**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
REDIS_URL=redis://localhost:6379/0
GROQ_API_KEY=your-groq-api-key
```

**`frontend/.env`**
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_BASE_URL=http://localhost:8000
```

### 6. Create test users

In Supabase Dashboard → Authentication → Users, create two accounts:
- `instructor@gradeops.test` — then run:
  ```sql
  UPDATE profiles SET role = 'instructor' WHERE email = 'instructor@gradeops.test';
  ```
- `ta@gradeops.test` — default role is `ta`, no change needed

---

## Running the Project

You need 4 terminals running simultaneously. On Windows, open `start_project.bat` file and change the `set CONDA_ENV=base` line to match with your conda environment name. A clear comment inside the file tell you how to find it. 
Save the file and then double-click it to open all at once.

```bash
# Terminal 1 — FastAPI backend
cd backend && uvicorn main:app --reload

# Terminal 2 — OCR worker
cd backend && celery -A worker.celery_app worker -Q ocr -c 1 --pool=solo --loglevel=info

# Terminal 3 — Grading worker
cd backend && celery -A worker.celery_app worker -Q grading -c 1 --pool=solo --loglevel=info

# Terminal 4 — Frontend
cd frontend && npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

> **Windows note:** `--pool=solo` is required for Celery on Windows. Remove it when deploying to Linux.

---

## Using the App

### As Instructor

1. Log in at `/login`
2. Click **Upload Exam** on the dashboard
3. Fill in exam title and build a rubric (add questions + grading conditions with marks)
4. Click **Create Exam & Continue**
5. Enter student name(s) and select PDF file(s) → **Upload & Start Grading**
6. Click **Upload More PDFs** to add more submissions to the same exam
7. Switch to the TA account to see grades arrive in real time

### As TA

1. Log in at `/login`
2. Click **Review Queue** on the dashboard
3. Select the exam from the dropdown
4. Review each grade card — it shows the answer scan, transcription, AI score, and per-condition breakdown
5. Use keyboard shortcuts to review quickly:
   - `A` — Approve the AI grade
   - `F` — Flag for instructor review
   - `0-9` — Set an override score, then `Enter` to confirm

---

## Architecture Decisions

**Why Supabase?** Single platform for auth, database, storage, realtime, and vector search — eliminates the need for separate services like MinIO, ChromaDB, and custom WebSockets.

**Why LangGraph?** Grading is a multi-step pipeline (parse rubric → evaluate → check plagiarism → write result). LangGraph makes the state transitions explicit and debuggable rather than tangling them in a single function.

**Why Celery + Redis?** PDF processing and LLM calls are slow (5–90 seconds each). Celery decouples them from the HTTP request cycle so the frontend stays responsive. Two separate queues (`ocr` and `grading`) allow independent scaling.

**Why sentence-transformers for plagiarism?** `all-MiniLM-L6-v2` is fast, lightweight, and produces 384-dimensional embeddings that work well for short answer similarity. pgvector handles the cosine similarity search natively in PostgreSQL, avoiding an external vector DB.

---

## Limitations & Future Work

- **OCR accuracy** — Groq Vision works well for neat handwriting; production use would benefit from Qwen2-VL-7B on GPU (code included, commented out in `worker/ocr/vision.py`)
- **Region detection** — Current heuristic divides pages into equal horizontal bands; a layout detection model (LayoutLM) would handle complex exam formats
- **Single question per page** — multi-question pages are partially supported but not fully tested
- **No email notifications** — TAs must check the dashboard manually; Supabase Edge Functions could trigger emails

---

## License

MIT
