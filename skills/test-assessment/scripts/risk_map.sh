#!/usr/bin/env bash
# risk_map.sh — identify high-risk source modules and check whether tests exist
#
# Usage: scripts/risk_map.sh <path>

set -uo pipefail

ROOT="${1:-.}"

if [[ ! -d "$ROOT" ]]; then
  echo "Error: '$ROOT' is not a directory" >&2
  exit 1
fi

cd "$ROOT" || exit 1

IGNORE_DIRS='node_modules|vendor|\.git|dist|build|target|\.venv|venv|__pycache__|\.next|\.nuxt|\.tests-dist|\.turbo|\.parcel-cache|\.svelte-kit|out|coverage|\.cache|bower_components|jspm_packages'

# Well-known config filenames at the repo root that match risk keywords but are
# config glue, not auth/payment logic. Excluded from risky-name detection.
CONFIG_EXCLUDE='^\./(auth|auth\.config|next-auth\.config|middleware|instrumentation|sentry\.client\.config|sentry\.server\.config|sentry\.edge\.config)\.(ts|tsx|js|jsx|mjs)$'

echo "=========================================="
echo " Risk Map: $ROOT"
echo "=========================================="
echo
echo "Identifying high-risk source modules and their test status."
echo "Risk signals: filename keywords (auth, payment, billing, etc.) and"
echo "imports of risk-relevant SDKs/libraries."
echo

# --- Find risky filenames ---
echo "── Source files with risk-suggestive names ────"

# Look for source files (not test files) whose path/name suggests risk
RISKY=$(find . -type f \( -name '*.js' -o -name '*.jsx' -o -name '*.ts' -o -name '*.tsx' -o -name '*.py' -o -name '*.go' -o -name '*.rb' -o -name '*.php' -o -name '*.java' -o -name '*.kt' -o -name '*.rs' -o -name '*.cs' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -vE '\.(test|spec)\.|_test\.|_spec\.|Test\.(java|cs|kt)|Tests\.(java|cs|kt)' \
  | grep -vE '\.d\.ts$|\.d\.tsx$' \
  | grep -iE '/(auth|authn|authz|login|session|password|token|oauth|payment|billing|invoice|subscription|charge|refund|stripe|plaid|paypal|crypto|encrypt|decrypt|signature|permission|role|acl|admin|delete|gdpr|webhook|migration)/?[^/]*$|/(auth|payment|billing|crypto|permission|delete|admin)\.[a-z]+$' \
  | grep -vE "$CONFIG_EXCLUDE" \
  | sort -u)

if [[ -z "$RISKY" ]]; then
  echo "  No files matched risk-keyword patterns."
  echo "  This may be a low-risk codebase, or risk lives in differently-named files."
else
  echo "$RISKY" | while read -r src; do
    [[ -z "$src" ]] && continue

    # Try to find a corresponding test file
    base=$(basename "$src")
    name="${base%.*}"
    ext="${base##*.}"
    dir=$(dirname "$src")

    # Common test file patterns
    test_found=""
    for pattern in \
      "$dir/$name.test.$ext" \
      "$dir/$name.spec.$ext" \
      "$dir/__tests__/$name.test.$ext" \
      "$dir/__tests__/$name.$ext" \
      "$dir/../tests/$name.test.$ext" \
      "$dir/../__tests__/$name.test.$ext"; do
      if [[ -f "$pattern" ]]; then
        test_found="$pattern"
        break
      fi
    done

    # If not found by direct path, search by basename
    if [[ -z "$test_found" ]]; then
      candidate=$(find . -type f 2>/dev/null \
        | grep -Ev "/($IGNORE_DIRS)/" \
        | grep -E "/(${name})\.(test|spec)\.[a-z]+$|/test_${name}\.py$|/${name}_test\.(go|py|rb)$|/${name}_spec\.rb$|/${name}Test\.(java|kt|php|cs)$" \
        | head -1)
      [[ -n "$candidate" ]] && test_found="$candidate"
    fi

    if [[ -n "$test_found" ]]; then
      # Count test cases in the test file
      cases=$(grep -cE '^\s*(it|test|def test_|func Test|@Test|public function test)' "$test_found" 2>/dev/null || true)
      cases=${cases:-0}
      printf "  ⚠ RISKY  %s\n         tested by: %s (%d cases)\n" "$src" "$test_found" "$cases"
    else
      printf "  ❌ RISKY  %s\n         NO TEST FILE FOUND\n" "$src"
    fi
  done
fi
echo

# --- Risky directory clusters ---
echo "── Source directories with risk-suggestive names ────"
RISKY_DIRS=$(find . -type d 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -iE '/(auth|payment|billing|crypto|permission|admin|webhook)s?$' \
  | sort -u | head -20)

if [[ -n "$RISKY_DIRS" ]]; then
  echo "$RISKY_DIRS" | while read -r d; do
    [[ -z "$d" ]] && continue
    src_count=$(find "$d" -maxdepth 2 -type f \( -name '*.js' -o -name '*.ts' -o -name '*.py' -o -name '*.go' -o -name '*.rb' -o -name '*.php' -o -name '*.java' \) 2>/dev/null \
      | grep -vE '\.(test|spec)\.|_test\.|_spec\.' | wc -l)
    test_count=$(find "$d" -maxdepth 3 -type f 2>/dev/null \
      | grep -E '\.(test|spec)\.|_test\.|_spec\.' | wc -l)

    # Also look for sibling test directory
    parent=$(dirname "$d")
    sibling_tests=$(find "$parent" -maxdepth 3 -type d \( -name '__tests__' -o -name 'tests' -o -name 'test' -o -name 'spec' \) -print0 2>/dev/null \
      | xargs -0 -r -I{} find {} -type f 2>/dev/null \
      | grep -E "$(basename "$d")" | wc -l)

    total_tests=$((test_count + sibling_tests))
    printf "  %s\n    sources: %d, related tests: %d\n" "$d" "$src_count" "$total_tests"
    if [[ "$src_count" -gt 0 && "$total_tests" -eq 0 ]]; then
      echo "    ❌ Risky directory with no detected tests"
    fi
  done
else
  echo "  No risk-keyword directories found."
fi
echo

# --- Files that import payment/auth SDKs ---
echo "── Files importing risk-relevant SDKs ────"
SDK_PATTERN='\b(stripe|plaid|paypal|braintree|square|adyen|jsonwebtoken|jwt|bcrypt|argon2|crypto|@auth0|passport|next-auth|firebase-admin|aws-sdk|googleapis)\b'

SDK_FILES=$(find . -type f \( -name '*.js' -o -name '*.ts' -o -name '*.jsx' -o -name '*.tsx' -o -name '*.py' \) 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -vE '\.(test|spec)\.|_test\.|_spec\.' \
  | grep -vE '^\./(e2e|cypress|playwright|tests?|__tests__|spec)/' \
  | grep -vE "$CONFIG_EXCLUDE" \
  | xargs -r grep -lE "(import|require|from).*$SDK_PATTERN" 2>/dev/null \
  | head -20)

if [[ -n "$SDK_FILES" ]]; then
  echo "$SDK_FILES" | while read -r src; do
    [[ -z "$src" ]] && continue
    base=$(basename "$src")
    name="${base%.*}"
    ext="${base##*.}"
    dir=$(dirname "$src")

    # Quick test-file lookup
    test_found=""
    for pattern in \
      "$dir/$name.test.$ext" \
      "$dir/$name.spec.$ext" \
      "$dir/__tests__/$name.test.$ext"; do
      [[ -f "$pattern" ]] && { test_found="$pattern"; break; }
    done

    if [[ -z "$test_found" ]]; then
      candidate=$(find . -type f 2>/dev/null \
        | grep -Ev "/($IGNORE_DIRS)/" \
        | grep -E "/(${name})\.(test|spec)\.[a-z]+$|/test_${name}\.py$" \
        | head -1)
      [[ -n "$candidate" ]] && test_found="$candidate"
    fi

    if [[ -n "$test_found" ]]; then
      printf "  ⚠ %s\n       tested by: %s\n" "$src" "$test_found"
    else
      printf "  ❌ %s\n       NO TEST FILE FOUND\n" "$src"
    fi
  done
else
  echo "  No risk-relevant SDK imports detected."
fi
echo

# --- High-churn files (most-changed = most-risky-to-leave-untested) ---
if git rev-parse --git-dir > /dev/null 2>&1; then
  echo "── Top 15 most-churned source files ────"
  echo "  (high churn + low coverage = high risk)"
  echo

  git log --pretty=format: --name-only 2>/dev/null \
    | grep -Ev "/($IGNORE_DIRS)/|^$" \
    | grep -E '\.(js|jsx|ts|tsx|py|go|rb|php|java|kt|rs|cs)$' \
    | grep -vE '\.(test|spec)\.|_test\.|_spec\.|Test\.(java|cs|kt)|Tests\.(java|cs|kt)' \
    | sort | uniq -c | sort -rn | head -15 \
    | while read -r count file; do
        # Try to find a test file
        base=$(basename "$file")
        name="${base%.*}"
        test_found=$(find . -type f 2>/dev/null \
          | grep -Ev "/($IGNORE_DIRS)/" \
          | grep -E "/(${name})\.(test|spec)\.|/test_${name}\.|/${name}_test\.|/${name}_spec\.|/${name}Test\." \
          | head -1)

        if [[ -n "$test_found" ]]; then
          printf "  %4d commits  ✓ %s\n" "$count" "$file"
        else
          printf "  %4d commits  ❌ %s  (no test)\n" "$count" "$file"
        fi
      done
fi
echo

echo "=========================================="
echo " Risk map complete."
echo "=========================================="
echo
echo "Next steps:"
echo "  1. Review files marked ❌ — these are the priority gaps"
echo "  2. For each ❌ file, decide what tests would catch real bugs"
echo "  3. Plot in the Critical/High × None/Sparse matrix"
