#!/usr/bin/env bash
# prove-it / verify.sh — prove that work shipped and works. Any site, any host.
#
#   verify.sh                                   uses ./.prove-it (or <git root>/.prove-it)
#   verify.sh <url> --expect "text" [options]   ad hoc; adds to the config if one exists
#
# Page      --expect S           string that must be in the page source       (repeatable)
#           --reject S           string that must NOT be in the page source   (repeatable)
#           --status N           expected HTTP status of <url>                (default 200)
# Deploy    --version-url U      URL whose response contains the live commit SHA
#           --sha REF            commit expected live and in CI               (default HEAD)
#           --wait SECS          keep polling deploy + CI for up to SECS      (default 0)
# Endpoint  --endpoint U         call this endpoint (repeatable; the flags below apply to the latest)
#           --method M           default POST
#           --data D             default {}
#           --content-type T     default application/json
#           --endpoint-status N  the status a healthy endpoint returns. Without it: UNVERIFIED.
#           --endpoint-expect S  string that must be in the response body
#           --endpoint-reject S  string that must NOT be in the response body
# Scope     --na LAYER           this layer does not apply here:
#                                git ci deploy pages endpoints storage analytics
#           --config FILE | --no-config
#
# Exit   0  every declared layer passed. The only code that means "you may say it works".
#        1  something FAILED
#        2  nothing failed, but at least one layer is UNVERIFIED
#        64 bad usage (unknown flag, bad config line). Nothing is ever silently ignored.
#
# Matching is literal (fixed strings, never regex) against the raw response, and the
# status code and body always come from the same request.

set -uo pipefail
export GH_PROMPT_DISABLED=1 GH_NO_UPDATE_NOTIFIER=1

# ---------- output ----------
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_G=$'\033[32m'; C_R=$'\033[31m'; C_Y=$'\033[33m'; C_D=$'\033[2m'; C_Z=$'\033[0m'
else C_G=""; C_R=""; C_Y=""; C_D=""; C_Z=""; fi
N_PASS=0; N_FAIL=0; N_UNV=0; N_NA=0; N_WARN=0
pass(){ N_PASS=$((N_PASS+1)); printf '  %sPASS%s        %s\n' "$C_G" "$C_Z" "$1"; }
fail(){ N_FAIL=$((N_FAIL+1)); printf '  %sFAIL%s        %s\n' "$C_R" "$C_Z" "$1"; }
unv(){  N_UNV=$((N_UNV+1));   printf '  %sUNVERIFIED%s  %s\n' "$C_Y" "$C_Z" "$1"; }
na(){   N_NA=$((N_NA+1));     printf '  %sN/A%s         %s\n' "$C_D" "$C_Z" "$1"; }
warn(){ N_WARN=$((N_WARN+1)); printf '  %sWARN%s        %s\n' "$C_Y" "$C_Z" "$1"; }
note(){ printf '              %s\n' "$1"; }
die(){ printf 'verify.sh: %s\n' "$1" >&2; exit 64; }
usage(){ sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'; }

# ---------- small helpers ----------
trim(){ local s="$1"; s="${s#"${s%%[![:space:]]*}"}"; s="${s%"${s##*[![:space:]]}"}"; printf '%s' "$s"; }
unquote(){ local s="$1" f l
  if [ ${#s} -ge 2 ]; then f="${s:0:1}"; l="${s:${#s}-1:1}"
    if [ "$f" = "$l" ] && { [ "$f" = '"' ] || [ "$f" = "'" ]; }; then s="${s:1:${#s}-2}"; fi
  fi; printf '%s' "$s"; }
is_num(){ case "$1" in ''|*[!0-9]*) return 1;; esac; return 0; }
host_of(){ local h="${1#*://}"; h="${h%%[/:?#]*}"; printf '%s' "$h" | tr 'A-Z' 'a-z'; }

# ---------- state ----------
VERSION_URL=""; SHA_REF=""; WAIT=0; CFG=""; CFG_DIR="$PWD"; USE_CFG=1; CTX=""
NA_N=0; NA_LAYER=(); NA_WHY=(); NA_REASON=""
P_N=0; P_URL=(); P_STATUS=()                                   # pages
E_N=0; E_URL=(); E_METHOD=(); E_DATA=(); E_CTYPE=(); E_STATUS=()   # endpoints
A_N=0; A_TGT=(); A_KIND=(); A_STR=()                           # assertions -> "p<i>" / "e<i>"
K_N=0; K_NAME=(); K_CMD=()                                     # custom checks

declare_na(){ case "$1" in git|ci|deploy|pages|endpoints|storage|analytics) ;;
    *) die "unknown layer '$1' for na (use: git ci deploy pages endpoints storage analytics)";; esac
  NA_LAYER[$NA_N]="$1"; NA_WHY[$NA_N]="$2"; NA_N=$((NA_N+1)); }
is_na(){ local i=0; while [ $i -lt $NA_N ]; do
    if [ "${NA_LAYER[$i]}" = "$1" ]; then NA_REASON="${NA_WHY[$i]}"; return 0; fi; i=$((i+1)); done; return 1; }
add_page(){ P_URL[$P_N]="$1"; P_STATUS[$P_N]="200"; CTX="p$P_N"; P_N=$((P_N+1)); }
add_endpoint(){ E_URL[$E_N]="$1"; E_METHOD[$E_N]="POST"; E_DATA[$E_N]='{}'
  E_CTYPE[$E_N]="application/json"; E_STATUS[$E_N]=""; CTX="e$E_N"; E_N=$((E_N+1)); }
add_assert(){ [ -n "$CTX" ] || die "'$1' needs a page or endpoint before it"
  A_TGT[$A_N]="$CTX"; A_KIND[$A_N]="$1"; A_STR[$A_N]="$2"; A_N=$((A_N+1)); }
set_status(){ [ -n "$CTX" ] || die "'status' needs a page or endpoint before it"
  is_num "$1" || die "status must be a number, got '$1'"
  case "$CTX" in p*) P_STATUS[${CTX#p}]="$1";; e*) E_STATUS[${CTX#e}]="$1";; esac; }
need_ep(){ case "$CTX" in e*) ;; *) die "'$1' only applies to an endpoint — put it after one";; esac; }

# ---------- config file: one directive per line, "<keyword> <rest of line>" ----------
load_config(){ local f="$1" line key rest ln=0 l w
  CFG_DIR=$(cd "$(dirname "$f")" && pwd)
  while IFS= read -r line || [ -n "$line" ]; do
    ln=$((ln+1)); line="${line%$'\r'}"; line=$(trim "$line")
    case "$line" in ''|\#*) continue;; esac
    key="${line%%[[:space:]]*}"; rest=$(trim "${line#"$key"}")
    case "$key" in
      page)          [ -n "$rest" ] || die "$f:$ln: 'page' needs a URL"; add_page "$rest" ;;
      endpoint)      [ -n "$rest" ] || die "$f:$ln: 'endpoint' needs a URL"; add_endpoint "$rest" ;;
      expect|reject) rest=$(unquote "$rest"); [ -n "$rest" ] || die "$f:$ln: '$key' needs a string"
                     add_assert "$key" "$rest" ;;
      status)        set_status "$rest" ;;
      method)        need_ep method; E_METHOD[${CTX#e}]="$rest" ;;
      data)          need_ep data; E_DATA[${CTX#e}]="$rest" ;;
      content-type)  need_ep content-type; E_CTYPE[${CTX#e}]="$rest" ;;
      version)       [ -n "$rest" ] || die "$f:$ln: 'version' needs a URL"; VERSION_URL="$rest"; CTX="" ;;
      sha)           SHA_REF="$rest" ;;
      wait)          is_num "$rest" || die "$f:$ln: 'wait' needs a number of seconds"; WAIT="$rest" ;;
      na)            l="${rest%%[[:space:]]*}"; w=$(trim "${rest#"$l"}")
                     declare_na "$l" "${w:-declared in $(basename "$f")}" ;;
      check)         l="${rest%%[[:space:]]*}"; w=$(trim "${rest#"$l"}")
                     { [ -n "$l" ] && [ -n "$w" ]; } || die "$f:$ln: use 'check <name> <command>'"
                     K_NAME[$K_N]="$l"; K_CMD[$K_N]="$w"; K_N=$((K_N+1)); CTX="" ;;
      *)             die "$f:$ln: unknown directive '$key'" ;;
    esac
  done < "$f"
}

# ---------- arguments ----------
takes_value(){ case "$1" in --expect|--reject|--status|--version-url|--sha|--wait|--endpoint|--method|--data|\
--content-type|--endpoint-status|--endpoint-expect|--endpoint-reject|--na|--config) return 0;; esac; return 1; }

ARGS=("$@"); ARGC=$#
i=0; while [ $i -lt $ARGC ]; do a="${ARGS[$i]}"          # pre-scan: which config?
  if takes_value "$a"; then i=$((i+1)); [ $i -lt $ARGC ] || die "$a needs a value"
    [ "$a" = "--config" ] && CFG="${ARGS[$i]}"
  elif [ "$a" = "--no-config" ]; then USE_CFG=0
  elif [ "$a" = "-h" ] || [ "$a" = "--help" ]; then usage; exit 0; fi
  i=$((i+1)); done

if [ $USE_CFG -eq 1 ] && [ -z "$CFG" ]; then
  if [ -f ./.prove-it ]; then CFG="./.prove-it"
  else TOP=$(git rev-parse --show-toplevel 2>/dev/null || true)
    if [ -n "$TOP" ] && [ -f "$TOP/.prove-it" ]; then CFG="$TOP/.prove-it"; fi
  fi
fi
if [ $USE_CFG -eq 1 ] && [ -n "$CFG" ]; then
  [ -f "$CFG" ] || die "config not found: $CFG"
  load_config "$CFG"; CTX=""
else CFG=""; fi

CLI_URL=""; CLI_STATUS=""; X_N=0; X_KIND=(); X_STR=()
i=0; while [ $i -lt $ARGC ]; do a="${ARGS[$i]}"; v=""
  if takes_value "$a"; then i=$((i+1)); v="${ARGS[$i]}"; fi
  case "$a" in
    --expect)          X_KIND[$X_N]="expect"; X_STR[$X_N]="$v"; X_N=$((X_N+1)) ;;
    --reject)          X_KIND[$X_N]="reject"; X_STR[$X_N]="$v"; X_N=$((X_N+1)) ;;
    --status)          is_num "$v" || die "--status needs a number"; CLI_STATUS="$v" ;;
    --version-url)     VERSION_URL="$v" ;;
    --sha)             SHA_REF="$v" ;;
    --wait)            is_num "$v" || die "--wait needs a number of seconds"; WAIT="$v" ;;
    --endpoint)        add_endpoint "$v" ;;
    --method)          need_ep --method; E_METHOD[${CTX#e}]="$v" ;;
    --data)            need_ep --data; E_DATA[${CTX#e}]="$v" ;;
    --content-type)    need_ep --content-type; E_CTYPE[${CTX#e}]="$v" ;;
    --endpoint-status) need_ep --endpoint-status; is_num "$v" || die "--endpoint-status needs a number"
                       E_STATUS[${CTX#e}]="$v" ;;
    --endpoint-expect) need_ep --endpoint-expect; add_assert expect "$v" ;;
    --endpoint-reject) need_ep --endpoint-reject; add_assert reject "$v" ;;
    --na)              declare_na "$v" "declared on the command line" ;;
    --config|--no-config) : ;;
    -*)                die "unknown flag '$a' — nothing is silently ignored (see --help)" ;;
    *)                 [ -z "$CLI_URL" ] || die "two URLs given ('$CLI_URL' and '$a') — put extra pages in .prove-it"
                       CLI_URL="$a" ;;
  esac
  i=$((i+1)); done

if [ -n "$CLI_URL" ]; then
  add_page "$CLI_URL"; [ -n "$CLI_STATUS" ] && P_STATUS[$((P_N-1))]="$CLI_STATUS"
  j=0; while [ $j -lt $X_N ]; do add_assert "${X_KIND[$j]}" "${X_STR[$j]}"; j=$((j+1)); done
elif [ $X_N -gt 0 ] || [ -n "$CLI_STATUS" ]; then
  die "--expect / --reject / --status need a <url> to apply to"
fi

# ---------- http ----------
TMP=$(mktemp -d 2>/dev/null || mktemp -d -t proveit) || die "cannot create a temp dir"
trap 'rm -rf "$TMP"' EXIT
UA="prove-it/2 (verify.sh; curl)"
CURL_RC=0; HTTP_CODE=""; HTTP_FINAL=""
TRIES="${PROVE_IT_TRIES:-3}"; GAP="${PROVE_IT_GAP:-10}"

fetch(){ local u="${1%%#*}" out                # GET, cache-busted; status + body from ONE request
  : > "$TMP/body"; : > "$TMP/hdr"
  case "$u" in *\?*) u="$u&cb=$RANDOM$RANDOM";; *) u="$u?cb=$RANDOM$RANDOM";; esac
  out=$(curl -sS -L --compressed --connect-timeout 10 --max-time 30 -A "$UA" \
        -H 'Cache-Control: no-cache' -H 'Pragma: no-cache' \
        -D "$TMP/hdr" -o "$TMP/body" -w '%{http_code} %{url_effective}' "$u" 2>"$TMP/err"); CURL_RC=$?
  HTTP_CODE="${out%% *}"; HTTP_FINAL="${out#* }"; }
has(){ grep -aqF -- "$1" "$TMP/body"; }        # literal match on a file: no pipe, no SIGPIPE, no regex
curl_err(){ local m; m=$(head -1 "$TMP/err" 2>/dev/null); printf '%s' "${m:-curl exit $CURL_RC}"; }
snippet(){ head -c 200 "$TMP/body" 2>/dev/null | tr '\n\r\t' '   '; }

echo "prove-it · $(date '+%Y-%m-%d %H:%M:%S %Z')"
[ -n "$CFG" ] && echo "config: $CFG"

# ---------- which commit are we proving? ----------
IN_GIT=0; git rev-parse --git-dir >/dev/null 2>&1 && IN_GIT=1
WANT_SHA=""
if [ -n "$SHA_REF" ]; then
  if [ $IN_GIT -eq 1 ] && S=$(git rev-parse --verify -q "$SHA_REF^{commit}" 2>/dev/null); then WANT_SHA="$S"
  else case "$SHA_REF" in *[!0-9a-fA-F]*) die "--sha '$SHA_REF' is neither a commit in this repo nor a hex SHA";; esac
    [ ${#SHA_REF} -ge 7 ] || die "--sha needs at least 7 hex characters"
    WANT_SHA=$(printf '%s' "$SHA_REF" | tr 'A-F' 'a-f'); fi
elif [ $IN_GIT -eq 1 ]; then WANT_SHA=$(git rev-parse HEAD 2>/dev/null || true); fi
SHORT="${WANT_SHA:0:7}"

# ====================================================================================
echo; echo "=== 1. CODE — committed and pushed? ==="
if is_na git; then na "git — $NA_REASON"
elif [ $IN_GIT -eq 0 ]; then
  unv "not a git repository — nothing proves what was committed or pushed (no repo for this site? declare 'na git')"
else
  DIRTY=$(git status --porcelain 2>/dev/null)
  if [ -z "$DIRTY" ]; then pass "working tree clean"
  else fail "uncommitted changes — $(printf '%s\n' "$DIRTY" | wc -l | tr -d ' ') path(s):"
    printf '%s\n' "$DIRTY" | head -10 | while IFS= read -r l; do note "$l"; done; fi
  BR=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
  if UP=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null) && [ -n "$UP" ]; then
    if git fetch -q "${UP%%/*}" 2>/dev/null; then
      L=$(git rev-parse HEAD); R=$(git rev-parse "$UP")
      if [ "$L" = "$R" ]; then pass "HEAD ${L:0:7} == $UP"
      else fail "HEAD ${L:0:7} != $UP ${R:0:7} — ahead $(git rev-list --count "$UP..HEAD"), behind $(git rev-list --count "HEAD..$UP")"; fi
    else unv "git fetch ${UP%%/*} failed — comparing against a stale remote ref would prove nothing"; fi
  else unv "branch '$BR' has no upstream — nothing proves it was pushed"; fi
fi

# ====================================================================================
echo; echo "=== 2. CI — every job, for THIS commit ==="
CI_ROWS=""; CI_TOTAL=0; CI_PENDING=0
ci_snapshot(){ local raw id st cc wf seen=$'\n'     # latest run per workflow, for WANT_SHA only
  raw=$(gh run list --commit "$WANT_SHA" --limit 100 \
        --json databaseId,status,conclusion,workflowName,createdAt \
        --jq 'sort_by(.createdAt)|reverse|.[]|[(.databaseId|tostring),.status,(if (.conclusion//"")=="" then "-" else .conclusion end),(if (.workflowName//"")=="" then "-" else .workflowName end)]|@tsv' \
        2>"$TMP/err") || return 1
  CI_ROWS=""; CI_TOTAL=0; CI_PENDING=0
  while IFS=$'\t' read -r id st cc wf; do
    [ -n "$id" ] || continue
    case "$seen" in *$'\n'"$wf"$'\n'*) continue;; esac
    seen="$seen$wf"$'\n'
    CI_ROWS="$CI_ROWS$id"$'\t'"$st"$'\t'"$cc"$'\t'"$wf"$'\n'
    CI_TOTAL=$((CI_TOTAL+1)); [ "$st" = "completed" ] || CI_PENDING=$((CI_PENDING+1))
  done <<<"$raw"
  return 0; }
bad_jobs(){ gh run view "$1" --json jobs \
  --jq '.jobs[]|select(.conclusion=="failure" or .conclusion=="cancelled" or .conclusion=="timed_out")|"\(.name) [\(.conclusion)]"' 2>/dev/null; }

if is_na ci; then na "ci — $NA_REASON"
elif ! command -v gh >/dev/null 2>&1; then
  unv "gh CLI not installed — open the CI for commit ${SHORT:-?} by hand and check every job (no CI here? declare 'na ci')"
elif ! gh auth status >/dev/null 2>&1; then unv "gh is not authenticated — cannot read CI"
elif [ -z "$WANT_SHA" ]; then unv "no commit to look up (not a git repo — pass --sha)"
else
  T0=$SECONDS; CI_ERR=0
  while :; do
    if ! ci_snapshot; then CI_ERR=1; break; fi
    if [ $CI_TOTAL -gt 0 ] && [ $CI_PENDING -eq 0 ]; then break; fi
    [ $((SECONDS-T0)) -ge "$WAIT" ] && break
    note "CI for $SHORT: $CI_TOTAL run(s), $CI_PENDING still running — waiting ($((SECONDS-T0))s of ${WAIT}s)"; sleep 15
  done
  if [ $CI_ERR -eq 1 ]; then unv "gh could not list runs: $(curl_err)"
  elif [ $CI_TOTAL -eq 0 ]; then
    unv "no CI runs exist for $SHORT — not triggered yet (use --wait), or this repo has no CI (then declare 'na ci')"
  else
    while IFS=$'\t' read -r id st cc wf; do
      [ -n "$id" ] || continue
      if [ "$st" != "completed" ]; then unv "$wf: still $st (run $id) — re-run with --wait"
      elif [ "$cc" = "success" ]; then
        BJ=$(bad_jobs "$id")
        if [ -z "$BJ" ]; then pass "$wf: every job green (run $id)"
        else fail "$wf: run is green but these jobs are not (run $id):"; printf '%s\n' "$BJ" | while IFS= read -r l; do note "$l"; done; fi
      elif [ "$cc" = "skipped" ] || [ "$cc" = "neutral" ]; then note "$wf: $cc for this commit (run $id) — proves nothing either way"
      else fail "$wf: $cc (run $id)"; bad_jobs "$id" | while IFS= read -r l; do note "$l"; done; fi
    done <<<"$CI_ROWS"
    RED=$(gh run list --limit 10 --json conclusion --jq '[.[]|select(.conclusion=="failure")]|length' 2>/dev/null || echo 0)
    if is_num "$RED" && [ "$RED" -ge 3 ]; then warn "$RED of the last 10 runs failed — a CI that is usually red stops being read"; fi
  fi
fi

# ====================================================================================
echo; echo "=== 3. DEPLOY — is the live build this commit? ==="
DEPLOY_OK=0
if is_na deploy; then na "deploy — $NA_REASON"
elif [ -z "$VERSION_URL" ]; then
  unv "no version URL — nothing proves the live site is this commit, so the page checks below may be reading an old build"
  note "fix: run scripts/stamp-version.sh in the build, then pass --version-url <site>/version.json"
elif [ -z "$WANT_SHA" ]; then
  fetch "$VERSION_URL"; unv "no commit to compare against (not a git repo — pass --sha)"; note "live says: $(snippet)"
else
  T0=$SECONDS
  while :; do
    fetch "$VERSION_URL"
    if [ $CURL_RC -eq 0 ] && { grep -aqiF -- "$SHORT" "$TMP/body" || grep -aqiF -- "$SHORT" "$TMP/hdr"; }; then DEPLOY_OK=1; break; fi
    [ $((SECONDS-T0)) -ge "$WAIT" ] && break
    note "live build is not $SHORT yet — waiting ($((SECONDS-T0))s of ${WAIT}s)"; sleep 10
  done
  if [ $DEPLOY_OK -eq 1 ]; then pass "live build is $SHORT ($VERSION_URL)"
  elif [ $CURL_RC -ne 0 ]; then fail "could not read $VERSION_URL: $(curl_err)"
  else fail "live build is NOT $SHORT — deploy unfinished, failed, or pointed somewhere else (HTTP $HTTP_CODE)"
    note "live says: $(snippet)"; fi
fi

# ====================================================================================
echo; echo "=== 4. PAGES — the right content, not just a 200 ==="
BUF_N=0; BUF_K=(); BUF_M=(); PAGE_BAD=0
buf(){ BUF_K[$BUF_N]="$1"; BUF_M[$BUF_N]="$2"; BUF_N=$((BUF_N+1)); }
flush_buf(){ local b=0; while [ $b -lt $BUF_N ]; do "${BUF_K[$b]}" "${BUF_M[$b]}"; b=$((b+1)); done; }
check_page(){ local p="$1" k=0 n_exp=0
  BUF_N=0; PAGE_BAD=0; fetch "${P_URL[$p]}"
  if [ $CURL_RC -ne 0 ]; then buf fail "request failed: $(curl_err)"; PAGE_BAD=1; return 0; fi
  if [ "$HTTP_CODE" = "${P_STATUS[$p]}" ]; then buf pass "HTTP $HTTP_CODE"
  else buf fail "HTTP $HTTP_CODE (expected ${P_STATUS[$p]})"; PAGE_BAD=1; fi
  while [ $k -lt $A_N ]; do
    if [ "${A_TGT[$k]}" = "p$p" ]; then
      if [ "${A_KIND[$k]}" = "expect" ]; then n_exp=$((n_exp+1))
        if has "${A_STR[$k]}"; then buf pass "contains: ${A_STR[$k]}"
        else buf fail "MISSING: ${A_STR[$k]}"; PAGE_BAD=1; fi
      else
        if has "${A_STR[$k]}"; then buf fail "STILL PRESENT (should be gone): ${A_STR[$k]}"; PAGE_BAD=1
        else buf pass "absent as intended: ${A_STR[$k]}"; fi
      fi
    fi; k=$((k+1)); done
  if [ $n_exp -eq 0 ]; then buf unv "no --expect string for this page — a status code alone proves nothing"; fi
  return 0; }
SQ="'"; QC="[\"$SQ]"
check_links(){ local pagehost tag href h label found=0 rc   # canonical / og:url: resolves? right domain?
  grep -aqi '<html' "$TMP/body" || return 0
  tr '\n\r' '  ' < "$TMP/body" > "$TMP/flat"; pagehost=$(host_of "$HTTP_FINAL")
  for label in canonical og:url; do
    if [ "$label" = "canonical" ]; then
      tag=$(grep -aoiE "<link[^>]*rel=${QC}?canonical${QC}?[^>]*>" "$TMP/flat" | head -1)
      href=$(printf '%s' "$tag" | sed -nE "s/.*[[:space:]]href=${QC}?([^\"$SQ >]+).*/\1/p")
    else
      tag=$(grep -aoiE "<meta[^>]*property=${QC}?og:url${QC}?[^>]*>" "$TMP/flat" | head -1)
      href=$(printf '%s' "$tag" | sed -nE "s/.*[[:space:]]content=${QC}?([^\"$SQ >]+).*/\1/p")
    fi
    case "$href" in http://*|https://*) ;; *) continue;; esac
    found=1; h=$(host_of "$href")
    curl -s -o /dev/null --connect-timeout 8 --max-time 10 -I "https://$h" 2>/dev/null; rc=$?
    if [ $rc -eq 6 ]; then fail "$label points at a domain that does not resolve: $h"
    elif [ "${h#www.}" != "${pagehost#www.}" ]; then warn "$label points at a different domain: $h (this page is on $pagehost)"
    else pass "$label domain resolves and matches: $h"; fi
  done
  [ $found -eq 0 ] && note "no canonical or og:url tag found"
  return 0; }

if is_na pages; then na "pages — $NA_REASON"
elif [ $P_N -eq 0 ]; then unv "no page given — pass a <url> with --expect, or add 'page' lines to .prove-it"
else
  [ $DEPLOY_OK -eq 1 ] && [ "$TRIES" -gt 2 ] && TRIES=2
  p=0; while [ $p -lt $P_N ]; do
    echo "  ${P_URL[$p]}"
    t=1; while :; do
      check_page $p
      [ $PAGE_BAD -eq 0 ] && break
      [ $t -ge "$TRIES" ] && break
      note "attempt $t did not match — retrying in ${GAP}s in case the edge is mid-rollout"; sleep "$GAP"; t=$((t+1))
    done
    flush_buf
    if [ $PAGE_BAD -eq 0 ] && [ $t -gt 1 ]; then warn "only matched on attempt $t — responses are inconsistent; re-run before trusting it"; fi
    [ $CURL_RC -eq 0 ] && [ "$HTTP_CODE" = "${P_STATUS[$p]}" ] && check_links
    p=$((p+1)); done
fi

# ====================================================================================
echo; echo "=== 5. ENDPOINTS — the expected answer, not just an answer ==="
call_ep(){ local e="$1" m out; m=$(printf '%s' "${E_METHOD[$e]}" | tr 'a-z' 'A-Z'); : > "$TMP/body"
  if [ "$m" = "GET" ]; then
    out=$(curl -sS --compressed --connect-timeout 10 --max-time 30 -A "$UA" \
          -o "$TMP/body" -w '%{http_code}' "${E_URL[$e]}" 2>"$TMP/err"); CURL_RC=$?
  elif [ "$m" = "HEAD" ]; then
    out=$(curl -sS -I --connect-timeout 10 --max-time 30 -A "$UA" \
          -o "$TMP/body" -w '%{http_code}' "${E_URL[$e]}" 2>"$TMP/err"); CURL_RC=$?
  else
    out=$(curl -sS --compressed --connect-timeout 10 --max-time 30 -A "$UA" -X "$m" \
          -H "Content-Type: ${E_CTYPE[$e]}" --data-raw "${E_DATA[$e]}" \
          -o "$TMP/body" -w '%{http_code}' "${E_URL[$e]}" 2>"$TMP/err"); CURL_RC=$?
  fi
  HTTP_CODE="$out"; EP_METHOD="$m"; }

if is_na endpoints; then na "endpoints — $NA_REASON"
elif [ $E_N -eq 0 ]; then unv "no endpoint given — pass --endpoint, or declare 'na endpoints' if the site has none"
else
  e=0; while [ $e -lt $E_N ]; do
    call_ep $e; echo "  $EP_METHOD ${E_URL[$e]}"
    if [ $CURL_RC -ne 0 ]; then fail "request failed: $(curl_err)"
    else
      WANT="${E_STATUS[$e]}"
      if [ -z "$WANT" ]; then unv "answered HTTP $HTTP_CODE — no expected status declared, so that proves nothing (add --endpoint-status)"
      elif [ "$HTTP_CODE" = "$WANT" ]; then pass "HTTP $HTTP_CODE, as expected"
      else fail "HTTP $HTTP_CODE (expected $WANT)"
        case "$HTTP_CODE" in 3*) note "redirects drop request bodies — point this at the final URL";; esac; fi
      k=0; while [ $k -lt $A_N ]; do
        if [ "${A_TGT[$k]}" = "e$e" ]; then
          if [ "${A_KIND[$k]}" = "expect" ]; then
            if has "${A_STR[$k]}"; then pass "body contains: ${A_STR[$k]}"; else fail "body MISSING: ${A_STR[$k]}"; fi
          else
            if has "${A_STR[$k]}"; then fail "body contains (should not): ${A_STR[$k]}"; else pass "body lacks, as intended: ${A_STR[$k]}"; fi
          fi
        fi; k=$((k+1)); done
      note "body: $(snippet)"
      case "$WANT" in 2*) note "a 2xx is the handshake, not the proof — read the record back at the destination (SKILL.md, layer 5)";; esac
    fi
    e=$((e+1)); done
fi

# ====================================================================================
run_check(){ local rc                                      # $1 name, $2 command — exit 0 means proven
  ( cd "$CFG_DIR" && bash -c "$2" ) >"$TMP/chk" 2>&1; rc=$?
  if [ $rc -eq 0 ]; then pass "$1: \`$2\` exited 0"; else fail "$1: \`$2\` exited $rc"; fi
  tail -5 "$TMP/chk" | while IFS= read -r l; do note "$l"; done; }
layer_checks(){ local j=0 ran=0                            # $1 layer, $2 message when nothing checks it
  if is_na "$1"; then na "$1 — $NA_REASON"; return 0; fi
  while [ $j -lt $K_N ]; do
    if [ "${K_NAME[$j]}" = "$1" ]; then run_check "$1" "${K_CMD[$j]}"; ran=1; fi; j=$((j+1)); done
  if [ $ran -eq 0 ]; then unv "$2"; fi; return 0; }

echo; echo "=== 6. STORAGE — write, then read it back ==="
layer_checks storage "a generic script cannot see your store — do SKILL.md layer 6 by hand, add 'check storage <command>', or declare 'na storage'"
echo; echo "=== 7. ANALYTICS — did the event arrive? ==="
layer_checks analytics "a generic script cannot see your analytics — do SKILL.md layer 7 by hand, add 'check analytics <command>', or declare 'na analytics'"

EXTRA=0; j=0; while [ $j -lt $K_N ]; do
  case "${K_NAME[$j]}" in storage|analytics) ;; *)
    [ $EXTRA -eq 0 ] && { echo; echo "=== PROJECT CHECKS ==="; EXTRA=1; }
    run_check "${K_NAME[$j]}" "${K_CMD[$j]}" ;; esac
  j=$((j+1)); done

# ====================================================================================
echo; echo "=== RESULT ==="
echo "  pass $N_PASS · fail $N_FAIL · unverified $N_UNV · n/a $N_NA · warn $N_WARN"
if [ $N_FAIL -gt 0 ]; then
  echo "  FAILED — do not report this as working. Lead with the FAIL lines."; exit 1
elif [ $N_UNV -gt 0 ]; then
  echo "  NOT PROVEN — nothing failed, but the UNVERIFIED layers were not checked."
  echo "  Report them as unverified, check them by hand, or declare them n/a. Do not say \"it works\"."; exit 2
else
  echo "  PROVEN — every declared layer passed. Claim only what is listed above."; exit 0
fi
