#!/usr/bin/env bash
# prove-it / stamp-version.sh — write the commit being built into version.json, so
# verify.sh can prove WHICH commit is live instead of trusting a status badge.
#
#   stamp-version.sh [publish-dir]      default: public
#
# Run it in the build step, pointed at the folder that gets published:
#   public (Next, Astro, Vite, CRA) · static (SvelteKit, Hugo, Gatsby) · dist / build / _site
#   "build": "bash scripts/stamp-version.sh public && next build"
#
# Works on any host: it reads whichever commit variable the platform provides, then
# falls back to git. No build step at all (WordPress, rsync, FTP)? Have the deploy
# script run:  git rev-parse HEAD > version.txt   — verify.sh only needs the SHA to
# appear somewhere in the response body or headers of the --version-url.

set -euo pipefail
OUT="${1:-public}"

SHA="${PROVE_IT_SHA:-}"                                   # explicit override always wins
for v in CF_PAGES_COMMIT_SHA WORKERS_CI_COMMIT_SHA VERCEL_GIT_COMMIT_SHA COMMIT_REF \
         RENDER_GIT_COMMIT RAILWAY_GIT_COMMIT_SHA AWS_COMMIT_ID SOURCE_VERSION \
         CI_COMMIT_SHA BITBUCKET_COMMIT CIRCLE_SHA1 GITHUB_SHA; do
  [ -n "$SHA" ] && break
  SHA="${!v:-}"
done
[ -n "$SHA" ] || SHA=$(git rev-parse HEAD 2>/dev/null || true)
[ -n "$SHA" ] || { echo "stamp-version: no commit SHA found — set PROVE_IT_SHA" >&2; exit 1; }

mkdir -p "$OUT"
printf '{"commit":"%s","built":"%s"}\n' "$SHA" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$OUT/version.json"
echo "stamp-version: $OUT/version.json -> ${SHA:0:12}"
