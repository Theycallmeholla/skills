#!/usr/bin/env bash
# init_style_guide.sh — scaffold an ELI5 style guide at docs/.eli5-style.md
# if one doesn't already exist at any of the conventional paths.
#
# Usage: scripts/init_style_guide.sh <repo-path>
#
# Exits 0 with one of two stdout lines:
#   FOUND <path>       — style guide already exists at <path>
#   CREATED <path>     — style guide was just created at <path>

set -uo pipefail

ROOT="${1:-.}"

if [[ ! -d "$ROOT" ]]; then
  echo "Error: '$ROOT' is not a directory" >&2
  exit 1
fi

# Resolve to absolute so the path is unambiguous in output
ABS_ROOT=$(cd "$ROOT" && pwd)

# Look for existing style guide at conventional paths
for path in \
  "$ABS_ROOT/docs/.eli5-style.md" \
  "$ABS_ROOT/.eli5-style.md" \
  "$ABS_ROOT/docs/_eli5-style.md"; do
  if [[ -f "$path" ]]; then
    echo "FOUND $path"
    exit 0
  fi
done

# Not found — locate the template (alongside this script)
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TEMPLATE="$SCRIPT_DIR/../assets/style-guide-template.md"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "Error: style guide template not found at $TEMPLATE" >&2
  exit 1
fi

# Create docs/ if it doesn't exist, then copy the template
TARGET="$ABS_ROOT/docs/.eli5-style.md"
mkdir -p "$ABS_ROOT/docs"
cp "$TEMPLATE" "$TARGET" || { echo "Error: could not write $TARGET" >&2; exit 1; }

echo "CREATED $TARGET"
