#!/usr/bin/env python3
"""Find what access already exists for a business, before asking anything.
Prints JSON. Never prints a secret's value: env keys by NAME only, service
accounts by client_email only.

    python3 discover.py --root <project dir> [--domain example.com]

Looks at:
  - .env* files in --root: key names matching known analytics/SEO/CRM sources
  - Google service-account keys (~/.config/gcloud-keys/*.json, the
    GOOGLE_APPLICATION_CREDENTIALS path, *.json at --root top level): which
    Search Console properties and GA4 properties each one can read
  - the live site (--domain): GA4 measurement ids, GTM, Clarity project id,
    Ahrefs analytics, sitemap(s) from robots.txt
  - MCP servers configured for Claude Code (names only)
Everything found is a CANDIDATE. The user confirms it's the right account.
"""
import argparse
import glob
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

ENV_PATTERNS = {
    "Google service account / credentials": r"GOOGLE_APPLICATION_CREDENTIALS|GOOGLE_.*(SERVICE|SA)_?(ACCOUNT|KEY)|GCP_.*KEY",
    "GA4 measurement id (site tag)": r"GA_ID|GA4|MEASUREMENT_ID|GTAG",
    "Microsoft Clarity": r"CLARITY",
    "GoHighLevel / LeadConnector": r"^GHL_|HIGHLEVEL|LEADCONNECTOR",
    "Ahrefs": r"AHREFS",
    "Semrush": r"SEMRUSH",
    "DataForSEO": r"DATAFORSEO",
    "Moz": r"^MOZ_",
    "Google Places / Maps": r"PLACES|MAPS_API",
    "HubSpot": r"HUBSPOT",
    "CallRail": r"CALLRAIL",
    "Bing Webmaster": r"BING",
}
MCP_HINTS = r"ga4|gsc|search.?console|analytics|clarity|ghl|highlevel|ahrefs|semrush|dataforseo|chrome|browser|playwright|puppeteer|serp|gbp|business.?profile"


def env_names(root):
    found = {}
    for f in sorted(glob.glob(str(root / ".env*"))):
        if f.endswith((".example", ".sample", ".template")):
            continue
        try:
            names = [l.split("=", 1)[0].strip() for l in open(f, errors="replace")
                     if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", l)]
        except OSError:
            continue
        for n in names:
            for label, rx in ENV_PATTERNS.items():
                if re.search(rx, n, re.I):
                    found.setdefault(label, []).append({"file": os.path.relpath(f, root), "key": n})
    return found


def sa_files(root):
    c = set(glob.glob(os.path.expanduser("~/.config/gcloud-keys/*.json")))
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        c.add(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    c |= set(glob.glob(str(root / "*.json")))
    out = []
    for f in sorted(c):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if isinstance(d, dict) and d.get("type") == "service_account":
            out.append((f, d.get("client_email")))
    return out


def sa_access(path):
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
    except ImportError:
        return {"error": "python google-auth not installed (pip install google-auth)"}
    res = {}
    for name, scope, url, pick in (
        ("gsc_properties", "webmasters.readonly", "https://www.googleapis.com/webmasters/v3/sites",
         lambda d: [f"{s['siteUrl']} ({s.get('permissionLevel')})" for s in d.get("siteEntry", [])]),
        ("ga4_properties", "analytics.readonly", "https://analyticsadmin.googleapis.com/v1beta/accountSummaries",
         lambda d: [f"{p.get('property')} {p.get('displayName')!r} (account {a.get('displayName')!r})"
                    for a in d.get("accountSummaries", []) for p in a.get("propertySummaries", [])]),
    ):
        try:
            cr = service_account.Credentials.from_service_account_file(path, scopes=[f"https://www.googleapis.com/auth/{scope}"])
            cr.refresh(Request())
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {cr.token}"})
            res[name] = pick(json.loads(urllib.request.urlopen(req, timeout=30).read()))
        except urllib.error.HTTPError as e:
            res[name] = {"error": f"{e.code}: {e.read()[:200].decode(errors='replace')}"}
        except Exception as e:
            res[name] = {"error": f"{type(e).__name__}: {e}"}
    return res


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode(errors="replace")


def site_scan(domain):
    out = {"domain": domain}
    try:
        page = fetch(f"https://{domain}/")
        out["ga4_measurement_ids"] = sorted(set(re.findall(r"\bG-[A-Z0-9]{6,12}\b", page)))
        out["gtm_containers"] = sorted(set(re.findall(r"\bGTM-[A-Z0-9]{4,10}\b", page)))
        out["clarity_project_ids"] = sorted(set(re.findall(r"clarity\.ms/tag/([a-z0-9]{6,14})", page)
                                            + re.findall(r"window,\s*document,\s*\\*[\"']clarity\\*[\"'],\s*\\*[\"']script\\*[\"'],\s*\\*[\"']([a-z0-9]{6,14})", page)))
        out["ahrefs_analytics"] = "analytics.ahrefs.com" in page
    except Exception as e:
        out["homepage_error"] = f"{type(e).__name__}: {e}"
    try:
        robots = fetch(f"https://{domain}/robots.txt")
        out["sitemaps"] = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", robots)
    except Exception as e:
        out["robots_error"] = f"{type(e).__name__}: {e}"
    if not out.get("sitemaps"):
        try:
            fetch(f"https://{domain}/sitemap.xml")
            out["sitemaps"] = [f"https://{domain}/sitemap.xml"]
        except Exception:
            out["sitemaps"] = []
    return out


def mcp_servers(root):
    names = {}
    try:
        d = json.load(open(os.path.expanduser("~/.claude.json")))
        for n in (d.get("mcpServers") or {}):
            names[n] = "user"
        for proj, cfg in (d.get("projects") or {}).items():
            if Path(proj) == root:
                for n in (cfg.get("mcpServers") or {}):
                    names[n] = "project (local)"
    except Exception:
        pass
    try:
        for n in (json.load(open(root / ".mcp.json")).get("mcpServers") or {}):
            names[n] = "project (.mcp.json)"
    except Exception:
        pass
    return {"relevant": {n: s for n, s in names.items() if re.search(MCP_HINTS, n, re.I)},
            "other_count": len([n for n in names if not re.search(MCP_HINTS, n, re.I)])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--domain")
    a = ap.parse_args()
    root = Path(a.root).expanduser().resolve()
    out = {"root": str(root), "env_keys": env_names(root),
           "service_accounts": [{"file": f, "client_email": e, **sa_access(f)} for f, e in sa_files(root)],
           "mcp_servers": mcp_servers(root)}
    if a.domain:
        out["site"] = site_scan(a.domain.replace("https://", "").replace("http://", "").strip("/"))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
