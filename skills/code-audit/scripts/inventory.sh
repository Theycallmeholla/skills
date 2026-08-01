#!/usr/bin/env bash
# inventory.sh — one-page overview of a codebase
#
# Usage: scripts/inventory.sh <path-to-repo>
#
# Output: stack summary, file/LOC counts by language, presence of key files.
# Designed to be the first command run during an audit.

set -uo pipefail

if (( BASH_VERSINFO[0] < 4 )); then
  echo "Error: inventory.sh requires bash >= 4 (brew install bash)" >&2
  exit 1
fi

ROOT="${1:-.}"

if [[ ! -d "$ROOT" ]]; then
  echo "Error: '$ROOT' is not a directory" >&2
  exit 1
fi

cd "$ROOT" || exit 1

# Directories to ignore for counting (vendored / generated / VCS)
IGNORE_DIRS='node_modules|vendor|\.git|\.svn|\.hg|dist|build|target|\.venv|venv|__pycache__|\.next|\.nuxt|out|coverage|\.cache|\.pytest_cache|\.mypy_cache|\.tox|bower_components|jspm_packages'

print_header() {
  echo
  echo "=========================================="
  echo " $1"
  echo "=========================================="
}

print_header "Codebase Inventory: $ROOT"
echo "Generated: $(date)"
echo "Git HEAD: $(git rev-parse --short HEAD 2>/dev/null || echo 'not a git repo')"
echo "Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'n/a')"

print_header "Repo Size"

# Total files and lines (excluding ignored dirs)
TOTAL_FILES=$(find . -type f 2>/dev/null | grep -Ev "(/($IGNORE_DIRS)/|^\./($IGNORE_DIRS)/)" | wc -l)
echo "Tracked files (excluding ignored dirs): $TOTAL_FILES"

# Repo size on disk (with and without ignored dirs)
SIZE_TOTAL=$(du -sh . 2>/dev/null | awk '{print $1}')
echo "Total size on disk: $SIZE_TOTAL"

if [[ -d node_modules ]]; then
  echo "  (node_modules size: $(du -sh node_modules 2>/dev/null | awk '{print $1}'))"
fi
if [[ -d vendor ]]; then
  echo "  (vendor size: $(du -sh vendor 2>/dev/null | awk '{print $1}'))"
fi

# Git history depth
if git rev-parse --git-dir > /dev/null 2>&1; then
  COMMITS=$(git rev-list --count HEAD 2>/dev/null || echo "?")
  CONTRIBUTORS=$(git shortlog -sn --all 2>/dev/null | wc -l)
  FIRST_COMMIT=$(git log --reverse --format=%ai 2>/dev/null | head -1 | cut -d' ' -f1)
  LAST_COMMIT=$(git log -1 --format=%ai 2>/dev/null | cut -d' ' -f1)
  echo "Commits: $COMMITS  Contributors: $CONTRIBUTORS"
  echo "Active: $FIRST_COMMIT → $LAST_COMMIT"
fi

print_header "Language Breakdown (by file count and rough LOC)"

# Map extensions to languages, count files and lines for each
declare -A EXT_LANG=(
  [js]="JavaScript"
  [mjs]="JavaScript"
  [cjs]="JavaScript"
  [jsx]="JavaScript (JSX)"
  [ts]="TypeScript"
  [tsx]="TypeScript (TSX)"
  [py]="Python"
  [rb]="Ruby"
  [php]="PHP"
  [go]="Go"
  [rs]="Rust"
  [java]="Java"
  [kt]="Kotlin"
  [scala]="Scala"
  [cs]="C#"
  [c]="C"
  [h]="C header"
  [cpp]="C++"
  [cc]="C++"
  [hpp]="C++ header"
  [swift]="Swift"
  [m]="Objective-C"
  [erl]="Erlang"
  [ex]="Elixir"
  [exs]="Elixir"
  [clj]="Clojure"
  [hs]="Haskell"
  [lua]="Lua"
  [pl]="Perl"
  [sh]="Shell"
  [bash]="Bash"
  [zsh]="Zsh"
  [vue]="Vue"
  [svelte]="Svelte"
  [astro]="Astro"
  [html]="HTML"
  [css]="CSS"
  [scss]="SCSS"
  [sass]="Sass"
  [less]="Less"
  [sql]="SQL"
  [graphql]="GraphQL"
  [proto]="Protobuf"
  [yml]="YAML"
  [yaml]="YAML"
  [toml]="TOML"
  [json]="JSON"
  [md]="Markdown"
  [tf]="Terraform"
)

# Build a list of (count, lines, extension) sorted by lines
declare -A COUNTS LINES
while IFS= read -r f; do
  ext="${f##*.}"
  ext="${ext,,}"
  if [[ -n "${EXT_LANG[$ext]:-}" ]]; then
    COUNTS[$ext]=$((${COUNTS[$ext]:-0} + 1))
    # Count lines, ignoring failures (binary files, etc.)
    nl=$(wc -l < "$f" 2>/dev/null || echo 0)
    LINES[$ext]=$((${LINES[$ext]:-0} + nl))
  fi
done < <(find . -type f 2>/dev/null | grep -Ev "(/($IGNORE_DIRS)/|^\./($IGNORE_DIRS)/)")

# Print sorted by lines desc
{
  printf "%-22s %10s %12s\n" "Language" "Files" "Lines"
  printf "%-22s %10s %12s\n" "--------" "-----" "-----"
  for ext in "${!LINES[@]}"; do
    printf "%-22s %10d %12d\n" "${EXT_LANG[$ext]}" "${COUNTS[$ext]}" "${LINES[$ext]}"
  done | sort -k3 -rn
} | head -25

print_header "Stack Markers (Manifests, Build Files, CI)"

check_file() {
  local label="$1"; shift
  for path in "$@"; do
    if compgen -G "$path" > /dev/null 2>&1; then
      for f in $path; do
        [[ -e "$f" ]] && echo "  ✓ $label: $f"
      done
    fi
  done
}

echo "Package managers / manifests:"
check_file "Node.js" "package.json"
check_file "npm lockfile" "package-lock.json"
check_file "yarn lockfile" "yarn.lock"
check_file "pnpm lockfile" "pnpm-lock.yaml"
check_file "Python (pip)" "requirements*.txt" "setup.py" "pyproject.toml" "Pipfile"
check_file "Python lockfile" "poetry.lock" "Pipfile.lock" "uv.lock"
check_file "Ruby" "Gemfile" "*.gemspec"
check_file "Ruby lockfile" "Gemfile.lock"
check_file "PHP" "composer.json"
check_file "PHP lockfile" "composer.lock"
check_file "Go" "go.mod" "go.sum"
check_file "Rust" "Cargo.toml" "Cargo.lock"
check_file "Java" "pom.xml" "build.gradle" "build.gradle.kts"
check_file ".NET" "*.csproj" "*.sln"
check_file "Terraform" "*.tf"
echo

echo "Build / dev tools:"
check_file "Docker" "Dockerfile" "docker-compose.yml" "docker-compose.yaml"
check_file "Make" "Makefile"
check_file "TypeScript config" "tsconfig.json"
check_file "ESLint" ".eslintrc*" "eslint.config.*"
check_file "Prettier" ".prettierrc*" "prettier.config.*"
check_file "Babel" ".babelrc*" "babel.config.*"
check_file "Webpack" "webpack.config.*"
check_file "Vite" "vite.config.*"
check_file "Editor config" ".editorconfig"
echo

echo "CI / CD:"
[[ -d .github/workflows ]] && echo "  ✓ GitHub Actions: $(ls .github/workflows/*.{yml,yaml} 2>/dev/null | wc -l) workflow file(s)"
check_file "GitLab CI" ".gitlab-ci.yml"
check_file "CircleCI" ".circleci/config.yml"
check_file "Travis" ".travis.yml"
check_file "Jenkins" "Jenkinsfile"
check_file "Buildkite" ".buildkite/pipeline.yml"
check_file "Drone" ".drone.yml"
check_file "Azure Pipelines" "azure-pipelines.yml"
echo

echo "Documentation / governance:"
check_file "README" "README*" "readme*"
check_file "License" "LICENSE*" "COPYING*"
check_file "Contributing" "CONTRIBUTING*"
check_file "Changelog" "CHANGELOG*"
check_file "Security policy" "SECURITY*"
check_file "Code of conduct" "CODE_OF_CONDUCT*"
echo

echo "Test / coverage:"
TEST_DIRS=$(find . -maxdepth 3 -type d \( -name test -o -name tests -o -name spec -o -name __tests__ -o -name '*_test*' \) 2>/dev/null | grep -Ev "(/($IGNORE_DIRS)/)" | head -5)
if [[ -n "$TEST_DIRS" ]]; then
  echo "  Test directories found:"
  echo "$TEST_DIRS" | sed 's/^/    /'
else
  echo "  ⚠ No test/spec directories found at top level"
fi

print_header "Top 10 Largest Source Files"
find . -type f 2>/dev/null \
  | grep -Ev "(/($IGNORE_DIRS)/|^\./($IGNORE_DIRS)/)" \
  | grep -E '\.(js|ts|jsx|tsx|py|rb|php|go|rs|java|cs|c|cpp|swift|kt|vue|svelte)$' \
  | xargs -I{} wc -l "{}" 2>/dev/null \
  | sort -rn \
  | head -11 \
  | tail -10 \
  | awk '{printf "  %6d  %s\n", $1, $2}'

print_header "Top 10 Most-Churned Files (by commit count)"
if git rev-parse --git-dir > /dev/null 2>&1; then
  git log --pretty=format: --name-only 2>/dev/null \
    | grep -Ev "^\s*$" \
    | grep -Ev "($IGNORE_DIRS)" \
    | sort | uniq -c | sort -rn | head -10 \
    | awk '{printf "  %4d commits  %s\n", $1, $2}'
else
  echo "  (not a git repo, skipping)"
fi

print_header "Suspicious Top-Level Items"
SUSPICIOUS=0
for f in node_modules vendor dist build out target .next; do
  if [[ -d "$f" ]] && git ls-files --error-unmatch "$f" > /dev/null 2>&1; then
    echo "  ⚠ $f/ is tracked in git (should usually be in .gitignore)"
    SUSPICIOUS=1
  fi
done

# Check for common credential files in git
# Build proper regex patterns (escape dots, replace * with .*)
for pattern in '\.env' '\.env\.local' '\.env\.production' '.*\.pem' '.*\.key' 'id_rsa'; do
  found=$(git ls-files 2>/dev/null | grep -E "(^|/)${pattern}\$" | head -3)
  if [[ -n "$found" ]]; then
    echo "  ⚠ Potential credential file tracked (pattern: $pattern):"
    echo "$found" | sed 's/^/      /'
    SUSPICIOUS=1
  fi
done

if [[ $SUSPICIOUS -eq 0 ]]; then
  echo "  None detected at top level."
fi

echo
echo "=========================================="
echo " Inventory complete."
echo "=========================================="
