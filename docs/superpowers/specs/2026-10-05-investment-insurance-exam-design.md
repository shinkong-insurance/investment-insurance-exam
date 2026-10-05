# 投資型保險考照網站 — 設計規格

- 日期：2026-10-05
- 狀態：已核准（brainstorming 完成，待寫實作計畫）
- 參考範本：`shinkong-insurance/currency-insurance-exam`（非 `insurance-exam-app`，見下方理由）

## 背景與目標

新光人壽需要一個投資型保險商品業務員資格測驗的練習網站，供員工（單位＋員編身分）自助練習章節題庫與科目模考。公司已有三個同系列產品：

- `insurance-exam-app`（人壽壽險，#/lk 以姓名/手機/考試日期註冊）
- `property-insurance-exam`
- `currency-insurance-exam`（外幣保單，#/lk 以**姓名/單位/員編**註冊，章節練習與科目模考分離）

本專案延續同一套架構與維運模式，新增第四個站台：**investment-insurance-exam**。

選擇以 `currency-insurance-exam` 為複製基底而非 `insurance-exam-app`，因為它已經同時具備：
1. `#/lk` 姓名/單位/員編 的授權變體（跟本案需求一致，不用改欄位邏輯）
2. 章節練習與科目模考分離的內容結構（跟本案「10 章＋第一科/第二科考古題」的結構一致）

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

- 以 `currency-insurance-exam` 現有程式碼為起點，建立全新、乾淨的 Git 歷史（不是 GitHub fork 關係），避免未來兩個產品的 git history 互相干擾
- GitHub repo：`shinkong-insurance/investment-insurance-exam`，Public（與既有三站一致）
- 保留原架構：`lib/app|core|features|models|providers|repositories` 分層、`#/lk` 自助註冊頁、章節練習／科目模考分離
- 需替換：題庫內容（`assets/json/questions.json`、`sections.json`）、品牌文字（app 名稱、首頁標題、favicon/logo）、Supabase 連線設定（指向本案專屬的新 Supabase 專案）

### 2. 內容與題庫資料流程

- **章節講義（10 份 PDF）** → 解析為 `sections.json`，對應「章節閱讀」頁（`section_reading_page.dart`）。每章一個 section，抽取文字重點＋可讀化整理，不做原始投影片排版還原
- **章節練習題（10 份 UMU xlsx，各章一份）** → 解析為按章分組的練習題，沿用 currency 站既有的 xlsx→questions.json 清洗腳本（欄位對應需依本案 xlsx 實際欄位調整，但清洗邏輯本身不重寫）
- **科目模考（第一科／第二科考古題 xlsx）** → 各自解析為獨立模考題組，對應 `mock_paper_page.dart` 的模考模式；**不與章節練習混合**，模考錯題也不回頭歸屬章節（如需讓模考錯題同時掛回對應章節，需使用者另外提出，本規格不包含）
- 統一輸出到 `assets/json/questions.json`（含 `chapter_id` 或 `subject_id` 欄位區分來源）與 `sections.json`；Flutter 端讀靜態 JSON，Supabase 只管授權與作答紀錄，不即時提供題目內容

### 3. 授權（`#/lk`）與後台管理

- 沿用 `currency-insurance-exam` 的 `#/lk` 變體：學生填 **姓名、單位、員編** 三欄即完成自助註冊，系統自動核發 60 天效期授權（`license_keys` 表 `max_uses=0`，不限次數；不使用 `key_sessions`）
- `lk_auth_service.dart` / `lk_gate_page.dart` 直接複製，僅調整品牌文字，欄位結構不變
- 後台 `admin.html`：延續既有三站的學生清單、統計（依單位/員編分組）、到期管理、刪除功能；因本案多了「科目模考」概念，統計頁需新增一個維度 —— 各單位在第一科／第二科模考的作答數與通過率；其餘既有修復（到期篩選、批次刪除、UTC 時區處理）直接沿用
- 管理員登入沿用既有 `admin_login_page.dart` 機制，不另外設計新的權限分層

### 4. Supabase 專案與部署

- 新建獨立 Supabase 專案（新 project ref，不與其他三站共用資料庫）
- 資料表比照 `currency-insurance-exam` 目前 schema：`license_keys`、學生資料表（含姓名/單位/員編欄位）、作答紀錄表；不使用 `key_sessions`
- 套用 currency 站已驗證的 RLS 政策（client 端表開 RLS + 對應 policy，撤銷 TRUNCATE 權限）與對應 migrations，依本案 schema 細節調整後搬入
- `supabase/functions/auto-register-student`：複製後調整欄位驗證邏輯（姓名/單位/員編的必填與格式檢查，取代原本的姓名/手機/考試日期驗證）
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
3. 「模考錯題是否回頭歸屬章節錯題本」目前設計為不歸屬，如需求有變動需使用者明確提出

## 範圍外（本次不做）

- 不建立跨站共用的多租戶平台（經使用者確認採「複製現有專案當模板」而非「多考試共用平台」）
- 不對教材機密聲明做額外的技術存取控制（如 private repo、Cloudflare Access），比照既有三站現況
