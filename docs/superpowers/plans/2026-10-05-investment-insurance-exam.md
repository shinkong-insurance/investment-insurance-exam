# 投資型保險考照網站 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `insurance-exam-app` 複製成新專案 `investment-insurance-exam`，換上投資型保險的 10 章內容與第一科/第二科科目模考，沿用 `currency-insurance-exam` 的 `#/lk`（姓名/單位/員編）授權變體，部署到獨立的 Supabase 專案與 GitHub Pages。

**Architecture:** Flutter Web app，靜態 JSON 題庫（不進 Supabase），`courseId = chapterId ~/ 100` 慣例。10 個真實章節為 `chapterId 101-110`（出現在一般章節列表）；第一科/第二科模考題目直接打 `chapterId 201/202` 標籤進 `questions.json`，**不**建對應的 `chapters.json` 條目（章節列表只讀 `chapters.json`，不會自動顯示沒有條目的 chapterId，零額外過濾程式碼）。Supabase 只管授權（`license_keys`/`key_sessions`/`students`）與作答紀錄同步（`key_favorites`/`key_wrong_answers`/`study_logs`），不存題目內容。

**Tech Stack:** Flutter (Dart) web, Riverpod, go_router, Supabase (Postgres + Edge Functions, Deno/TypeScript), Python 3（題庫解析腳本，標準庫 `zipfile`/`xml.etree` 讀 xlsx，不依賴 `openpyxl`）。

**Spec:** `docs/superpowers/specs/2026-10-05-investment-insurance-exam-design.md`

## Global Constraints

- GitHub repo：`shinkong-insurance/investment-insurance-exam`，Public，`main` 放原始碼、`gh-pages` 放 build 產物
- `pubspec.yaml`：`name: investment_insurance_exam`，`description: 投資型保險商品業務員資格測驗學習APP`
- GitHub Pages base href：`/investment-insurance-exam/`
- localStorage 鍵值前綴：`inv_`（避免跟同網域下 `insurance-exam-app` 無前綴、`currency-insurance-exam` 的 `fx_` 衝突）
- `courseId = chapterId ~/ 100`：10 章章節練習一律 `chapterId 101-110`（`courseId 1`）；第一科模考 `chapterId 201`、第二科模考 `chapterId 202`（`courseId 2`，但**不建 chapters.json 條目**）
- `/exam` 路由實際的 query 參數名稱（已對照 `lib/app/router.dart` 逐字確認，不是憑印象）：`count`、`chapter`（不是 `chapterId`）、`courseId`、`wrongPriority`、`paper`（不是 `paperName`，雖然 Dart 類別欄位叫 `paperName`）
- 原始教材 PDF/xlsx 等機密檔案一律留在 `source-materials/`（已 gitignore），不進 git history
- 所有 Supabase 資料表／欄位名稱必須逐字對照既有程式碼實際查詢用到的名字（`lk_auth_service.dart`／`cloud_sync_service.dart`／`study_logger.dart`），不得自行發明新名字

---

## Task 1：建立新專案骨架、改品牌文字

**Files:**
- Create（透過複製）：`/Users/fortune/investment-insurance-exam/` 下整份 `insurance-exam-app` 原始碼（排除 `.git`、`build/`、`.dart_tool/`）
- Modify: `pubspec.yaml`、`web/index.html`、`lib/features/home/home_page.dart`（標題文字）

- [ ] **Step 1：複製 insurance-exam-app 原始碼到新專案目錄**

```bash
cd /Users/fortune/insurance-exam-app
git checkout gh-pages -- . 2>/dev/null || true  # 確保工作區乾淨，已在 main/gh-pages 無未提交變更時略過
rsync -a --exclude='.git' --exclude='build' --exclude='.dart_tool' --exclude='source-materials' \
  /Users/fortune/insurance-exam-app/ /Users/fortune/investment-insurance-exam/app/
```

（放進 `app/` 子目錄，跟 `source-materials/`、`docs/` 平級，保持 repo 根目錄乾淨）

- [ ] **Step 2：調整 `pubspec.yaml`**

```yaml
name: investment_insurance_exam
description: 投資型保險商品業務員資格測驗學習APP
```

（版本號重設為 `version: 1.0.0+1`，其餘 dependencies 原封不動）

- [ ] **Step 3：調整網頁標題**

`app/web/index.html` 與 `app/index.html` 裡的 `<title>` 改成「投資型保險資格測驗」。

- [ ] **Step 4：調整首頁顯示文字**

`app/lib/features/home/home_page.dart`：把寫死的「13 章」「保險實務」「保險法規」等字樣先保留不動（這些要等 Task 9/10 的章節內容就緒後，在 Task 11 統一處理），本步驟只處理 AppBar／頁首大標題字串（搜尋 `'保險業務員資格測驗'` 或類似字樣，改成「投資型保險資格測驗」）。

- [ ] **Step 5：確認可以跑起來**

```bash
cd /Users/fortune/investment-insurance-exam/app
flutter pub get
flutter analyze
```

Expected: `flutter analyze` 0 error（此時題庫還是舊的人壽題庫，不影響能不能 analyze 過）

- [ ] **Step 6：初始化新 git 歷史、commit**

```bash
cd /Users/fortune/investment-insurance-exam
git add app/
git commit -m "chore: scaffold investment-insurance-exam from insurance-exam-app base"
```

---

## Task 2：localStorage 鍵值前綴隔離

**Files:**
- Modify: `app/lib/core/services/lk_auth_service.dart`
- Modify: `app/lib/core/services/shared_preferences_store.dart`（如果裡面也有裸鍵名）

**Interfaces:**
- Consumes: 無
- Produces: 所有後續 Task 讀寫 `SharedPreferences` 一律透過這些已加前綴的 key 常數，不直接寫字串字面值

- [ ] **Step 1：幫 lk_auth_service.dart 的鍵名加前綴**

把：

```dart
const _kLkKeyId      = 'lk_key_id';
const _kLkKeyCode    = 'lk_key_code';
const _kLkBatchName  = 'lk_batch_name';
const _kLkExpiresAt  = 'lk_expires_at';
const _kLkDeviceId   = 'lk_device_id';
const _kLkLoggedIn   = 'lk_logged_in';
```

改成：

```dart
// 'inv_' 前綴：本站與 insurance-exam-app（無前綴）、currency-insurance-exam
// （'fx_' 前綴）、property-insurance-exam 共用同一個 GitHub Pages 網域
// shinkong-insurance.github.io（只是 path 不同），localStorage 以 origin
// 為界、不分 path，沒有前綴會跟其他站台的登入 session 互相污染。
const _kLkKeyId      = 'inv_lk_key_id';
const _kLkKeyCode    = 'inv_lk_key_code';
const _kLkBatchName  = 'inv_lk_batch_name';
const _kLkExpiresAt  = 'inv_lk_expires_at';
const _kLkDeviceId   = 'inv_lk_device_id';
const _kLkLoggedIn   = 'inv_lk_logged_in';
```

- [ ] **Step 2：檢查 `shared_preferences_store.dart`、`database_helper.dart` 有沒有其他裸鍵名**

```bash
cd /Users/fortune/investment-insurance-exam/app
grep -n "SharedPreferences\|getString\|setString\|getBool\|setBool" lib/core/database/shared_preferences_store.dart lib/core/database/database_helper.dart
```

把其中任何字面值鍵名（非 `_kLk*` 常數引用的）也統一加上 `inv_` 前綴。逐一確認後才進下一步（本計畫不先列出確切清單，因為確切鍵名要看執行當下 grep 結果——但「每一個都要加前綴」是硬性要求，不可只改 lk_auth_service.dart 就收工）。

- [ ] **Step 3：跑現有測試確認沒改壞**

```bash
flutter test
```

Expected: 全數通過（此時 lk_gate_page_test.dart 還是舊欄位版本，Task 3 會重寫）

- [ ] **Step 4：Commit**

```bash
git add app/lib/core/services/
git commit -m "fix: prefix localStorage keys to avoid cross-site collision on shared GitHub Pages origin"
```

---

## Task 3：移植 `#/lk` 姓名/單位/員編 授權變體（Dart 端）

**Files:**
- Modify: `app/lib/features/auth/lk_gate_page.dart`（整個改寫）
- Modify: `app/lib/core/services/lk_auth_service.dart`（只改 `autoRegister()` 簽名與內部邏輯）
- Delete: `app/lib/core/utils/exam_date_options.dart`、`app/test/core/utils/exam_date_options_test.dart`（確認無其他引用後，見 Step 4）
- Test: `app/test/features/auth/lk_gate_page_test.dart`（改寫）

**Interfaces:**
- Produces: `LkAuthService.autoRegister({required String name, required String unitName, required String employeeId})` → `Future<LkLoginResponse>`（跟 `currency-insurance-exam` 的簽名一致，後續 Task 不會再變動這個簽名）

- [ ] **Step 1：改寫 `lk_auth_service.dart` 的 `autoRegister()`**

把原本：

```dart
static Future<LkLoginResponse> autoRegister({
  required String name,
  required String phone,
  required DateTime examDate,
  String? referrerName,
  String? referrerPhone,
  String? referrerUnit,
  String? referrerId,
}) async {
  try {
    final res = await _sb.functions.invoke('auto-register-student', body: {
      'name': name,
      'phone': phone,
      'exam_date': examDate.toIso8601String().substring(0, 10),
      if (referrerName != null) 'referrer_name': referrerName,
      if (referrerPhone != null) 'referrer_phone': referrerPhone,
      if (referrerUnit != null) 'referrer_unit': referrerUnit,
      if (referrerId != null) 'referrer_id': referrerId,
    });
    ...
```

改成（其餘回傳處理邏輯不變，只換簽名與 body）：

```dart
static Future<LkLoginResponse> autoRegister({
  required String name,
  required String unitName,
  required String employeeId,
}) async {
  try {
    final res = await _sb.functions.invoke('auto-register-student', body: {
      'name': name,
      'unit_name': unitName,
      'employee_id': employeeId,
    });
    ...
```

（`res.data` 解析、`FunctionException` 處理、`SharedPreferences` 寫入那幾段完全不動，原封不動保留）

- [ ] **Step 2：改寫 `lk_gate_page.dart`**

整個檔案改成 `currency-insurance-exam` 的版本（已在 spec 討論時完整讀過，欄位是 `_nameCtrl`/`_unitCtrl`/`_employeeIdCtrl` 三個 `TextEditingController`），只改兩處文字：

1. `import '../../core/utils/exam_date_options.dart';` 這行刪掉（不再需要）
2. `_buildRegisterForm()` 裡的標題文字 `'外幣保險資格測驗'` 改成 `'投資型保險資格測驗'`（出現兩處：註冊表單與授權碼登入表單標題）

其餘程式碼（三個欄位的 controller、`_submitRegister()` 的必填檢查、`_loginWithCode()`、`_LkFormatter`）逐字沿用 currency 版本。

- [ ] **Step 3：跑 `flutter analyze` 確認沒有殘留引用**

```bash
cd /Users/fortune/investment-insurance-exam/app
flutter analyze
```

Expected: 0 error（若報 `exam_date_options.dart` 找不到被引用的符號，代表 Step 2 漏改）

- [ ] **Step 4：確認 `exam_date_options.dart` 沒有其他引用後刪除**

```bash
grep -rn "exam_date_options\|examDateOptions\|formatExamDate" lib/ test/
```

Expected: 只剩 `lib/core/utils/exam_date_options.dart` 自己與 `test/core/utils/exam_date_options_test.dart`（定義處），沒有其他呼叫端。確認後：

```bash
rm lib/core/utils/exam_date_options.dart test/core/utils/exam_date_options_test.dart
flutter analyze && flutter test
```

Expected: 0 error，測試全過

- [ ] **Step 5：改寫 widget test**

把 `app/test/features/auth/lk_gate_page_test.dart` 改成測試三個必填欄位（姓名/單位/員編）的檢核邏輯，參考 `currency-insurance-exam` 的 `test/features/auth/lk_gate_page_test.dart` 四個測試案例的寫法（欄位名稱換成本案的 `unitCtrl`/`employeeIdCtrl`）。

```bash
flutter test test/features/auth/lk_gate_page_test.dart
```

Expected: 4 個測試全過

- [ ] **Step 6：Commit**

```bash
git add app/lib/features/auth/ app/lib/core/services/lk_auth_service.dart app/test/
git commit -m "feat: port name/unit/employee-id #/lk auth variant from currency-insurance-exam"
```

---

## Task 4：Supabase schema 與 Edge Function

**Files:**
- Create: `app/supabase/migrations/0001_init_schema.sql`
- Create: `app/supabase/functions/auto-register-student/index.ts`

**Interfaces:**
- Produces: `auto-register-student` Edge Function 接受 `{name, unit_name, employee_id}`，回傳 `{key_id, key_code, expires_at}` 或 `{error}`（跟 Task 3 的 `autoRegister()` body 逐字對應）

- [ ] **Step 1：寫 consolidated init migration**

```sql
-- app/supabase/migrations/0001_init_schema.sql
-- 本專案題庫內容走靜態 JSON（assets/json/），不建 course/chapters/questions/
-- sections 這類內容表。這裡只建授權與個人作答紀錄用的表，逐字對照
-- lib/core/services/lk_auth_service.dart、cloud_sync_service.dart、
-- study_logger.dart 實際查詢用到的表名與欄位名，不是重新設計。

create extension if not exists "uuid-ossp";

create table license_keys (
  id uuid primary key default uuid_generate_v4(),
  key_code text unique not null,
  batch_name text,
  max_uses int not null default 1,      -- 0 = 無限
  used_count int not null default 0,
  expires_at timestamptz not null,
  is_active boolean not null default true
);

create table key_sessions (
  id uuid primary key default uuid_generate_v4(),
  key_id uuid not null references license_keys(id) on delete cascade,
  device_id text not null,
  login_count int not null default 1,
  last_used_at timestamptz,
  unique (key_id, device_id)
);

-- lk_auth_service.dart 用 _sb.rpc('increment_key_used_count', params: {'k_id': keyId}) 呼叫
create or replace function increment_key_used_count(k_id uuid)
returns void as $$
  update license_keys set used_count = used_count + 1 where id = k_id;
$$ language sql;

create table key_favorites (
  key_id uuid not null references license_keys(id) on delete cascade,
  device_id text not null,
  question_id text not null,
  created_at timestamptz not null default now(),
  unique (key_id, device_id, question_id)
);

create table key_wrong_answers (
  key_id uuid not null references license_keys(id) on delete cascade,
  device_id text not null,
  question_id text not null,
  wrong_count int not null default 1,
  last_wrong_at timestamptz not null default now(),
  unique (key_id, device_id, question_id)
);

create table students (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  unit_name text,
  employee_id text,
  key_id uuid references license_keys(id),
  key_code text,
  expires_at timestamptz,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create index students_name_unit_emp_idx on students (name, unit_name, employee_id);

-- study_logger.dart 的 _insert() 直接把這些欄位當頂層物件送出
create table study_logs (
  id uuid primary key default uuid_generate_v4(),
  license_key text not null,
  event_type text not null,
  chapter_id text,
  section_id text,
  duration_seconds int,
  questions_total int,
  questions_correct int,
  metadata jsonb,
  created_at timestamptz not null default now()
);

-- 這些都是授權／個人作答紀錄表，沿用 insurance-exam-app／currency-insurance-exam
-- 現狀的信任模型：不加 RLS ownership 限制。原因：前端一律用 anon key +
-- 純 .eq('key_id', ...) 過濾，沒有 Supabase Auth session／JWT claim 可供
-- RLS 驗證「這個 key_id 真的屬於呼叫端」，加了只會讓現有程式碼打不通。
-- 這是跟三個既有站台一致的既有風險，不在本案中另外解決。
```

- [ ] **Step 2：複製 `auto-register-student` Edge Function**

把 `currency-insurance-exam` 的 `supabase/functions/auto-register-student/index.ts` 整份複製到
`app/supabase/functions/auto-register-student/index.ts`，**不需要改任何欄位名稱**
（已經是 `unit_name`/`employee_id`，跟 Task 3 的 Dart 呼叫端欄位名完全吻合）。

- [ ] **Step 3：Commit**

```bash
git add app/supabase/
git commit -m "feat: add Supabase schema and auto-register-student Edge Function"
```

**注意**：本任務只產出檔案，**實際建立 Supabase 專案、跑 migration、deploy function 是 Task 5 的人工操作步驟**，需要使用者的 Supabase 帳號權限，我無法代為完成帳號層級的操作。

---

## Task 5：建立 Supabase 專案並接上 Flutter（需使用者配合）

**Files:**
- Modify: `app/lib/core/services/supabase_config.dart`

- [ ] **Step 1：使用者在 Supabase Dashboard 建立新專案**

請使用者（或由使用者授權後由我用 `supabase` CLI）建立一個新 Supabase 專案，命名建議
`investment-insurance-exam`，記下 Project URL 與 anon public key。

- [ ] **Step 2：套用 migration**

```bash
cd /Users/fortune/investment-insurance-exam/app
supabase link --project-ref <新專案的 project-ref>
supabase db push
```

Expected: `0001_init_schema.sql` 套用成功，Dashboard 的 Table Editor 看得到 6 張表

- [ ] **Step 3：Deploy Edge Function**

```bash
supabase functions deploy auto-register-student
```

- [ ] **Step 4：更新 `supabase_config.dart`**

```dart
// lib/core/services/supabase_config.dart
const String supabaseUrl = '<新專案的 Project URL>';
const String supabaseAnonKey = '<新專案的 anon public key>';
```

- [ ] **Step 5：建立 admin.html 登入用的 Supabase Auth 帳號**

`web/admin.html`（Task 12 會複製進來）用的是 `sb.auth.signInWithPassword({email, password})`
真實 Supabase Auth 帳號，不是另外存在自訂表裡的密碼。在 Supabase Dashboard →
Authentication → Users → Add user，建立一組管理員帳號（例如
`admin@skl.com.tw`，密碼自訂），記下密碼供 Task 12/14 測試登入使用。

- [ ] **Step 6：建立一組測試授權碼，方便後續 QA**

在 Dashboard SQL editor 跑：

```sql
insert into license_keys (key_code, batch_name, max_uses, expires_at, is_active)
values ('SK-2026-TEST-0001', 'TEST', 0, '2026-12-31T23:59:59Z', true);
```

- [ ] **Step 7：用 curl 驗證 Edge Function 三種情境**（比照 currency 站上線時的做法）

```bash
# 缺欄位
curl -s -X POST '<Project URL>/functions/v1/auto-register-student' \
  -H "Authorization: Bearer <anon key>" -H "Content-Type: application/json" \
  -d '{"name":"測試"}'
# Expected: {"error":"請填寫單位"}

# 新員編
curl -s -X POST '<Project URL>/functions/v1/auto-register-student' \
  -H "Authorization: Bearer <anon key>" -H "Content-Type: application/json" \
  -d '{"name":"測試學員","unit_name":"測試部門","employee_id":"TEST-001"}'
# Expected: {"key_id":"...","key_code":"SK-....","expires_at":"..."}

# 同姓名+單位+員編重複送出（應續權，不重複建立）
curl -s -X POST '<Project URL>/functions/v1/auto-register-student' \
  -H "Authorization: Bearer <anon key>" -H "Content-Type: application/json" \
  -d '{"name":"測試學員","unit_name":"測試部門","employee_id":"TEST-001"}'
# Expected: 回傳同一組 key_id/key_code，expires_at 往後延 60 天
```

- [ ] **Step 8：清掉測試資料、Commit 設定檔**

```sql
delete from students where employee_id = 'TEST-001';
```

```bash
git add app/lib/core/services/supabase_config.dart
git commit -m "chore: connect to dedicated Supabase project"
```

---

## Task 6：章節練習題庫解析腳本（UMU xlsx → questions.json）

**Files:**
- Create: `scripts/parse_chapter_questions.py`
- Create（執行腳本後產生）: `app/assets/json/questions.json`（本 Task 先產出 10 章部分，Task 7 再補第一科/第二科）

**Interfaces:**
- Produces: `questions.json` 每筆物件 `{id, chapterId, questionNo, question, options: [4 strings], answer: 1-4, explanation}`（跟 `lib/models/question.dart` 的 `fromJson` 逐欄對應）

- [ ] **Step 1：寫 xlsx 讀取函式（標準庫，不依賴 openpyxl）**

```python
# scripts/parse_chapter_questions.py
import zipfile
import xml.etree.ElementTree as ET
import re
import json
import glob
import os

NS = {'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def _col_to_idx(ref: str) -> int:
    letters = re.match(r'[A-Z]+', ref).group()
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch) - ord('A') + 1)
    return idx - 1


def read_xlsx_rows(path: str) -> list[list[str]]:
    """讀 xlsx 的 sheet1，回傳每列的儲存格字串陣列（依欄位字母對齊，缺的補空字串）。"""
    with zipfile.ZipFile(path) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in root.findall('a:si', NS):
                text = ''.join(t.text or '' for t in si.findall('.//a:t', NS))
                shared.append(text)
        sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        rows = []
        for row in sheet.findall('.//a:row', NS):
            cells = {}
            maxidx = -1
            for c in row.findall('a:c', NS):
                idx = _col_to_idx(c.get('r'))
                v = c.find('a:v', NS)
                t = c.get('t')
                val = v.text if v is not None else ''
                if t == 's' and val != '':
                    val = shared[int(val)]
                cells[idx] = val
                maxidx = max(maxidx, idx)
            rows.append([cells.get(i, '') for i in range(max(maxidx + 1, 10))])
        return rows
```

- [ ] **Step 2：寫執行到失敗會報錯的測試（用真實的第五章檔案，題數最少，21 題）**

```python
# scripts/test_parse_chapter_questions.py
from parse_chapter_questions import read_xlsx_rows, parse_chapter_file

SRC = "/Users/fortune/investment-insurance-exam/source-materials/UMU_題庫(投資型第五章測驗).xlsx"


def test_read_xlsx_rows_header():
    rows = read_xlsx_rows(SRC)
    assert rows[1][:6] == ['問題描述', '題型', '正確答案', '分值', '難度', '答案說明']


def test_parse_chapter_file_count_and_shape():
    questions = parse_chapter_file(SRC, chapter_id=105, start_question_no=1, start_id=10500)
    assert len(questions) == 21
    q = questions[0]
    assert q['chapterId'] == 105
    assert q['questionNo'] == 1
    assert q['id'] == 10500
    assert len(q['options']) == 4
    assert q['answer'] in (1, 2, 3, 4)
    assert q['question']  # 非空
```

```bash
cd /Users/fortune/investment-insurance-exam/scripts
python3 -m pytest test_parse_chapter_questions.py -v
```

Expected: FAIL（`parse_chapter_file` 還沒定義）

- [ ] **Step 3：實作 `parse_chapter_file()`**

```python
ANSWER_LETTER_TO_INDEX = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}


def parse_chapter_file(path: str, chapter_id: int, start_question_no: int, start_id: int) -> list[dict]:
    rows = read_xlsx_rows(path)
    out = []
    qno = start_question_no
    qid = start_id
    for row in rows[2:]:  # 第0列標題、第1列欄名，從第2列起是題目
        if len(row) < 2 or not row[1]:
            continue  # 題型欄空白＝沒有題目（例如尾端空白列）
        question_text = row[0].strip()
        answer_letter = row[2].strip().upper()
        options = [row[6].strip(), row[7].strip(), row[8].strip(), row[9].strip()]
        options = [o for o in options if o]  # 去掉空白選項（例如只有4個選項時選項E欄是空的）
        if answer_letter not in ANSWER_LETTER_TO_INDEX or ANSWER_LETTER_TO_INDEX[answer_letter] > len(options):
            raise ValueError(f"{path}: 第 {qno} 題正解 '{answer_letter}' 對應不到選項，需人工複核: {question_text[:30]}")
        out.append({
            'id': qid,
            'chapterId': chapter_id,
            'questionNo': qno,
            'question': question_text,
            'options': options,
            'answer': ANSWER_LETTER_TO_INDEX[answer_letter],
            'explanation': (row[5] or '').strip(),
        })
        qno += 1
        qid += 1
    return out
```

- [ ] **Step 4：跑測試確認通過**

```bash
python3 -m pytest test_parse_chapter_questions.py -v
```

Expected: PASS

- [ ] **Step 5：跑全部 10 章並寫出 `questions.json`**

```python
# scripts/build_questions_json.py（獨立執行腳本，不是測試）
from parse_chapter_questions import parse_chapter_file
import json

CHAPTERS = [
    (101, "UMU_題庫(投資型第一章測驗).xlsx"),
    (102, "UMU_題庫(投資型第二章測驗).xlsx"),
    (103, "UMU_題庫(投資型第三章測驗).xlsx"),
    (104, "UMU_題庫(投資型第四章測驗).xlsx"),
    (105, "UMU_題庫(投資型第五章測驗).xlsx"),
    (106, "UMU_題庫(投資型第六章測驗).xlsx"),
    (107, "UMU_題庫(投資型第七章測驗).xlsx"),
    (108, "UMU_題庫(投資型第八章測驗).xlsx"),
    (109, "UMU_題庫(投資型第九章測驗).xlsx"),
    (110, "UMU_題庫(投資型第十章測驗).xlsx"),
]
SRC_DIR = "/Users/fortune/investment-insurance-exam/source-materials/"

all_questions = []
for chapter_id, fname in CHAPTERS:
    qs = parse_chapter_file(SRC_DIR + fname, chapter_id=chapter_id,
                             start_question_no=1, start_id=chapter_id * 100)
    all_questions.extend(qs)
    print(f"chapter {chapter_id}: {len(qs)} 題")

with open("/Users/fortune/investment-insurance-exam/app/assets/json/questions_chapters.json", "w", encoding="utf-8") as f:
    json.dump(all_questions, f, ensure_ascii=False, indent=2)
print("total:", len(all_questions))
```

```bash
cd /Users/fortune/investment-insurance-exam/scripts
python3 build_questions_json.py
```

Expected: 10 行輸出對應各章題數（201/76/88/125/21/82/65/71/59/212，總計 1000 題），
若任何一章在解析途中因為「正解對應不到選項」丟出 `ValueError`，先處理該筆再重跑（見
Task 8 的校驗與人工複核流程）。

- [ ] **Step 6：Commit**

```bash
cd /Users/fortune/investment-insurance-exam
git add scripts/
git commit -m "feat: add UMU xlsx chapter question parser"
```

（此時 `questions_chapters.json` 是中繼產物，先不搬進 `app/assets/json/questions.json`，等 Task 7 的科目模考題一起合併）

---

## Task 7：科目模考題庫解析與去重合併（第一科/第二科）

**Files:**
- Create: `scripts/build_mock_exam_questions.py`
- Create: `scripts/test_build_mock_exam_questions.py`

**Interfaces:**
- Consumes: `read_xlsx_rows()`（Task 6 Step 1）
- Produces: `app/assets/json/questions_mock.json`：每筆跟 Task 6 同樣的 `Question` 形狀，`chapterId` 為 201 或 202

- [ ] **Step 1：寫正規化＋去重邏輯的測試**

```python
# scripts/test_build_mock_exam_questions.py
from build_mock_exam_questions import normalize_question_text, load_subject_questions

def test_normalize_strips_fullwidth_punct_and_whitespace():
    a = normalize_question_text("下列何者為貨幣市場的證券？")
    b = normalize_question_text("下列何者為貨幣市場的證券?")
    assert a == b

def test_load_subject_one_dedup_count():
    # 第一科：UMU 50 題 + 11501 範本 50 題，已知重複 5 題（含 1 題答案衝突、
    # 已由使用者確認以 UMU 版正解為準），去重後應為 95 題
    questions = load_subject_questions(
        umu_path="/Users/fortune/investment-insurance-exam/source-materials/UMU_題庫(投資型考古題第一科測驗).xlsx",
        template_path="/Users/fortune/investment-insurance-exam/source-materials/第一科(考古題11501).xlsx",
        chapter_id=201,
        start_id=20100,
    )
    assert len(questions) == 95

def test_load_subject_two_dedup_count():
    questions = load_subject_questions(
        umu_path="/Users/fortune/investment-insurance-exam/source-materials/UMU_題庫(投資型考古題第二科測驗).xlsx",
        template_path="/Users/fortune/investment-insurance-exam/source-materials/第二科(考古題11501).xlsx",
        chapter_id=202,
        start_id=20200,
    )
    assert len(questions) == 181
```

```bash
cd /Users/fortune/investment-insurance-exam/scripts
python3 -m pytest test_build_mock_exam_questions.py -v
```

Expected: FAIL（`build_mock_exam_questions` 模組還沒寫）

- [ ] **Step 2：實作**

```python
# scripts/build_mock_exam_questions.py
import re
from parse_chapter_questions import read_xlsx_rows, ANSWER_LETTER_TO_INDEX

_PUNCT_MAP = str.maketrans({
    '？': '?', '，': ',', '；': ';', '：': ':', '！': '!', '（': '(', '）': ')',
    '「': '"', '」': '"', '『': '"', '』': '"', '、': ',', '　': '', '\xa0': '',
})


def normalize_question_text(s: str) -> str:
    s = (s or '').translate(_PUNCT_MAP)
    return re.sub(r'\s+', '', s)


def _load_real_rows(path: str) -> list[list[str]]:
    """跳過標題列／欄名列／空白題型列，只留真正的題目列。"""
    rows = read_xlsx_rows(path)
    return [r for r in rows[2:] if len(r) > 1 and r[1]]


def load_subject_questions(umu_path: str, template_path: str, chapter_id: int, start_id: int) -> list[dict]:
    """合併 UMU 平台版與 11501 範本版，依題幹正規化後去重；重複時一律保留
    UMU 版的內容與正解（已與使用者逐題核對 5 題答案衝突案例，確認 UMU 版為準）。"""
    umu_rows = _load_real_rows(umu_path)
    tpl_rows = _load_real_rows(template_path)

    seen = {}
    ordered_keys = []
    for row in umu_rows:
        key = normalize_question_text(row[0])
        if key not in seen:
            seen[key] = row
            ordered_keys.append(key)
    for row in tpl_rows:
        key = normalize_question_text(row[0])
        if key not in seen:
            seen[key] = row
            ordered_keys.append(key)
        # 已存在（來自 UMU）→ 略過，不覆蓋

    out = []
    qno = 1
    qid = start_id
    for key in ordered_keys:
        row = seen[key]
        answer_letter = row[2].strip().upper()
        options = [row[6].strip(), row[7].strip(), row[8].strip(), row[9].strip()]
        options = [o for o in options if o]
        if answer_letter not in ANSWER_LETTER_TO_INDEX or ANSWER_LETTER_TO_INDEX[answer_letter] > len(options):
            raise ValueError(f"科目模考 chapter {chapter_id} 第 {qno} 題正解對應不到選項，需人工複核: {row[0][:30]}")
        out.append({
            'id': qid,
            'chapterId': chapter_id,
            'questionNo': qno,
            'question': row[0].strip(),
            'options': options,
            'answer': ANSWER_LETTER_TO_INDEX[answer_letter],
            'explanation': (row[5] or '').strip(),
        })
        qno += 1
        qid += 1
    return out
```

- [ ] **Step 3：跑測試**

```bash
python3 -m pytest test_build_mock_exam_questions.py -v
```

Expected: PASS（95、181 兩個數字跟 spec 文件記錄的去重結果一致）

**注意（人工核對項）**：spec 文件記錄第二科「關於時間不變性投資組合保險策略（TIPP）」這題 UMU 版選項 D 在原始 xlsx 是空白儲存格、選項 C 文字尾端疑似誤串接「以上皆非」。本 Step 3 測試只驗證「有 4 個非空選項」這個形狀，**不會抓到選項內容本身的錯字**，所以這一題：

- [ ] **Step 4：人工核對 TIPP 那一題的選項文字，必要時手動修正**

執行以下指令印出該題目前解析出來的樣子：

```python
from build_mock_exam_questions import load_subject_questions
qs = load_subject_questions(
    umu_path="/Users/fortune/investment-insurance-exam/source-materials/UMU_題庫(投資型考古題第二科測驗).xlsx",
    template_path="/Users/fortune/investment-insurance-exam/source-materials/第二科(考古題11501).xlsx",
    chapter_id=202, start_id=20200,
)
tipp = [q for q in qs if 'TIPP' in q['question'] or '時間不變性' in q['question']][0]
print(tipp)
```

對照原始 xlsx 儲存格人工確認選項 C/D 的正確文字，若有誤直接在 `load_subject_questions()`
回傳的資料上手動修正這一筆（或在腳本裡加一個小的 override dict，不要改動一般邏輯）。

- [ ] **Step 5：產生 `questions_mock.json` 並與章節題庫合併成最終 `questions.json`**

```python
# scripts/build_questions_json.py 補上這段（接續 Task 6 Step 5 的腳本）
from build_mock_exam_questions import load_subject_questions

mock1 = load_subject_questions(
    umu_path=SRC_DIR + "UMU_題庫(投資型考古題第一科測驗).xlsx",
    template_path=SRC_DIR + "第一科(考古題11501).xlsx",
    chapter_id=201, start_id=20100,
)
mock2 = load_subject_questions(
    umu_path=SRC_DIR + "UMU_題庫(投資型考古題第二科測驗).xlsx",
    template_path=SRC_DIR + "第二科(考古題11501).xlsx",
    chapter_id=202, start_id=20200,
)
print("第一科模考:", len(mock1), " 第二科模考:", len(mock2))

final_questions = all_questions + mock1 + mock2
with open("/Users/fortune/investment-insurance-exam/app/assets/json/questions.json", "w", encoding="utf-8") as f:
    json.dump(final_questions, f, ensure_ascii=False, indent=2)
print("final total:", len(final_questions))
```

```bash
python3 build_questions_json.py
```

Expected: 「第一科模考: 95　第二科模考: 181」，final total = 1000 + 95 + 181 = 1276

- [ ] **Step 6：Commit**

```bash
cd /Users/fortune/investment-insurance-exam
git add scripts/ app/assets/json/questions.json
git commit -m "feat: build final questions.json (10 chapters + two subject mock exams, deduped)"
```

---

## Task 8：題庫自動校驗

**Files:**
- Create: `scripts/validate_questions.py`

- [ ] **Step 1：寫校驗腳本**

```python
# scripts/validate_questions.py
import json
import sys
from collections import Counter

def validate(path: str) -> list[str]:
    with open(path, encoding='utf-8') as f:
        questions = json.load(f)

    errors = []
    ids = Counter(q['id'] for q in questions)
    for qid, count in ids.items():
        if count > 1:
            errors.append(f"重複 id: {qid} (出現 {count} 次)")

    per_chapter_qno = {}
    for q in questions:
        key = (q['chapterId'], q['questionNo'])
        per_chapter_qno.setdefault(key, []).append(q['id'])
    for key, qids in per_chapter_qno.items():
        if len(qids) > 1:
            errors.append(f"章節 {key[0]} 題號 {key[1]} 重複: ids={qids}")

    for q in questions:
        n_options = len(q['options'])
        if n_options < 2:
            errors.append(f"id {q['id']}: 選項數過少 ({n_options})")
        if not (1 <= q['answer'] <= n_options):
            errors.append(f"id {q['id']}: 正解 {q['answer']} 超出選項範圍 (共 {n_options} 個選項)")
        if not q['question'].strip():
            errors.append(f"id {q['id']}: 題幹為空")
        if q['chapterId'] not in range(101, 111) and q['chapterId'] not in (201, 202):
            errors.append(f"id {q['id']}: chapterId {q['chapterId']} 不在預期範圍 (101-110, 201, 202)")

    return errors


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else \
        "/Users/fortune/investment-insurance-exam/app/assets/json/questions.json"
    errors = validate(path)
    if errors:
        print(f"發現 {len(errors)} 個問題：")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("校驗通過，無問題。")
```

- [ ] **Step 2：對最終 `questions.json` 跑校驗**

```bash
cd /Users/fortune/investment-insurance-exam/scripts
python3 validate_questions.py
```

Expected: `校驗通過，無問題。`——若有輸出任何問題，逐一回到 Task 6/7 的來源 xlsx 人工核對後修正腳本，重跑 Task 6/7/8 直到乾淨為止（不可以略過報錯的題目直接上線）。

- [ ] **Step 3：Commit**

```bash
cd /Users/fortune/investment-insurance-exam
git add scripts/validate_questions.py
git commit -m "test: add questions.json structural validator"
```

---

## Task 9：章節講義內容（PDF → sections.json）

**Files:**
- Create: `app/assets/json/sections.json`
- Create: `scripts/sections_draft/chapter_101.json` … `chapter_110.json`（中繼草稿，逐章撰寫後再組裝）

這個任務是**內容整理**而非純程式碼任務：10 份 PDF 共 862 頁，需要逐章閱讀後摘要整理成學習重點，不是能完全自動化的機械轉換。

- [ ] **Step 1：逐章用 Read 工具讀取 PDF 全文（含圖表）**

對每一章（第一章 83 頁、第二章 17 頁、…、第十章 119 頁），用 Read 工具以
`pages` 參數分批讀（每次最多 20 頁），讀完整份 PDF 的文字與圖表內容。

- [ ] **Step 2：依固定模板整理成該章的 section 草稿**

每章輸出一個 JSON 檔 `scripts/sections_draft/chapter_10X.json`，格式：

```json
{
  "chapterId": 101,
  "sections": [
    {"order": 1, "title": "第一節 導論", "content": "……（依 PDF 該節內容摘要整理成條理清楚的學習重點，保留關鍵定義、法規條號、公式，不照抄投影片逐字稿，但不可遺漏考試會考的關鍵概念）"},
    {"order": 2, "title": "第二節 投資型保險商品的種類", "content": "……"}
  ]
}
```

每章的「節」切分依照 PDF 裡本來就有的「第X節」投影片分隔（已在前面的 PDF 品管抽查中確認每章都有清楚的「第X節」標題投影片，例如第一章有「第一節 導論」「第二節 投資型保險商品的種類」「第三節 投資型保險之運作」「第四節 投資型保險相關風險介紹」四節）。

- [ ] **Step 2 驗收標準**：每個草稿檔案，每個 section 的 `content` 至少包含該節投影片裡出現的**每一個條列重點**（允許改寫成完整句子，不可整段省略），且不包含頁首頁尾的「僅供內部教育訓練使用」「機密等級」等版權標記文字（那些不是教材內容）。

- [ ] **Step 3：寫組裝腳本，把 10 份草稿合併成 `sections.json`**

```python
# scripts/build_sections_json.py
import json
import glob

DRAFT_DIR = "/Users/fortune/investment-insurance-exam/scripts/sections_draft/"
OUT_PATH = "/Users/fortune/investment-insurance-exam/app/assets/json/sections.json"

all_sections = []
section_id = 10100
for path in sorted(glob.glob(DRAFT_DIR + "chapter_*.json")):
    with open(path, encoding='utf-8') as f:
        draft = json.load(f)
    chapter_id = draft['chapterId']
    for s in draft['sections']:
        all_sections.append({
            'id': section_id,
            'chapterId': chapter_id,
            'order': s['order'],
            'title': s['title'],
            'content': s['content'],
        })
        section_id += 1

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(all_sections, f, ensure_ascii=False, indent=2)
print("total sections:", len(all_sections))
```

```bash
cd /Users/fortune/investment-insurance-exam/scripts
python3 build_sections_json.py
```

Expected: 印出 section 總數（10 章，每章視投影片「第X節」數量而定，預期落在 30-50 筆之間）

- [ ] **Step 4：驗證 `sections.json` 的形狀跟 `lib/models/section.dart` 的 `fromJson` 對得上**

```bash
cd /Users/fortune/investment-insurance-exam/app
grep -n "factory Section.fromJson" -A 10 lib/models/section.dart
```

對照欄位名稱（`id`/`chapterId`/`order`/`title`/`content`），確認 Step 3 產出的 JSON 鍵名逐字相符，不符就回去改 Step 3 的腳本。

- [ ] **Step 5：Commit**

```bash
cd /Users/fortune/investment-insurance-exam
git add scripts/sections_draft/ scripts/build_sections_json.py app/assets/json/sections.json
git commit -m "feat: add chapter study-note sections parsed from lecture PDFs"
```

---

## Task 10：`chapters.json` 組裝（只有 10 個真實章節，不含科目模考虛擬章節）

**Files:**
- Create: `app/assets/json/chapters.json`

- [ ] **Step 1：直接手寫 10 筆（章節標題取自 PDF 的「第X章」標題投影片，已在品管抽查時讀過）**

```json
[
  {"id": 101, "courseId": 1, "unitNo": 1, "title": "投資型保險概論", "weight": ""},
  {"id": 102, "courseId": 1, "unitNo": 1, "title": "投資型保險法令介紹", "weight": ""},
  {"id": 103, "courseId": 1, "unitNo": 1, "title": "金融體系概述", "weight": ""},
  {"id": 104, "courseId": 1, "unitNo": 1, "title": "證券投資信託及顧問之規範與制度", "weight": ""},
  {"id": 105, "courseId": 1, "unitNo": 1, "title": "貨幣時間價值", "weight": ""},
  {"id": 106, "courseId": 1, "unitNo": 1, "title": "債券評價", "weight": ""},
  {"id": 107, "courseId": 1, "unitNo": 1, "title": "證券評價", "weight": ""},
  {"id": 108, "courseId": 1, "unitNo": 1, "title": "風險、報酬與投資組合", "weight": ""},
  {"id": 109, "courseId": 1, "unitNo": 1, "title": "資本資產訂價模式、績效評估及調整", "weight": ""},
  {"id": 110, "courseId": 1, "unitNo": 1, "title": "投資工具簡介", "weight": ""}
]
```

**不要**加入 `chapterId 201/202` 的條目——`chapter_list_page.dart` 只讀這份檔案來決定章節列表要顯示什麼（已對照程式碼確認 `chaptersProvider` 純讀 `chapters.json`、不會從 `questions.json` 反推章節），不加條目就不會出現在一般章節練習列表，不需要寫任何過濾程式碼。

- [ ] **Step 2：確認 `course.json`／`Chapter` model 沒有被其他地方引用需要配套更動**

```bash
cd /Users/fortune/investment-insurance-exam/app
grep -rn "course\.json\|Course(" lib/ --include="*.dart"
```

Expected: 無輸出（已事先確認 `course.json`／`Course` model 在 `insurance-exam-app` 原始碼裡完全沒被引用，是死檔案，本專案不需要處理它，留著不動即可）

- [ ] **Step 3：跑 `flutter test` 確認章節列表相關測試沒壞**

```bash
flutter test
```

- [ ] **Step 4：Commit**

```bash
cd /Users/fortune/investment-insurance-exam
git add app/assets/json/chapters.json
git commit -m "feat: add chapters.json for the 10 real study chapters"
```

---

## Task 11：首頁新增「科目模考」入口

**Files:**
- Modify: `app/lib/features/home/home_page.dart`

**Interfaces:**
- Consumes: `questions.json` 裡 `chapterId 201`（95 題）、`chapterId 202`（181 題）；路由
  `/exam` 的實際 query 參數名稱（已在 Global Constraints 核對）：`count`、`chapter`、`paper`

- [ ] **Step 1：移除原本人壽題庫殘留的區塊文字**

把 Task 1 Step 4 暫時保留的「章節練習」區塊（`保險實務（50 題）`／`保險法規（100 題）`／
A/B/C 卷那幾個 `_FeatureCard`）整段刪掉——那是 `insurance-exam-app` 原本的「保險實務/保險法規」
隨機模考，本專案不需要這個子功能，只保留「章節閱讀」「科目模考（新增）」「錯題本/收藏/進度」。

- [ ] **Step 2：在「題庫練習」區塊位置加入「科目模考」區塊**

```dart
// ── 科目模考 ──────────────────────────────────
_SectionHeader(title: '科目模考', icon: Icons.assignment_turned_in),
const SizedBox(height: 10),
_FeatureCard(
  icon: Icons.timer,
  title: '第一科模考（95 題）',
  subtitle: '官方考古題全數收錄 · 每次隨機出題',
  color: Colors.orange,
  onTap: () => context.push('/exam?count=95&chapter=201&paper=%E7%AC%AC%E4%B8%80%E7%A7%91'),
),
_FeatureCard(
  icon: Icons.assignment,
  title: '第二科模考（181 題）',
  subtitle: '官方考古題全數收錄 · 每次隨機出題',
  color: Colors.deepOrange,
  onTap: () => context.push('/exam?count=181&chapter=202&paper=%E7%AC%AC%E4%BA%8C%E7%A7%91'),
),
const SizedBox(height: 20),
```

（`%E7%AC%AC%E4%B8%80%E7%A7%91` 是「第一科」UTF-8 URL-encode，`%E7%AC%AC%E4%BA%8C%E7%A7%91` 是「第二科」；也可以直接用 `Uri.encodeComponent('第一科')` 在 `onTap` 裡動態組字串，兩種寫法擇一，後者可讀性較好：）

```dart
onTap: () => context.push('/exam?count=95&chapter=201&paper=${Uri.encodeComponent('第一科')}'),
```

- [ ] **Step 3：調整「13 章」等寫死的章節數字**

搜尋 `home_page.dart` 裡任何寫死的 `'13 章'`、`'13'` 字樣（Task 1 Step 4 提到先保留的那幾處），
改成 `'10 章'` 或改用 `chapters.length`／`chaptersProvider` 動態算出的數字（優先用動態算法，
避免以後章節數變動又要手動改字串）。

- [ ] **Step 4：手動啟動 app 檢查首頁畫面**

```bash
cd /Users/fortune/investment-insurance-exam/app
flutter run -d chrome --web-port=8765
```

人工確認：首頁「科目模考」區塊兩個按鈕顯示正確題數，點擊後能進入測驗頁、AppBar 顯示「第一科」/「第二科」卷別名稱。

- [ ] **Step 5：Commit**

```bash
cd /Users/fortune/investment-insurance-exam
git add app/lib/features/home/home_page.dart
git commit -m "feat: add subject mock exam entry points on home page"
```

---

## Task 12：後台管理（移植 unit/employee_id 版 admin.html，新增科目模考統計維度）

**Files:**
- Create: `app/web/admin.html`（以 `currency-insurance-exam` 的 `web/admin.html` 為起點）
- Modify: `app/web/admin.html`（新增科目模考統計區塊）

- [ ] **Step 1：複製 currency 站的 admin.html 當起點**

```bash
cp /Users/fortune/currency-insurance-exam/web/admin.html \
   /Users/fortune/investment-insurance-exam/app/web/admin.html
```

（這份已經有姓名/單位/員編的學員表格、搜尋、依單位分組統計、刪除功能，跟本案欄位需求完全吻合，不需要重新搬 `insurance-exam-app` 的電話/考試日期版本再改欄位）

- [ ] **Step 2：改掉品牌文字與 Supabase 連線設定**

把檔案裡的 `SUPABASE_URL`／`SUPABASE_ANON_KEY`（或等效的連線設定常數）換成 Task 5 建立的新專案資訊；把頁面標題、品牌文字裡「外幣保險」字樣改成「投資型保險」。

- [ ] **Step 3：新增「科目模考統計」區塊**

在既有「依單位分組」統計表格下方新增一段，查詢 `study_logs` 表（`event_type = 'exam_session'`，
`chapter_id in ('201','202')`），依 `license_key` join `students.key_code` 取得 `unit_name`，
算出各單位在第一科/第二科的作答次數與平均正確率：

```html
<h2>科目模考統計（依單位）</h2>
<table id="mock-exam-stats-table">
  <thead>
    <tr><th>單位</th><th>科目</th><th>作答次數</th><th>平均正確率</th><th>及格率（&ge;60%）</th></tr>
  </thead>
  <tbody id="mock-exam-stats-body"></tbody>
</table>
```

```javascript
async function loadMockExamStats() {
  const { data: logs, error } = await supabase
    .from('study_logs')
    .select('license_key, chapter_id, questions_total, questions_correct')
    .in('chapter_id', ['201', '202']);
  if (error) { console.error(error); return; }

  const { data: students } = await supabase
    .from('students')
    .select('key_code, unit_name');
  const unitByKeyCode = Object.fromEntries(
    (students || []).map(s => [s.key_code, s.unit_name || '未填寫'])
  );

  // key: `${unit}__${subject}` -> { count, correctSum, totalSum, passCount }
  const grouped = {};
  for (const log of logs || []) {
    const unit = unitByKeyCode[log.license_key] || '未知';
    const subject = log.chapter_id === '201' ? '第一科' : '第二科';
    const key = `${unit}__${subject}`;
    const g = grouped[key] || { unit, subject, count: 0, correctSum: 0, totalSum: 0, passCount: 0 };
    const rate = log.questions_total > 0 ? log.questions_correct / log.questions_total : 0;
    g.count += 1;
    g.correctSum += log.questions_correct;
    g.totalSum += log.questions_total;
    if (rate >= 0.6) g.passCount += 1;  // 及格標準先假設 60%，如實際及格標準不同請調整這個常數
    grouped[key] = g;
  }

  const tbody = document.getElementById('mock-exam-stats-body');
  tbody.innerHTML = '';
  for (const g of Object.values(grouped)) {
    const avgRate = g.totalSum > 0 ? (g.correctSum / g.totalSum * 100).toFixed(1) : '0.0';
    const passRate = (g.passCount / g.count * 100).toFixed(1);
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${g.unit}</td><td>${g.subject}</td><td>${g.count}</td><td>${avgRate}%</td><td>${passRate}%</td>`;
    tbody.appendChild(tr);
  }
}
```

**注意**：「及格標準 60%」是我先假設的預設值（程式碼裡已加註解標明），實際投資型保險資格測驗的官方及格分數如果不是 60 分，上線前請告知，一行數字可改。

- [ ] **Step 4：人工在瀏覽器測試**

本機跑 Flutter（`flutter run -d chrome --web-port=8765`）後，另開分頁打開
`http://localhost:8765/admin.html`，用 Task 5 建立的管理員帳號登入，確認學員列表、
依單位統計、新增的科目模考統計區塊都能正常載入、沒有 console error。

- [ ] **Step 5：同步複製到 `web/admin.html` 以外的建置用副本（若有）**

```bash
diff app/web/admin.html app/admin.html 2>/dev/null
```

若 `app/admin.html`（repo 根目錄）跟 `app/web/admin.html` 是兩份需要同步的檔案（比照
`insurance-exam-app` 的既有慣例），把同樣的內容複製過去，保持兩邊一致。

- [ ] **Step 6：Commit**

```bash
cd /Users/fortune/investment-insurance-exam
git add app/web/admin.html app/admin.html
git commit -m "feat: port unit/employee-id admin.html, add subject mock exam stats"
```

---

## Task 13：GitHub repo 建立與部署腳本

**Files:**
- Create: `deploy.sh`

- [ ] **Step 1：在 GitHub 建立新 repo（需使用者 GitHub 權限，用 `gh` CLI）**

```bash
cd /Users/fortune/investment-insurance-exam
gh repo create shinkong-insurance/investment-insurance-exam --public \
  --description "投資型保險商品業務員資格測驗學習APP" --source=. --remote=origin
```

- [ ] **Step 2：push `main` 分支（只放 `app/` 底下的原始碼，不含 `source-materials/`）**

本 repo 根目錄同時有 `app/`（Flutter 專案）、`source-materials/`（gitignored）、`docs/`
（spec/plan）。為了讓 `main` 分支乾淨地對應「Flutter 專案根目錄」（比照其他三站的慣例，
`main` 分支的根目錄本身就是 Flutter 專案根目錄，不是巢狀在 `app/` 子目錄下），這一步要把
`app/` 內容攤平到 repo 根目錄：

```bash
git subtree split --prefix=app -b main-flat
git checkout main-flat
git checkout -b main
git branch -D main-flat
git push -u origin main
```

- [ ] **Step 3：寫部署腳本（git worktree 做法，避免重演先前 rsync 路徑誤刪 assets 的問題）**

```bash
#!/bin/zsh
# deploy.sh — build Flutter web 並部署到 gh-pages 分支
# 用 git worktree 而非裸 rsync 到隨意路徑，每個路徑都是明確的絕對路徑或
# 相對於本腳本所在目錄算出來的，不靠猜測或相對 cd 疊加。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$REPO_ROOT/build/web"
WORKTREE_DIR="$REPO_ROOT/.gh-pages-worktree"

echo "[1/5] flutter pub get"
cd "$REPO_ROOT"
flutter pub get

echo "[2/5] flutter build web --release --base-href /investment-insurance-exam/"
flutter build web --release --base-href /investment-insurance-exam/

echo "[3/5] 準備 gh-pages worktree"
if [ ! -d "$WORKTREE_DIR" ]; then
  git fetch origin gh-pages 2>/dev/null || true
  if git show-ref --verify --quiet refs/remotes/origin/gh-pages; then
    git worktree add "$WORKTREE_DIR" gh-pages
  else
    git worktree add -b gh-pages "$WORKTREE_DIR"
  fi
fi

echo "[4/5] 同步 build 產物到 worktree（明確來源/目的地，均為絕對路徑）"
rsync -a --delete \
  --exclude='.git' \
  "$BUILD_DIR/" \
  "$WORKTREE_DIR/"

echo "[5/5] commit + push gh-pages"
cd "$WORKTREE_DIR"
git add -A
if git diff --cached --quiet; then
  echo "無變更，略過 commit"
else
  git commit -m "deploy: $(date '+%Y-%m-%d %H:%M:%S')"
  git push origin gh-pages
fi

echo "完成：https://shinkong-insurance.github.io/investment-insurance-exam/"
```

```bash
chmod +x deploy.sh
```

- [ ] **Step 4：跑一次部署腳本**

```bash
./deploy.sh
```

Expected: 最後印出 GitHub Pages 網址，且 `.gh-pages-worktree/` 底下能看到完整 `build/web` 內容
（`index.html`、`main.dart.js`、`assets/`、`admin.html` 都在）

- [ ] **Step 5：確認 GitHub Pages 設定指到 `gh-pages` 分支**

```bash
gh api repos/shinkong-insurance/investment-insurance-exam/pages 2>&1 || \
gh api repos/shinkong-insurance/investment-insurance-exam/pages -X POST -f source[branch]=gh-pages -f source[path]=/
```

- [ ] **Step 6：Commit 部署腳本到 main**

```bash
cd /Users/fortune/investment-insurance-exam
git add deploy.sh
git commit -m "chore: add git-worktree-based deploy script"
git push origin main
```

---

## Task 14：上線前瀏覽器端對端 QA

- [ ] **Step 1：確認 GitHub Pages build 完成**

```bash
gh api repos/shinkong-insurance/investment-insurance-exam/pages/builds/latest
```

Expected: `"status": "built"`

- [ ] **Step 2：`#/lk` 自助註冊流程**

用瀏覽器打開 `https://shinkong-insurance.github.io/investment-insurance-exam/#/lk`，
填姓名「測試學員」/單位「測試部門」/員編「QA-TEST-001」送出，確認直接登入並導到首頁，
首頁「10 章」「科目模考」區塊正常顯示。

- [ ] **Step 3：章節練習**

點「章節閱讀」進入任一章節，確認內容正常顯示（非亂碼、非空白）；進入該章節練習模式作答幾題，
確認計分與錯題記錄功能正常。

- [ ] **Step 4：科目模考**

點「第一科模考」，確認題數顯示 95 題、AppBar 顯示「第一科」；完整作答（或至少作答到交卷），
確認交卷後跳轉結果頁、分數計算正確，錯題有進錯題本（抽查 1-2 題）。對「第二科模考」（181 題）
重複同樣流程。

- [ ] **Step 5：後台管理**

打開 `https://shinkong-insurance.github.io/investment-insurance-exam/admin.html`，用 Task 5
建立的管理員帳號登入，確認剛剛的測試學員（QA-TEST-001）出現在學員列表、依單位統計正確、
科目模考統計區塊有抓到剛剛作答的 1-2 筆紀錄。

- [ ] **Step 6：清除測試資料**

在 admin.html 把測試學員「QA-TEST-001」刪除，Supabase Dashboard 確認 `students`／
`key_wrong_answers`／`study_logs` 裡的測試資料都清乾淨，不留在正式資料庫。

- [ ] **Step 7：把本次 QA 結果記錄進 CLAUDE.md（仿照其他三站的慣例）**

於 repo 根目錄新增 `CLAUDE.md`，記錄本次上線的日期、題數、Supabase 專案 ref（不含 anon key
明碼）、已知限制（60% 及格標準為假設值、科目模考答錯共用一般錯題本且 `chapterId % 100`
顯示會誤標成「第1章/第2章」等本計畫明確記錄過的行為），方便之後接手的人不用重新摸索。
