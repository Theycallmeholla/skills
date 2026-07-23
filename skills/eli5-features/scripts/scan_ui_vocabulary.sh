#!/usr/bin/env bash
# scan_ui_vocabulary.sh — extract user-facing strings from a codebase so the
# ELI5 doc can use the exact same words the user sees on screen.
#
# Usage: scripts/scan_ui_vocabulary.sh <repo-path> [optional-subdir-filter]

set -uo pipefail

ROOT="${1:-.}"
FILTER="${2:-}"  # optional: limit scan to a subdirectory

if [[ ! -d "$ROOT" ]]; then
  echo "Error: '$ROOT' is not a directory" >&2
  exit 1
fi

cd "$ROOT" || exit 1

IGNORE_DIRS='node_modules|vendor|\.git|dist|build|target|\.venv|venv|__pycache__|\.next|\.nuxt|\.tests-dist|out|coverage|\.cache|bower_components'

SEARCH_PATH="."
if [[ -n "$FILTER" ]]; then
  if [[ -d "$FILTER" ]]; then
    SEARCH_PATH="$FILTER"
  else
    echo "Warning: filter dir '$FILTER' not found, scanning whole repo" >&2
  fi
fi

echo "=========================================="
echo " UI Vocabulary Scan"
echo " Root: $ROOT"
[[ -n "$FILTER" ]] && echo " Scope: $FILTER"
echo "=========================================="
echo

# --- Translation / i18n files (ground truth) ---
echo "── Translation files ────"
I18N_FILES=$(find "$SEARCH_PATH" -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -iE '/(locales?|i18n|translations?|messages)/.*\.(json|js|ts|yaml|yml|po)$' \
  | head -10)

if [[ -n "$I18N_FILES" ]]; then
  echo "  Found i18n files (ground truth for UI strings):"
  echo "$I18N_FILES" | sed 's/^/    /'
  echo
  echo "  ⚠ These contain the exact UI strings. Read them directly for verbatim labels."
else
  echo "  No i18n files detected. Scraping JSX strings instead."
fi
echo

# --- Button labels (JSX) ---
echo "── Button labels (JSX <Button> / <button>) ────"
# Two passes: plain text content, and string literals inside JSX expressions like {cond ? 'A' : 'B'}
BTN_TEXT=$(find "$SEARCH_PATH" -type f \( -name '*.jsx' -o -name '*.tsx' -o -name '*.vue' -o -name '*.svelte' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | xargs -r grep -hE '<[Bb]utton[^/>]*>' 2>/dev/null)

# Pass A: literal text content
echo "$BTN_TEXT" \
  | grep -oE '<[Bb]utton[^>]*>\s*[A-Z][^<{]+' \
  | sed -E 's/.*>[[:space:]]*//' \
  | sed 's/[[:space:]]*$//' \
  | sort -u | head -15 \
  | sed 's/^/  /'

# Pass B: string literals embedded near Button (ternary expressions, conditional rendering)
# Look at the file regions around Button declarations
find "$SEARCH_PATH" -type f \( -name '*.jsx' -o -name '*.tsx' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | xargs -r grep -hE -A 1 '<[Bb]utton\b' 2>/dev/null \
  | grep -oE "'[A-Z][a-zA-Z][^']{1,40}'" \
  | sort -u | head -10 \
  | sed "s/^/  (in Button expr) /"
echo

# --- aria-label / title attributes ---
echo "── aria-label / title attributes ────"
find "$SEARCH_PATH" -type f \( -name '*.jsx' -o -name '*.tsx' -o -name '*.html' -o -name '*.vue' -o -name '*.svelte' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | xargs -r grep -hE '(aria-label|title)="[^"]+"' 2>/dev/null \
  | grep -oE '(aria-label|title)="[^"]+"' \
  | sort -u | head -20 \
  | sed 's/^/  /'
echo

# --- Page titles ---
echo "── Page titles (<title>, metadata.title, document.title) ────"
find "$SEARCH_PATH" -type f \( -name '*.jsx' -o -name '*.tsx' -o -name '*.html' -o -name '*.ts' -o -name '*.js' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | xargs -r grep -hE '<title[^>]*>[^<]+</title>|title:\s*["'\''][^"'\'']+["'\'']|document\.title\s*=\s*["'\''][^"'\'']+' 2>/dev/null \
  | grep -oE '<title[^>]*>[^<]+|title:\s*["'\''][^"'\'']+["'\'']|document\.title\s*=\s*["'\''][^"'\'']+' \
  | sort -u | head -20 \
  | sed 's/^/  /'
echo

# --- Headings (h1, h2 in JSX) ---
echo "── Headings (h1, h2) ────"
find "$SEARCH_PATH" -type f \( -name '*.jsx' -o -name '*.tsx' -o -name '*.html' -o -name '*.vue' -o -name '*.svelte' -o -name '*.md' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | xargs -r grep -hE '<h[12][^>]*>\s*[A-Z][^<{]+' 2>/dev/null \
  | grep -oE '<h[12][^>]*>\s*[A-Z][^<{]+' \
  | sed -E 's/.*>[[:space:]]*//' \
  | sed 's/[[:space:]]*$//' \
  | sort -u | head -20 \
  | sed 's/^/  /'
echo

# --- Form field labels and placeholders ---
echo "── Form field labels and placeholders ────"
find "$SEARCH_PATH" -type f \( -name '*.jsx' -o -name '*.tsx' -o -name '*.html' -o -name '*.vue' -o -name '*.svelte' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | xargs -r grep -hE 'placeholder="[^"]+"|<label[^>]*>[^<]+</label>' 2>/dev/null \
  | grep -oE 'placeholder="[^"]+"|<label[^>]*>[^<]+' \
  | sort -u | head -20 \
  | sed 's/^/  /'
echo

# --- Status / state names (common patterns) ---
echo "── Likely status / state names ────"
# Case-insensitive match for status/state assignments AND type unions like type Status = 'A' | 'B'
find "$SEARCH_PATH" -type f \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | xargs -r grep -hEi "(status|state)\s*[:=]|type\s+(status|state)\s*=" 2>/dev/null \
  | grep -oE '["'\''][A-Z][a-zA-Z _-]{2,40}["'\'']' \
  | sort -u | head -20 \
  | sed 's/^/  /'
echo

# --- Centralized copy files ---
echo "── Centralized copy/strings files ────"
COPY_FILES=$(find "$SEARCH_PATH" -type f \( -name 'copy.*' -o -name 'strings.*' -o -name 'labels.*' -o -name 'messages.*' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | head -10)
if [[ -n "$COPY_FILES" ]]; then
  echo "$COPY_FILES" | sed 's/^/  /'
  echo
  echo "  ⚠ These often contain the exact UI strings — read them directly."
else
  echo "  None found."
fi
echo

# --- Navigation / route names ---
echo "── Navigation / route names ────"
find "$SEARCH_PATH" -type f \( -name '*.tsx' -o -name '*.jsx' -o -name '*.ts' -o -name '*.js' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | xargs -r grep -hE '<Link[^>]+>[^<]+|<NavLink[^>]+>[^<]+|<MenuItem[^>]+>[^<]+' 2>/dev/null \
  | grep -oE '>\s*[A-Z][a-zA-Z &-]+\s*$|>\s*[A-Z][a-zA-Z &-]+\s*<' \
  | sed -E 's/^>[[:space:]]*//' \
  | sed 's/[[:space:]]*<$//' \
  | sort -u | head -15 \
  | sed 's/^/  /'
echo

echo "=========================================="
echo " Vocabulary scan complete."
echo "=========================================="
echo
echo "Next: pick the terms relevant to the feature being documented."
echo "Use those exact words (with same capitalization) in the doc."
