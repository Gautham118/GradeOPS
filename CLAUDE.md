# CLAUDE.md — GradeOps

> **Purpose**: This file is the single source of truth for AI coding agents building GradeOps.
> Read it fully before writing any code. Every architectural decision, constraint, and convention
> documented here must be respected in all generated code.

---

## 1. Project Overview

**GradeOps** is a Human-in-the-Loop (HITL) exam grading pipeline that automates the grading of
handwritten exam PDFs using Vision-Language Models (VLMs) and LLM-based rubric evaluation,
with a real-time TA review dashboard for human oversight and correction.

### Core User Roles
| Role | Capabilities |
|------|-------------|
| `instructor` | Create exams, define rubrics, upload bulk PDFs, view final grades |
| `ta` | Review AI-generated grades in queue, approve/override/flag, cannot create exams |

### High-Level Flow
```
Instructor uploads PDFs
        ↓
Celery OCR worker (PyMuPDF + Qwen2-VL) extracts & transcribes answer crops
        ↓
Celery grading worker (LangGraph + Groq LLM) scores each answer against rubric
        ↓
Grades land in Supabase → Realtime pushes to TA dashboard
        ↓
TA reviews AI grade (crop image + score + breakdown) → Approve / Override / Flag
        ↓
Final grades locked in DB
```

---

## 2. Repository Structure

```
gradeops/
├── docker-compose.yml          # Orchestrates api, worker-ocr, worker-grading, redis, frontend
├── .env.example                # Template for all required env vars
├── README.md
│
├── backend/                    # FastAPI application
│   ├── main.py                 # App factory, CORS middleware, router registration
│   ├── requirements.txt
│   ├── Dockerfile
│   │
│   ├── core/
│   │   ├── config.py           # Pydantic Settings, Supabase client singletons
│   │   ├── auth.py             # JWT decode via python-jose (Supabase JWT secret)
│   │   └── deps.py             # require_role() FastAPI Dependency
│   │
│   ├── routers/
│   │   ├── exams.py            # POST /exams (instructor only), GET /exams
│   │   ├── submissions.py      # POST /submissions/bulk (multipart, instructor only)
│   │   └── grades.py           # GET /grades, PATCH /grades/:id (TA only for PATCH)
│   │
│   ├── schemas/
│   │   ├── exam.py             # ExamCreate, ExamOut (Pydantic v2)
│   │   ├── submission.py       # SubmissionOut
│   │   └── grade.py            # GradeOut, TAOverride
│   │
│   └── worker/
│       ├── celery_app.py       # Celery instance + task routing
│       ├── tasks.py            # run_ocr_task, run_grading_task (Celery task wrappers)
│       │
│       ├── ocr/
│       │   ├── pipeline.py     # Orchestrates: fetc h PDF → pages → crops → VLM → DB
│       │   ├── pdf_utils.py    # PyMuPDF: PDF bytes → list of PIL Images (2x zoom)
│       │   └── crop_utils.py   # Heuristic region detector; returns list of {question_id, bbox}
│       │
│       └── grading/
│           ├── graph.py        # LangGraph StateGraph definition and runner
│           ├── nodes.py        # parse_rubric, evaluate_partial_credit, check_plagiarism, write_result
│           ├── prompts.py      # All LLM system prompts as module-level constants
│           └── embedder.py     # sentence-transformers → pgvector similarity search
│
├── frontend/                   # React + Vite application
│   ├── package.json
│   ├── index.html
│   ├── Dockerfile
│   └── src/
│       ├── main.jsx            # React root, BrowserRouter
│       ├── supabaseClient.js   # createClient() singleton (anon key)
│       │
│       ├── pages/
│       │   ├── Login.jsx       # Supabase Auth UI component
│       │   ├── Dashboard.jsx   # Role-aware landing (redirects by role)
│       │   ├── ExamUpload.jsx  # Rubric builder + PDF multi-file dropzone
│       │   └── ReviewQueue.jsx # TA grading dashboard (main HITL interface)
│       │
│       ├── components/
│       │   ├── GradeCard.jsx        # Crop image + AI score + breakdown accordion + action buttons
│       │   ├── RubricEditor.jsx     # Dynamic form: add/remove rubric conditions with marks
│       │   ├── KeyboardHints.jsx    # Floating overlay showing A/F/0-9/Enter shortcuts
│       │   └── ProtectedRoute.jsx   # Checks session + role, redirects if unauthorized
│       │
│       └── hooks/
│           ├── useSession.js          # Supabase onAuthStateChange wrapper
│           └── useRealtimeGrades.js   # Supabase Realtime subscription + initial fetch
│
└── supabase/
    └── migrations/
        ├── 001_create_profiles.sql
        ├── 002_create_exams.sql
        ├── 003_create_submissions.sql
        ├── 004_create_grades.sql
        ├── 005_rls_policies.sql
        └── 006_pgvector_embeddings.sql
```

---

## 3. Technology Stack

### Backend
| Layer | Technology | Version / Notes |
|-------|-----------|-----------------|
| Web framework | FastAPI | Latest stable |
| ASGI server | Uvicorn | |
| Auth | python-jose (JWT decode) | Supabase HS256 JWT secret |
| DB / Storage | supabase-py | Admin client + Anon client |
| Task queue | Celery | Two separate queues: `ocr`, `grading` |
| Message broker | Redis | `redis://localhost:6379/0` |
| PDF processing | PyMuPDF (fitz) | 2x matrix zoom for OCR quality |
| Image processing | Pillow | Crop manipulation |
| VLM (OCR) | Qwen2-VL-7B-Instruct | via `transformers` on GPU; swap to Groq vision for local dev |
| LLM (grading) | Groq API | `llama-3.3-70b-versatile` or `mixtral-8x7b-32768` |
| Agent framework | LangGraph | `StateGraph` with typed state |
| Embeddings | sentence-transformers | `all-MiniLM-L6-v2` → pgvector |
| Schema validation | Pydantic v2 | `pydantic-settings` for env loading |

### Frontend
| Layer | Technology | Notes |
|-------|-----------|-------|
| Framework | React 18 | Functional components, hooks only |
| Build tool | Vite | `npm create vite@latest . -- --template react` |
| Routing | react-router-dom v6 | |
| Auth UI | @supabase/auth-ui-react | Login page |
| Supabase client | @supabase/supabase-js | v2 |
| Realtime | Supabase Realtime (postgres_changes) | INSERT on grades table |
| Styling | Tailwind CSS | Utility-first; add via `npm install -D tailwindcss` |

### Infrastructure
| Component | Technology |
|-----------|-----------|
| Database | Supabase (PostgreSQL 15) |
| Storage | Supabase Storage (two buckets) |
| Auth | Supabase Auth |
| Realtime | Supabase Realtime |
| Vector search | pgvector extension |
| Container orchestration | Docker Compose (local dev) |

---

## 4. Environment Variables

All variables are loaded via `core/config.py` using `pydantic-settings`. Create `.env` in
`backend/` during development.

```env
# Supabase
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=<anon-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
SUPABASE_JWT_SECRET=<jwt-secret>           # Settings → API → JWT Secret

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM APIs
GROQ_API_KEY=<groq-api-key>
OPENAI_API_KEY=<optional-fallback>

# Frontend (Vite — prefix with VITE_)
VITE_SUPABASE_URL=https://<project-ref>.supabase.co
VITE_SUPABASE_ANON_KEY=<anon-key>
```

> **Agent rule**: Never hardcode secrets. Always reference `settings.<VAR_NAME>` in backend code
> and `import.meta.env.VITE_<VAR>` in frontend code.

---

## 5. Database Schema

Run migrations in strict order (001 → 006) via Supabase SQL editor.

### 001_create_profiles.sql
```sql
-- Extends Supabase Auth users with a role
create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  role text not null check (role in ('instructor', 'ta')),
  full_name text,
  created_at timestamptz default now()
);

-- Auto-create profile on signup
create or replace function handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into profiles (id, email, role)
  values (new.id, new.email, 'ta');  -- default role; instructor must be set manually
  return new;
end;
$$;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure handle_new_user();
```

### 002_create_exams.sql
```sql
create table exams (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  subject text,
  rubric_json jsonb not null,  -- {"questions": [{"id": "q1", "text": "...", "max_marks": 10, "conditions": [...]}]}
  created_by uuid references profiles(id),
  created_at timestamptz default now()
);
```

### 003_create_submissions.sql
```sql
create table submissions (
  id uuid primary key default gen_random_uuid(),
  exam_id uuid references exams(id) on delete cascade,
  student_name text not null,
  pdf_path text not null,  -- Supabase Storage path: exam-pdfs/<path>
  status text default 'uploaded' check (status in ('uploaded', 'processing', 'ocr_complete', 'graded')),
  uploaded_by uuid references profiles(id),
  created_at timestamptz default now()
);
```

### 004_create_grades.sql
```sql
create table grades (
  id uuid primary key default gen_random_uuid(),
  submission_id uuid references submissions(id) on delete cascade,
  exam_id uuid references exams(id),          -- denormalized for efficient querying
  question_id text not null,                  -- matches rubric_json question id
  transcription text,                         -- Qwen-VL output
  crop_url text,                              -- Supabase Storage path: answer-crops/<path>
  ai_score integer,
  max_marks integer,
  breakdown jsonb,                            -- [{condition, awarded, marks_given, reason}]
  justification text,
  ai_model_used text,
  status text default 'pending_review'
    check (status in ('ocr_complete', 'pending_review', 'approved', 'overridden', 'flagged')),
  ta_score integer,                           -- set on override
  ta_note text,
  reviewed_by uuid references profiles(id),
  reviewed_at timestamptz,
  plagiarism_flag boolean default false,
  embedding vector(384),                      -- sentence-transformers all-MiniLM-L6-v2
  created_at timestamptz default now()
);
create index on grades (exam_id, status);
create index on grades using ivfflat (embedding vector_cosine_ops);
```

### 005_rls_policies.sql
```sql
-- Profiles: users can only read their own
alter table profiles enable row level security;
create policy "Own profile" on profiles for all using (auth.uid() = id);

-- Exams: instructors can insert, everyone can read
alter table exams enable row level security;
create policy "Instructors insert exams" on exams for insert
  using ((select role from profiles where id = auth.uid()) = 'instructor');
create policy "All read exams" on exams for select using (true);

-- Submissions: instructors manage, TAs read
alter table submissions enable row level security;
create policy "Instructors manage submissions" on submissions for all
  using ((select role from profiles where id = auth.uid()) = 'instructor');
create policy "TAs read submissions" on submissions for select
  using ((select role from profiles where id = auth.uid()) = 'ta');

-- Grades: TAs can read and update (HITL actions), backend worker uses service role (bypasses RLS)
alter table grades enable row level security;
create policy "TAs read grades" on grades for select using (true);
create policy "TAs update grades" on grades for update
  using ((select role from profiles where id = auth.uid()) = 'ta');
```

### 006_pgvector_embeddings.sql
```sql
create extension if not exists vector;
-- The embedding column is already added in 004; this migration just ensures the extension exists
-- and creates the HNSW index for production (more accurate than IVFFlat for small datasets)
create index if not exists grades_embedding_hnsw
  on grades using hnsw (embedding vector_cosine_ops);
```

### Storage Buckets
Create these manually in Supabase Dashboard → Storage:
- `exam-pdfs` — **Private** (access via service role only)
- `answer-crops` — **Authenticated** (TA frontend needs to display crop images)

---

## 6. Backend Implementation Details

### core/config.py — Critical Rules
- Initialize **two** Supabase clients:
  - `supabase_admin` using `SERVICE_ROLE_KEY` → bypasses RLS, used **only** in Celery workers
  - `supabase_anon` using `ANON_KEY` → respects RLS, used in FastAPI routes
- Never use `supabase_admin` inside HTTP request handlers

```python
from supabase import create_client, Client
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str
    REDIS_URL: str = "redis://localhost:6379/0"
    GROQ_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
supabase_admin: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
supabase_anon: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
```

### core/auth.py — JWT Verification
- Supabase issues HS256 JWTs signed with the project's JWT secret
- Decode with `python-jose`, extract `sub` (user UUID) and role from `user_metadata`
- The role is stored in the `profiles` table and should be fetched once and added to the token
  via Supabase's `auth.users` raw_user_meta_data, or looked up in `profiles` on each request

```python
from jose import jwt, JWTError
from fastapi import HTTPException, Header
from core.config import settings

async def get_current_user(authorization: str = Header(...)) -> dict:
    try:
        token = authorization.removeprefix("Bearer ")
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}  # Supabase JWTs have no audience by default
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
```

### core/deps.py — Role-Based Access
```python
from fastapi import Depends, HTTPException
from core.auth import get_current_user
from core.config import supabase_admin

def require_role(*allowed_roles: str):
    async def checker(user: dict = Depends(get_current_user)):
        user_id = user.get("sub")
        profile = supabase_admin.table("profiles").select("role").eq("id", user_id).single().execute()
        if profile.data["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return {**user, "role": profile.data["role"]}
    return checker
```

### routers/exams.py
- `POST /exams` — `Depends(require_role("instructor"))`, insert into `exams` table
- `GET /exams` — `Depends(get_current_user)`, returns all exams (both roles)
- Request body: `ExamCreate(title, subject, rubric_json)` where `rubric_json` schema:

```json
{
  "questions": [
    {
      "id": "q1",
      "text": "Explain Newton's second law",
      "max_marks": 10,
      "conditions": [
        {"text": "Mentions F = ma", "marks": 3},
        {"text": "Provides real-world example", "marks": 3},
        {"text": "Correct units stated", "marks": 4}
      ]
    }
  ]
}
```

### routers/submissions.py
- `POST /submissions/bulk` — `Depends(require_role("instructor"))`
- Accept: `multipart/form-data` with `exam_id: str` + `files: List[UploadFile]`
- For each file:
  1. Read bytes with `await file.read()`
  2. Upload to `exam-pdfs/{exam_id}/{uuid}.pdf` via `supabase_admin.storage`
  3. Insert `submissions` record with status `uploaded`
  4. Enqueue `run_ocr_task.delay(submission_id)`
- Return list of created submission IDs

### routers/grades.py
- `GET /grades` — query params: `exam_id`, `status` (default `pending_review`), `page`, `limit`
- `PATCH /grades/{id}` — `Depends(require_role("ta"))`, body: `TAOverride`

```python
class TAOverride(BaseModel):
    action: Literal["approve", "override", "flag"]
    ta_score: Optional[int] = None   # required when action == "override"
    ta_note: Optional[str] = None
```

- On approve: `status = "approved"`, `reviewed_by = user_id`, `reviewed_at = now()`
- On override: `status = "overridden"`, `ta_score = body.ta_score`
- On flag: `status = "flagged"` (signals instructor to re-examine)

---

## 7. Celery Worker Details

### Task Routing
```python
# worker/celery_app.py
celery.conf.task_routes = {
    "worker.tasks.run_ocr_task": {"queue": "ocr"},
    "worker.tasks.run_grading_task": {"queue": "grading"},
}
```

Start two separate worker processes:
```bash
celery -A worker.celery_app worker -Q ocr -c 2 --loglevel=info
celery -A worker.celery_app worker -Q grading -c 4 --loglevel=info
```

### worker/ocr/pipeline.py — Detailed Steps
1. Fetch `submissions` record using `submission_id` via `supabase_admin`
2. Fetch the parent `exams` record to get `rubric_json`
3. Download PDF bytes: `supabase_admin.storage.from_("exam-pdfs").download(sub["pdf_path"])`
4. Open with `fitz.open(stream=pdf_bytes, filetype="pdf")`
5. For each page: render at 2x zoom (`fitz.Matrix(2, 2)`) → convert to PIL Image
6. Call `detect_question_regions(img, rubric_json, page_num)` → list of `{question_id, bbox}`
7. For each crop region:
   a. `img.crop(bbox)` → save as JPEG bytes
   b. Call VLM transcription (see below)
   c. Upload crop to `answer-crops/{submission_id}/{question_id}.jpg`
   d. Insert `grades` record: `{submission_id, exam_id, question_id, transcription, crop_url, status: "ocr_complete"}`
   e. Enqueue `run_grading_task.delay(grade_id)`
8. Update `submissions.status = "processing"`

### VLM Transcription Strategy
- **GPU environment (Colab/Kaggle/production)**: Use `transformers` + Qwen2-VL-7B-Instruct
- **Local dev**: Use Groq vision API (faster, no GPU needed):

```python
def qwen_vl_transcribe(crop_img: Image.Image) -> str:
    """Transcribe handwritten answer crop to text."""
    # Convert PIL Image to base64
    buffer = io.BytesIO()
    crop_img.save(buffer, format="JPEG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode()

    # Local dev: Groq vision
    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",  # Groq vision model
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                {"type": "text", "text": "Transcribe this handwritten exam answer exactly as written. Output only the transcription, nothing else."}
            ]
        }],
        max_tokens=500
    )
    return response.choices[0].message.content
```

### worker/ocr/crop_utils.py — Region Detection
The heuristic approach divides pages based on rubric structure:
- If rubric has N questions and PDF has P pages: assign `ceil(N/P)` questions per page
- Divide each page image into equal horizontal bands (one per question)
- Return bounding boxes as `(left, top, right, bottom)` in pixel coords
- For production: replace with a layout detection model (LayoutLM or simple line detection)

```python
def detect_question_regions(img: Image.Image, rubric_json: dict, page_num: int) -> list[dict]:
    questions = rubric_json.get("questions", [])
    width, height = img.size
    questions_per_page = max(1, len(questions) // max(1, page_num + 1))
    start_idx = page_num * questions_per_page

    regions = []
    for i in range(questions_per_page):
        q_idx = start_idx + i
        if q_idx >= len(questions):
            break
        top = int((i / questions_per_page) * height)
        bottom = int(((i + 1) / questions_per_page) * height)
        regions.append({
            "question_id": questions[q_idx]["id"],
            "bbox": (0, top, width, bottom)
        })
    return regions
```

---

## 8. LangGraph Grading Agent

### State Schema
```python
from typing import TypedDict, Optional

class GradeState(TypedDict):
    grade_id: str
    transcription: str
    rubric: dict           # Single question rubric object from exam's rubric_json
    ai_score: int
    max_marks: int
    breakdown: list        # [{condition, awarded, marks_given, reason}]
    justification: str
    plagiarism_flag: bool
    similar_answers: list  # From pgvector search
```

### Graph Topology
```
parse_rubric → evaluate_partial_credit → check_plagiarism → write_result → END
```

### Node Implementations

**parse_rubric** — Fetches grade + rubric from DB, populates state:
```python
def parse_rubric(state: GradeState) -> GradeState:
    grade = supabase_admin.table("grades").select("*, submissions(exam_id)").eq("id", state["grade_id"]).single().execute().data
    exam = supabase_admin.table("exams").select("rubric_json").eq("id", grade["submissions"]["exam_id"]).single().execute().data
    rubric_questions = exam["rubric_json"]["questions"]
    rubric = next(q for q in rubric_questions if q["id"] == grade["question_id"])
    return {**state, "transcription": grade["transcription"], "rubric": rubric, "max_marks": rubric["max_marks"]}
```

**evaluate_partial_credit** — Core LLM grading call:
```python
def evaluate_partial_credit(state: GradeState) -> GradeState:
    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    user_prompt = f"""
STUDENT ANSWER:
{state['transcription']}

RUBRIC:
Question: {state['rubric']['text']}
Max marks: {state['rubric']['max_marks']}
Conditions:
{json.dumps(state['rubric']['conditions'], indent=2)}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": GRADING_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=800,
        temperature=0.1  # Low temperature for consistent grading
    )
    result = json.loads(response.choices[0].message.content)
    return {**state, "ai_score": result["awarded_marks"], "breakdown": result["breakdown"], "justification": result["justification"]}
```

**check_plagiarism** — pgvector similarity search:
```python
def check_plagiarism(state: GradeState) -> GradeState:
    from worker.grading.embedder import embed_text, find_similar
    embedding = embed_text(state["transcription"])
    similar = find_similar(embedding, state["grade_id"], threshold=0.92)
    return {**state, "plagiarism_flag": len(similar) > 0, "similar_answers": similar}
```

**write_result** — Persists to DB:
```python
def write_result(state: GradeState) -> GradeState:
    supabase_admin.table("grades").update({
        "ai_score": state["ai_score"],
        "max_marks": state["max_marks"],
        "breakdown": state["breakdown"],
        "justification": state["justification"],
        "plagiarism_flag": state["plagiarism_flag"],
        "ai_model_used": "llama-3.3-70b-versatile",
        "status": "pending_review",
        "embedding": state.get("embedding")  # stored for future similarity searches
    }).eq("id", state["grade_id"]).execute()
    return state
```

### prompts.py
```python
GRADING_SYSTEM_PROMPT = """
You are a strict academic grader. You will be given a student's handwritten answer (transcribed) and a rubric with conditions.

For each rubric condition, decide:
- awarded: true/false
- marks_given: integer
- reason: one sentence

Respond ONLY with valid JSON in this exact format:
{
  "awarded_marks": <int>,
  "max_marks": <int>,
  "breakdown": [
    {"condition": "<str>", "awarded": <bool>, "marks_given": <int>, "reason": "<str>"}
  ],
  "justification": "<2-3 sentence overall justification>"
}

Do not output anything before or after the JSON. Do not use markdown code blocks.
"""
```

### embedder.py
```python
from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embed_text(text: str) -> list[float]:
    return get_model().encode(text).tolist()

def find_similar(embedding: list[float], exclude_grade_id: str, threshold: float = 0.92) -> list[dict]:
    # Use Supabase RPC for vector similarity search
    result = supabase_admin.rpc("find_similar_answers", {
        "query_embedding": embedding,
        "similarity_threshold": threshold,
        "exclude_id": exclude_grade_id
    }).execute()
    return result.data or []
```

Add this function to Supabase via SQL editor:
```sql
create or replace function find_similar_answers(
  query_embedding vector(384),
  similarity_threshold float,
  exclude_id uuid
)
returns table (grade_id uuid, similarity float) language sql as $$
  select id as grade_id, 1 - (embedding <=> query_embedding) as similarity
  from grades
  where id != exclude_id
    and embedding is not null
    and 1 - (embedding <=> query_embedding) > similarity_threshold;
$$;
```

---

## 9. Frontend Implementation Details

### supabaseClient.js
```javascript
import { createClient } from "@supabase/supabase-js"

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)
```

### hooks/useSession.js
```javascript
import { useEffect, useState } from "react"
import { supabase } from "../supabaseClient"

export function useSession() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setLoading(false)
    })
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
    })
    return () => subscription.unsubscribe()
  }, [])

  return { session, loading }
}
```

### hooks/useRealtimeGrades.js
```javascript
import { useEffect, useState } from "react"
import { supabase } from "../supabaseClient"

export function useRealtimeGrades(examId) {
  const [grades, setGrades] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!examId) return

    // Initial fetch of pending grades
    supabase
      .from("grades")
      .select("*, submissions(student_name)")
      .eq("exam_id", examId)
      .eq("status", "pending_review")
      .order("created_at", { ascending: true })
      .then(({ data, error }) => {
        if (!error) setGrades(data || [])
        setLoading(false)
      })

    // Subscribe to new grades arriving from grading worker
    const channel = supabase
      .channel(`grades-${examId}`)
      .on("postgres_changes", {
        event: "INSERT",
        schema: "public",
        table: "grades",
        filter: `exam_id=eq.${examId}`
      }, (payload) => {
        if (payload.new.status === "pending_review") {
          setGrades(prev => [...prev, payload.new])
        }
      })
      .subscribe()

    return () => supabase.removeChannel(channel)
  }, [examId])

  return { grades, loading, setGrades }
}
```

### pages/ReviewQueue.jsx — Keyboard Shortcuts
```javascript
useEffect(() => {
  const handleKeyDown = (e) => {
    if (!currentGrade) return
    if (e.key === "a" || e.key === "A") handleAction("approve")
    if (e.key === "f" || e.key === "F") handleAction("flag")
    if (e.key >= "0" && e.key <= "9") setOverrideScore(parseInt(e.key))
    if (e.key === "Enter" && overrideScore !== null) handleAction("override", overrideScore)
  }
  window.addEventListener("keydown", handleKeyDown)
  return () => window.removeEventListener("keydown", handleKeyDown)
}, [currentGrade, overrideScore])
```

The `handleAction` function fires `PATCH /grades/:id` to the FastAPI backend with the bearer
token from the Supabase session, then removes the graded card from the local queue state.

### components/GradeCard.jsx — Required Props
```typescript
interface GradeCardProps {
  grade: {
    id: string
    crop_url: string          // Supabase Storage path → generate signed URL
    transcription: string
    ai_score: number
    max_marks: number
    breakdown: Array<{condition: string, awarded: boolean, marks_given: number, reason: string}>
    justification: string
    plagiarism_flag: boolean
    submissions: { student_name: string }
  }
  onApprove: (id: string) => void
  onOverride: (id: string, score: number, note: string) => void
  onFlag: (id: string) => void
}
```

To display crop images from private storage, generate signed URLs:
```javascript
const { data } = await supabase.storage
  .from("answer-crops")
  .createSignedUrl(grade.crop_url, 3600)  // 1-hour expiry
```

### components/ProtectedRoute.jsx
```javascript
export function ProtectedRoute({ children, requiredRole }) {
  const { session, loading } = useSession()
  const [role, setRole] = useState(null)

  useEffect(() => {
    if (session) {
      supabase.from("profiles").select("role").eq("id", session.user.id).single()
        .then(({ data }) => setRole(data?.role))
    }
  }, [session])

  if (loading) return <div>Loading...</div>
  if (!session) return <Navigate to="/login" />
  if (requiredRole && role !== requiredRole) return <Navigate to="/dashboard" />
  return children
}
```

---

## 10. Docker Compose Configuration

```yaml
version: "3.9"

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      redis:
        condition: service_healthy
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app  # Hot reload in dev

  worker-ocr:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A worker.celery_app worker -Q ocr -c 2 --loglevel=info
    env_file: .env
    depends_on:
      redis:
        condition: service_healthy

  worker-grading:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A worker.celery_app worker -Q grading -c 4 --loglevel=info
    env_file: .env
    depends_on:
      redis:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    environment:
      - VITE_SUPABASE_URL=${VITE_SUPABASE_URL}
      - VITE_SUPABASE_ANON_KEY=${VITE_SUPABASE_ANON_KEY}
    command: npm run dev -- --host 0.0.0.0
```

### backend/Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### frontend/Dockerfile
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

---

## 11. requirements.txt

```txt
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
supabase>=2.4.0
python-jose[cryptography]>=3.3.0
pydantic-settings>=2.2.0
celery>=5.3.6
redis>=5.0.3
pymupdf>=1.24.0
pillow>=10.3.0
sentence-transformers>=3.0.0
langchain>=0.2.0
langgraph>=0.1.0
groq>=0.9.0
openai>=1.30.0
python-multipart>=0.0.9
```

---

## 12. API Specification

### Authentication
All requests require: `Authorization: Bearer <supabase-jwt-token>`

### Endpoints

| Method | Path | Role | Description |
|--------|------|------|-------------|
| POST | `/exams` | instructor | Create exam with rubric |
| GET | `/exams` | any | List all exams |
| GET | `/exams/{id}` | any | Get single exam with rubric |
| POST | `/submissions/bulk` | instructor | Upload multiple PDF files |
| GET | `/submissions?exam_id=` | any | List submissions for exam |
| GET | `/grades?exam_id=&status=&page=&limit=` | any | Paginated grade queue |
| GET | `/grades/{id}` | any | Single grade detail |
| PATCH | `/grades/{id}` | ta | HITL action: approve/override/flag |
| GET | `/health` | none | `{"status": "ok"}` |

---

## 13. Coding Conventions & Rules for Agents

1. **Schema validation**: Use Pydantic v2 models for all request/response bodies. Import from `pydantic`, not `pydantic.v1`.

2. **Async vs sync**: FastAPI route handlers must be `async def`. Supabase-py is synchronous — call it normally (no `await`). Celery task functions must be regular `def` (not async).

3. **Error handling in routes**: Wrap DB operations in try/except; raise `HTTPException` with appropriate status codes. Never expose raw exception messages to clients.

4. **Error handling in workers**: Celery tasks must catch all exceptions, log them, and update the relevant `submissions` or `grades` record with a `failed` status rather than crashing silently.

5. **Supabase client selection**:
   - `supabase_admin` → Celery workers only
   - `supabase_anon` → FastAPI route handlers only
   - Never cross these boundaries

6. **LLM JSON parsing**: Always wrap `json.loads(llm_response)` in try/except. If parsing fails, retry once with a clarifying prompt, then fall back to a default zero-score result with `justification = "LLM parse error"`.

7. **Storage paths**: Use consistent path format: `exam-pdfs/{exam_id}/{submission_id}.pdf` and `answer-crops/{submission_id}/{question_id}.jpg`.

8. **Frontend API calls**: All backend calls from frontend must:
   - Include `Authorization: Bearer ${session.access_token}` header
   - Use `VITE_API_BASE_URL` env var (default `http://localhost:8000`)
   - Handle 401 by redirecting to `/login`

9. **React state**: Do not use class components. Use only functional components with hooks. No Redux — Supabase Realtime + useState is sufficient.

10. **No placeholder UI**: Every UI component must be functional and wired to real data or real API calls. No hardcoded mock data in production code (stubs are acceptable only in dev mode behind an env flag).

---

## 14. Build Order for Agents

Implement in this exact sequence to avoid dependency failures:

1. **DB migrations** (001 → 006) + Supabase bucket creation
2. **`core/config.py`** — Settings + Supabase client singletons
3. **`core/auth.py`** + **`core/deps.py`** — Auth foundation
4. **Pydantic schemas** — All schema files before any routers
5. **`routers/exams.py`** — Simplest router, no ML dependency
6. **`routers/submissions.py`** — Stub Celery call initially
7. **`routers/grades.py`** — HITL action endpoint
8. **`main.py`** — Wire everything together, verify `/health` returns 200
9. **`worker/celery_app.py`** + **`worker/tasks.py`** — Task wiring
10. **`worker/ocr/pdf_utils.py`** → **`crop_utils.py`** → **`pipeline.py`**
11. **`worker/grading/prompts.py`** → **`embedder.py`** → **`nodes.py`** → **`graph.py`**
12. **Frontend**: `supabaseClient.js` → `useSession.js` → `Login.jsx` → `ProtectedRoute.jsx` → `useRealtimeGrades.js` → `GradeCard.jsx` → `ReviewQueue.jsx` → `ExamUpload.jsx` → `Dashboard.jsx`
13. **Docker Compose** — Integration test with all services running

---

## 15. Demo Checklist

The demo must show this sequence to be compelling:

- [ ] Instructor logs in → sees dashboard with role-appropriate nav
- [ ] Instructor creates an exam with a 3-question rubric via `ExamUpload.jsx`
- [ ] Instructor uploads 10 handwritten answer PDFs (bulk upload)
- [ ] Live: Celery processes submissions → TA dashboard starts populating in real-time (Supabase Realtime)
- [ ] TA view: GradeCards appear with crop image, AI score, and breakdown
- [ ] TA uses keyboard shortcut `A` to approve a correct grade instantly
- [ ] TA uses number key + `Enter` to override an incorrect AI score
- [ ] TA uses `F` to flag a suspected plagiarism case
- [ ] Final grades table shows mix of `approved`, `overridden`, `flagged` statuses

**Demo data**: 10 handwritten answer sheets (write 3–4 variations of good/partial/wrong answers, photograph on phone, convert to PDF). Prepare rubric JSON before the demo and save it.
