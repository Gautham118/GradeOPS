create table exams (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  subject text,
  rubric_json jsonb not null,  -- {"questions": [{"id": "q1", "text": "...", "max_marks": 10, "conditions": [...]}]}
  created_by uuid references profiles(id),
  created_at timestamptz default now()
);
