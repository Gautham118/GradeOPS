-- Profiles: users can only read their own
alter table profiles enable row level security;
create policy "Own profile" on profiles for all using (auth.uid() = id);

-- Exams: instructors can insert, everyone can read
alter table exams enable row level security;
create policy "Instructors insert exams" on exams for insert
  using ((select role from profiles where id = auth.uid()) = 'instructor');
create policy "All read exams" on exams for select using (true);

-- Submissions: instructors manage, TAs read
-- alter table submissions enable row level security;              -- Claude added this, but it's not needed
-- create policy "Instructors manage submissions" on submissions for all
--   using ((select role from profiles where id = auth.uid()) = 'instructor');

alter table submissions enable row level security;

create policy "Instructors read submissions"
on submissions for select
using ((select role from profiles where id = auth.uid()) = 'instructor');

create policy "Instructors insert submissions"
on submissions for insert
with check ((select role from profiles where id = auth.uid()) = 'instructor');

create policy "Instructors update submissions"
on submissions for update
using ((select role from profiles where id = auth.uid()) = 'instructor');

create policy "TAs read submissions" on submissions for select
  using ((select role from profiles where id = auth.uid()) = 'ta');

-- Grades: TAs can read and update (HITL actions), backend worker uses service role (bypasses RLS)
alter table grades enable row level security;
create policy "TAs read grades" on grades for select using (true);
create policy "TAs update grades" on grades for update
  using ((select role from profiles where id = auth.uid()) = 'ta');
