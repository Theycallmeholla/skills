#!/usr/bin/env python3
"""Pull every scriptable source a business profile enables, save a snapshot,
and print a compact summary that leads with what changed.

    python3 pull.py --profile <dir>            # the folder holding profile.json
    python3 pull.py --profile <dir> --days 7   # shorter windows
    python3 pull.py --profile <dir> --no-inspect
    python3 pull.py --profile <dir> --check    # test every connection, list what's missing

Profiles store POINTERS to credentials (a key name in the profile's .env or in
another env file, or a key-file path), never values. Sources not enabled in the profile are skipped. A source that
fails records its exact error and the rest still run.

Sources here: gsc, indexing, ga4 (service_account method only), clarity,
ghl, ahrefs_dr, commands. GA4 via an MCP and anything behind a browser login
(GBP, Clarity heatmaps) are done by Claude per SKILL.md, not by this script.
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import html
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
GHL = "https://services.leadconnectorhq.com"

P = {}          # profile.json
PDIR = None     # profile folder
ROOT = None     # project root the profile's relative paths resolve against


# ---------------------------------------------------------------- helpers

def http(method, url, headers=None, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Accept": "application/json", "User-Agent": UA, **(headers or {})}
    if data is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {url.split('?')[0]} -> {e.code}: {e.read()[:300].decode(errors='replace')}")


def resolve(path):
    p = Path(os.path.expanduser(path))
    return p if p.is_absolute() else ROOT / p


def env_path(ref):
    """Where a key is read from: the profile's own .env unless the source
    names another file (e.g. a project's existing .env.local)."""
    return resolve(ref["env_file"]) if ref.get("env_file") else PDIR / ".env"


def secret(ref):
    """ref = {"env_key": "NAME"} (profile .env), {"env_file": ".env.local",
    "env_key": "NAME"}, or {"env": "NAME"} (shell environment)."""
    if ref.get("env"):
        v = os.environ.get(ref["env"])
        if not v:
            raise RuntimeError(f"environment variable {ref['env']} is not set")
        return v
    f = env_path(ref)
    if not f.exists():
        raise RuntimeError(f"{f} does not exist")
    for line in f.read_text().splitlines():
        if line.startswith(ref["env_key"] + "="):
            v = line.split("=", 1)[1].strip().strip('"').strip("'")
            if v:
                return v
    raise RuntimeError(f"{ref['env_key']} is missing or empty in {f}")


def section(fn, *a):
    try:
        return fn(*a)
    except Exception as e:  # recorded and shown, never fatal
        return {"error": f"{type(e).__name__}: {e}"}


def enabled(name):
    s = (P.get("sources") or {}).get(name)
    return s if s and s.get("enabled", True) else None


def path_of(url):
    u = urllib.parse.urlparse(url)
    p = (u.path or "/").rstrip("/") or "/"
    return p + (f"?{u.query}" if u.query else "")


def windows(end, days):
    cs = end - dt.timedelta(days=days - 1)
    pe = cs - dt.timedelta(days=1)
    return (cs, end), (pe - dt.timedelta(days=days - 1), pe)


def sa_token(key_file, scope):
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    creds = service_account.Credentials.from_service_account_file(
        str(resolve(key_file)), scopes=[f"https://www.googleapis.com/auth/{scope}"])
    creds.refresh(Request())
    return creds.token


# ---------------------------------------------------------------- GSC

def gsc_query(tok, site, start, end, dims, limit=1000, filters=None):
    body = {"startDate": str(start), "endDate": str(end), "dimensions": dims, "rowLimit": limit}
    if filters:
        body["dimensionFilterGroups"] = [{"filters": filters}]
    s = urllib.parse.quote(site, safe="")
    return http("POST", f"https://www.googleapis.com/webmasters/v3/sites/{s}/searchAnalytics/query",
                {"Authorization": f"Bearer {tok}"}, body).get("rows", [])


def totals(rows):
    c = sum(r["clicks"] for r in rows)
    i = sum(r["impressions"] for r in rows)
    pos = sum(r["position"] * r["impressions"] for r in rows) / i if i else None
    return {"clicks": c, "impressions": i, "ctr": round(c / i * 100, 2) if i else None,
            "position": round(pos, 1) if pos else None}


def m4(r):
    return {"clicks": r["clicks"], "impressions": r["impressions"],
            "ctr": round(r["ctr"] * 100, 2), "position": round(r["position"], 1)} if r else None


def pull_gsc(days):
    cfg = enabled("gsc")
    site = cfg["site"]
    tok = sa_token(cfg["key_file"], "webmasters.readonly")
    today = dt.date.today()
    recent = gsc_query(tok, site, today - dt.timedelta(days=10), today, ["date"])
    if not recent:
        raise RuntimeError(f"no GSC rows in the last 10 days for {site}")
    latest = max(dt.date.fromisoformat(r["keys"][0]) for r in recent)
    (cs, ce), (ps, pe) = windows(latest, days)
    q = lambda s, e, dims, limit=1000, f=None: gsc_query(tok, site, s, e, dims, limit, f)

    country = (P.get("market") or {}).get("gsc_country")
    cf_ = [{"dimension": "country", "operator": "equals", "expression": country}] if country else None

    weeks = {}
    for r in q(latest - dt.timedelta(days=83), latest, ["date"]):
        d = dt.date.fromisoformat(r["keys"][0])
        wk = latest - dt.timedelta(days=((latest - d).days // 7) * 7 + 6)
        w = weeks.setdefault(str(wk), {"clicks": 0, "impressions": 0})
        w["clicks"] += r["clicks"]
        w["impressions"] += r["impressions"]

    def keyed(dims, s, e, limit=1000, f=None):
        return {tuple(r["keys"]): r for r in q(s, e, dims, limit, f)}

    pc, pp = keyed(["page"], cs, ce), keyed(["page"], ps, pe)
    pages = [{"page": path_of(k[0]), "cur": m4(pc.get(k)), "prev": m4(pp.get(k))} for k in set(pc) | set(pp)]
    pages.sort(key=lambda r: -((r["cur"] or {}).get("impressions", 0)))

    def delta(r, f):
        return (r["cur"] or {}).get(f, 0) - (r["prev"] or {}).get(f, 0)

    rules = P.get("opportunity_rules") or {"min_impressions": 20, "position_min": 4, "position_max": 20}
    movers = {
        "clicks": sorted([r for r in pages if delta(r, "clicks")], key=lambda r: -abs(delta(r, "clicks")))[:8],
        "impressions": sorted(pages, key=lambda r: -abs(delta(r, "impressions")))[:8],
        "position": sorted([r for r in pages if r["cur"] and r["prev"]
                            and (r["cur"]["impressions"] >= rules["min_impressions"])
                            and abs(r["cur"]["position"] - r["prev"]["position"]) >= 3],
                           key=lambda r: r["cur"]["position"] - r["prev"]["position"])[:8],
    }

    qc, qp = keyed(["query"], cs, ce), keyed(["query"], ps, pe)
    queries = sorted(({"query": k[0], "cur": m4(v), "prev": m4(qp.get(k))} for k, v in qc.items()),
                     key=lambda r: -r["cur"]["impressions"])

    noise = P.get("noise") or {}
    noise_pairs = {(page, qq) for page, qs in (noise.get("queries_by_page") or {}).items() for qq in qs}
    wrong = set(noise.get("wrong_audience_pages") or [])
    qp_c = q(cs, ce, ["query", "page"], 5000)
    qp_p = keyed(["query", "page"], ps, pe, 5000)
    qp_m = keyed(["query", "page"], cs, ce, 5000, cf_) if cf_ else {}
    per_q = {}
    for r in qp_c:
        per_q.setdefault(r["keys"][0], set()).add(path_of(r["keys"][1]))
    opps = []
    for r in qp_c:
        qq, url = r["keys"]
        pth = path_of(url)
        if r["impressions"] < rules["min_impressions"] or not (rules["position_min"] <= r["position"] <= rules["position_max"]):
            continue
        flags = []
        if (pth, qq) in noise_pairs:
            flags.append("noise:known")
        if pth in wrong:
            flags.append("noise:wrong-audience-page")
        if len(per_q[qq]) > 1:
            flags.append("split:" + ",".join(sorted(per_q[qq])))
        prev = qp_p.get((qq, url))
        mk = qp_m.get((qq, url))
        opps.append({"query": qq, "page": pth, **m4(r),
                     "market_impressions": mk["impressions"] if mk else (None if not cf_ else 0),
                     "prev_impressions": prev["impressions"] if prev else 0,
                     "prev_position": round(prev["position"], 1) if prev else None, "flags": flags})
    opps.sort(key=lambda o: -o["impressions"])

    out = {
        "site": site, "latest_date": str(latest),
        "window": {"cur": [str(cs), str(ce)], "prev": [str(ps), str(pe)]},
        "totals": {"cur": totals(q(cs, ce, ["date"])), "prev": totals(q(ps, pe, ["date"]))},
        "weekly": dict(sorted(weeks.items())),
        "pages": pages[:40], "movers": movers, "queries": queries[:60],
        "new_queries": [x for x in queries if not x["prev"] and x["cur"]["impressions"] >= rules["min_impressions"]][:25],
        "countries": [{"country": r["keys"][0], "clicks": r["clicks"], "impressions": r["impressions"]}
                      for r in sorted(q(cs, ce, ["country"], 20), key=lambda r: -r["clicks"])[:10]],
        "opportunities": opps[:40],
    }
    if cf_:
        out["market"] = country
        out["totals_market"] = {"cur": totals(q(cs, ce, ["date"], 1000, cf_)), "prev": totals(q(ps, pe, ["date"], 1000, cf_))}
    return out


def pull_indexing(newest):
    cfg = enabled("indexing")
    gsc = enabled("gsc") or {}
    site = cfg.get("site") or gsc["site"]
    key = cfg.get("key_file") or gsc["key_file"]
    xml = urllib.request.urlopen(urllib.request.Request(cfg["sitemap"], headers={"User-Agent": UA}), timeout=30).read().decode()
    urls = [html.unescape(u) for u in re.findall(r"<loc>([^<]+)</loc>", xml)]
    if "<sitemapindex" in xml:  # follow one level of sitemap index
        subs, urls = urls, []
        for s in subs:
            x = urllib.request.urlopen(urllib.request.Request(s, headers={"User-Agent": UA}), timeout=30).read().decode()
            urls += [html.unescape(u) for u in re.findall(r"<loc>([^<]+)</loc>", x)]
    tok = sa_token(key, "webmasters.readonly")
    reuse = {}
    if newest and (dt.date.today() - dt.date.fromisoformat(newest["_date"])).days < 7:
        for r in ((newest.get("indexing") or {}).get("all") or []):
            if r.get("verdict") == "PASS":
                reuse[r["url"]] = {**r, "reused_from": newest["_date"]}

    def inspect(u):
        if path_of(u) in reuse:
            return reuse[path_of(u)]
        try:
            r = http("POST", "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
                     {"Authorization": f"Bearer {tok}"}, {"inspectionUrl": u, "siteUrl": site})
            s = r.get("inspectionResult", {}).get("indexStatusResult", {})
            return {"url": path_of(u), "verdict": s.get("verdict"), "coverage": s.get("coverageState"),
                    "last_crawl": s.get("lastCrawlTime"), "google_canonical": s.get("googleCanonical")}
        except Exception as e:
            return {"url": path_of(u), "error": str(e)[:200]}

    with cf.ThreadPoolExecutor(8) as ex:
        res = list(ex.map(inspect, urls))
    return {"count": len(res), "reused": sum(1 for r in res if r.get("reused_from")),
            "indexed": sum(1 for r in res if r.get("verdict") == "PASS"),
            "by_coverage": dict(Counter(r.get("coverage") or ("ERROR" if r.get("error") else "unknown") for r in res)),
            "not_indexed": [r for r in res if r.get("verdict") != "PASS"], "all": res}


# ---------------------------------------------------------------- GA4 (service account method)

def pull_ga4(days):
    """Only when the profile says method=service_account. UNTESTED success path:
    written from the Data API v1beta runReport contract; the first profile to
    use it must confirm the numbers against the GA4 UI once."""
    cfg = enabled("ga4")
    if cfg.get("method") != "service_account":
        return {"skipped": f"method={cfg.get('method')}: Claude reads GA4 per SKILL.md"}
    tok = sa_token(cfg["key_file"], "analytics.readonly")
    end = dt.date.today() - dt.timedelta(days=1)
    (cs, ce), (ps, pe) = windows(end, days)
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{cfg['property_id']}:runReport"

    def rep(dims, mets, s, e, limit=250):
        r = http("POST", url, {"Authorization": f"Bearer {tok}"}, {
            "dateRanges": [{"startDate": str(s), "endDate": str(e)}],
            "dimensions": [{"name": d} for d in dims], "metrics": [{"name": m} for m in mets], "limit": limit})
        return [{"dims": [v["value"] for v in row.get("dimensionValues", [])],
                 "mets": [v["value"] for v in row.get("metricValues", [])]} for row in r.get("rows", [])]

    ch = ["sessions", "totalUsers", "engagementRate", "averageSessionDuration"]
    return {"window": {"cur": [str(cs), str(ce)], "prev": [str(ps), str(pe)]},
            "channels_cur": rep(["sessionDefaultChannelGroup"], ch, cs, ce),
            "channels_prev": rep(["sessionDefaultChannelGroup"], ch, ps, pe),
            "landing": rep(["sessionDefaultChannelGroup", "landingPage"], ["sessions", "engagedSessions", "averageSessionDuration"], cs, ce),
            "events_cur": rep(["eventName"], ["eventCount", "totalUsers"], cs, ce),
            "events_prev": rep(["eventName"], ["eventCount", "totalUsers"], ps, pe)}


# ---------------------------------------------------------------- Clarity

def pull_clarity():
    """Data Export API: last 1-3 days only, 10 requests per project per day.
    Calls are counted in clarity-calls.json so repeated runs can't burn the day."""
    cfg = enabled("clarity")
    tok = secret(cfg)
    ledger_f = PDIR / "clarity-calls.json"
    today = dt.date.today().isoformat()
    ledger = json.loads(ledger_f.read_text()) if ledger_f.exists() else {}
    used = ledger.get(today, 0)
    dims = cfg.get("dimensions", ["URL", "Channel"])
    if used + len(dims) > cfg.get("daily_budget", 8):
        return {"skipped": f"{used} Clarity calls already made today; budget {cfg.get('daily_budget', 8)} of Clarity's 10/day"}
    out = {"days": cfg.get("num_days", 3)}
    for d in dims:
        r = http("GET", "https://www.clarity.ms/export-data/api/v1/project-live-insights?"
                 + urllib.parse.urlencode({"numOfDays": out["days"], "dimension1": d}),
                 {"Authorization": f"Bearer {tok}"})
        used += 1
        out[d] = {m["metricName"]: m.get("information", []) for m in r}
    ledger[today] = used
    ledger_f.write_text(json.dumps({k: v for k, v in ledger.items() if k >= (dt.date.today() - dt.timedelta(days=7)).isoformat()}))

    # Per-page table from the URL breakdown: sessions, friction, attention.
    pages = {}
    by = out.get("URL") or {}
    for metric, rows in by.items():
        for r in rows:
            u = r.get("Url")
            if not u:
                continue
            p = pages.setdefault(path_of(u), {})
            if metric == "Traffic":
                p["sessions"] = r.get("totalSessionCount")
                p["bot_sessions"] = r.get("totalBotSessionCount")
                p["users"] = r.get("distinctUserCount")
            elif metric == "ScrollDepth":
                p["scroll_depth"] = r.get("averageScrollDepth")
            elif metric == "EngagementTime":
                p["active_time"] = r.get("activeTime")
                p["total_time"] = r.get("totalTime")
            else:
                p[metric] = r.get("subTotal")
                p[metric + "_pct"] = r.get("sessionsWithMetricPercentage")
    out["pages"] = pages
    return out


# ---------------------------------------------------------------- GHL

def classify(cid, email, name, tags):
    ppl = P.get("people") or {}
    e = (email or "").strip().lower()
    local = e.split("@")[0]
    if cid in (ppl.get("internal_contact_ids") or {}):
        return "internal", ppl["internal_contact_ids"][cid]
    if e and e.split("@")[-1] in (ppl.get("internal_email_domains") or []):
        return "internal", "internal email domain"
    if e in (ppl.get("internal_emails") or []):
        return "internal", "known internal email"
    if ppl.get("test_word_rule", True) and (re.search(r"\btest\b", name or "", re.I)
                                            or re.search(r"(^|[._+-])test([._+-]|$)", local)):
        return "internal", "the word 'test' in name/email"
    if set(tags or []) & set(ppl.get("internal_tags") or ["test"]):
        return "internal", "internal tag"
    if cid in (ppl.get("confirmed_real") or {}):
        return "real", ppl["confirmed_real"][cid]
    return "unconfirmed", ""


class Ghl:
    def __init__(self, cfg):
        self.cfg = cfg
        k = secret(cfg)
        self.h21 = {"Authorization": f"Bearer {k}", "Version": "2021-04-15"}
        self.h28 = {"Authorization": f"Bearer {k}", "Version": "2021-07-28"}
        self.cache = {}

    def contact(self, cid):
        if cid not in self.cache:
            try:
                self.cache[cid] = http("GET", f"{GHL}/contacts/{cid}", self.h28).get("contact", {})
            except RuntimeError as e:
                self.cache[cid] = {"_error": str(e)[:120]}
        return self.cache[cid]

    def person(self, cid, fallback=""):
        c = self.contact(cid)
        name = " ".join(x for x in (c.get("firstName"), c.get("lastName")) if x) or fallback
        cls, why = classify(cid, c.get("email"), name, c.get("tags"))
        keep = set(self.cfg.get("report_tags") or [])
        prefixes = tuple(self.cfg.get("report_tag_prefixes") or [])
        return {"contact_id": cid, "name": name, "email": c.get("email"), "class": cls, "why": why,
                "tags": [t for t in c.get("tags", []) if t in keep or (prefixes and t.startswith(prefixes))],
                **({"lookup_error": c["_error"]} if "_error" in c else {})}

    def tagged(self, tag):
        out, page = [], 1
        while True:
            r = http("POST", f"{GHL}/contacts/search", self.h28, {
                "locationId": self.cfg["location_id"], "page": page, "pageLimit": 100,
                "filters": [{"field": "tags", "operator": "contains", "value": tag}]})
            out += r.get("contacts", [])
            if len(out) >= r.get("total", 0) or not r.get("contacts"):
                return out
            page += 1


def pull_ghl(ghl, days):
    cfg, loc = ghl.cfg, ghl.cfg["location_id"]
    now = dt.datetime.now(dt.timezone.utc)
    cur_start, prev_start = now - dt.timedelta(days=days), now - dt.timedelta(days=2 * days)
    out = {"window_days": days}

    if cfg.get("calendar_ids"):
        ms = lambda t: int(t.timestamp() * 1000)
        ev = []
        for cal in cfg["calendar_ids"]:
            # The events filter is on appointment START time; bucket by dateAdded (booking time).
            ev += http("GET", f"{GHL}/calendars/events?locationId={loc}&calendarId={cal}"
                       f"&startTime={ms(prev_start - dt.timedelta(days=30))}&endTime={ms(now + dt.timedelta(days=60))}",
                       ghl.h21).get("events", [])
        b = {"cur": [], "prev": []}
        for e in ev:
            added = dt.datetime.fromisoformat(e["dateAdded"].replace("Z", "+00:00"))
            k = "cur" if added >= cur_start else "prev" if added >= prev_start else None
            if k:
                b[k].append({"booked_at": e["dateAdded"][:16], "starts": e.get("startTime"),
                             "status": e.get("appointmentStatus"), "title": e.get("title"),
                             **ghl.person(e["contactId"], e.get("title", ""))})
        out["bookings"] = b
        last = next((e for e in sorted(ev, key=lambda e: e["dateAdded"], reverse=True)
                     if e.get("appointmentStatus") != "cancelled" and ghl.person(e["contactId"])["class"] == "real"), None)
        out["last_real_booking"] = {"booked_at": last["dateAdded"][:10], "title": last.get("title")} if last else None

    out["tags"] = {}
    for tag in cfg.get("count_tags") or []:
        rows = []
        for c in ghl.tagged(tag):
            ghl.cache[c["id"]] = c
            rows.append({**ghl.person(c["id"]), "added": (c.get("dateAdded") or "")[:10]})
        out["tags"][tag] = rows

    if cfg.get("pipeline_id"):
        pipes = http("GET", f"{GHL}/opportunities/pipelines?locationId={loc}", ghl.h28).get("pipelines", [])
        sp = next((p for p in pipes if p["id"] == cfg["pipeline_id"]), {})
        names = {s["id"]: s["name"] for s in sp.get("stages", [])}
        opps, url = [], f"{GHL}/opportunities/search?location_id={loc}&pipeline_id={cfg['pipeline_id']}&limit=100"
        while url:
            r = http("GET", url, ghl.h28)
            opps += r.get("opportunities", [])
            url = r.get("meta", {}).get("nextPageUrl") if r.get("opportunities") else None
        out["pipeline"] = {"name": sp.get("name"), "total": len(opps),
                           "by_stage": dict(Counter(names.get(o["pipelineStageId"], o["pipelineStageId"]) for o in opps)),
                           "by_status": dict(Counter(o.get("status") for o in opps)),
                           "won": [{"name": o["name"], "value": o.get("monetaryValue"), "at": (o.get("lastStatusChangeAt") or "")[:10]}
                                   for o in opps if o.get("status") == "won"]}
    return out


# ---------------------------------------------------------------- Ahrefs DR, custom commands

def pull_ahrefs():
    cfg = enabled("ahrefs_dr")
    r = http("GET", f"https://api.ahrefs.com/v3/public/domain-rating-free?target={urllib.parse.quote(cfg['target'])}",
             {"Authorization": f"Bearer {secret(cfg)}"})
    return {"domain_rating": r["domain_rating"]["domain_rating"]}


def pull_commands(ghl, days):
    """Profile-defined commands (e.g. reading tool records off a server). Each
    prints JSON rows on its last stdout line. Rows with contactId are classified
    through GHL when GHL is enabled."""
    out = {}
    cutoff = (time.time() - days * 86400) * 1000
    for c in enabled("commands").get("list", []):
        try:
            r = subprocess.run(c["run"], shell=True, cwd=str(PDIR), capture_output=True, text=True, timeout=c.get("timeout", 120))
            if r.returncode != 0:
                raise RuntimeError(f"exit {r.returncode}: {r.stderr.strip()[-300:]}")
            rows = json.loads(r.stdout.strip().splitlines()[-1])
            for x in rows:
                at = x.get("at_ms") or 0
                x["date"] = dt.datetime.fromtimestamp(at / 1000).strftime("%Y-%m-%d") if at else None
                x["in_window"] = at >= cutoff
                if ghl and x.get("contactId"):
                    p = ghl.person(x["contactId"])
                    x.update({"class": p["class"], "why": p["why"], "email": p["email"], "name": p["name"]})
            rows.sort(key=lambda x: x.get("date") or "", reverse=True)
            out[c["name"]] = {"description": c.get("description"), "rows": rows}
        except Exception as e:
            out[c["name"]] = {"error": f"{type(e).__name__}: {e}"}
    return out


# ---------------------------------------------------------------- KPIs + summary

def kpis(out):
    k = {}
    g = out.get("gsc") or {}
    if "totals" in g:
        for f in ("clicks", "impressions", "ctr", "position"):
            k[f"search_{f}"] = g["totals"]["cur"][f]
        if "totals_market" in g:
            k["search_clicks_market"] = g["totals_market"]["cur"]["clicks"]
    ix = out.get("indexing") or {}
    if "indexed" in ix:
        k["indexed_urls"] = f"{ix['indexed']}/{ix['count']}"
    a = out.get("ahrefs_dr") or {}
    if "domain_rating" in a:
        k["domain_rating"] = a["domain_rating"]
    gh = out.get("ghl") or {}
    if "bookings" in gh:
        k["real_booking_people"] = len({r["contact_id"] for r in gh["bookings"]["cur"]
                                        if r["class"] == "real" and r["status"] != "cancelled"})
    if "pipeline" in gh:
        k["pipeline_won"] = len(gh["pipeline"]["won"])
    cl = out.get("clarity") or {}
    if "pages" in cl:
        k["clarity_sessions_3d"] = sum((p.get("sessions") or 0) for p in cl["pages"].values())
        k["clarity_dead_clicks_3d"] = sum((p.get("DeadClickCount") or 0) for p in cl["pages"].values())
        k["clarity_rage_clicks_3d"] = sum((p.get("RageClickCount") or 0) for p in cl["pages"].values())
    return k


def fmt_page(r):
    c, p = r["cur"] or {}, r["prev"] or {}
    return (f"{r['page']}: clicks {p.get('clicks', 0)}->{c.get('clicks', 0)}, impr {p.get('impressions', 0)}->{c.get('impressions', 0)}, "
            f"pos {p.get('position', '-')}->{c.get('position', '-')}")


def summary(out, prev):
    L = [f"PROFILE {P.get('business', {}).get('name')} ({PDIR}) pulled {out['pulled_at']}, {out['days']}-day windows"]
    if prev:
        pk = prev.get("kpis") or {}
        ch = [f"{k}: {pk[k]} -> {v}" for k, v in out["kpis"].items() if k in pk and pk[k] != v]
        L.append(f"SINCE LAST SNAPSHOT ({prev['_date']}): " + ("; ".join(ch) if ch else "no KPI changed" if pk else "previous snapshot has no KPIs"))
    for name in ("gsc", "indexing", "ga4", "clarity", "ghl", "ahrefs_dr", "commands"):
        s = out.get(name)
        if isinstance(s, dict) and "error" in s:
            L.append(f"{name.upper()} ERROR: {s['error']}")
        elif isinstance(s, dict) and "skipped" in s:
            L.append(f"{name.upper()} skipped: {s['skipped']}")

    g = out.get("gsc") or {}
    if "totals" in g:
        c, p = g["totals"]["cur"], g["totals"]["prev"]
        L.append(f"GSC {g['site']} {g['window']['cur'][0]}..{g['window']['cur'][1]} vs {g['window']['prev'][0]}..{g['window']['prev'][1]} (data lags to {g['latest_date']})")
        L.append(f"  all:    clicks {p['clicks']}->{c['clicks']} | impr {p['impressions']}->{c['impressions']} | CTR {p['ctr']}%->{c['ctr']}% | pos {p['position']}->{c['position']}")
        if "totals_market" in g:
            c, p = g["totals_market"]["cur"], g["totals_market"]["prev"]
            L.append(f"  {g['market']}:    clicks {p['clicks']}->{c['clicks']} | impr {p['impressions']}->{c['impressions']} | CTR {p['ctr']}%->{c['ctr']}% | pos {p['position']}->{c['position']}")
        L.append("  weekly clicks: " + " ".join(f"{k[5:]}={v['clicks']}" for k, v in g["weekly"].items()))
        L.append("  countries (clicks): " + ", ".join(f"{r['country']} {r['clicks']}" for r in g["countries"][:6]))
        L.append("  movers, clicks:      " + " | ".join(fmt_page(r) for r in g["movers"]["clicks"][:5]))
        L.append("  movers, impressions: " + " | ".join(fmt_page(r) for r in g["movers"]["impressions"][:5]))
        if g["movers"]["position"]:
            L.append("  movers, position (>=3 places): " + " | ".join(fmt_page(r) for r in g["movers"]["position"][:6]))
        L.append("  top pages: " + " | ".join(fmt_page(r) for r in g["pages"][:10]))
        L.append("  opportunity candidates (query -> page: impr, clicks, pos [prev impr/pos], market impr, flags):")
        for o in g["opportunities"][:20]:
            L.append(f"    {o['query']!r} -> {o['page']}: {o['impressions']} impr, {o['clicks']} clk, pos {o['position']}"
                     f" [{o['prev_impressions']}/{o['prev_position']}] mkt {o['market_impressions']} {' '.join(o['flags'])}")
        if g["new_queries"]:
            L.append("  new queries: " + "; ".join(f"{q['query']} ({q['cur']['impressions']} impr, pos {q['cur']['position']})" for q in g["new_queries"][:10]))

    ix = out.get("indexing") or {}
    if "count" in ix:
        L.append(f"INDEXING {ix['indexed']}/{ix['count']} sitemap URLs indexed ({ix['reused']} reused from a snapshot under 7 days old): {ix['by_coverage']}")
        paged = [r for r in ix["not_indexed"] if re.search(r"[?&]page=\d+", r["url"])]
        if paged:
            L.append(f"    {len(paged)} paginated (?page=N) URLs not indexed: {dict(Counter(r.get('coverage') for r in paged))}")
        for r in [r for r in ix["not_indexed"] if r not in paged][:25]:
            L.append(f"    {r['url']}: {r.get('coverage') or r.get('error')}")

    ga = out.get("ga4") or {}
    if "channels_cur" in ga:
        L.append(f"GA4 (service account) {ga['window']['cur']} vs {ga['window']['prev']}: channels cur {ga['channels_cur']} | prev {ga['channels_prev']}")

    cl = out.get("clarity") or {}
    if "pages" in cl:
        rows = sorted(cl["pages"].items(), key=lambda kv: -(kv[1].get("sessions") or 0))
        L.append(f"CLARITY last {cl['days']} days, per page (sessions, bots, scroll %, active s, dead/rage/quickback clicks):")
        for pth, v in rows[:12]:
            L.append(f"    {pth}: {v.get('sessions')} sess, {v.get('bot_sessions')} bot, scroll {v.get('scroll_depth')}, active {v.get('active_time')}s, "
                     f"dead {v.get('DeadClickCount')} rage {v.get('RageClickCount')} qb {v.get('QuickbackClick')} err {v.get('ScriptErrorCount')}")
        if "Channel" in cl:
            t = cl["Channel"].get("Traffic", [])
            L.append("  by channel: " + ", ".join(f"{r.get('Channel')} {r.get('totalSessionCount')} sess/{r.get('totalBotSessionCount')} bot" for r in t))

    gh = out.get("ghl") or {}
    if "bookings" in gh:
        for k in ("cur", "prev"):
            rows = gh["bookings"][k]
            live = [r for r in rows if r["status"] != "cancelled"]
            ppl = lambda cls: {r["contact_id"] for r in live if r["class"] == cls}
            L.append(f"BOOKINGS {k} ({gh['window_days']}d by booking time, cancelled excluded): {len(ppl('real'))} real people, "
                     f"{len(ppl('unconfirmed'))} UNCONFIRMED, {len(ppl('internal'))} internal; {len(rows) - len(live)} cancelled")
            for r in rows:
                if r["class"] != "internal":
                    L.append(f"    {r['booked_at']} {r['class']}: {r['name']} <{r['email']}> {r['status']} tags={r['tags']}")
        L.append(f"  last real booking: {gh.get('last_real_booking')}")
    for tag, rows in (gh.get("tags") or {}).items():
        ext = [r for r in rows if r["class"] != "internal"]
        L.append(f"TAG {tag}: {len(rows)} contacts, {len(ext)} not internal: " + "; ".join(f"{r['added']} {r['name']} ({r['class']})" for r in ext[:10]))
    if "pipeline" in gh:
        sp = gh["pipeline"]
        L.append(f"PIPELINE {sp['name']}: {sp['total']} opps, stages {sp['by_stage']}, status {sp['by_status']}, won {sp['won']}")

    for name, c in (out.get("commands") or {}).items():
        if "error" in c:
            L.append(f"COMMAND {name} ERROR: {c['error']}")
            continue
        ext = [r for r in c["rows"] if r.get("class") != "internal"]
        L.append(f"COMMAND {name} ({c.get('description')}): {len(c['rows'])} rows, {len(ext)} not internal, "
                 f"{sum(1 for r in ext if r['in_window'])} of those in window")
        for r in ext[:12]:
            L.append("    " + json.dumps({k: v for k, v in r.items() if k not in ("in_window",)}, default=str)[:260])

    a = out.get("ahrefs_dr") or {}
    if "domain_rating" in a:
        L.append(f"AHREFS DR: {a['domain_rating']}")
    return "\n".join(L)


# ---------------------------------------------------------------- --check

SOURCES = [
    ("gsc", "Search Console", "Google service-account key file with Full access to the property",
     "Add the key's client_email as a Full user: GSC > Settings > Users and permissions. Put the key JSON somewhere private and set sources.gsc.key_file."),
    ("indexing", "Indexing", "Search Console access (Full) + a sitemap URL",
     "Set sources.indexing.sitemap (discover.py lists it from robots.txt). Needs the GSC key as a Full user; Restricted can't run URL Inspection."),
    ("ga4", "GA4", "a GA4 MCP tool, or a service-account key with Viewer on the property",
     "GA4 Admin > Property access management > add the service account's client_email as Viewer, or connect a GA4 MCP server."),
    ("clarity", "Clarity metrics", "CLARITY_EXPORT_TOKEN (Clarity project admin makes it)",
     "Clarity > Settings > Data Export > Generate new API token. Paste it into the profile .env as CLARITY_EXPORT_TOKEN=..."),
    ("ghl", "GoHighLevel (leads)", "GHL private integration token + location id",
     "GHL sub-account > Settings > Private Integrations: token with contacts, calendars/events and opportunities read. Paste into the profile .env as GHL_PRIVATE_INTEGRATION_KEY=..."),
    ("ahrefs_dr", "Domain Rating", "AHREFS_API_KEY (free tier works)",
     "Ahrefs account > API keys. Paste into the profile .env as AHREFS_API_KEY=..."),
]
BROWSER_FIX = {
    "clarity_heatmaps": ("Clarity heatmaps", "Someone signs into clarity.microsoft.com in a browser Claude can drive; list it under browser.clarity_heatmaps."),
    "google_business_profile": ("Business Profile", "Someone signs into the profile's Google account in a browser Claude can drive; list it under browser.google_business_profile."),
}


def check_source(key, clarity_live):
    """(status, detail) from one real call. 'ok', 'warn' or 'fail'."""
    cfg = enabled(key)
    if key == "gsc":
        tok = sa_token(cfg["key_file"], "webmasters.readonly")
        sites = {s["siteUrl"]: s.get("permissionLevel") for s in
                 http("GET", "https://www.googleapis.com/webmasters/v3/sites", {"Authorization": f"Bearer {tok}"}).get("siteEntry", [])}
        if cfg["site"] not in sites:
            return "fail", f"key can't see {cfg['site']} (it sees: {', '.join(sites) or 'nothing'})"
        return "ok", f"{cfg['site']} readable ({sites[cfg['site']]})"
    if key == "indexing":
        gsc = enabled("gsc") or {}
        site, kf = cfg.get("site") or gsc.get("site"), cfg.get("key_file") or gsc.get("key_file")
        tok = sa_token(kf, "webmasters.readonly")
        urllib.request.urlopen(urllib.request.Request(cfg["sitemap"], headers={"User-Agent": UA}), timeout=30).read(200)
        home = "https://" + P["business"]["domains"][0] + "/"
        r = http("POST", "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
                 {"Authorization": f"Bearer {tok}"}, {"inspectionUrl": home, "siteUrl": site})
        v = r.get("inspectionResult", {}).get("indexStatusResult", {}).get("coverageState")
        return "ok", f"sitemap loads; test inspection of {home} works ({v})"
    if key == "ga4":
        if cfg.get("method") == "mcp":
            return "warn", f"read through MCP tool {cfg.get('mcp_tool')}; the script can't call MCPs, Claude tests it with one tiny report"
        tok = sa_token(cfg["key_file"], "analytics.readonly")
        r = http("POST", f"https://analyticsdata.googleapis.com/v1beta/properties/{cfg['property_id']}:runReport",
                 {"Authorization": f"Bearer {tok}"}, {"dateRanges": [{"startDate": str(dt.date.today() - dt.timedelta(days=1)), "endDate": str(dt.date.today() - dt.timedelta(days=1))}],
                                                      "metrics": [{"name": "sessions"}]})
        rows = r.get("rows") or []
        return "ok", f"property {cfg['property_id']} readable (yesterday: {rows[0]['metricValues'][0]['value'] if rows else 0} sessions)"
    if key == "clarity":
        secret(cfg)  # raises if the key is missing
        ledger_f = PDIR / "clarity-calls.json"
        if not clarity_live:
            last = None
            for h in sorted((PDIR / "history").glob("*.json"), reverse=True):
                if "pages" in (json.loads(h.read_text()).get("clarity") or {}):
                    last = h.stem
                    break
            if last:
                return "ok", f"key present; last successful pull {last} (live test skipped: Clarity allows 10 calls/day; use --test-clarity)"
            return "warn", "key present, never used successfully; run --check --test-clarity (spends 1 of 10 daily calls)"
        http("GET", "https://www.clarity.ms/export-data/api/v1/project-live-insights?numOfDays=1&dimension1=Device",
             {"Authorization": f"Bearer {secret(cfg)}"})
        led = json.loads(ledger_f.read_text()) if ledger_f.exists() else {}
        led[dt.date.today().isoformat()] = led.get(dt.date.today().isoformat(), 0) + 1
        ledger_f.write_text(json.dumps(led))
        return "ok", "live test call worked (1 of today's 10 used)"
    if key == "ghl":
        g = Ghl(cfg)
        r = http("POST", f"{GHL}/contacts/search", g.h28, {"locationId": cfg["location_id"], "page": 1, "pageLimit": 1})
        parts = [f"contacts readable ({r.get('total')} total)"]
        if cfg.get("pipeline_id"):
            pipes = http("GET", f"{GHL}/opportunities/pipelines?locationId={cfg['location_id']}", g.h28).get("pipelines", [])
            parts.append("pipeline found" if any(p["id"] == cfg["pipeline_id"] for p in pipes) else "PIPELINE ID NOT FOUND")
        if cfg.get("calendar_ids"):
            now = int(time.time() * 1000)
            for cal in cfg["calendar_ids"]:
                http("GET", f"{GHL}/calendars/events?locationId={cfg['location_id']}&calendarId={cal}&startTime={now}&endTime={now + 86400000}", g.h21)
            parts.append(f"{len(cfg['calendar_ids'])} calendar(s) readable")
        return ("fail" if "NOT FOUND" in " ".join(parts) else "ok"), "; ".join(parts)
    if key == "ahrefs_dr":
        return "ok", f"DR {pull_ahrefs()['domain_rating']} for {cfg['target']}"
    raise RuntimeError(f"no check for {key}")


def check(clarity_live=False):
    ICON = {"ok": "OK  ", "warn": "WARN", "fail": "FAIL", "off": "--  "}
    rows = []
    for key, label, needs, fix in SOURCES:
        if not enabled(key):
            rows.append(("off", label, needs, "not set up. To add: " + fix))
            continue
        try:
            st, detail = check_source(key, clarity_live)
        except Exception as e:
            st, detail = "fail", f"{type(e).__name__}: {e}. Fix: {fix}"
        rows.append((st, label, needs, detail))
    for c in (enabled("commands") or {}).get("list", []):
        try:
            r = subprocess.run(c["run"], shell=True, cwd=str(PDIR), capture_output=True, text=True, timeout=c.get("timeout", 120))
            if r.returncode != 0:
                raise RuntimeError(f"exit {r.returncode}: {r.stderr.strip()[-200:]}")
            n = len(json.loads(r.stdout.strip().splitlines()[-1]))
            rows.append(("ok", f"command: {c['name']}", c.get("run"), f"ran, {n} rows"))
        except Exception as e:
            rows.append(("fail", f"command: {c['name']}", c.get("run"), f"{type(e).__name__}: {e}"))
    browser = {k: v for k, v in (P.get("browser") or {}).items() if not k.startswith("_")}
    for k, (label, fix) in BROWSER_FIX.items():
        if k in browser:
            rows.append(("warn", label, "browser login", f"listed ({browser[k].get('browser') or browser[k].get('login')}); only confirmed when Claude opens it"))
        else:
            rows.append(("off", label, "browser login", "not set up. To add: " + fix))
    for k, v in browser.items():
        if k not in BROWSER_FIX:
            rows.append(("warn", k, "browser login", "listed; only confirmed when Claude opens it"))

    envf = PDIR / ".env"
    print(f"CONNECTIONS for {P.get('business', {}).get('name')} (profile {PDIR})")
    print(f"profile .env: {'present' if envf.exists() else 'none (sources point at other env files or none needed)'}")
    for st, label, needs, detail in rows:
        print(f"[{ICON[st]}] {label:<22} needs: {needs}\n         {detail}")
    counts = Counter(r[0] for r in rows)
    print(f"\n{counts['ok']} connected, {counts['warn']} to confirm, {counts['fail']} broken, {counts['off']} not set up")
    return 1 if counts["fail"] else 0


def main():
    global P, PDIR, ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True, help="folder holding profile.json")
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--no-inspect", action="store_true")
    ap.add_argument("--check", action="store_true", help="test every connection and print what's missing; pulls nothing")
    ap.add_argument("--test-clarity", action="store_true", help="with --check: make a live Clarity call (1 of 10/day)")
    a = ap.parse_args()
    PDIR = Path(a.profile).expanduser().resolve()
    P = json.loads((PDIR / "profile.json").read_text())
    # Relative paths in the profile resolve against the project root. The
    # default layout is <root>/.claude/how-are-we-doing/<slug>/profile.json.
    root = os.path.expanduser(P.get("root", "../../.."))
    ROOT = Path(root) if os.path.isabs(root) else (PDIR / root).resolve()
    days = a.days or P.get("default_days", 28)
    if a.check:
        raise SystemExit(check(a.test_clarity))

    hist = PDIR / "history"
    hist.mkdir(exist_ok=True)
    today = dt.date.today().isoformat()

    def load(p):
        s = json.loads(p.read_text())
        s["_date"] = p.stem
        return s

    snaps = sorted(hist.glob("*.json"))
    earlier = [p for p in snaps if p.stem < today]
    prev = load(earlier[-1]) if earlier else None
    newest = load(snaps[-1]) if snaps else None

    ghl = None
    if enabled("ghl"):
        try:
            ghl = Ghl(enabled("ghl"))
        except Exception as e:
            ghl_err = {"error": f"{type(e).__name__}: {e}"}

    out = {"pulled_at": dt.datetime.now().isoformat(timespec="seconds"), "days": days}
    with cf.ThreadPoolExecutor(6) as ex:
        futs = {}
        if enabled("gsc"):
            futs["gsc"] = ex.submit(section, pull_gsc, days)
        if enabled("indexing") and not a.no_inspect:
            futs["indexing"] = ex.submit(section, pull_indexing, newest)
        if enabled("ga4"):
            futs["ga4"] = ex.submit(section, pull_ga4, days)
        if enabled("clarity"):
            futs["clarity"] = ex.submit(section, pull_clarity)
        if enabled("ahrefs_dr"):
            futs["ahrefs_dr"] = ex.submit(section, pull_ahrefs)
        if enabled("ghl"):
            out["ghl"] = section(pull_ghl, ghl, days) if ghl else ghl_err
        if enabled("commands"):
            out["commands"] = section(pull_commands, ghl, days)
        for k, f in futs.items():
            out[k] = f.result()
    out["kpis"] = kpis(out)
    (hist / f"{today}.json").write_text(json.dumps(out, indent=1, default=str))
    print(summary(out, prev))
    print(f"\nfull data: {hist / (today + '.json')}")


if __name__ == "__main__":
    main()
