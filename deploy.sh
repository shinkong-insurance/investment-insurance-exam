#!/usr/bin/env bash
# deploy.sh — build Flutter web (app/) 並部署到 gh-pages 分支
# 用 git worktree 而非裸 rsync 到隨意路徑；所有路徑皆由本腳本所在目錄推得。
# DRY_RUN=1 ./deploy.sh  → 做到 commit 為止，不 push。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
APP_DIR="$REPO_ROOT/app"
BUILD_DIR="$APP_DIR/build/web"
WORKTREE_DIR="$REPO_ROOT/.gh-pages-worktree"
DRY_RUN="${DRY_RUN:-0}"

# --- [0] 佔位值守門：必須在 build / 動任何 worktree 之前 ---
echo "[0/5] 檢查 Supabase 佔位值"
for f in "$APP_DIR/lib/core/services/supabase_config.dart" "$APP_DIR/web/admin.html"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: 找不到 $f，拒絕部署" >&2
    exit 1
  fi
  if grep -q -e 'REPLACE-WITH-NEW-PROJECT' -e 'REPLACE_WITH_NEW_ANON_KEY' "$f"; then
    echo "ERROR: $f 仍含 Supabase 佔位值 (REPLACE-WITH-NEW-PROJECT / REPLACE_WITH_NEW_ANON_KEY)，拒絕部署" >&2
    exit 1
  fi
done

echo "[1/5] flutter pub get"
cd "$APP_DIR"
flutter pub get

echo "[2/5] flutter build web --release --base-href /investment-insurance-exam/"
flutter build web --release --base-href /investment-insurance-exam/

# --- build 產物守門：避免空/失敗的 build 搭配 rsync --delete 清空站台 ---
if [ ! -f "$BUILD_DIR/index.html" ] || [ ! -f "$BUILD_DIR/main.dart.js" ]; then
  echo "ERROR: $BUILD_DIR 缺少 index.html 或 main.dart.js，build 疑似失敗，拒絕部署" >&2
  exit 1
fi

echo "[3/5] 準備 gh-pages worktree"
cd "$REPO_ROOT"
git worktree prune
if [ ! -d "$WORKTREE_DIR" ]; then
  git fetch origin gh-pages 2>/dev/null || true
  if git show-ref --verify --quiet refs/remotes/origin/gh-pages; then
    git worktree add -B gh-pages "$WORKTREE_DIR" origin/gh-pages
  elif git show-ref --verify --quiet refs/heads/gh-pages; then
    git worktree add "$WORKTREE_DIR" gh-pages
  else
    # 全新 orphan 分支：只放 build 產物，不可帶入原始碼
    git worktree add --detach "$WORKTREE_DIR"
    cd "$WORKTREE_DIR"
    git checkout --orphan gh-pages
    git rm -rf . -q
    cd "$REPO_ROOT"
  fi
fi
if [ "$(git -C "$WORKTREE_DIR" symbolic-ref --short HEAD 2>/dev/null || true)" != "gh-pages" ]; then
  echo "ERROR: $WORKTREE_DIR 不在 gh-pages 分支，拒絕同步" >&2
  exit 1
fi

echo "[4/5] 同步 build 產物到 worktree"
rsync -a --delete --exclude='.git' "$BUILD_DIR/" "$WORKTREE_DIR/"
touch "$WORKTREE_DIR/.nojekyll"

echo "[5/5] commit + push gh-pages"
cd "$WORKTREE_DIR"
git add -A
if git diff --cached --quiet; then
  echo "無變更，略過 commit"
else
  git commit -q -m "deploy: $(date '+%Y-%m-%d %H:%M:%S')"
  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY_RUN=1：略過 push。將會執行：git push origin gh-pages"
    git --no-pager log --stat --oneline -1 | head -20
  else
    git push origin gh-pages
  fi
fi

echo "完成：https://shinkong-insurance.github.io/investment-insurance-exam/"
