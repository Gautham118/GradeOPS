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
