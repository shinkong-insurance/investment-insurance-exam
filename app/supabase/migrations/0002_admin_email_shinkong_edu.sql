-- app/supabase/migrations/0002_admin_email_shinkong_edu.sql
-- 使用者決策（2026-10-06）：管理員 Auth 帳號改為 admin@shinkong.edu.tw，
-- 取代 0001 寫死的 admin@skl.com.tw。
-- 本檔重建 0001 的兩條管理員 policy（指令/角色/結構與 0001 相同，只換 email）。
-- 套用後 admin@skl.com.tw 不再具有任何管理員權限（students 讀寫、license_keys 寫入）。
-- 0001 已套用到線上 DB，故保持原樣不改；此檔為增量。

drop policy if exists students_admin_all on public.students;
create policy students_admin_all on public.students
  for all to authenticated
  using ((auth.jwt() ->> 'email') = 'admin@shinkong.edu.tw')
  with check ((auth.jwt() ->> 'email') = 'admin@shinkong.edu.tw');

drop policy if exists license_keys_admin_write on public.license_keys;
create policy license_keys_admin_write on public.license_keys
  for all to authenticated
  using ((auth.jwt() ->> 'email') = 'admin@shinkong.edu.tw')
  with check ((auth.jwt() ->> 'email') = 'admin@shinkong.edu.tw');
