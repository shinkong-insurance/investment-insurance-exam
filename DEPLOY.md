# 部署與維運

## 部署

Flutter 專案在 `app/`，部署腳本在 repo 根目錄，build 後發佈到 `gh-pages` 分支（GitHub Pages）。

```bash
./deploy.sh              # 正式：build + commit + push gh-pages
DRY_RUN=1 ./deploy.sh    # 演練：做到 commit 為止，不 push
```

- 腳本會先檢查 `app/lib/core/services/supabase_config.dart` 與 `app/web/admin.html` 沒有佔位值
  （`REPLACE-WITH-NEW-PROJECT` / `REPLACE_WITH_NEW_ANON_KEY`），否則直接拒絕。
- build 缺 `index.html` 或 `main.dart.js` 也會拒絕，避免 `rsync --delete` 清空站台。
- `gh-pages` 為 orphan 分支，只含 build 產物；worktree 位於 `.gh-pages-worktree/`（已 gitignore）。
- 網址：https://shinkong-insurance.github.io/investment-insurance-exam/

## Supabase keep-alive

Supabase 免費方案專案約 7 天低活動就會被暫停；本站流量低，所以
`.github/workflows/supabase-keepalive.yml` 每天打一次 `license_keys` 查詢。
另外 Public repo 的排程 workflow 在 60 天無 repo 活動後會被自動停用，因此每月 1 號會
提交一次 `.github/keepalive.txt`。

repo 建立後設定兩個 repository variables（anon key 本來就公開於前端 bundle，不需 secret）：

```bash
gh variable set SUPABASE_URL --body "https://<project>.supabase.co" -R shinkong-insurance/investment-insurance-exam
gh variable set SUPABASE_ANON_KEY --body "<anon key>" -R shinkong-insurance/investment-insurance-exam
```

注意：若預設分支啟用 branch protection，會擋下每月的 bot commit，需允許 github-actions[bot] 或排除該規則。

## 備援

若 keep-alive 失敗（GitHub 會寄信給 repo owner）：檢查上述 variables；Supabase 在暫停前約一週
也會寄警告信，專案若已暫停，到 Supabase dashboard 按 Restore 即可。
