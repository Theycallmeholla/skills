#!/usr/bin/env bash
# ui_inventory.sh — best-effort orientation for a UX audit in code mode.
# Lists route/page files, components, form elements, and visible copy strings
# so you can reconstruct the flow map. Heuristic and framework-agnostic-ish;
# treat output as a starting point, not ground truth.
#
# Usage: ./ui_inventory.sh <path-to-frontend-root>

set -uo pipefail
ROOT="${1:-.}"

if [ ! -d "$ROOT" ]; then
  echo "Path not found: $ROOT" >&2
  exit 1
fi

# Source globs we care about; prune the usual noise.
PRUNE=( -path '*/node_modules/*' -o -path '*/.next/*' -o -path '*/dist/*' -o -path '*/build/*' -o -path '*/.git/*' )
SRC_FIND() { find "$ROOT" \( "${PRUNE[@]}" \) -prune -o -type f \( "$@" \) -print 2>/dev/null; }

echo "==================================================================="
echo "UX AUDIT — UI INVENTORY"
echo "Root: $ROOT"
echo "==================================================================="

echo
echo "### Detected framework signals"
for f in next.config.js next.config.mjs next.config.ts remix.config.js svelte.config.js vite.config.ts vite.config.js angular.json; do
  [ -f "$ROOT/$f" ] && echo "  - $f"
done
grep -lEr "\"(next|react-router-dom|@remix-run|svelte|vue|@angular/core)\"" "$ROOT"/package.json 2>/dev/null \
  | while read -r p; do echo "  - dependency hints in $p:"; grep -oE "\"(next|react-router-dom|@remix-run|svelte|vue|@angular/core)\"" "$p" | sort -u | sed 's/^/      /'; done

echo
echo "### Routes / pages (these are usually your flow steps)"
# Next.js app router
SRC_FIND -name "page.tsx" -o -name "page.jsx" -o -name "page.ts" -o -name "page.js" | sed "s|^$ROOT/|  app  |"
# Next.js pages router + generic page-ish dirs
SRC_FIND -path "*/pages/*" -name "*.tsx" -o -path "*/pages/*" -name "*.jsx" | grep -v "/api/" | sed "s|^$ROOT/|  pg   |"
# Route definitions in code (React Router etc.)
echo "  -- inline route definitions --"
grep -rEn "<Route|createBrowserRouter|router\.(push|replace)|redirect\(" "$ROOT" \
  --include=*.tsx --include=*.jsx --include=*.ts --include=*.js \
  2>/dev/null | grep -vE "node_modules|\.next|dist/|build/" | head -40 | sed 's/^/  /'

echo
echo "### Multi-step / wizard signals (the spine of a flow)"
grep -rEni "step|wizard|stepper|currentStep|onboard|funnel" "$ROOT" \
  --include=*.tsx --include=*.jsx --include=*.ts --include=*.js \
  2>/dev/null | grep -vE "node_modules|\.next|dist/|build/" | head -30 | sed 's/^/  /'

echo
echo "### Forms & inputs (concentrate audit attention here)"
grep -rEl "<form|useForm|<Formik|register\(|<input|<select|<textarea" "$ROOT" \
  --include=*.tsx --include=*.jsx --include=*.vue --include=*.svelte 2>/dev/null | grep -vE "node_modules|\.next|dist/|build/" | head -40 | sed "s|^$ROOT/|  |"
echo "  -- placeholder-as-label risk (placeholder with no nearby <label>) --"
grep -rEn "placeholder=" "$ROOT" --include=*.tsx --include=*.jsx --include=*.vue --include=*.svelte 2>/dev/null \
  | grep -vE "node_modules|\.next|dist/|build/" | head -25 | sed 's/^/  /'

echo
echo "### Validation & error messaging"
grep -rEni "zod|yup|resolver|mode:\s*['\"](onSubmit|onBlur|onChange)|errors\.|setError|error message|invalid" "$ROOT" \
  --include=*.tsx --include=*.jsx --include=*.ts --include=*.js --include=*.vue --include=*.svelte \
  2>/dev/null | grep -vE "node_modules|\.next|dist/|build/" | head -30 | sed 's/^/  /'

echo
echo "### Feedback / status signals (loading, progress, confirmation)"
grep -rEni "loading|isPending|isSubmitting|spinner|skeleton|progress|toast|success|confirm" "$ROOT" \
  --include=*.tsx --include=*.jsx --include=*.vue --include=*.svelte 2>/dev/null | grep -vE "node_modules|\.next|dist/|build/" | wc -l | sed 's/^/  occurrences: /'
echo "  (low counts here may indicate missing feedback states — verify by reading)"

echo
echo "### Button / CTA copy (audit for vague labels like 'Submit'/'Continue')"
grep -rEoh ">[^<>{}]*(Submit|Continue|Next|Go|Done|Save|Sign up|Sign in|Create|Get started|Buy|Start)[^<>{}]*<" "$ROOT" \
  --include=*.tsx --include=*.jsx --include=*.vue --include=*.svelte 2>/dev/null | sed 's/^>//; s/<$//' | sort | uniq -c | sort -rn | head -25 | sed 's/^/  /'

echo
echo "==================================================================="
echo "Inventory complete. This is orientation only — read the flagged"
echo "files to build the actual flow map."
echo "==================================================================="
