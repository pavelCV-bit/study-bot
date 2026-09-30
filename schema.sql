-- Выполни один раз в Supabase: SQL Editor -> New query -> вставить -> Run
create table if not exists study_tasks (
  id bigint generated always as identity primary key,
  title text not null,
  deadline date,
  note text,
  done boolean not null default false,
  last_reminded_on date,
  created_at timestamptz not null default now()
);

-- Закрываем таблицу от публичного доступа. Бот ходит в неё секретным ключом.
alter table study_tasks enable row level security;
