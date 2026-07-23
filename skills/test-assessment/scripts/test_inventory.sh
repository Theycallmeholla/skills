#!/usr/bin/env bash
# test_inventory.sh — inventory the test suite of a codebase
#
# Usage: scripts/test_inventory.sh <path>

set -uo pipefail

ROOT="${1:-.}"

if [[ ! -d "$ROOT" ]]; then
  echo "Error: '$ROOT' is not a directory" >&2
  exit 1
fi

cd "$ROOT" || exit 1

IGNORE_DIRS='node_modules|vendor|\.git|dist|build|target|\.venv|venv|__pycache__|\.next|\.nuxt|\.tests-dist|\.turbo|\.parcel-cache|\.svelte-kit|out|coverage|\.cache|bower_components|jspm_packages'

echo "=========================================="
echo " Test Suite Inventory: $ROOT"
echo "=========================================="
echo

# --- Test file detection ---
echo "── Test files by pattern ────"

# JS/TS
JS_TEST_COUNT=$(find . -type f \( -name '*.test.js' -o -name '*.test.jsx' -o -name '*.test.ts' -o -name '*.test.tsx' -o -name '*.test.mjs' -o -name '*.spec.js' -o -name '*.spec.jsx' -o -name '*.spec.ts' -o -name '*.spec.tsx' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" | wc -l)
[[ "$JS_TEST_COUNT" -gt 0 ]] && printf "  JS/TS test files:    %5d\n" "$JS_TEST_COUNT"

# Python
PY_TEST_COUNT=$(find . -type f \( -name 'test_*.py' -o -name '*_test.py' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" | wc -l)
[[ "$PY_TEST_COUNT" -gt 0 ]] && printf "  Python test files:   %5d\n" "$PY_TEST_COUNT"

# Go
GO_TEST_COUNT=$(find . -type f -name '*_test.go' 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" | wc -l)
[[ "$GO_TEST_COUNT" -gt 0 ]] && printf "  Go test files:       %5d\n" "$GO_TEST_COUNT"

# Ruby
RB_TEST_COUNT=$(find . -type f \( -name '*_spec.rb' -o -name '*_test.rb' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" | wc -l)
[[ "$RB_TEST_COUNT" -gt 0 ]] && printf "  Ruby test files:     %5d\n" "$RB_TEST_COUNT"

# PHP
PHP_TEST_COUNT=$(find . -type f -name '*Test.php' 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" | wc -l)
[[ "$PHP_TEST_COUNT" -gt 0 ]] && printf "  PHP test files:      %5d\n" "$PHP_TEST_COUNT"

# Java/Kotlin
JAVA_TEST_COUNT=$(find . -type f \( -name '*Test.java' -o -name '*Tests.java' -o -name '*Test.kt' -o -name '*Tests.kt' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" | wc -l)
[[ "$JAVA_TEST_COUNT" -gt 0 ]] && printf "  Java/Kotlin tests:   %5d\n" "$JAVA_TEST_COUNT"

# Rust
RS_TEST_COUNT=0
if find . -type f -name 'Cargo.toml' 2>/dev/null | grep -Ev "/($IGNORE_DIRS)/" | head -1 | grep -q .; then
  RS_TEST_COUNT=$(find . -type d -name 'tests' 2>/dev/null \
    | grep -Ev "/($IGNORE_DIRS)/" \
    | xargs -r -I{} find {} -type f -name '*.rs' 2>/dev/null | wc -l)
  INLINE_TEST_FILES=$(find . -type f -name '*.rs' 2>/dev/null \
    | grep -Ev "/($IGNORE_DIRS)/" \
    | xargs -r grep -l '#\[test\]' 2>/dev/null | wc -l)
  [[ "$INLINE_TEST_FILES" -gt 0 ]] && printf "  Rust files w/ #[test]: %3d\n" "$INLINE_TEST_FILES"
  [[ "$RS_TEST_COUNT" -gt 0 ]] && printf "  Rust integration tests:%3d\n" "$RS_TEST_COUNT"
fi

# C#
CS_TEST_COUNT=$(find . -type f -name '*Tests.cs' 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" | wc -l)
[[ "$CS_TEST_COUNT" -gt 0 ]] && printf "  C# test files:       %5d\n" "$CS_TEST_COUNT"

TOTAL_TEST_FILES=$((JS_TEST_COUNT + PY_TEST_COUNT + GO_TEST_COUNT + RB_TEST_COUNT + PHP_TEST_COUNT + JAVA_TEST_COUNT + RS_TEST_COUNT + CS_TEST_COUNT))
echo
echo "  Total test files:  $TOTAL_TEST_FILES"
echo

if [[ "$TOTAL_TEST_FILES" -eq 0 ]]; then
  echo "  ⚠ No test files detected by common naming conventions."
  echo "    This codebase appears to have no tests. Verify manually before"
  echo "    concluding — some projects use unusual conventions."
  echo
fi

# --- Source file count for ratio ---
echo "── Source-to-test ratio ────"

# All source
SRC_COUNT=$(find . -type f \( -name '*.js' -o -name '*.jsx' -o -name '*.ts' -o -name '*.tsx' -o -name '*.py' -o -name '*.go' -o -name '*.rb' -o -name '*.php' -o -name '*.java' -o -name '*.kt' -o -name '*.rs' -o -name '*.cs' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -vE '\.(test|spec)\.|_test\.|_spec\.|Test\.(java|cs|kt)|Tests\.(java|cs|kt)' \
  | wc -l | tr -d ' ')

# Logic source: lib/, src/, app/api, services/, domain/, internal/, packages/*/src + non-tsx Python/Go/etc.
LOGIC_COUNT=$(find . -type f \( -name '*.js' -o -name '*.ts' -o -name '*.py' -o -name '*.go' -o -name '*.rb' -o -name '*.php' -o -name '*.java' -o -name '*.kt' -o -name '*.rs' -o -name '*.cs' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -vE '\.(test|spec)\.|_test\.|_spec\.|Test\.(java|cs|kt)|Tests\.(java|cs|kt)' \
  | grep -E '/(lib|src|app/api|services|domain|internal|core|server|backend|utils|helpers|repositories|models|controllers)/' \
  | wc -l | tr -d ' ')

# UI/component source: .tsx, .jsx, components/, pages/, views/, app/**/page.tsx
UI_COUNT=$(find . -type f \( -name '*.tsx' -o -name '*.jsx' -o -name '*.vue' -o -name '*.svelte' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -vE '\.(test|spec)\.' \
  | wc -l | tr -d ' ')

echo "  Source files (all):  $SRC_COUNT"
if [[ "$LOGIC_COUNT" -gt 0 || "$UI_COUNT" -gt 0 ]]; then
  echo "    of which logic:    $LOGIC_COUNT (lib/src/app-api/services/etc — typically test-worthy)"
  echo "    of which UI/comp:  $UI_COUNT (.tsx/.jsx/.vue/.svelte — often untested by design)"
fi
echo "  Test files:          $TOTAL_TEST_FILES"

if [[ "$LOGIC_COUNT" -gt 0 && "$TOTAL_TEST_FILES" -gt 0 ]]; then
  LOGIC_RATIO=$(awk "BEGIN {printf \"%.2f\", $TOTAL_TEST_FILES / $LOGIC_COUNT}")
  echo "  Logic ratio:         $LOGIC_RATIO test files per logic source file (this is the meaningful number)"
  if awk "BEGIN {exit !($LOGIC_RATIO < 0.15)}"; then
    echo "  ⚠ Low logic-test ratio — likely many untested modules"
  fi
fi
if [[ "$SRC_COUNT" -gt 0 && "$TOTAL_TEST_FILES" -gt 0 ]]; then
  RATIO=$(awk "BEGIN {printf \"%.2f\", $TOTAL_TEST_FILES / $SRC_COUNT}")
  echo "  Overall ratio:       $RATIO (includes UI; less meaningful)"
fi
echo

# --- Test framework detection ---
echo "── Test frameworks detected ────"
FRAMEWORKS_FOUND=0

# Jest
if [[ -f package.json ]] && grep -qE '"jest"\s*:' package.json 2>/dev/null; then
  echo "  ✓ Jest (package.json)"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
fi
[[ -f jest.config.js || -f jest.config.ts || -f jest.config.json || -f jest.config.mjs ]] && {
  echo "  ✓ Jest (config file)"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
}

# Vitest
[[ -f vitest.config.js || -f vitest.config.ts || -f vitest.config.mjs ]] && {
  echo "  ✓ Vitest"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
}

# Node native test runner (node:test) — easy to miss because there's no config file
if [[ -f package.json ]]; then
  if grep -qE '"test"\s*:.*node\s+--test' package.json 2>/dev/null; then
    echo "  ✓ Node native test runner (node:test, via npm scripts)"
    FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
  fi
fi
# Also check for direct imports from 'node:test' in source
NODE_TEST_IMPORTS=$(find . -type f \( -name '*.js' -o -name '*.mjs' -o -name '*.ts' -o -name '*.tsx' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | xargs -r grep -lE "(import|require).*['\"]node:test['\"]" 2>/dev/null \
  | head -1)
if [[ -n "$NODE_TEST_IMPORTS" ]]; then
  if ! grep -qE '"test"\s*:.*node\s+--test' package.json 2>/dev/null; then
    echo "  ✓ Node native test runner (node:test, via imports)"
    FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
  fi
fi

# Mocha
[[ -f .mocharc.js || -f .mocharc.json || -f .mocharc.yml || -f .mocharc.cjs ]] && {
  echo "  ✓ Mocha"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
}

# Playwright
[[ -f playwright.config.js || -f playwright.config.ts ]] && {
  echo "  ✓ Playwright"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
}

# Cypress
[[ -f cypress.config.js || -f cypress.config.ts || -d cypress ]] && {
  echo "  ✓ Cypress"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
}

# Pytest
[[ -f pytest.ini || -f conftest.py ]] && {
  echo "  ✓ Pytest"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
}
if [[ -f pyproject.toml ]] && grep -qE '\[tool\.pytest' pyproject.toml 2>/dev/null; then
  echo "  ✓ Pytest (pyproject.toml)"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
fi

# RSpec
[[ -f .rspec || -d spec ]] && {
  echo "  ✓ RSpec"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
}

# Minitest (Ruby)
if [[ -d test ]] && find test -name '*_test.rb' 2>/dev/null | head -1 | grep -q .; then
  echo "  ✓ Minitest (Ruby)"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
fi

# PHPUnit
[[ -f phpunit.xml || -f phpunit.xml.dist ]] && {
  echo "  ✓ PHPUnit"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
}

# Pest
[[ -f Pest.php ]] && {
  echo "  ✓ Pest"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
}

# Go test (always available if there are *_test.go files)
[[ "$GO_TEST_COUNT" -gt 0 ]] && {
  echo "  ✓ Go testing (built-in)"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
}

# Cargo test
if [[ -f Cargo.toml ]] && [[ "$RS_TEST_COUNT" -gt 0 || "${INLINE_TEST_FILES:-0}" -gt 0 ]]; then
  echo "  ✓ Cargo test (built-in)"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
fi

# JUnit / Maven / Gradle
if [[ -f pom.xml ]] && grep -qE 'junit|testng' pom.xml 2>/dev/null; then
  echo "  ✓ JUnit/TestNG (Maven)"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
fi
if [[ -f build.gradle || -f build.gradle.kts ]] && grep -qE 'junit|testng' build.gradle* 2>/dev/null; then
  echo "  ✓ JUnit/TestNG (Gradle)"
  FRAMEWORKS_FOUND=$((FRAMEWORKS_FOUND + 1))
fi

[[ "$FRAMEWORKS_FOUND" -eq 0 ]] && echo "  ⚠ No test framework configuration detected"
echo

# --- What does `npm test` actually run? ---
if [[ -f package.json ]]; then
  echo "── npm test command ────"
  TEST_CMD=$(grep -E '"test"\s*:' package.json 2>/dev/null | head -1 | sed -E 's/.*"test"\s*:\s*"(.*)".*/\1/')
  if [[ -n "$TEST_CMD" ]]; then
    echo "  test: $TEST_CMD"
  else
    echo "  (no \"test\" script defined in package.json — may indicate untested project)"
  fi
  # Look for other test:* scripts
  OTHER_TEST_SCRIPTS=$(grep -E '"test:[a-z0-9_-]+"\s*:' package.json 2>/dev/null | sed -E 's/^\s*"([^"]+)"\s*:\s*"(.*)".*$/  \1: \2/')
  if [[ -n "$OTHER_TEST_SCRIPTS" ]]; then
    echo "$OTHER_TEST_SCRIPTS"
  fi
  echo
fi

# --- Test directory structure ---
echo "── Test directory layout ────"
for d in test tests __tests__ spec specs e2e cypress playwright integration unit; do
  if [[ -d "$d" ]]; then
    COUNT=$(find "$d" -type f 2>/dev/null | wc -l)
    printf "  ./%-15s  %4d files\n" "$d" "$COUNT"
  fi
done

# Look for nested test dirs
NESTED=$(find . -type d \( -name 'test' -o -name 'tests' -o -name '__tests__' -o -name 'spec' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -v '^\./[^/]*$' \
  | head -10)
if [[ -n "$NESTED" ]]; then
  echo
  echo "  Nested test directories (sample):"
  echo "$NESTED" | head -10 | awk '{print "    " $0}'
fi
echo

# --- Coverage artifacts ---
echo "── Coverage artifacts ────"
COVERAGE_FOUND=0
for f in coverage .coverage coverage.xml coverage.json lcov.info htmlcov coverage.txt .nyc_output; do
  if [[ -e "$f" ]]; then
    echo "  ✓ Found: $f"
    COVERAGE_FOUND=$((COVERAGE_FOUND + 1))
  fi
done
[[ "$COVERAGE_FOUND" -eq 0 ]] && echo "  No coverage artifacts found in working tree."
echo

# --- CI config detection ---
echo "── CI configuration ────"
CI_FOUND=0
for f in .github/workflows .gitlab-ci.yml .circleci/config.yml .travis.yml Jenkinsfile azure-pipelines.yml bitbucket-pipelines.yml .drone.yml buildkite.yml; do
  if [[ -e "$f" ]]; then
    echo "  ✓ $f"
    CI_FOUND=$((CI_FOUND + 1))
  fi
done

if [[ "$CI_FOUND" -eq 0 ]]; then
  echo "  ⚠ No CI configuration detected — tests may not be enforced"
fi

# Try to find test invocation in CI files
if [[ -d .github/workflows ]]; then
  TEST_REFS=$(grep -rIE '\b(test|jest|pytest|rspec|phpunit|go test|cargo test|mvn test|gradle test)\b' .github/workflows 2>/dev/null | wc -l)
  echo "  Test-like commands in workflows: $TEST_REFS occurrences"
fi
echo

# --- Quick test count by counting test cases ---
echo "── Test case count (rough) ────"

if [[ "$JS_TEST_COUNT" -gt 0 ]]; then
  JS_CASES=$(find . -type f \( -name '*.test.js' -o -name '*.test.jsx' -o -name '*.test.ts' -o -name '*.test.tsx' -o -name '*.spec.js' -o -name '*.spec.ts' \) 2>/dev/null \
    | grep -Ev "/($IGNORE_DIRS)/" \
    | xargs -r grep -hE '^\s*(it|test)\s*\(' 2>/dev/null | wc -l)
  printf "  JS/TS test cases:    ~%5d\n" "$JS_CASES"
fi

if [[ "$PY_TEST_COUNT" -gt 0 ]]; then
  PY_CASES=$(find . -type f \( -name 'test_*.py' -o -name '*_test.py' \) 2>/dev/null \
    | grep -Ev "/($IGNORE_DIRS)/" \
    | xargs -r grep -hE '^\s*def test_' 2>/dev/null | wc -l)
  printf "  Python test cases:   ~%5d\n" "$PY_CASES"
fi

if [[ "$GO_TEST_COUNT" -gt 0 ]]; then
  GO_CASES=$(find . -type f -name '*_test.go' 2>/dev/null \
    | grep -Ev "/($IGNORE_DIRS)/" \
    | xargs -r grep -hE '^func Test' 2>/dev/null | wc -l)
  printf "  Go test cases:       ~%5d\n" "$GO_CASES"
fi

if [[ "$RB_TEST_COUNT" -gt 0 ]]; then
  RB_CASES=$(find . -type f \( -name '*_spec.rb' -o -name '*_test.rb' \) 2>/dev/null \
    | grep -Ev "/($IGNORE_DIRS)/" \
    | xargs -r grep -hE "^\s*(it|test|specify)\s+['\"\s]" 2>/dev/null | wc -l)
  printf "  Ruby test cases:     ~%5d\n" "$RB_CASES"
fi

echo

# --- Test type classification ---
echo "── Test types detected ────"

# Build the list of test files (we'll grep it 3 times; cheap on most repos)
TEST_FILE_LIST=$(find . -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -E '\.(test|spec)\.(js|jsx|ts|tsx|mjs|cjs)$|(test_|_test)\.py$|_test\.go$|(_spec|_test)\.rb$|Test\.php$|Tests?\.(java|kt)$')

E2E_FILES=$(echo "$TEST_FILE_LIST" | grep -cE '/(e2e|cypress|playwright|integration-e2e)/' || true)
E2E_FILES=${E2E_FILES:-0}

INTEGRATION_FILES=$(echo "$TEST_FILE_LIST" | grep -cE '/(integration|integration-tests?|api-tests?|contract|route-contract)/' || true)
INTEGRATION_FILES=${INTEGRATION_FILES:-0}

UNIT_FILES=$(echo "$TEST_FILE_LIST" | grep -vE '/(e2e|cypress|playwright|integration|contract|route-contract)/' | grep -c . || true)
UNIT_FILES=${UNIT_FILES:-0}

printf "  Unit-ish test files:        %4d\n" "$UNIT_FILES"
printf "  Integration/contract files: %4d\n" "$INTEGRATION_FILES"
printf "  E2E test files:             %4d\n" "$E2E_FILES"
echo

# Flag missing layers
if [[ "$INTEGRATION_FILES" -eq 0 && "$UNIT_FILES" -gt 5 ]]; then
  echo "  ⚠ No integration / contract test directory detected."
  echo "    Unit tests catch logic bugs; integration tests catch the seams."
fi
if [[ "$E2E_FILES" -eq 0 && "$TOTAL_TEST_FILES" -gt 0 && -f package.json && "${UI_COUNT:-0}" -gt 5 ]]; then
  echo "  ⚠ No E2E tests detected. Consider at least one golden-path browser test."
fi
if [[ "$E2E_FILES" -gt "$UNIT_FILES" && "$UNIT_FILES" -gt 0 ]]; then
  echo "  ⚠ More E2E tests than unit tests — inverted-pyramid risk (slow, flaky CI)."
fi
echo

echo "=========================================="
echo " Inventory complete."
echo "=========================================="
