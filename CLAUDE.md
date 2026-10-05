# 投資型保險考照網站

**這份文件假設你對這個 repo 完全沒有記憶，寫了完整現況、所有已經做的決策、和
下一步要做什麼，不要憑印象或猜測跳過它。**

## 目前狀態（2026-10-05 晚上，交接點）

**還沒開始寫程式。** 目前只完成了 brainstorming（設計規格）與 writing-plans（實作計畫），
兩份文件都已寫好並 commit 在這個 repo：

- 設計規格：[`docs/superpowers/specs/2026-10-05-investment-insurance-exam-design.md`](docs/superpowers/specs/2026-10-05-investment-insurance-exam-design.md)
- 實作計畫：[`docs/superpowers/plans/2026-10-05-investment-insurance-exam.md`](docs/superpowers/plans/2026-10-05-investment-insurance-exam.md)（**14 個 Task，從這裡接續執行**）

**下一步**：從實作計畫的 **Task 1** 開始執行（複製 `insurance-exam-app` 建立新專案骨架）。
使用者尚未選擇執行方式（subagent-driven 逐任務派發 vs. inline 在對話中批次執行），
下次接續時先問一次要用哪種。

## 這個專案是什麼

新光人壽「投資型保險商品業務員資格測驗」練習網站，比照公司既有三個同系列產品
（`insurance-exam-app` 人壽壽險、`property-insurance-exam`、`currency-insurance-exam` 外幣保單）
再加一個第四站。學生用 `#/lk` 自助註冊（姓名/單位/員編），自動取得 60 天使用權限，
練習 10 章題庫＋兩科官方考古題模考；後台 `admin.html` 管理學生名單與統計。

## 關鍵決策（重要：不要重新討論這些，直接採用）

讀 spec 文件的「修訂記錄」段落可以看到完整的決策演變過程，這裡只列最終結論：

1. **複製基底是 `insurance-exam-app`，不是 `currency-insurance-exam`**——雖然一開始以為
   後者更合適（它已經有姓名/單位/員編的 `#/lk` 變體），但深入看過 currency 站實際原始碼後
   發現它的題庫內容已經演化成存在 Supabase、有 `reviewed` 審核閘門、外加關卡/口訣卡/講義
   viewer 這些本案不需要的複雜度。改用 `insurance-exam-app`（本來就是靜態 JSON 架構）當基底，
   只從 currency 站移植「`#/lk` 姓名/單位/員編」這一個變體的具體檔案。

2. **科目模考不用新寫測驗引擎**——`insurance-exam-app` 本來就有 `courseId = chapterId ~/ 100`
   的慣例，且 `ExamPage` 的 `getRandomQuestions(count, chapterId:)` 在 `count >= 題庫總數` 時
   效果就是「全部出題、每次洗牌」。所以第一科/第二科模考直接做成兩個「虛擬章節」
   （`chapterId 201/202`），**不建 `chapters.json` 條目**（章節列表只讀 `chapters.json`，
   不會自動顯示沒條目的 chapterId），零新增 Dart 邏輯。

3. **兩個「零額外開發」的使用者決策**：科目模考答錯共用一般章節練習同一本錯題本；
   科目模考每次作答沿用既有洗牌邏輯，不強制對應官方原始題號順序。

4. **機密教材聲明保留原樣**——每份講義 PDF 都載明「僅供內部教學使用，不得對外展示或散布」，
   使用者已確認公司內部有控管機制，比照既有三站現況（Public repo + GitHub Pages），
   不另外做存取限制設計。

5. **科目模考內容來源已核對確認**——每科目實際有兩份來源 xlsx（UMU 平台既有題庫 vs.
   「11501」批次上傳模板），逐題比對後發現部分重複（第一科 5 題、第二科 19 題），其中
   5 題正解矛盾（第一科 1 題、第二科 4 題），**已經使用者逐題核對確認：正解一律以 UMU
   版為準**。去重後最終題數：第一科 95 題、第二科 181 題。

6. **localStorage 要加 `inv_` 前綴**——三個既有站台共用同一個 GitHub Pages 網域
   `shinkong-insurance.github.io`（只是 path 不同），localStorage 以 origin 為界不分 path，
   沒有前綴會跟其他站台的登入 session 互相污染。

7. **原始教材檔案（PDF/xlsx/ppt）一律留在 `source-materials/`，已 gitignore，不進 git
   history**——這些是機密內部教材，只有解析後的 `questions.json`/`sections.json` 會進 repo。

## 原始素材現況

`source-materials/` 底下：10 份章節 PDF（已轉檔完成並通過品管，第八章原本遺漏已補轉）、
10 份對應的 UMU 章節題庫 xlsx、4 份科目模考相關 xlsx（每科各兩份來源，見上方決策 5）。
盤點與品管細節見 spec 文件「原始素材盤點」段落。

## 執行時的具體地雷（已經在計畫裡標注，這裡再提醒一次最容易漏掉的）

- `/exam` 路由的 query 參數叫 `chapter`，**不是** `chapterId`（已對照 `insurance-exam-app`
  的 `lib/app/router.dart` 逐字確認）
- `course.json` 在 `insurance-exam-app` 裡完全沒被引用，是死檔案，不用處理
- `admin.html` 用真的 Supabase Auth 帳號登入（`signInWithPassword`），不是存在自訂表的密碼，
  Task 5 要記得在 Supabase Dashboard 建帳號
- 部署腳本故意用 git worktree 而非裸 rsync 到猜測的路徑——`insurance-exam-app` 之前真的因為
  rsync 路徑誤配刪過 assets（事後用 git checkout 救回），這次要避免重演

## 下次接續時怎麼做

1. 讀這份文件 + 實作計畫文件的 Task 1
2. 問使用者要 subagent-driven 還是 inline 執行
3. 照計畫逐一完成 Task 1 → Task 14，每個 Task 做完記得 commit（計畫裡每個 Task 都寫了
   commit 的 step，不要跳過）
