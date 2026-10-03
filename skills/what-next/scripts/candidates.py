#!/usr/bin/env python3
"""List every candidate action the latest how-are-we-doing snapshot supports,
with its evidence row, and flag the ones a pending watchlist read blocks.

    python3 candidates.py --profile <dir>              # readable list
    python3 candidates.py --profile <dir> --json       # machine-readable
    python3 candidates.py --profile <dir> --today 2026-10-03

This is the deterministic half of what-next: it finds and quotes. It does NOT
rank, apply the buyer test, or decide. Claude does that per SKILL.md, and must
read each flagged watchlist line itself: the date matching here is a helper,
not a verdict.

Reads: profile.json, history/*.json (newest = the snapshot judged; the one
before it gives "since last snapshot"), watchlist.md.
"""
import argparse
import datetime as dt
import json
import re
from collections import Counter
from pathlib import Path

DATE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")
PATH = re.compile(r"(?<![\w.])(/[a-z0-9][a-z0-9\-/_.]*)", re.I)


# ---------------------------------------------------------------- watchlist

def watchlist_items(text):
    """Open items as {text, due, paths}. An item starts with '- ' at column 0
    under '## Open'; following indented lines belong to it."""
    if not text:
        return []
    m = re.search(r"^## Open\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    body = m.group(1) if m else ""
    items, cur = [], None
    for line in body.splitlines():
        if line.startswith("- "):
            cur = [line[2:]]
            items.append(cur)
        elif cur is not None and line.strip():
            cur.append(line.strip())
    out = []
    for parts in items:
        t = " ".join(parts)
        head = parts[0]
        # The due date is the one after "From"/"due"/"read" in the first line, else none.
        dm = re.search(r"(?:From|from|due|Due|read on|Read on)\s*~?(20\d\d-\d\d-\d\d)", head)
        out.append({
            "text": t,
            "head": re.sub(r"\*\*", "", head)[:160],
            "due": dm.group(1) if dm else None,
            "parked_for_next_run": bool(re.match(r"\W*next run", head, re.I)),
            "paths": sorted({p.rstrip(".,)`") for p in PATH.findall(t) if not p.startswith("//")}),
        })
    return out


def mentions(items, page, today):
    """Watchlist items that name this page, and whether one blocks it."""
    hits = [i for i in items if page and page != "/" and any(p == page or p.startswith(page + "?") for p in i["paths"])]
    blocked = next((i for i in hits if i["due"] and i["due"] > today), None)
    return hits, blocked


# ---------------------------------------------------------------- candidates

def collect(prof, snap, prev_snap, items, today):
    C = []
    noise = prof.get("noise") or {}
    wrong = set(noise.get("wrong_audience_pages") or [])
    noise_q = {(pg, q) for pg, qs in (noise.get("queries_by_page") or {}).items() for q in qs}
    rules = prof.get("opportunity_rules") or {}
    pmin, pmax = rules.get("position_min", 4), rules.get("position_max", 20)
    imin = rules.get("min_impressions", 20)
    bots = set(noise.get("bot_channels") or [])

    def add(kind, tier, subject, evidence, page=None, **extra):
        hits, blocked = mentions(items, page, today)
        C.append({"kind": kind, "tier": tier, "subject": subject, "page": page, "evidence": evidence,
                  "watchlist": [h["head"] for h in hits],
                  "blocked_until": blocked["due"] if blocked else None,
                  "noise": page in wrong, **extra})

    g, ga, cl, gh, ix = (snap.get(x) or {} for x in ("gsc", "ga4", "clarity", "ghl", "indexing"))
    gwin = f"GSC {g['window']['cur'][0]}→{g['window']['cur'][1]}" if "window" in g else "GSC"
    awin = f"GA4 {ga['window']['cur'][0]}→{ga['window']['cur'][1]}" if ga.get("window") else "GA4"

    # Tier 1: money already in reach.
    for r in (gh.get("bookings") or {}).get("cur") or []:
        if r.get("class") == "unconfirmed" and r.get("status") != "cancelled":
            add("unconfirmed_lead", 1, r.get("title") or r.get("contact_id"),
                f"GHL booking made {r.get('booked_at')}, call {r.get('starts')}, tags {r.get('tags')}",
                contact_id=r.get("contact_id"))
    pl = gh.get("pipeline")
    if pl and set((pl.get("by_status") or {})) <= {"open"} and pl.get("total"):
        add("pipeline_hygiene", 1, pl.get("name"),
            f"GHL {pl['total']} opportunities, all open, stages {pl.get('by_stage')}: clients won can't be measured")

    # Tier 2: where real leads actually come from.
    src = Counter()
    real_labels = (prof.get("people") or {}).get("confirmed_real") or {}
    for win in ("cur", "prev"):
        for r in (gh.get("bookings") or {}).get(win) or []:
            if r.get("class") != "real" or r.get("status") == "cancelled":
                continue
            tag = next((t[7:] for t in r.get("tags") or [] if t.startswith("source:")), None)
            label = real_labels.get(r.get("contact_id"), "")
            paren = re.search(r"\(([^):]+)", label)
            src[tag or (paren.group(1).strip() if paren else "unknown")] += 1
    if src:
        add("lead_sources", 2, "real bookings by source, last 56 days",
            "GHL real bookings (this + prior window), source tag or owner's label: "
            + ", ".join(f"{k} {v}" for k, v in src.most_common()))
    for i in items:
        if i["parked_for_next_run"]:
            add("parked_task", 2, i["head"], "watchlist item parked for the next run")

    # Tier 3: buyer traffic that arrives and leaves.
    for r in ga.get("landing") or []:
        ch, pg = r.get("sessionDefaultChannelGroup"), r.get("landingPage")
        s, e = r.get("sessions") or 0, r.get("engagedSessions") or 0
        if ch in bots or pg in (None, "(not set)") or s < 5:
            continue
        if e / s < 0.4:
            add("landing_leak", 3, f"{pg} ({ch})", f"{awin}: {s} sessions, {e} engaged", page=pg)
    for pg, p in (cl.get("pages") or {}).items():
        base = pg.split("?")[0]
        sess = p.get("sessions") or 0
        flags = []
        if (p.get("RageClickCount") or 0) > 0:
            flags.append(f"{p['RageClickCount']} rage clicks")
        if sess >= 3 and (p.get("DeadClickCount") or 0) >= 3:
            flags.append(f"{p['DeadClickCount']} dead clicks")
        if (p.get("QuickbackClick") or 0) > 0:
            flags.append(f"{p['QuickbackClick']} quickbacks")
        if (p.get("ScriptErrorCount") or 0) > 0:
            flags.append(f"{p['ScriptErrorCount']} script errors")
        if sess >= 3 and (p.get("scroll_depth") or 100) < 30:
            flags.append(f"scroll {p.get('scroll_depth')}%")
        if flags:
            add("on_page_friction", 3, pg, f"Clarity last {cl.get('days', 3)}d: {sess} sessions, " + ", ".join(flags), page=base)

    # Tier 4: search demand near page one.
    for r in g.get("opportunities") or []:
        if (r["page"], r["query"]) in noise_q:
            continue
        if not (pmin <= (r.get("position") or 0) <= pmax) or (r.get("impressions") or 0) < imin:
            continue
        kind = "split_query" if any(str(f).startswith("split") for f in r.get("flags") or []) else "near_miss_query"
        add(kind, 4, f"'{r['query']}' → {r['page']}",
            f"{gwin}: {r['impressions']} impr, {r['clicks']} clicks, pos {r['position']} "
            f"(prior {r.get('prev_impressions')} impr, pos {r.get('prev_position')}), market impr {r.get('market_impressions')}",
            page=r["page"])
    for r in (g.get("movers") or {}).get("clicks") or []:
        c, p = (r.get("cur") or {}).get("clicks", 0), (r.get("prev") or {}).get("clicks", 0)
        if p >= 3 and c < p:
            add("click_loss", 4, r["page"], f"{gwin}: clicks {p}→{c}, impr {(r.get('prev') or {}).get('impressions')}→{(r.get('cur') or {}).get('impressions')}, "
                f"pos {(r.get('prev') or {}).get('position')}→{(r.get('cur') or {}).get('position')}", page=r["page"])
    for r in (g.get("new_queries") or [])[:5]:
        if (r.get("impressions") or 0) >= 50:
            add("new_demand", 5, f"'{r.get('query')}'", f"{gwin}: new query, {r['impressions']} impr, pos {r.get('position')}")

    # Tier 5: plumbing.
    for r in ix.get("not_indexed") or []:
        if re.search(r"[?&]page=", r["url"]):
            continue
        path = re.sub(r"^https?://[^/]+", "", r["url"]) or "/"
        add("not_indexed", 5, path, f"URL Inspection: {r.get('coverage')}, last crawl {r.get('last_crawl')}", page=path)
    return C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--today")
    a = ap.parse_args()
    pdir = Path(a.profile).expanduser().resolve()
    prof = json.loads((pdir / "profile.json").read_text())
    snaps = sorted((pdir / "history").glob("*.json"))
    if not snaps:
        raise SystemExit("no snapshots: run how-are-we-doing first")
    snap = json.loads(snaps[-1].read_text())
    prev_snap = json.loads(snaps[-2].read_text()) if len(snaps) > 1 else None
    wl = pdir / "watchlist.md"
    items = watchlist_items(wl.read_text() if wl.exists() else "")
    today = a.today or dt.date.today().isoformat()
    cands = collect(prof, snap, prev_snap, items, today)
    # Age comes from when the data was pulled, not the filename: a renamed or
    # back-dated file must not make fresh data look stale (or stale data fresh).
    pulled = str(snap.get("pulled_at") or snaps[-1].stem)[:10]
    age = (dt.date.fromisoformat(today) - dt.date.fromisoformat(pulled)).days
    missing = [s for s in ("gsc", "ga4", "ghl", "indexing", "clarity") if not snap.get(s) or "skipped" in snap.get(s, {}) or "error" in snap.get(s, {})]
    due = [i for i in items if i["due"] and i["due"] <= today]
    meta = {"snapshot": snaps[-1].stem, "pulled": pulled, "age_days": age, "missing_sources": missing, "today": today,
            "watchlist_due": [i["head"] for i in due],
            "watchlist_open": [{"head": i["head"], "due": i["due"], "paths": i["paths"]} for i in items]}
    if a.json:
        print(json.dumps({"meta": meta, "candidates": cands}, indent=1))
        return
    print(f"SNAPSHOT {meta['snapshot']} (pulled {pulled}, {age} days old) | missing: {', '.join(missing) or 'none'} | today {today}")
    if due:
        print("WATCHLIST DUE: " + " | ".join(meta["watchlist_due"]))
    for t in range(1, 6):
        rows = [c for c in cands if c["tier"] == t]
        if not rows:
            continue
        print(f"\nTIER {t}")
        for c in rows:
            flag = (f"  [BLOCKED until {c['blocked_until']}]" if c["blocked_until"] else "") + ("  [NOISE page]" if c["noise"] else "")
            print(f"  {c['kind']}: {c['subject']}{flag}\n      {c['evidence']}")
            for w in c["watchlist"]:
                print(f"      watchlist: {w}")


if __name__ == "__main__":
    main()
