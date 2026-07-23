#!/usr/bin/env bash
# deps_check.sh — auto-detect package manager(s) and run their audit commands
#
# Usage: scripts/deps_check.sh <path>
#
# Runs each detected ecosystem's audit. Skips ecosystems whose tools aren't
# installed, with a note about how to install them. Output is captured for
# inclusion in the audit report.

set -uo pipefail

ROOT="${1:-.}"

if [[ ! -d "$ROOT" ]]; then
  echo "Error: '$ROOT' is not a directory" >&2
  exit 1
fi

cd "$ROOT" || exit 1

echo "=========================================="
echo " Dependency audit: $ROOT"
echo "=========================================="
echo

DETECTED=0

# Helper: print a section header for an ecosystem
section() {
  echo
  echo "── $1 ────────────────────────────────────"
}

# Helper: check tool availability
have() { command -v "$1" > /dev/null 2>&1; }

# ---------------- Node.js ----------------
if [[ -f package.json ]]; then
  DETECTED=1
  section "Node.js (package.json detected)"

  # Identify which package manager is in use by lockfile
  if [[ -f pnpm-lock.yaml ]]; then
    PKG_MGR="pnpm"
  elif [[ -f yarn.lock ]]; then
    PKG_MGR="yarn"
  elif [[ -f package-lock.json ]]; then
    PKG_MGR="npm"
  else
    PKG_MGR="npm"
    echo "  ⚠ No lockfile found (no package-lock.json, yarn.lock, or pnpm-lock.yaml)."
    echo "    This means non-deterministic installs across environments."
  fi
  echo "  Package manager: $PKG_MGR"

  # Direct dep counts
  if have jq; then
    DEPS=$(jq '.dependencies // {} | length' package.json)
    DEV_DEPS=$(jq '.devDependencies // {} | length' package.json)
    echo "  Direct dependencies: $DEPS  (dev: $DEV_DEPS)"
  fi

  # Postinstall scripts (supply-chain risk)
  if grep -qE '"(post|pre)install"' package.json; then
    echo "  ⚠ pre/postinstall scripts present in package.json — review them:"
    grep -nE '"(post|pre)install"' package.json | head -5 | sed 's/^/      /'
  fi

  # Audit
  case "$PKG_MGR" in
    npm)
      if have npm; then
        echo
        echo "  Running: npm audit --omit=dev --audit-level=low"
        npm audit --omit=dev --audit-level=low 2>&1 | tail -40
      else
        echo "  npm not installed; cannot run npm audit"
      fi
      ;;
    yarn)
      if have yarn; then
        echo
        # Yarn Berry uses 'yarn npm audit', Yarn Classic uses 'yarn audit'
        yarn_version=$(yarn --version 2>/dev/null)
        if [[ "$yarn_version" =~ ^1\. ]]; then
          echo "  Running: yarn audit --level=low (Yarn Classic)"
          yarn audit --level=low 2>&1 | tail -40
        else
          echo "  Running: yarn npm audit (Yarn Berry)"
          yarn npm audit 2>&1 | tail -40
        fi
      else
        echo "  yarn not installed; cannot run audit"
      fi
      ;;
    pnpm)
      if have pnpm; then
        echo
        echo "  Running: pnpm audit"
        pnpm audit 2>&1 | tail -40
      else
        echo "  pnpm not installed; cannot run audit"
      fi
      ;;
  esac

  # Outdated check
  if have "$PKG_MGR"; then
    echo
    echo "  Outdated dependencies (top 20):"
    case "$PKG_MGR" in
      npm) npm outdated 2>&1 | head -21 ;;
      yarn) yarn outdated 2>&1 | head -21 ;;
      pnpm) pnpm outdated 2>&1 | head -21 ;;
    esac
  fi
fi

# ---------------- Python ----------------
PY_MANIFEST=""
[[ -f requirements.txt ]] && PY_MANIFEST="requirements.txt"
[[ -f pyproject.toml ]] && PY_MANIFEST="${PY_MANIFEST:+$PY_MANIFEST,}pyproject.toml"
[[ -f Pipfile ]] && PY_MANIFEST="${PY_MANIFEST:+$PY_MANIFEST,}Pipfile"
[[ -f setup.py ]] && PY_MANIFEST="${PY_MANIFEST:+$PY_MANIFEST,}setup.py"

if [[ -n "$PY_MANIFEST" ]]; then
  DETECTED=1
  section "Python ($PY_MANIFEST detected)"

  # Lockfile check
  if [[ -f poetry.lock ]]; then
    echo "  Lockfile: poetry.lock"
  elif [[ -f Pipfile.lock ]]; then
    echo "  Lockfile: Pipfile.lock"
  elif [[ -f uv.lock ]]; then
    echo "  Lockfile: uv.lock"
  elif [[ -f requirements.txt ]] && grep -qE '==' requirements.txt; then
    echo "  Lockfile: requirements.txt (pinned)"
  else
    echo "  ⚠ No clear lockfile / pinned requirements detected."
  fi

  if have pip-audit; then
    echo
    echo "  Running: pip-audit"
    if [[ -f requirements.txt ]]; then
      pip-audit -r requirements.txt 2>&1 | tail -40
    else
      pip-audit 2>&1 | tail -40
    fi
  else
    echo "  pip-audit not installed."
    echo "  Install with: pipx install pip-audit  (or: pip install pip-audit)"
  fi

  if have safety; then
    echo
    echo "  Running: safety check"
    safety check 2>&1 | tail -30
  fi
fi

# ---------------- Ruby ----------------
if [[ -f Gemfile ]]; then
  DETECTED=1
  section "Ruby (Gemfile detected)"

  if [[ -f Gemfile.lock ]]; then
    echo "  Lockfile: Gemfile.lock present"
  else
    echo "  ⚠ Gemfile.lock missing"
  fi

  if have bundle-audit; then
    echo
    echo "  Running: bundle-audit check --update"
    bundle-audit check --update 2>&1 | tail -30
  elif have bundler-audit; then
    echo
    echo "  Running: bundler-audit check --update"
    bundler-audit check --update 2>&1 | tail -30
  else
    echo "  bundler-audit not installed."
    echo "  Install with: gem install bundler-audit"
  fi
fi

# ---------------- Go ----------------
if [[ -f go.mod ]]; then
  DETECTED=1
  section "Go (go.mod detected)"

  if [[ -f go.sum ]]; then
    echo "  go.sum: present"
  else
    echo "  ⚠ go.sum missing"
  fi

  if have govulncheck; then
    echo
    echo "  Running: govulncheck ./..."
    govulncheck ./... 2>&1 | tail -40
  else
    echo "  govulncheck not installed."
    echo "  Install with: go install golang.org/x/vuln/cmd/govulncheck@latest"
  fi

  if have go; then
    echo
    echo "  Direct module count: $(go list -m all 2>/dev/null | wc -l)"
    echo "  Outdated check (sample): "
    go list -m -u all 2>/dev/null | grep -E '\[' | head -10
  fi
fi

# ---------------- Rust ----------------
if [[ -f Cargo.toml ]]; then
  DETECTED=1
  section "Rust (Cargo.toml detected)"

  if [[ -f Cargo.lock ]]; then
    echo "  Cargo.lock: present"
  else
    echo "  ⚠ Cargo.lock missing"
  fi

  if have cargo-audit; then
    echo
    echo "  Running: cargo audit"
    cargo audit 2>&1 | tail -40
  else
    echo "  cargo-audit not installed."
    echo "  Install with: cargo install cargo-audit"
  fi
fi

# ---------------- PHP ----------------
if [[ -f composer.json ]]; then
  DETECTED=1
  section "PHP (composer.json detected)"

  if [[ -f composer.lock ]]; then
    echo "  composer.lock: present"
  else
    echo "  ⚠ composer.lock missing"
  fi

  if have composer; then
    echo
    echo "  Running: composer audit"
    composer audit 2>&1 | tail -40
    echo
    echo "  Running: composer outdated --direct (top 20)"
    composer outdated --direct 2>&1 | head -21
  else
    echo "  composer not installed."
  fi
fi

# ---------------- Java ----------------
if [[ -f pom.xml ]]; then
  DETECTED=1
  section "Java / Maven (pom.xml detected)"
  echo "  Maven projects need explicit configuration of dependency-check."
  echo "  Recommended: add OWASP dependency-check-maven plugin."
  echo "  Alternative: scan pom.xml with snyk / mend / dependabot."
fi

if [[ -f build.gradle || -f build.gradle.kts ]]; then
  DETECTED=1
  section "Java / Gradle (build.gradle detected)"
  echo "  Gradle projects need explicit configuration of dependency-check."
  echo "  Recommended: apply OWASP dependency-check Gradle plugin."
fi

# ---------------- .NET ----------------
if compgen -G "*.csproj" > /dev/null || compgen -G "*.sln" > /dev/null; then
  DETECTED=1
  section ".NET ($(ls *.csproj *.sln 2>/dev/null | head -3 | tr '\n' ' '))"

  if have dotnet; then
    echo
    echo "  Running: dotnet list package --vulnerable --include-transitive"
    dotnet list package --vulnerable --include-transitive 2>&1 | tail -40
  else
    echo "  dotnet CLI not installed."
  fi
fi

# ---------------- Docker base images ----------------
if [[ -f Dockerfile ]]; then
  DETECTED=1
  section "Dockerfile"
  echo "  Base images:"
  grep -nE '^FROM ' Dockerfile | sed 's/^/    /'
  if grep -qE '^FROM .+:latest' Dockerfile; then
    echo "  ⚠ Uses ':latest' tag — non-reproducible. Pin to a specific tag or digest."
  fi
  if ! grep -qE '^FROM .+@sha256:' Dockerfile; then
    echo "  ⚠ No base image pinned by digest. Tag-based pins are mutable."
  fi
fi

# ---------------- Summary ----------------
echo
echo "=========================================="
if [[ $DETECTED -eq 0 ]]; then
  echo " No supported manifest detected."
  echo " Looked for: package.json, requirements.txt, pyproject.toml,"
  echo " Gemfile, go.mod, Cargo.toml, composer.json, pom.xml, *.csproj"
else
  echo " Dependency audit complete."
  echo
  echo " For deeper scanning, consider:"
  echo "   - Snyk:        https://snyk.io/"
  echo "   - Dependabot:  built into GitHub"
  echo "   - Renovate:    https://www.mend.io/renovate/"
  echo "   - OSV-Scanner: https://github.com/google/osv-scanner"
fi
echo "=========================================="
