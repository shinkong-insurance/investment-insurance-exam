-- Mirrored from the remote migration history (created outside this repo on 2026-10-06 02:33 UTC).
-- Kept verbatim so local and remote migration history match.
create or replace function public.keepalive()
returns timestamptz
language sql
stable
set search_path = ''
as $$ select now() $$;

revoke execute on function public.keepalive() from public;
grant execute on function public.keepalive() to anon, authenticated, service_role;
