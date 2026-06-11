#!/usr/bin/env bash
# Publish latest app to Autodesk Git and update the Pages site (gh-pages branch).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

REMOTE="${1:-origin}"
PAGES_BRANCH="gh-pages"

echo "==> Syncing ${PAGES_BRANCH} from main..."
git checkout "$PAGES_BRANCH"
git checkout main -- \
  index.html \
  custom-symbols.json \
  fonts/ \
  references/ \
  letter_fonts.json \
  letter_pair_exceptions.json \
  letter_ty_glyphs.json \
  preview_grid.png \
  preview_symbols.png

if ! git diff --quiet HEAD; then
  git commit -m "Update Pages site from main ($(date +%Y-%m-%d))."
  echo "Committed Pages update."
else
  echo "Pages branch already matches main deploy files."
fi

echo "==> Pushing main to ${REMOTE}..."
git checkout main
git push "$REMOTE" main

echo "==> Pushing ${PAGES_BRANCH} to ${REMOTE} (updates https://pages.git.autodesk.com/zhouka/Visual-design-tools/)..."
git push "$REMOTE" "$PAGES_BRANCH"

echo "Done. Wait 1–2 minutes, then hard-refresh the Pages URL."
