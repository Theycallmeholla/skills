#!/usr/bin/env bash
# find_smells.sh — surface common code smells: oversized files, TODO markers,
#                  dangerous patterns, suspicious code shapes
#
# Usage: scripts/find_smells.sh <path>

set -uo pipefail

ROOT="${1:-.}"

if [[ ! -d "$ROOT" ]]; then
  echo "Error: '$ROOT' is not a directory" >&2
  exit 1
fi

cd "$ROOT" || exit 1

IGNORE_DIRS='node_modules|vendor|\.git|dist|build|target|\.venv|venv|__pycache__|\.next|\.nuxt|out|coverage|\.cache|bower_components|jspm_packages'
SOURCE_EXTS='\.(js|jsx|mjs|cjs|ts|tsx|py|rb|php|go|rs|java|kt|cs|c|cpp|swift|vue|svelte|sh|bash)$'

echo "=========================================="
echo " Code smell scan: $ROOT"
echo "=========================================="
echo

# --- Oversized files ---
echo "── Files over 500 lines (refactor candidates) ────"
find . -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -E "$SOURCE_EXTS" \
  | xargs -I{} wc -l "{}" 2>/dev/null \
  | awk '$1 > 500' \
  | sort -rn \
  | head -20 \
  | awk '{printf "  %6d  %s\n", $1, $2}'
echo

# --- TODO / FIXME / HACK / XXX markers ---
echo "── TODO / FIXME / HACK / XXX markers ────"
TODO_HITS=$(find . -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -E "$SOURCE_EXTS" \
  | xargs -r grep -HInE '\b(TODO|FIXME|HACK|XXX|BUG)\b' 2>/dev/null \
  | head -30)
if [[ -n "$TODO_HITS" ]]; then
  echo "$TODO_HITS"
  TODO_TOTAL=$(find . -type f 2>/dev/null \
    | grep -Ev "/($IGNORE_DIRS)/" \
    | grep -E "$SOURCE_EXTS" \
    | xargs -r grep -cHE '\b(TODO|FIXME|HACK|XXX|BUG)\b' 2>/dev/null \
    | awk -F: '{s+=$NF} END {print s+0}')
  echo
  if [[ "${TODO_TOTAL:-0}" -gt 30 ]]; then
    echo "  (showing first 30 of $TODO_TOTAL total)"
  else
    echo "  ($TODO_TOTAL total)"
  fi
else
  echo "  None found."
fi
echo

# --- Empty catch blocks (silent error swallowing) ---
echo "── Empty catch blocks ────"
find . -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -E '\.(js|jsx|ts|tsx|java|cs)$' \
  | xargs -r grep -HInE 'catch\s*\([^)]*\)\s*\{\s*\}' 2>/dev/null \
  | head -10
echo

echo "── Bare 'except:' in Python ────"
find . -type f -name '*.py' 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | xargs -r grep -HInE '^\s*except\s*:' 2>/dev/null \
  | head -10
echo

# --- Eval and friends ---
echo "── eval / new Function / exec patterns ────"
find . -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -E "$SOURCE_EXTS" \
  | xargs -r grep -HInE '\b(eval|exec|new Function)\s*\(' 2>/dev/null \
  | grep -vE '/(test|tests|spec|__tests__)/' \
  | head -15
echo

# --- Commented-out code blocks (heuristic: 5+ consecutive comment lines that look like code) ---
echo "── Long commented-out blocks (heuristic) ────"
# Look for files with many consecutive commented lines containing code-like punctuation
# This is a rough heuristic; expect noise
find . -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -E '\.(js|jsx|ts|tsx|py|rb|php|go|java)$' \
  | while read -r f; do
      count=$(awk '
        /^[[:space:]]*(\/\/|#).*[(){};=]/ { c++; if (c >= 5) { print FILENAME; exit } next }
        { c = 0 }
      ' "$f" 2>/dev/null)
      [[ -n "$count" ]] && echo "  $count"
    done | sort -u | head -10
echo

# --- console.log / print debugging left behind ---
echo "── Possible debug prints left in source ────"
find . -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -E '\.(js|jsx|ts|tsx)$' \
  | xargs -r grep -HInE '\bconsole\.(log|debug|info)\b' 2>/dev/null \
  | grep -vE '/(test|tests|spec|__tests__)/' \
  | head -10

PRINT_HITS=$(find . -type f -name '*.py' 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | xargs -r grep -HInE '^\s*print\s*\(' 2>/dev/null \
  | grep -vE '/(test|tests|spec)/' \
  | head -5)
[[ -n "$PRINT_HITS" ]] && { echo; echo "  Python print() in non-test files:"; echo "$PRINT_HITS"; }
echo

# --- Disabled lint / typecheck escapes ---
echo "── Suppressed lint / type errors ────"
find . -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -E "$SOURCE_EXTS" \
  | xargs -r grep -HInE '@ts-ignore|@ts-nocheck|@ts-expect-error|eslint-disable|# type: ignore|# noqa\b|@SuppressWarnings' 2>/dev/null \
  | head -15
echo

# --- Wildcard imports (smell in most languages) ---
echo "── Wildcard imports ────"
find . -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -E '\.(js|ts|py|java)$' \
  | xargs -r grep -HInE 'import \*|from .+ import \*' 2>/dev/null \
  | head -10
echo

# --- 'any' type usage in TypeScript ---
TS_FILES=$(find . -type f \( -name '*.ts' -o -name '*.tsx' \) 2>/dev/null | grep -Ev "/($IGNORE_DIRS)/" | head -1)
if [[ -n "$TS_FILES" ]]; then
  echo "── TypeScript ': any' usage ────"
  ANY_COUNT=$(find . -type f \( -name '*.ts' -o -name '*.tsx' \) 2>/dev/null \
    | grep -Ev "/($IGNORE_DIRS)/" \
    | xargs -r grep -cHE ':\s*any\b|<any>|as any\b' 2>/dev/null \
    | awk -F: '{s+=$NF} END {print s+0}')
  echo "  Total ': any' / 'as any' / '<any>' occurrences: $ANY_COUNT"
  if [[ "$ANY_COUNT" -gt 0 ]]; then
    echo "  Top files by 'any' usage:"
    find . -type f \( -name '*.ts' -o -name '*.tsx' \) 2>/dev/null \
      | grep -Ev "/($IGNORE_DIRS)/" \
      | xargs -r grep -cHE ':\s*any\b|<any>|as any\b' 2>/dev/null \
      | awk -F: '$NF > 0 {print $0}' \
      | sort -t: -k2 -rn \
      | head -8 \
      | awk -F: '{printf "    %4d  %s\n", $NF, $1}'
  fi
  echo
fi

# --- Synchronous I/O in Node (perf smell) ---
NODE_FILES=$(find . -type f \( -name '*.js' -o -name '*.ts' \) 2>/dev/null | grep -Ev "/($IGNORE_DIRS)/" | head -1)
if [[ -n "$NODE_FILES" ]]; then
  echo "── Synchronous fs / exec in Node code ────"
  find . -type f \( -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' \) 2>/dev/null \
    | grep -Ev "/($IGNORE_DIRS)/" \
    | xargs -r grep -HInE '\b(readFileSync|writeFileSync|existsSync|readdirSync|statSync|execSync|spawnSync)\b' 2>/dev/null \
    | grep -vE '/(test|tests|spec|__tests__|scripts/|bin/)' \
    | head -10
  echo
fi

# --- Disabled TLS verification (security smell, also a quality smell) ---
echo "── Disabled TLS verification ────"
find . -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -E "$SOURCE_EXTS" \
  | xargs -r grep -HInE 'verify\s*=\s*False|rejectUnauthorized\s*:\s*false|InsecureSkipVerify\s*:\s*true|VERIFY_NONE|CURLOPT_SSL_VERIFYPEER\s*=>\s*(false|0)' 2>/dev/null \
  | head -10
echo

# --- Long function detection (heuristic) ---
echo "── Functions over 80 lines (heuristic, may have false positives) ────"
LONGFN_FILES=$(find . -type f \( -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' -o -name '*.py' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/")
LONGFN_COUNT=$(printf '%s\n' "$LONGFN_FILES" | grep -c .)
if [[ "$LONGFN_COUNT" -gt 200 ]]; then
  echo "  note: sampled first 200 of $LONGFN_COUNT files"
fi
printf '%s\n' "$LONGFN_FILES" \
  | head -200 \
  | while read -r f; do
      awk -v file="$f" '
        # Detect function start (simplified)
        /^([[:space:]]*(export[[:space:]]+)?(async[[:space:]]+)?function([^A-Za-z0-9_]|$)|[[:space:]]*(const|let|var)[[:space:]]+[A-Za-z0-9_]+[[:space:]]*=[[:space:]]*(async[[:space:]]+)?\(.*\)[[:space:]]*=>[[:space:]]*\{|[[:space:]]*def[[:space:]]+[A-Za-z0-9_]+|[[:space:]]*[A-Za-z0-9_]+[[:space:]]*\(.*\)[[:space:]]*\{)/ {
          if (in_fn && lines > 80) {
            printf "  %4d lines: %s:%d\n", lines, file, start_line
          }
          in_fn = 1; lines = 0; start_line = NR; next
        }
        in_fn { lines++ }
        END {
          if (in_fn && lines > 80) printf "  %4d lines: %s:%d\n", lines, file, start_line
        }
      ' "$f" 2>/dev/null
    done | sort -rn | head -10
echo

# --- Deeply nested directories (architecture smell) ---
echo "── Deepest directory paths ────"
find . -type d 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | awk -F/ '{print NF-1, $0}' \
  | sort -rn \
  | head -5 \
  | awk '{printf "  depth %d: %s\n", $1, $2}'

echo
echo "=========================================="
echo " Smell scan complete."
echo "=========================================="
