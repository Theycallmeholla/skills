#!/usr/bin/env bash
# inspect_target.sh — dump structural info about a single source file to inform test suggestions
#
# Usage: scripts/inspect_target.sh <path/to/file>

set -uo pipefail

TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 <path/to/file>" >&2
  exit 1
fi

if [[ ! -f "$TARGET" ]]; then
  echo "Error: '$TARGET' is not a file" >&2
  exit 1
fi

EXT="${TARGET##*.}"
LOC=$(wc -l < "$TARGET" | tr -d ' ')

echo "=========================================="
echo " Target: $TARGET"
echo "=========================================="
echo

echo "── Basic ────"
echo "  Lines:    $LOC"
echo "  Ext:      .$EXT"
echo

# --- Imports ---
echo "── Imports / requires ────"
case "$EXT" in
  ts|tsx|js|jsx|mjs|cjs)
    grep -nE "^\s*(import|const\s+\{?[^=]+\}?\s*=\s*require)" "$TARGET" 2>/dev/null | head -20
    ;;
  py)
    grep -nE "^\s*(from|import)\s+" "$TARGET" 2>/dev/null | head -20
    ;;
  go)
    awk '/^import \(/,/^\)/' "$TARGET" 2>/dev/null | head -25
    grep -nE "^import\s+\"" "$TARGET" 2>/dev/null | head -10
    ;;
  rb)
    grep -nE "^\s*(require|require_relative)\s+" "$TARGET" 2>/dev/null | head -20
    ;;
  php)
    grep -nE "^\s*(use|require|include)\s+" "$TARGET" 2>/dev/null | head -20
    ;;
  java|kt)
    grep -nE "^\s*import\s+" "$TARGET" 2>/dev/null | head -20
    ;;
  rs)
    grep -nE "^\s*(use|extern\s+crate)\s+" "$TARGET" 2>/dev/null | head -20
    ;;
  cs)
    grep -nE "^\s*using\s+" "$TARGET" 2>/dev/null | head -20
    ;;
  *)
    echo "  (no import detection for .$EXT)"
    ;;
esac
echo

# --- Exports / public surface ---
echo "── Public surface (exports / public functions) ────"
case "$EXT" in
  ts|tsx|js|jsx|mjs|cjs)
    grep -nE "^\s*export\s+(default\s+)?(async\s+)?(function|const|let|var|class|interface|type|enum)" "$TARGET" 2>/dev/null
    grep -nE "^\s*export\s*\{" "$TARGET" 2>/dev/null
    grep -nE "^\s*module\.exports\s*=" "$TARGET" 2>/dev/null
    ;;
  py)
    # Module-level functions and classes (not indented)
    grep -nE "^(async\s+)?def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(" "$TARGET" 2>/dev/null
    grep -nE "^class\s+[A-Z][a-zA-Z0-9_]*" "$TARGET" 2>/dev/null
    # __all__ if defined
    grep -nE "^__all__\s*=" "$TARGET" 2>/dev/null
    ;;
  go)
    # Exported = capitalized first letter
    grep -nE "^func\s+(\([^)]+\)\s+)?[A-Z][a-zA-Z0-9_]*\s*\(" "$TARGET" 2>/dev/null
    grep -nE "^type\s+[A-Z][a-zA-Z0-9_]*\s+(struct|interface)" "$TARGET" 2>/dev/null
    ;;
  rb)
    grep -nE "^\s*(def\s+self\.|def\s+)[a-z_][a-z0-9_]*" "$TARGET" 2>/dev/null
    grep -nE "^\s*class\s+[A-Z]" "$TARGET" 2>/dev/null
    grep -nE "^\s*module\s+[A-Z]" "$TARGET" 2>/dev/null
    ;;
  php)
    grep -nE "^\s*(public|protected|private)?\s*(static\s+)?function\s+[a-zA-Z_]" "$TARGET" 2>/dev/null
    grep -nE "^\s*(class|interface|trait)\s+[A-Z]" "$TARGET" 2>/dev/null
    ;;
  java|kt)
    grep -nE "^\s*(public|protected)\s+(static\s+)?(\S+\s+)+[a-zA-Z_][a-zA-Z0-9_]*\s*\(" "$TARGET" 2>/dev/null
    grep -nE "^\s*(public\s+)?(class|interface|object)\s+" "$TARGET" 2>/dev/null
    ;;
  rs)
    grep -nE "^\s*pub\s+(async\s+)?fn\s+[a-z_]" "$TARGET" 2>/dev/null
    grep -nE "^\s*pub\s+(struct|enum|trait)\s+[A-Z]" "$TARGET" 2>/dev/null
    ;;
  cs)
    grep -nE "^\s*public\s+(static\s+)?(\S+\s+)+[A-Z][a-zA-Z0-9_]*\s*\(" "$TARGET" 2>/dev/null
    grep -nE "^\s*public\s+(class|interface|record|struct)\s+" "$TARGET" 2>/dev/null
    ;;
esac
echo

# --- Branches (rough count) ---
echo "── Branch density ────"
IF_COUNT=$(grep -cE '\bif\s*\(|\bif\s+[a-zA-Z_]' "$TARGET" 2>/dev/null || true)
SWITCH_COUNT=$(grep -cE '\bswitch\s*\(|\bcase\s+[A-Z_a-z0-9]' "$TARGET" 2>/dev/null || true)
TERNARY_COUNT=$(grep -cE '\?\s*[^:]+\s*:\s*' "$TARGET" 2>/dev/null || true)
EARLY_RETURN=$(grep -cE '^\s*(return|throw|raise|panic\(|t\.Fatal)' "$TARGET" 2>/dev/null || true)
IF_COUNT=${IF_COUNT:-0}
SWITCH_COUNT=${SWITCH_COUNT:-0}
TERNARY_COUNT=${TERNARY_COUNT:-0}
EARLY_RETURN=${EARLY_RETURN:-0}

printf "  if statements:        %3d\n" "$IF_COUNT"
printf "  switch / case:        %3d\n" "$SWITCH_COUNT"
printf "  ternary expressions:  %3d\n" "$TERNARY_COUNT"
printf "  return / throw / raise: %3d\n" "$EARLY_RETURN"

TOTAL_BRANCHES=$((IF_COUNT + SWITCH_COUNT + TERNARY_COUNT))
echo
if [[ "$TOTAL_BRANCHES" -gt 30 ]]; then
  echo "  ⚠ High branch density — consider whether this should be split before adding tests"
fi
echo

# --- Throw sites / error paths ---
echo "── Throw / reject / panic sites ────"
case "$EXT" in
  ts|tsx|js|jsx|mjs|cjs)
    grep -nE '\bthrow\s+new|\bthrow\s+[A-Z]|Promise\.reject|reject\s*\(' "$TARGET" 2>/dev/null | head -10
    ;;
  py)
    grep -nE '\braise\s+' "$TARGET" 2>/dev/null | head -10
    ;;
  go)
    grep -nE 'return.*err|panic\(|t\.Fatal|fmt\.Errorf' "$TARGET" 2>/dev/null | head -10
    ;;
  rb)
    grep -nE '\braise\s+' "$TARGET" 2>/dev/null | head -10
    ;;
  php)
    grep -nE '\bthrow\s+new' "$TARGET" 2>/dev/null | head -10
    ;;
  java|kt)
    grep -nE 'throw\s+new' "$TARGET" 2>/dev/null | head -10
    ;;
  rs)
    grep -nE 'panic!\(|return\s+Err\(|\?$' "$TARGET" 2>/dev/null | head -10
    ;;
esac
echo

# --- Async / IO indicators ---
echo "── Async / I/O indicators ────"
ASYNC_HITS=$(grep -cE '\b(async|await|Promise|then\s*\(|setImmediate|process\.next)\b' "$TARGET" 2>/dev/null || true)
DB_HITS=$(grep -cE '\b(prisma|knex|sequelize|typeorm|mongoose|db\.|sql\.|query\(|findUnique|findMany|insertOne|execute)\b' "$TARGET" 2>/dev/null || true)
HTTP_HITS=$(grep -cE '\b(fetch\(|axios\.|http\.|got\(|request\(|XMLHttpRequest)\b' "$TARGET" 2>/dev/null || true)
FS_HITS=$(grep -cE '\bfs\.|readFile|writeFile|readdir|os\.path|pathlib' "$TARGET" 2>/dev/null || true)
ENV_HITS=$(grep -cE 'process\.env|os\.environ|os\.getenv|System\.getenv' "$TARGET" 2>/dev/null || true)
ASYNC_HITS=${ASYNC_HITS:-0}
DB_HITS=${DB_HITS:-0}
HTTP_HITS=${HTTP_HITS:-0}
FS_HITS=${FS_HITS:-0}
ENV_HITS=${ENV_HITS:-0}

[[ "$ASYNC_HITS" -gt 0 ]] && printf "  async / promise calls: %3d\n" "$ASYNC_HITS"
[[ "$DB_HITS" -gt 0 ]]    && printf "  DB-like calls:         %3d\n" "$DB_HITS"
[[ "$HTTP_HITS" -gt 0 ]]  && printf "  HTTP calls:            %3d\n" "$HTTP_HITS"
[[ "$FS_HITS" -gt 0 ]]    && printf "  Filesystem calls:      %3d\n" "$FS_HITS"
[[ "$ENV_HITS" -gt 0 ]]   && printf "  process.env reads:     %3d\n" "$ENV_HITS"

if [[ "$ASYNC_HITS" -eq 0 && "$DB_HITS" -eq 0 && "$HTTP_HITS" -eq 0 && "$FS_HITS" -eq 0 ]]; then
  echo "  No I/O detected — likely a pure-logic target (good unit-test candidate)."
fi
echo

# --- Module-level side effects (red flag for testability) ---
echo "── Module-level statements (testability check) ────"
case "$EXT" in
  ts|tsx|js|jsx|mjs|cjs)
    # Look for top-level `new SomeClient(...)` or function calls (not just `const x = ...` literals)
    SIDE_EFFECTS=$(grep -nE '^(const|let|var)\s+[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*new\s+[A-Z]|^[a-zA-Z_][a-zA-Z0-9_]*\s*\(' "$TARGET" 2>/dev/null \
      | grep -vE 'export\s+|=\s*(function|async|\([^)]*\)\s*=>)' | head -5)
    ;;
  py)
    # Module-level non-def, non-class, non-import statements that aren't assignments to literals
    SIDE_EFFECTS=$(grep -nE '^[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[A-Z][a-zA-Z0-9_]*\s*\(' "$TARGET" 2>/dev/null | head -5)
    ;;
  *)
    SIDE_EFFECTS=""
    ;;
esac

if [[ -n "$SIDE_EFFECTS" ]]; then
  echo "  ⚠ Module-level statements that may run on import:"
  echo "$SIDE_EFFECTS" | sed 's/^/    /'
  echo "    These can complicate unit testing — see references/untestable-code.md"
else
  echo "  No obvious module-level side effects."
fi
echo

# --- Find existing tests for this file ---
echo "── Existing tests for this target ────"
BASE=$(basename "$TARGET")
NAME="${BASE%.*}"
DIR=$(dirname "$TARGET")

# Walk up to find repo root (.git or package.json or pyproject.toml)
# Start from absolute path so the walk-up actually crosses directories
ABS_DIR=$(cd "$DIR" 2>/dev/null && pwd) || ABS_DIR="$DIR"
REPO_ROOT="$ABS_DIR"
while [[ "$REPO_ROOT" != "/" && -n "$REPO_ROOT" ]]; do
  if [[ -d "$REPO_ROOT/.git" || -f "$REPO_ROOT/package.json" || -f "$REPO_ROOT/pyproject.toml" || -f "$REPO_ROOT/Cargo.toml" || -f "$REPO_ROOT/go.mod" || -f "$REPO_ROOT/Gemfile" || -f "$REPO_ROOT/composer.json" ]]; then
    break
  fi
  PARENT=$(dirname "$REPO_ROOT")
  [[ "$PARENT" == "$REPO_ROOT" ]] && break
  REPO_ROOT="$PARENT"
done
# Fallback: if no marker found, use current working directory
if [[ "$REPO_ROOT" == "/" || -z "$REPO_ROOT" ]]; then
  REPO_ROOT="$PWD"
fi

# Search for test files referencing this target
EXISTING=$(find "$REPO_ROOT" -type f 2>/dev/null \
  | grep -Ev '/(node_modules|\.git|dist|build|\.tests-dist|\.next|venv|\.venv)/' \
  | grep -E "/(${NAME})\.(test|spec)\.[a-z]+$|/test_${NAME}\.py$|/${NAME}_test\.(go|py|rb)$|/${NAME}_spec\.rb$|/${NAME}Test\.(java|kt|php|cs)$" \
  | head -5)

if [[ -n "$EXISTING" ]]; then
  echo "  Tests found:"
  echo "$EXISTING" | sed 's/^/    /'

  echo
  echo "  Existing test cases (sample):"
  echo "$EXISTING" | head -1 | while read -r tf; do
    grep -nE "^\s*(it|test|describe|def test_|func Test|@Test)" "$tf" 2>/dev/null | head -10 | sed 's/^/    /'
  done
else
  echo "  No tests detected for this target."
fi
echo

echo "=========================================="
echo " Inspection complete."
echo "=========================================="
