#!/usr/bin/env bash
# slop-scan: render the page, measure AI fingerprints, save screenshots.
# Usage: bash render.sh <url | folder | file.html> [outdir]
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:?usage: render.sh <url|folder|file.html> [outdir]}"
OUT="${2:-./slop-shots}"
CACHE="${SLOP_SCAN_CACHE:-$HOME/.cache/slop-scan}"
mkdir -p "$OUT" "$CACHE"
if [ ! -d "$CACHE/node_modules/playwright" ]; then
  echo "First run: installing Playwright into $CACHE ..." >&2
  npm install --silent --prefix "$CACHE" playwright >&2 || { echo "npm install failed. Use Claude in Chrome or screenshots instead." >&2; exit 1; }
fi
SERVER_PID=""
if [[ ! "$TARGET" =~ ^https?:// ]]; then
  DIR="$TARGET"; PAGE="index.html"
  if [ -f "$TARGET" ]; then DIR="$(dirname "$TARGET")"; PAGE="$(basename "$TARGET")"; fi
  PORT=$(python3 -c 'import socket;s=socket.socket();s.bind(("",0));print(s.getsockname()[1])')
  (cd "$DIR" && exec python3 -c "import http.server as h,functools,sys;H=h.SimpleHTTPRequestHandler;H.extensions_map.update({'.html':'text/html; charset=utf-8','.htm':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8'});h.ThreadingHTTPServer(('127.0.0.1',int(sys.argv[1])),H).serve_forever()" "$PORT" >/dev/null 2>&1) &
  SERVER_PID=$!
  sleep 1
  URL="http://127.0.0.1:$PORT/$PAGE"
else
  URL="$TARGET"
fi
trap '[ -n "$SERVER_PID" ] && kill "$SERVER_PID" 2>/dev/null' EXIT
run() { NODE_PATH="$CACHE/node_modules" node "$HERE/render-scan.cjs" "$URL" "$OUT"; }
run; code=$?
if [ $code -eq 3 ]; then
  echo "Installing Chromium for Playwright ..." >&2
  "$CACHE/node_modules/.bin/playwright" install chromium >&2 && run
  code=$?
fi
exit $code
