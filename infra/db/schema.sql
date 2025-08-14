create extension if not exists pg_trgm;
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  display_name text,
  created_at timestamptz default now()
);
create table if not exists listings (
  id uuid primary key default gen_random_uuid(),
  owner uuid references users(id),
  title text not null,
  description text,
  category text check (category in ('sports','yugioh','pokemon','idol')),
  sport text,
  year int,
  base text,
  card_type text,
  set_name text,
  grade text,
  is_verified boolean default false,
  price numeric,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
create index if not exists listings_search_idx on listings using gin ((coalesce(title,'') || ' ' || coalesce(description,'') || ' ' || coalesce(set_name,'')) gin_trgm_ops);
