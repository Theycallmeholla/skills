#!/usr/bin/env bash
# test_smells.sh — surface common test-quality smells
#
# Usage: scripts/test_smells.sh <path>

set -uo pipefail

ROOT="${1:-.}"

if [[ ! -d "$ROOT" ]]; then
  echo "Error: '$ROOT' is not a directory" >&2
  exit 1
fi

cd "$ROOT" || exit 1

IGNORE_DIRS='node_modules|vendor|\.git|dist|build|target|\.venv|venv|__pycache__|\.next|\.nuxt|\.tests-dist|\.turbo|\.parcel-cache|\.svelte-kit|out|coverage|\.cache|bower_components|jspm_packages'

# Test file matchers — extensions we'll search for test files
JS_TEST_FILES='\.(test|spec)\.(js|jsx|ts|tsx|mjs|cjs)$'
PY_TEST_FILES='(test_|_test)\.py$|^test_.*\.py$'
GO_TEST_FILES='_test\.go$'
RB_TEST_FILES='(_spec|_test)\.rb$'
PHP_TEST_FILES='Test\.php$'
JAVA_TEST_FILES='Tests?\.(java|kt)$'

ALL_TEST_FILES_RE="$JS_TEST_FILES|$PY_TEST_FILES|$GO_TEST_FILES|$RB_TEST_FILES|$PHP_TEST_FILES|$JAVA_TEST_FILES"

echo "=========================================="
echo " Test Smell Scan: $ROOT"
echo "=========================================="
echo

list_test_files() {
  find . -type f 2>/dev/null \
    | grep -Ev "/($IGNORE_DIRS)/" \
    | grep -E "$ALL_TEST_FILES_RE"
}

# --- Focused tests (.only / fdescribe / fit) — CRITICAL if in CI ---
echo "── Focused tests (.only, fit, fdescribe) — CRITICAL if committed ────"
FOCUSED=$(list_test_files \
  | xargs -r grep -HInE '\b(describe|it|test)\.only\b|\bfdescribe\b|\bfit\b\s*\(' 2>/dev/null \
  | head -20)
if [[ -n "$FOCUSED" ]]; then
  echo "$FOCUSED"
  echo
  echo "  ⚠ These cause CI to silently skip all other tests in their file/suite."
else
  echo "  None found."
fi
echo

# --- Skipped tests ---
echo "── Skipped tests ────"
SKIPPED_JS=$(list_test_files \
  | grep -E "$JS_TEST_FILES" \
  | xargs -r grep -HInE '\b(describe|it|test)\.skip\b|\bxit\b\s*\(|\bxdescribe\b\s*\(' 2>/dev/null)
SKIPPED_PY=$(list_test_files \
  | grep -E "$PY_TEST_FILES" \
  | xargs -r grep -HInE '@(pytest\.mark\.skip|pytest\.mark\.skipif|unittest\.skip)' 2>/dev/null)
SKIPPED_GO=$(list_test_files \
  | grep -E "$GO_TEST_FILES" \
  | xargs -r grep -HInE 't\.Skip\(' 2>/dev/null)
SKIPPED_RB=$(list_test_files \
  | grep -E "$RB_TEST_FILES" \
  | xargs -r grep -HInE '\b(xit|xdescribe|pending|skip)\b' 2>/dev/null)
SKIPPED_JAVA=$(list_test_files \
  | grep -E "$JAVA_TEST_FILES" \
  | xargs -r grep -HInE '@Disabled|@Ignore' 2>/dev/null)
SKIPPED_PHP=$(list_test_files \
  | grep -E "$PHP_TEST_FILES" \
  | xargs -r grep -HInE 'markTestSkipped|markTestIncomplete' 2>/dev/null)

ALL_SKIPPED=$(printf '%s\n%s\n%s\n%s\n%s\n%s\n' "$SKIPPED_JS" "$SKIPPED_PY" "$SKIPPED_GO" "$SKIPPED_RB" "$SKIPPED_JAVA" "$SKIPPED_PHP" | grep -v '^$')
SKIP_COUNT=$(echo "$ALL_SKIPPED" | grep -c . 2>/dev/null || true)
SKIP_COUNT=${SKIP_COUNT:-0}

if [[ "$SKIP_COUNT" -gt 0 ]]; then
  echo "  Total skipped: $SKIP_COUNT"
  echo
  echo "$ALL_SKIPPED" | head -15
  if [[ "$SKIP_COUNT" -gt 15 ]]; then
    echo "  ... ($SKIP_COUNT total, showing first 15)"
  fi
else
  echo "  None found."
fi
echo

# --- Tautological assertions ---
echo "── Tautological assertions (always-pass) ────"
TAUT=$(list_test_files \
  | xargs -r grep -HInE 'expect\(true\)\.toBe\(true\)|expect\(false\)\.toBe\(false\)|expect\(1\)\.toBe\(1\)|expect\(0\)\.toBe\(0\)|expect\(null\)\.toBe\(null\)|assertEquals\(true,\s*true\)|assertEquals\(false,\s*false\)|assertEquals\(1,\s*1\)|assert\s+True\s*$|assert\s+1\s*==\s*1\b' 2>/dev/null \
  | head -10)
if [[ -n "$TAUT" ]]; then
  echo "$TAUT"
else
  echo "  None obvious. (Heuristic — may have false negatives.)"
fi
echo

# --- Hardcoded sleeps ---
echo "── Hardcoded sleeps in tests (flakiness signal) ────"
SLEEPS=$(list_test_files \
  | xargs -r grep -HInE '\bsleep\s*\(\s*[0-9]+\s*\)|setTimeout\s*\([^,]+,\s*[0-9]{3,}\s*\)|Thread\.sleep\s*\(\s*[0-9]+\s*\)' 2>/dev/null \
  | head -15)
if [[ -n "$SLEEPS" ]]; then
  SLEEP_COUNT=$(echo "$SLEEPS" | wc -l)
  echo "  Occurrences (sample):"
  echo "$SLEEPS" | head -10
  echo "  Total: $SLEEP_COUNT — review for flakiness"
else
  echo "  None found."
fi
echo

# --- Tests hitting real services ---
echo "── Tests referencing real-looking URLs / hosts ────"
URLS=$(list_test_files \
  | xargs -r grep -HInE 'https?://(api|www)\.[a-zA-Z0-9-]+\.(com|net|org|io|co)' 2>/dev/null \
  | grep -vE 'example\.(com|org|net)|localhost|127\.0\.0\.1|test\.com|0\.0\.0\.0' \
  | head -10)
if [[ -n "$URLS" ]]; then
  echo "$URLS"
  echo
  echo "  ⚠ These may indicate tests that hit real services. Verify each."
else
  echo "  None found."
fi
echo

# --- Tests with no assertions (heuristic: no expect/assert in test body) ---
echo "── Test files possibly missing assertions (heuristic) ────"

# JS/TS: count test cases vs assertion-like calls per file
JS_NO_ASSERT=$(list_test_files \
  | grep -E "$JS_TEST_FILES" \
  | while read -r f; do
      cases=$(grep -cE '^\s*(it|test)\s*\(' "$f" 2>/dev/null || true)
      asserts=$(grep -cE '\b(expect|assert|should)\b' "$f" 2>/dev/null || true)
      cases=${cases:-0}
      asserts=${asserts:-0}
      if [[ "$cases" -gt 0 && "$asserts" -lt "$cases" ]]; then
        printf "  %s — %d cases, %d assertions\n" "$f" "$cases" "$asserts"
      fi
    done | head -10)
[[ -n "$JS_NO_ASSERT" ]] && { echo "  JS/TS files where assertions < test cases:"; echo "$JS_NO_ASSERT"; echo; }

# Python: count def test_ vs assert
PY_NO_ASSERT=$(list_test_files \
  | grep -E "$PY_TEST_FILES" \
  | while read -r f; do
      cases=$(grep -cE '^\s*def test_' "$f" 2>/dev/null || true)
      asserts=$(grep -cE '\bassert\b' "$f" 2>/dev/null || true)
      cases=${cases:-0}
      asserts=${asserts:-0}
      if [[ "$cases" -gt 0 && "$asserts" -lt "$cases" ]]; then
        printf "  %s — %d cases, %d asserts\n" "$f" "$cases" "$asserts"
      fi
    done | head -10)
[[ -n "$PY_NO_ASSERT" ]] && { echo "  Python files where asserts < test cases:"; echo "$PY_NO_ASSERT"; echo; }

# --- Excessive mocking ---
echo "── Heavy mock usage ────"
HEAVY_MOCK=$(list_test_files \
  | while read -r f; do
      mocks=$(grep -cE '\b(mock|jest\.mock|jest\.fn|sinon\.|@patch|MagicMock|when\(|Mockito\.)' "$f" 2>/dev/null || true)
      mocks=${mocks:-0}
      if [[ "$mocks" -gt 10 ]]; then
        printf "  %4d mock-like calls: %s\n" "$mocks" "$f"
      fi
    done | sort -rn | head -10)
if [[ -n "$HEAVY_MOCK" ]]; then
  echo "$HEAVY_MOCK"
  echo "  ⚠ Files with very heavy mocking may be testing mocks rather than code."
else
  echo "  No files with extreme mock counts (>10 calls)."
fi
echo

# --- Snapshot test usage ---
echo "── Snapshot test usage ────"
SNAP=$(list_test_files \
  | xargs -r grep -lHE 'toMatchSnapshot|assertSnapshot|matchInlineSnapshot' 2>/dev/null | wc -l)
SNAP_DIRS=$(find . -type d -name '__snapshots__' 2>/dev/null | grep -Ev "/($IGNORE_DIRS)/" | wc -l)
echo "  Files using snapshot assertions: $SNAP"
echo "  __snapshots__ directories: $SNAP_DIRS"
if [[ "$SNAP" -gt 20 ]]; then
  echo "  ⚠ Heavy snapshot usage — review process is critical or these become rubber stamps"
fi
echo

# --- TODO/FIXME in test files (often indicates incomplete tests) ---
echo "── TODOs in test files ────"
TODOS_IN_TESTS=$(list_test_files \
  | xargs -r grep -HInE '\b(TODO|FIXME|XXX)\b' 2>/dev/null \
  | head -10)
if [[ -n "$TODOS_IN_TESTS" ]]; then
  echo "$TODOS_IN_TESTS"
else
  echo "  None found."
fi
echo

# --- Hidden assertions in setup ---
echo "── Assertions inside setup hooks (beforeEach / beforeAll / setUp) ────"
# Walk each test file with awk; find lines between a hook opener and its closer that contain assertions.
SETUP_HITS=$(list_test_files \
  | grep -E "$JS_TEST_FILES" \
  | while read -r f; do
      [[ -z "$f" ]] && continue
      awk -v file="$f" '
        # Track hook entry: lines like beforeEach(... { or beforeAll(async () => {
        /^[[:space:]]*(beforeEach|beforeAll|before)[[:space:]]*\(/ {
          in_hook = 1
          depth = 0
          start_line = NR
          # count opening braces on this line
          for (i = 1; i <= length($0); i++) {
            c = substr($0, i, 1)
            if (c == "{") depth++
            else if (c == "}") depth--
          }
          next
        }
        in_hook {
          for (i = 1; i <= length($0); i++) {
            c = substr($0, i, 1)
            if (c == "{") depth++
            else if (c == "}") depth--
          }
          # Look for assertion-like calls inside the hook body
          if (/(^|[^A-Za-z0-9_])(expect|assert|should\.|chai\.)[[:space:]]*\(/) {
            printf "%s:%d: %s\n", file, NR, $0
          }
          if (depth <= 0) { in_hook = 0 }
        }
      ' "$f"
    done | head -15)

# Python: assert inside setUp / setUpClass / fixture-decorated functions
SETUP_HITS_PY=$(list_test_files \
  | grep -E "$PY_TEST_FILES" \
  | while read -r f; do
      [[ -z "$f" ]] && continue
      awk -v file="$f" '
        /^[[:space:]]*def[[:space:]]+(setUp|setUpClass|tearDown|tearDownClass)[[:space:]]*\(/ {
          in_setup = 1
          start_indent = match($0, /[^ ]/)
          next
        }
        in_setup {
          # leave when indentation drops to or below def line
          this_indent = match($0, /[^ ]/)
          if (this_indent > 0 && this_indent <= start_indent && !/^[[:space:]]*$/) { in_setup = 0; next }
          if (/^[[:space:]]*assert([^A-Za-z0-9_]|$)/) {
            printf "%s:%d: %s\n", file, NR, $0
          }
        }
      ' "$f"
    done | head -10)

if [[ -n "$SETUP_HITS" || -n "$SETUP_HITS_PY" ]]; then
  echo "  ⚠ Found assertion-like calls inside setup/teardown hooks:"
  [[ -n "$SETUP_HITS" ]] && echo "$SETUP_HITS"
  [[ -n "$SETUP_HITS_PY" ]] && echo "$SETUP_HITS_PY"
  echo
  echo "  Assertions in setup produce 'setup failed' errors instead of meaningful test failures."
  echo "  Move them into test bodies, or convert to a real precondition check."
else
  echo "  None found."
fi
echo

# --- Test name quality (vague names) ---
echo "── Vague test names ────"
VAGUE=$(list_test_files \
  | xargs -r grep -HInE "(it|test)\s*\(\s*['\"](works|test [0-9]+|tests?|returns? (true|false)|test_[0-9]+|foo|bar|baz)['\"]" 2>/dev/null \
  | head -10)
if [[ -n "$VAGUE" ]]; then
  echo "$VAGUE"
else
  echo "  None obvious."
fi
echo

# --- Long test files ---
echo "── Test files over 500 lines (often god-files of tests) ────"
list_test_files \
  | xargs -I{} wc -l "{}" 2>/dev/null \
  | awk '$1 > 500' \
  | sort -rn \
  | head -10 \
  | awk '{printf "  %5d lines: %s\n", $1, $2}'
echo

# --- Tests in source directories vs test directories ---
echo "── Test file location patterns ────"
IN_SRC=$(list_test_files | grep -E '/(src|lib|app)/' | wc -l)
IN_TEST_DIR=$(list_test_files | grep -E '/(test|tests|__tests__|spec)/' | wc -l)
ELSEWHERE=$(list_test_files | grep -vE '/(src|lib|app|test|tests|__tests__|spec)/' | wc -l)

[[ "$IN_SRC" -gt 0 ]]      && echo "  Tests alongside source (in src/lib/app):  $IN_SRC"
[[ "$IN_TEST_DIR" -gt 0 ]] && echo "  Tests in dedicated test directories:      $IN_TEST_DIR"
[[ "$ELSEWHERE" -gt 0 ]]   && echo "  Tests in other locations:                 $ELSEWHERE"
echo

echo "=========================================="
echo " Smell scan complete."
echo "=========================================="
