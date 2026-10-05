# 投資型保險考照網站 — 設計規格

- 日期：2026-10-05（2026-10-05 第二次修訂：基底從 `currency-insurance-exam` 改回
  `insurance-exam-app`，見「修訂記錄」）
- 狀態：已核准（brainstorming 完成，待寫實作計畫）
- 參考範本：`shinkong-insurance/insurance-exam-app`

## 背景與目標

新光人壽需要一個投資型保險商品業務員資格測驗的練習網站，供員工（單位＋員編身分）自助練習章節題庫與科目模考。公司已有三個同系列產品：

- `insurance-exam-app`（人壽壽險，#/lk 以姓名/手機/考試日期註冊；內容為靜態 JSON；已有「兩科」courseId 慣例）
- `property-insurance-exam`
- `currency-insurance-exam`（外幣保單，#/lk 以**姓名/單位/員編**註冊；題庫內容已演化為存在 Supabase、`reviewed` 審核閘門、關卡/口訣卡/講義 viewer 等進階功能）

本專案延續同一套架構與維運模式，新增第四個站台：**investment-insurance-exam**。

### 修訂記錄

**第一次設計（已作廢）**：原打算以 `currency-insurance-exam` 為複製基底，因其已有
`#/lk` 姓名/單位/員編 變體、且章節練習與科目模考分離。

**第二次修訂（本次採用）**：寫實作計畫前深入看了 `currency-insurance-exam` 的實際
原始碼（而非只看最近幾次 commit 的 diff），發現它已經演化出遠比預期複雜的內容架構——
題庫實際存在 Supabase（非靜態 JSON）、有 `reviewed` 審核閘門、以及本案完全不需要的
關卡（levels）／口訣卡（mnemonics）／講義 viewer（guide）功能，這些都是外幣站為了
處理自己多批次題庫沿革才長出來的複雜度。經與使用者確認，**題庫內容architecture
改採最簡化的靜態 JSON**（維持本規格一開始的決定不變）。

因此改採 **`insurance-exam-app`** 為複製基底（它本來就是靜態 JSON 架構），只從
`currency-insurance-exam` **移植「`#/lk` 姓名/單位/員編」這一個變體的具體檔案**
（`lk_gate_page.dart`、`lk_auth_service.dart` 的 `autoRegister()` 签名、
`auto-register-student` Edge Function），其餘功能不搬。

深入看 `insurance-exam-app` 原始碼時，還發現它自己已經有「兩科」的底層慣例可以直接
沿用於「科目模考」，見下方「科目模考的實作方式」一節，細節改動見架構決策 §2、§3。

## 原始素材盤點

位置：`/Users/fortune/investment-insurance-exam/source-materials/`（git-ignored，機密教材不進公開 repo，見「內容授權與機密標示」一節）

- 10 份章節講義 PDF（已由原始 .ppt 轉檔，已完成品管，見下方「PDF 轉檔品管結果」）
- 10 份對應章節的 UMU 題庫 xlsx（`UMU_題庫(投資型第X章測驗).xlsx`）
- 2 份科目考古題 xlsx：`第一科(考古題11501).xlsx`、`第二科(考古題11501).xlsx`

### PDF 轉檔品管結果（2026-10-05 已完成）

全數 10 章 PDF 皆已檢查通過：
- `pdfinfo` 檢查頁數與頁面尺寸（統一 720×540pt），無 Error/Warning
- 皆有正常可抽取文字（`pdftotext` 無亂碼替代字元）
- 目視抽查第一章（83 頁）開頭/結尾、第十章（119 頁）開頭/結尾，圖表、表格、投影片排版正確無缺頁
- 第八章原本遺漏（誤存為 .key），已於 2026-10-05 補轉為 PDF（122 頁），複驗通過

各章頁數：第一章 83、第二章 17、第三章 78、第四章 57、第五章 15、第六章 21、第七章 59、第八章 122、第九章 32、第十章 119。

### 內容授權與機密標示

每份講義 PDF 頁首皆標註「僅供內部教育訓練使用／機密等級:密」，結尾頁載明「此份資料僅供內部教學使用，不得對外展示或散布」。

**決策（使用者已確認，2026-10-05）**：此聲明文字原樣保留在內容中，不做遮蔽或竄改；公司對此教材的使用已有內部控管機制，比照既有三站的作法延續（GitHub repo 與 GitHub Pages 皆為 Public，`#/lk` 僅作為網頁端的使用門檻，不是內容存取控制）。本規格不在此之上做額外的存取限制設計。

## 架構決策

### 1. 專案基底與 Repo 策略

- 以 `insurance-exam-app` 現有程式碼為起點，建立全新、乾淨的 Git 歷史（不是 GitHub fork 關係），避免未來兩個產品的 git history 互相干擾
- GitHub repo：`shinkong-insurance/investment-insurance-exam`，Public（與既有三站一致）
- 保留原架構：`lib/app|core|features|models|providers|repositories` 分層、靜態 JSON 內容、`course/chapter` 兩層結構、既有的 `chapter_list_page` / `quiz_page` / `exam_page` / `favorite_page` / `wrong_book_page` / `progress_page`
- 需替換：題庫內容（`assets/json/questions.json`、`sections.json`、`chapters.json`、`course.json`）、品牌文字（app 名稱、首頁標題、favicon/logo）、Supabase 連線設定（指向本案專屬的新 Supabase 專案）
- `#/lk` 授權頁只移植「姓名/單位/員編」這一個變體（從 `currency-insurance-exam` 搬對應檔案過來改掉原本 insurance-exam-app 的姓名/電話/考試日期/推薦人欄位），其餘不動

### 2. 內容與題庫資料流程、科目模考的實作方式

**`insurance-exam-app` 既有的 course/chapter 慣例**（本案直接沿用，不新創概念）：
`chapterId`、`questionId` 皆為整數，且 **`chapterId ~/ 100 == courseId`**
（例如 chapterId 101~110 屬於 courseId 1）。`ExamPage` 既有
`getRandomQuestionsByCourse(count, courseId)` 與 `getRandomQuestions(count, chapterId: id)`
兩種既有查詢，選題時 `pool.shuffle(); pool.take(count)` ——當 `count >= pool.length`
時效果等同「取出全部題目，只是順序洗牌」。`ExamPage` 也已支援 `paperName` 參數用於
AppBar 顯示卷別名稱。

**本案資料配置**：
- **10 章章節練習** → `courseId = 1`，`chapterId = 101..110`（跟 `insurance-exam-app` 原本編碼風格一致），對應「章節閱讀」`sections.json` 與「章節練習」`questions.json`。每章講義 PDF 解析為一個 section（抽取文字重點＋可讀化整理，不還原原始投影片排版）；每章 UMU xlsx 解析為該 chapterId 底下的練習題（沿用 currency 站已驗證的 xlsx→json 清洗邏輯，欄位對應依本案 xlsx 實際欄位調整，清洗邏輯本身不重寫）
- **科目模考（第一科／第二科考古題）** → 各自建成一個「虛擬章節」：`courseId = 2`，`chapterId = 201`（第一科）、`chapterId = 202`（第二科），**不出現在一般章節列表 UI**，只在首頁新增一個「科目模考」區塊，各自連到
  `/exam?count=<該科目總題數>&chapterId=201&paperName=第一科` /
  `.../?chapterId=202&paperName=第二科`。因為 `count` 設為該科目全部題數，
  實際效果就是「全部出題、每次洗牌」——**零新增 Dart 邏輯，完全複用既有已上線驗證過的測驗／計分引擎**
- 兩個決策（已與使用者確認，2026-10-05）：
  1. 科目模考答錯**跟章節練習共用同一本錯題本**（`key_wrong_answers`），不特殊判斷區分來源
  2. 科目模考每次作答**沿用既有洗牌邏輯**，題目順序不強制對應官方原始題號順序
- 統一輸出到 `assets/json/questions.json`、`sections.json`、`chapters.json`（新增 201/202 兩筆虛擬章節）、`course.json`（新增 courseId 2）；Flutter 端讀靜態 JSON，Supabase 只管授權與作答紀錄，不即時提供題目內容

### 3. 授權（`#/lk`）與後台管理

- 從 `currency-insurance-exam` 移植 `#/lk` 姓名/單位/員編 變體：學生填 **姓名、單位、員編** 三欄即完成自助註冊，系統自動核發 60 天效期授權（`license_keys` 表 `max_uses=0`，不限次數）；手動授權碼登入的備用路徑（`key_sessions` 表）維持不動，比照兩站既有行為
- `lk_auth_service.dart`（`autoRegister()` 簽名改為 `name/unitName/employeeId`）、`lk_gate_page.dart`（雙欄位改三欄位）直接從 currency 站複製對應的程式碼區塊，替換掉 insurance-exam-app 原本的姓名/電話/考試日期/推薦人欄位；`auto_register-student` Edge Function 幾乎原封不動複製（currency 版本已經用 `unit_name`/`employee_id`，欄位名稱直接吻合，不用重新命名）
- **localStorage 鍵值前綴要換新的**（例如 `inv_`）：三個既有站台都部署在同一個 GitHub Pages 網域 `shinkong-insurance.github.io`（只是 path 不同），而 localStorage 是以 origin 為界、不分 path，`currency-insurance-exam` 已經因此需要加 `fx_` 前綴避免跟 `insurance-exam-app`（無前綴）衝突。本案若沿用無前綴或沿用 `fx_`，登入 session 會跟既有站台互相污染
- 後台 `admin.html`：延續既有三站的學生清單、統計（依單位/員編分組）、到期管理、刪除功能；因本案多了「科目模考」概念，統計頁需新增一個維度 —— 各單位在第一科／第二科模考的作答數與通過率；其餘既有修復（到期篩選、批次刪除、UTC 時區處理）直接沿用
- 管理員登入沿用既有 `admin_login_page.dart` 機制，不另外設計新的權限分層

### 4. Supabase 專案與部署

- 新建獨立 Supabase 專案（新 project ref，不與其他三站共用資料庫）
- 資料表**比照 `insurance-exam-app` 實際程式碼會查詢的表**（逐一對照
  `lk_auth_service.dart`／`cloud_sync_service.dart`／`study_logger.dart` 的
  `.from(...)` 呼叫，不是重新設計）：
  - `license_keys`（`id, key_code, batch_name, max_uses, used_count, expires_at, is_active`）
  - `key_sessions`（`id, key_id, device_id, login_count, last_used_at`，`unique(key_id, device_id)`）
  - `key_favorites`（`key_id, device_id, question_id, created_at`，`unique(key_id, device_id, question_id)`）
  - `key_wrong_answers`（`key_id, device_id, question_id, wrong_count, last_wrong_at`，`unique(key_id, device_id, question_id)`）
  - `students`（`id, name, unit_name, employee_id, key_id, key_code, expires_at, is_active, created_at`）
  - `study_logs`（`id, license_key, event_type, chapter_id, section_id, duration_seconds, questions_total, questions_correct, metadata jsonb, created_at`）
  - RPC `increment_key_used_count(k_id uuid)`：`update license_keys set used_count = used_count + 1 where id = k_id`
  - **本案不需要** `course/chapters/questions/sections/levels/mnemonic_cards` 這類內容表（`currency-insurance-exam` 現狀才有，本案走靜態 JSON，見 §2）
- RLS：這些都是授權／個人作答紀錄表，沿用 `insurance-exam-app`／`currency-insurance-exam` 現狀的信任模型——不加 RLS ownership 限制（原因：目前前端一律用 anon key + 純 `.eq('key_id', ...)` 過濾，沒有 Supabase Auth session／JWT claim 可供 RLS 驗證「這個 key_id 真的屬於呼叫端」，加了只會打不通。此為既有風險，跟三站現況一致，不在本案中另外解決）
- `supabase/functions/auto-register-student`：近乎原封不動複製 currency 站版本（欄位已經是 `unit_name`/`employee_id`）
- 部署流程延續既有模式：`main` 分支放 Flutter 原始碼，`gh-pages` 分支放 build 產物；`flutter build web` 後用既有 rsync 腳本同步
  - **已知風險提醒**：`insurance-exam-app` 先前曾因 rsync 路徑誤配，誤刪 assets（已用 git checkout 救回）。建立本專案的建置腳本時，要直接沿用已經修正過的路徑設定，不要重新摸索
- GitHub Pages 開啟於 `gh-pages` 分支；網域先用預設的 `shinkong-insurance.github.io/investment-insurance-exam`，若有自訂網域需求待確認後再調整

### 5. 題庫解析品管與測試

- 沿用三站已踩過的已知坑與對應清洗邏輯：UMU 題庫常見「選項標記重複」「題幹跨行導致切割錯位」「選項標記嵌入題幹」等問題，套用既有的視覺行聚類＋正則去重複標記腳本
- 解析完跑自動校驗：每題有效選項數是否正確（4 或 5 個）、正解是否存在於選項中、題號有無重複、`chapter_id`/`subject_id` 歸屬是否正確；未通過校驗者才進入人工複核清單
- **科目模考題（考古題）需額外核對官方答案**：過去經驗顯示考古題題庫的正解欄位有時本身有誤植，上線前應抽樣與官方公告答案核對，不可照單全收
- 測試：沿用 `test/` 既有 widget test 型態（參考 `lk_gate_page_test.dart`），新增本案特有的欄位驗證測試（單位/員編必填）
- 上線前瀏覽器實測流程：`#/lk` 註冊 → 章節練習 → 科目模考 → 後台統計/刪除，驗證程序比照 `insurance-exam-app` 上線時的做法

## 未決事項（進入實作計畫前待確認）

1. 本案 UMU xlsx 的實際欄位結構尚未逐一核對（僅確認檔案存在與基本盤點），實作階段解析腳本撰寫時需先讀取欄位確認對應關係
2. 自訂網域需求未定，預設先用 GitHub Pages 預設網址

## 範圍外（本次不做）

- 不建立跨站共用的多租戶平台（經使用者確認採「複製現有專案當模板」而非「多考試共用平台」）
- 不對教材機密聲明做額外的技術存取控制（如 private repo、Cloudflare Access），比照既有三站現況
