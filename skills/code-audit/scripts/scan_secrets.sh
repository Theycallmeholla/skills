#!/usr/bin/env bash
# scan_secrets.sh — regex-based search for credentials, keys, and tokens
#
# Usage: scripts/scan_secrets.sh <path>
#
# This is a fast first pass, not a replacement for gitleaks/trufflehog.
# It produces enough signal to know whether a deeper scan is warranted.

set -uo pipefail

ROOT="${1:-.}"

if [[ ! -d "$ROOT" ]]; then
  echo "Error: '$ROOT' is not a directory" >&2
  exit 1
fi

cd "$ROOT" || exit 1

IGNORE_DIRS='node_modules|vendor|\.git|\.svn|\.hg|dist|build|target|\.venv|venv|__pycache__|\.next|\.nuxt|out|coverage|\.cache|bower_components|jspm_packages'

echo "=========================================="
echo " Secret scan: $ROOT"
echo "=========================================="
echo

# Collect file list once for reuse
TMPFILES=$(mktemp)
trap 'rm -f $TMPFILES' EXIT
find . -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -Ev "\.(jpg|jpeg|png|gif|webp|ico|svg|pdf|woff|woff2|ttf|eot|mp4|mp3|webm|zip|tar|gz|tgz|bz2|7z|rar|exe|dll|so|dylib|class|jar|war|min\.js|min\.css)$" \
  > "$TMPFILES"

scan() {
  local label="$1"
  local pattern="$2"
  local results
  # -I skips binary, -n shows line numbers, -E uses extended regex
  results=$(< "$TMPFILES" xargs grep -InE -e "$pattern" 2>/dev/null | head -20)
  if [[ -n "$results" ]]; then
    echo "── $label ────"
    echo "$results"
    echo
  fi
}

echo "(Showing up to 20 hits per category. Empty section = no hits.)"
echo

# --- Cloud provider keys ---
scan "AWS Access Key" 'AKIA[0-9A-Z]{16}'
scan "AWS Secret Key (heuristic)" 'aws_secret_access_key\s*[:=]\s*["'\''][A-Za-z0-9/+=]{40}["'\'']'
scan "AWS Session Token" 'aws_session_token\s*[:=]\s*["'\''][A-Za-z0-9/+=]{100,}["'\'']'
scan "GCP Service Account" '"type":\s*"service_account"'
scan "GCP API Key" 'AIza[0-9A-Za-z\-_]{35}'
scan "Azure Storage Account Key" 'DefaultEndpointsProtocol=.*AccountKey='

# --- Code hosting / CI ---
scan "GitHub Personal Access Token" '\b(ghp_|github_pat_)[A-Za-z0-9_]{36,}'
scan "GitHub OAuth" '\bgho_[A-Za-z0-9_]{36}'
scan "GitHub App Token" '\b(ghu_|ghs_)[A-Za-z0-9_]{36}'
scan "GitLab Personal Access Token" '\bglpat-[A-Za-z0-9_-]{20}'
scan "Travis CI Token" 'travis(-ci|_token)\s*[:=]\s*["'\''][A-Za-z0-9]{20,}["'\'']'
scan "CircleCI Token" 'circle(ci)?[_-]?token\s*[:=]\s*["'\''][A-Za-z0-9]{40}["'\'']'

# --- SaaS APIs ---
scan "Slack Token" '\bxox[baprs]-[A-Za-z0-9-]{10,}'
scan "Slack Webhook" 'https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/'
scan "Stripe Live Secret Key" '\bsk_live_[0-9a-zA-Z]{24,}'
scan "Stripe Live Restricted Key" '\brk_live_[0-9a-zA-Z]{24,}'
scan "SendGrid API Key" '\bSG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}'
scan "Twilio Account SID" '\bAC[a-z0-9]{32}'
scan "Twilio Auth Token (heuristic)" 'twilio.*auth.*[:=]\s*["'\''][a-z0-9]{32}["'\'']'
scan "Mailgun API Key" '\bkey-[a-z0-9]{32}'
scan "Postmark Token" 'postmark.*[:=]\s*["'\''][a-f0-9-]{36}["'\'']'
scan "Pusher Secret" 'pusher.*secret.*[:=]\s*["'\''][a-z0-9]{20,}["'\'']'
scan "Algolia Admin Key" 'algolia.*admin.*[:=]\s*["'\''][a-z0-9]{32}["'\'']'
scan "Datadog API Key" 'dd_api_key\s*[:=]\s*["'\''][a-f0-9]{32}["'\'']'
scan "Heroku API Key" 'heroku.*[:=]\s*["'\''][a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}["'\'']'

# --- Generic patterns ---
scan "Generic 'password = ...'" '(password|passwd|pwd)\s*[:=]\s*["'\''][^"'\'' ]{6,}["'\'']'
scan "Generic 'secret = ...'" '\b(secret|secret_key|secretkey)\s*[:=]\s*["'\''][^"'\'' ]{8,}["'\'']'
scan "Generic 'token = ...'" '\b(token|access_token|auth_token)\s*[:=]\s*["'\''][^"'\'' ]{16,}["'\'']'
scan "Generic 'api_key = ...'" '\b(api_key|apikey|api-key)\s*[:=]\s*["'\''][^"'\'' ]{12,}["'\'']'

# --- Cryptographic material ---
scan "Private Key Block" '-----BEGIN [A-Z ]*PRIVATE KEY-----'
scan "OpenSSH Private Key" 'OPENSSH PRIVATE KEY'
scan "PGP Private Key" 'PGP PRIVATE KEY BLOCK'

# --- Connection strings ---
# Generic scheme prefix instead of alternation list: macOS libc ERE silently
# fails to match groups of 3+ alternatives followed by this tail.
scan "URL with embedded credentials" '[a-zA-Z][a-zA-Z0-9+.-]*://[^:/[:space:]]+:[^@/[:space:]]+@'
scan "JDBC URL with password" 'jdbc:[a-z]+://[^?]+\?.*password='

# --- Files commonly containing secrets ---
echo "── Suspicious files (presence, not content) ────"
find . -type f 2>/dev/null \
  | grep -Ev "/($IGNORE_DIRS)/" \
  | grep -E '(^|/)(\.env(\.|$)|.*\.pem$|.*\.key$|id_rsa|id_dsa|.*\.p12$|.*\.pfx$|.*credentials.*|.*secret.*\.json$|service-account.*\.json)' \
  | head -20

# --- Check git history for past credentials (light) ---
if git rev-parse --git-dir > /dev/null 2>&1; then
  echo
  echo "── Git history scan (light: last 200 commits) ────"
  history_hits=$(git log -p -200 2>/dev/null \
    | grep -InE 'AKIA[0-9A-Z]{16}|sk_live_[0-9a-zA-Z]{24,}|ghp_[A-Za-z0-9_]{36,}|-----BEGIN [A-Z ]*PRIVATE KEY-----' \
    | head -10)
  if [[ -n "$history_hits" ]]; then
    echo "⚠ Found credential-shaped strings in recent commit history:"
    echo "$history_hits"
    echo
    echo "  Even if removed in HEAD, history is permanent. Rotate any real credentials."
  else
    echo "  No obvious credentials in last 200 commits' patches."
  fi
fi

echo
echo "=========================================="
echo " Scan complete."
echo " Verify each hit — many will be test fixtures or example values."
echo " For production-grade scanning, run: gitleaks detect / trufflehog filesystem ."
echo "=========================================="
