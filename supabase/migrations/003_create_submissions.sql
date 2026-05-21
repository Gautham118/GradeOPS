create table submissions (
  id uuid primary key default gen_random_uuid(),
  exam_id uuid references exams(id) on delete cascade,
  student_name text not null,
  pdf_path text not null,  -- Supabase Storage path: exam-pdfs/<path>
  status text default 'uploaded' check (status in ('uploaded', 'processing', 'ocr_complete', 'graded')),
  uploaded_by uuid references profiles(id),
  created_at timestamptz default now()
);
