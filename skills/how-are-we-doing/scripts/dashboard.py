#!/usr/bin/env python3
"""Build the visual dashboard for a business profile from its history snapshots.

    python3 dashboard.py --profile <dir>            # writes <dir>/dashboard.html
    python3 dashboard.py --profile <dir> --out x.html

Reads every history/<date>.json plus profile.json. Writes one self-contained
HTML page (inline SVG charts, no libraries) for the Artifact tool to publish.

Counts only: no contact names, emails, contact ids or free-tool business names
ever reach the page. Queries and page paths are fine.

Every number shows its source and window. Small counts get "44 → 53 (+9)",
never a percentage. Sections whose source is missing say "not measured".
"""
import argparse
import datetime as dt
import html
import json
import math
from collections import Counter
from pathlib import Path

E = html.escape

# KPI lines that get a sparkline across snapshots, with which direction is good.
KPI_META = {
    "real_booking_people": ("Real bookings, 28d", "up"),
    "search_clicks": ("Search clicks", "up"),
    "search_clicks_market": ("Search clicks, market", "up"),
    "search_impressions": ("Search impressions", "up"),
    "search_position": ("Avg position", "down"),
    "search_ctr": ("Search CTR %", "up"),
    "organic_engaged_pct": ("Organic engaged %", "up"),
    "gbp_rating": ("Google rating", "up"),
    "pipeline_won": ("Clients won", "up"),
    "clarity_rage_clicks_3d": ("Rage clicks, 3d", "down"),
    "organic_sessions": ("Organic sessions", "up"),
    "domain_rating": ("Domain Rating", "up"),
    "gbp_reviews": ("Google reviews", "up"),
    "clarity_sessions_3d": ("Clarity sessions, 3d", "up"),
    "clarity_dead_clicks_3d": ("Dead clicks, 3d", "down"),
    "bot_channel_sessions": ("Bot-channel sessions", "down"),
}


# ---------------------------------------------------------------- formatting

def num(v):
    if v is None:
        return "–"
    if isinstance(v, float) and not v.is_integer():
        return f"{v:,.2f}".rstrip("0").rstrip(".")
    return f"{int(v):,}"


def delta(cur, prev, good="up"):
    """'44 → 53 (+9)' style chip. Counts, never percentages."""
    if cur is None or prev is None or not isinstance(cur, (int, float)) or not isinstance(prev, (int, float)):
        return ""
    d = cur - prev
    if abs(d) < 1e-9:
        return f'<span class="chip flat" title="no change">= {num(prev)}</span>'
    better = (d > 0) == (good == "up")
    arrow = "▲" if d > 0 else "▼"
    sign = "+" if d > 0 else "−"
    cls = "good" if better else "bad"
    word = "better" if better else "worse"
    return (f'<span class="chip {cls}" title="{word} than {num(prev)}">'
            f'<span class="ar" aria-hidden="true">{arrow}</span>{sign}{num(abs(d))} '
            f'<span class="was">from {num(prev)}</span></span>')


def nice_ticks(vmax, n=4):
    if vmax <= 0:
        return [0, 1]
    raw = vmax / n
    mag = 10 ** math.floor(math.log10(raw))
    step = next(s * mag for s in (1, 2, 2.5, 5, 10) if s * mag >= raw)
    top = step * math.ceil(vmax / step)
    t, out = 0, []
    while t <= top + 1e-9:
        out.append(round(t, 6))
        t += step
    return out


# ---------------------------------------------------------------- charts

def column_chart(points, label, unit):
    """points = [(x_label, value)]. One series, one axis, labels on max + last."""
    if not points:
        return '<p class="nm">Not measured.</p>'
    vals = [v for _, v in points]
    ticks = nice_ticks(max(vals))
    W, H, R, T, B = 640, 220, 12, 22, 28
    L = 16 + 7 * len(num(ticks[-1]))
    top = ticks[-1] or 1
    pw, ph = W - L - R, H - T - B
    band = pw / len(points)
    bw = min(24, band * 0.6)
    y = lambda v: T + ph - (v / top) * ph
    s = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="{E(label)}">']
    for t in ticks:
        s.append(f'<line x1="{L}" x2="{W - R}" y1="{y(t):.1f}" y2="{y(t):.1f}" class="grid"/>')
        s.append(f'<text x="{L - 8}" y="{y(t) + 4:.1f}" class="tick" text-anchor="end">{num(t)}</text>')
    imax = vals.index(max(vals))
    for i, (xl, v) in enumerate(points):
        cx = L + band * i + band / 2
        x0, x1, y0, y1 = cx - bw / 2, cx + bw / 2, y(0), y(v)
        r = min(4, (y0 - y1) / 2, bw / 2)
        if v > 0:
            d = (f"M{x0:.1f},{y0:.1f} L{x0:.1f},{y1 + r:.1f} Q{x0:.1f},{y1:.1f} {x0 + r:.1f},{y1:.1f} "
                 f"L{x1 - r:.1f},{y1:.1f} Q{x1:.1f},{y1:.1f} {x1:.1f},{y1 + r:.1f} L{x1:.1f},{y0:.1f} Z")
            s.append(f'<path d="{d}" class="bar{" last" if i == len(points) - 1 else ""}"/>')
        tip = f"Week of {xl}: {num(v)} {unit}"
        s.append(f'<rect x="{cx - band / 2:.1f}" y="{T}" width="{band:.1f}" height="{ph}" class="hit" '
                 f'tabindex="0" data-tip="{E(tip)}" aria-label="{E(tip)}"/>')
        if i in (imax, len(points) - 1):
            s.append(f'<text x="{cx:.1f}" y="{y1 - 6:.1f}" class="val" text-anchor="middle">{num(v)}</text>')
        if len(points) <= 8 or i % 2 == (len(points) - 1) % 2:
            s.append(f'<text x="{cx:.1f}" y="{H - 8}" class="tick" text-anchor="middle">{E(xl)}</text>')
    s.append(f'<line x1="{L}" x2="{W - R}" y1="{y(0):.1f}" y2="{y(0):.1f}" class="axis"/></svg>')
    table = "".join(f"<tr><td>{E(x)}</td><td class='n'>{num(v)}</td></tr>" for x, v in points)
    s.append(f'<details class="as-table"><summary>Show as table</summary><div class="tw"><table>'
             f'<thead><tr><th>Week of</th><th class="n">{E(unit.capitalize())}</th></tr></thead>'
             f'<tbody>{table}</tbody></table></div></details>')
    return "".join(s)


def sparkline(series):
    """series = [(date, value)], >= 2 points."""
    if len(series) < 2:
        return ""
    W, H, P = 120, 34, 5
    vs = [v for _, v in series]
    lo, hi = min(vs), max(vs)
    span = (hi - lo) or 1
    xs = [P + i * (W - 2 * P) / (len(vs) - 1) for i in range(len(vs))]
    ys = [H - P - (v - lo) / span * (H - 2 * P) for v in vs]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    area = f"{xs[0]:.1f},{H - P} {pts} {xs[-1]:.1f},{H - P}"
    tip = " · ".join(f"{d[5:]}: {num(v)}" for d, v in series)
    return (f'<svg viewBox="0 0 {W} {H}" class="spark" role="img" aria-label="Per snapshot: {E(tip)}" data-tip="{E(tip)}" tabindex="0">'
            f'<polygon points="{area}" class="sp-area"/><polyline points="{pts}" class="sp-line"/>'
            f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="4" class="sp-dot"/></svg>')


def hbars(rows, unit):
    """rows = [(label, value, prev_or_None)] as horizontal bars, one scale."""
    if not rows:
        return '<p class="nm">Not measured.</p>'
    top = max(v for _, v, _ in rows) or 1
    out = ['<div class="hb">']
    for lab, v, p in rows:
        w = max(0.5, v / top * 100)
        prev = f'<span class="was">prior {num(p)}</span>' if p is not None else ""
        out.append(f'<div class="hb-row" data-tip="{E(lab)}: {num(v)} {unit}" tabindex="0">'
                   f'<span class="hb-lab">{E(lab)}</span>'
                   f'<span class="hb-track"><span class="hb-fill" style="width:{w:.1f}%"></span></span>'
                   f'<span class="hb-val">{num(v)} {prev}</span></div>')
    out.append("</div>")
    return "".join(out)


# ---------------------------------------------------------------- sections

def tile(label, value, sub="", chip="", spark="", src=""):
    return (f'<div class="tile"><div class="t-lab">{E(label)}</div>'
            f'<div class="t-row"><div class="t-val">{value}</div>{spark}</div>'
            f'<div class="t-chip">{chip}</div>'
            f'{f"<div class=t-sub>{sub}</div>" if sub else ""}'
            f'<div class="src">{src}</div></div>')


def series_for(snaps, key):
    out = []
    for d, s in snaps:
        v = (s.get("kpis") or {}).get(key)
        if isinstance(v, (int, float)):
            out.append((d, v))
    return out


def bookings_block(gh):
    b = gh.get("bookings") or {}
    def counts(lst):
        live = [r for r in lst if r.get("status") != "cancelled"]
        c = Counter(r.get("class") for r in live)
        people = lambda cls: len({r.get("contact_id") for r in live if r.get("class") == cls})
        return {"real": people("real"), "unconfirmed": people("unconfirmed"),
                "internal": c.get("internal", 0), "cancelled": sum(1 for r in lst if r.get("status") == "cancelled")}
    cur, prev = counts(b.get("cur") or []), counts(b.get("prev") or [])
    rows = "".join(
        f"<tr><td>{lab}</td><td class='n'>{cur[k]}</td><td class='n'>{prev[k]}</td></tr>"
        for k, lab in (("real", "Real people"), ("unconfirmed", "Unconfirmed (owner to confirm)"),
                       ("internal", "Internal / test"), ("cancelled", "Cancelled")))
    src = Counter()
    for r in b.get("cur") or []:
        if r.get("status") == "cancelled" or r.get("class") == "internal":
            continue
        tags = [t for t in r.get("tags") or [] if t.startswith("source:")]
        src[tags[0][7:] if tags else "not tagged"] += 1
    srcs = "".join(f'<li><span class="pill">{E(k)}</span> {v}</li>' for k, v in src.most_common()) or "<li>None</li>"
    last = (gh.get("last_real_booking") or {}).get("booked_at", "not measured")
    return (f'<div class="tw"><table><thead><tr><th>Bookings</th><th class="n">This 28d</th><th class="n">Prior 28d</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>'
            f'<p class="kv"><span>Last real booking</span> <b>{E(str(last))}</b></p>'
            f'<p class="kv"><span>First-visit source, this window</span></p><ul class="pills">{srcs}</ul>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    pdir = Path(a.profile).expanduser().resolve()
    prof = json.loads((pdir / "profile.json").read_text())
    snaps = [(p.stem, json.loads(p.read_text())) for p in sorted((pdir / "history").glob("*.json"))]
    if not snaps:
        raise SystemExit("no snapshots; run pull.py first")
    date, s = snaps[-1]
    last_snap = snaps[-2][1] if len(snaps) > 1 else None
    biz = prof.get("business") or {}
    market = (prof.get("market") or {}).get("gsc_country", "market")
    k = s.get("kpis") or {}
    pk = (last_snap or {}).get("kpis") or {}
    not_measured = []

    g, ga, cl, gh, ix, gbp = (s.get(x) or {} for x in ("gsc", "ga4", "clarity", "ghl", "indexing", "gbp"))
    for name, sec in (("Search Console", g), ("GA4", ga), ("Clarity", cl), ("GoHighLevel", gh), ("Indexing", ix)):
        if not sec or "error" in sec or "skipped" in sec:
            why = sec.get("error") or sec.get("skipped") or "no data in this snapshot" if sec else "not set up or not recorded"
            not_measured.append(f"{name}: {why}")

    # windows strip
    win = []
    if "window" in g:
        win.append(f"Search Console {g['window']['cur'][0]} → {g['window']['cur'][1]} vs prior 28d")
    if ga.get("window"):
        win.append(f"GA4 {ga['window']['cur'][0]} → {ga['window']['cur'][1]}")
    if gh.get("bookings"):
        win.append(f"Bookings last {gh.get('window_days', s.get('days', 28))}d by booking date")
    if cl.get("days"):
        win.append(f"Clarity last {cl['days']} days")
    if gbp.get("range"):
        win.append(f"Business Profile {gbp['range']} (read {gbp.get('read_at', '?')})")

    since = [f"{KPI_META.get(key, (key,))[0]} {num(pk[key])} → {num(v)}" for key, v in k.items()
             if key in pk and pk[key] != v and isinstance(v, (int, float))]

    # tiles
    tiles = []
    if gh.get("bookings"):
        cur_unc = len({r["contact_id"] for r in gh["bookings"]["cur"] if r.get("class") == "unconfirmed" and r.get("status") != "cancelled"})
        prev_real = len({r["contact_id"] for r in gh["bookings"]["prev"] if r.get("class") == "real" and r.get("status") != "cancelled"})
        hero = (f'<section class="hero"><div class="h-lab">Real bookings, last 28 days</div>'
                f'<div class="h-row"><div class="h-val">{num(k.get("real_booking_people"))}</div>'
                f'<div>{delta(k.get("real_booking_people"), prev_real)}'
                f'{f"<div class=h-sub>+{cur_unc} unconfirmed, waiting on the owner</div>" if cur_unc else ""}</div></div>'
                f'<div class="src">GoHighLevel calendar, people classified by the profile. Prior = the 28 days before.</div></section>')
    else:
        hero = '<section class="hero"><div class="h-lab">Leads</div><div class="h-val">–</div><div class="src">Not measured: no CRM in this profile.</div></section>'
    if "totals" in g:
        c, p = g["totals"]["cur"], g["totals"]["prev"]
        sub = ""
        if "totals_market" in g:
            mc, mp = g["totals_market"]["cur"], g["totals_market"]["prev"]
            sub = f"{E(market.upper())} only: <b>{num(mc['clicks'])}</b> {delta(mc['clicks'], mp['clicks'])}"
        tiles.append(tile("Search clicks", num(c["clicks"]), sub, delta(c["clicks"], p["clicks"]),
                          sparkline(series_for(snaps, "search_clicks")), "Search Console, 28d vs prior 28d"))
        tiles.append(tile("Avg position", num(c["position"]), f"CTR {c['ctr']}% (prior {p['ctr']}%)",
                          delta(c["position"], p["position"], "down"), sparkline(series_for(snaps, "search_position")),
                          "Search Console. Lower is better; it moves when new queries appear."))
    org_cur = next((r for r in ga.get("channels_cur") or [] if r.get("sessionDefaultChannelGroup") == "Organic Search"), None)
    org_prev = next((r for r in ga.get("channels_prev") or [] if r.get("sessionDefaultChannelGroup") == "Organic Search"), None)
    if org_cur:
        tiles.append(tile("Organic sessions", num(org_cur["sessions"]),
                          f"{round(org_cur['engagementRate'] * 100)}% engaged"
                          + (f" (prior {round(org_prev['engagementRate'] * 100)}%)" if org_prev else ""),
                          delta(org_cur["sessions"], (org_prev or {}).get("sessions")),
                          sparkline(series_for(snaps, "organic_sessions")), "GA4, Organic Search channel"))
    if "indexed" in ix:
        pct = ix["indexed"] / max(ix["count"], 1) * 100
        tiles.append(tile("Indexed pages", f"{ix['indexed']}<small>/{ix['count']}</small>",
                          f'<span class="meter" role="img" aria-label="{ix["indexed"]} of {ix["count"]} indexed"><span style="width:{pct:.1f}%"></span></span>',
                          "", "", "Search Console URL Inspection of the sitemap"))
    if gbp.get("metrics"):
        m = gbp["metrics"][0]
        rv = gbp.get("reviews") or {}
        tiles.append(tile(m["label"], num(m["value"]),
                          f"{E(m.get('comparison', ''))}" + (f" · {rv['rating']}★, {rv['count']} reviews" if rv else ""),
                          "", "", f"Google Business Profile, {E(gbp.get('range', ''))} as shown on screen"))
    if "domain_rating" in k:
        tiles.append(tile("Domain Rating", num(k["domain_rating"]), "", delta(k["domain_rating"], pk.get("domain_rating")),
                          sparkline(series_for(snaps, "domain_rating")), "Ahrefs, vs last snapshot"))

    # weekly charts
    weekly = g.get("weekly") or {}
    clicks_chart = column_chart([(w[5:], v["clicks"]) for w, v in weekly.items()], "Search clicks per week", "clicks")
    impr_chart = column_chart([(w[5:], v["impressions"]) for w, v in weekly.items()], "Search impressions per week", "impressions")

    # funnel
    funnel_html = ""
    fe = ((prof.get("sources") or {}).get("ga4") or {}).get("funnel_events") or []
    if fe and ga.get("events_cur"):
        ev_c = {r["eventName"]: r["eventCount"] for r in ga["events_cur"]}
        ev_p = {r["eventName"]: r["eventCount"] for r in ga.get("events_prev") or []}
        rows = [(e, ev_c.get(e, 0), ev_p.get(e, 0) if ga.get("events_prev") else None) for e in fe]
        funnel_html = (f'<section class="card"><h2>Booking funnel</h2>{hbars(rows, "events")}'
                       f'<p class="src">GA4 event counts, {E(ga["window"]["cur"][0])} → {E(ga["window"]["cur"][1])}. '
                       f'Funnel signals, not a lead count: GA4 counts tests and misses some bookings. No rates are computed across sources.</p></section>')

    # channels
    ch_html = ""
    if ga.get("channels_cur"):
        bots = set((prof.get("noise") or {}).get("bot_channels") or [])
        prev_by = {r["sessionDefaultChannelGroup"]: r for r in ga.get("channels_prev") or []}
        rows = []
        for r in ga["channels_cur"]:
            n = r["sessionDefaultChannelGroup"]
            pr = prev_by.get(n, {})
            flag = ' <span class="pill warn">mostly bots</span>' if n in bots else ""
            rows.append(f"<tr><td>{E(n)}{flag}</td><td class='n'>{num(r['sessions'])}</td><td class='n'>{num(pr.get('sessions'))}</td>"
                        f"<td class='n'>{round(r['engagementRate'] * 100)}%</td></tr>")
        ch_html = (f'<section class="card"><h2>Traffic by channel</h2><div class="tw"><table><thead><tr><th>Channel</th>'
                   f'<th class="n">Sessions</th><th class="n">Prior</th><th class="n">Engaged</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
                   f'<p class="src">GA4. Judge growth on the engaged, non-bot rows.</p></section>')

    # pages + queries
    pages_html = ""
    if g.get("pages"):
        rows = "".join(
            f"<tr><td class='path'>{E(r['page'])}</td><td class='n'>{num((r['cur'] or {}).get('clicks', 0))}</td>"
            f"<td class='n'>{num((r['prev'] or {}).get('clicks', 0))}</td><td class='n'>{num((r['cur'] or {}).get('impressions', 0))}</td>"
            f"<td class='n'>{num((r['cur'] or {}).get('position'))}</td></tr>" for r in g["pages"][:10])
        pages_html = (f'<section class="card wide"><h2>Top pages in search</h2><div class="tw"><table><thead><tr><th>Page</th><th class="n">Clicks</th>'
                      f'<th class="n">Prior</th><th class="n">Impr.</th><th class="n">Pos.</th></tr></thead><tbody>{rows}</tbody></table></div>'
                      f'<p class="src">Search Console, 28d vs prior 28d.</p></section>')
    q_html = ""
    if g.get("opportunities"):
        rows = "".join(
            f"<tr><td>{E(r['query'])}<div class='path'>{E(r['page'])}</div></td><td class='n'>{num(r['impressions'])}</td>"
            f"<td class='n'>{num(r['clicks'])}</td><td class='n'>{num(r['position'])}</td><td class='n'>{num(r.get('market_impressions'))}</td></tr>"
            for r in g["opportunities"][:10])
        q_html = (f'<section class="card wide"><h2>Queries ranking just off page one</h2><div class="tw"><table><thead><tr><th>Query → page</th>'
                  f'<th class="n">Impr.</th><th class="n">Clicks</th><th class="n">Pos.</th><th class="n">{E(market.upper())} impr.</th></tr></thead>'
                  f'<tbody>{rows}</tbody></table></div><p class="src">Search Console, positions 4–20 with real impressions. '
                  f'Run /what-next to decide which, if any, are worth acting on.</p></section>')

    # indexing
    ix_html = ""
    if ix.get("not_indexed"):
        items = "".join(f"<li><span class='path'>{E(r['url'])}</span> <span class='pill'>{E(r['coverage'])}</span></li>"
                        for r in ix["not_indexed"] if "?page=" not in r["url"])
        paged = sum(1 for r in ix["not_indexed"] if "?page=" in r["url"])
        ix_html = (f'<section class="card"><h2>Not indexed</h2><ul class="list">{items}</ul>'
                   + (f'<p class="src">Plus {paged} paginated list URLs.</p>' if paged else "")
                   + '<p class="src">Search Console URL Inspection.</p></section>')

    # clarity
    cl_html = ""
    if cl.get("pages"):
        # /audit/<id> pages are one named client's report: keep them off the page.
        ranked = sorted(((u, p) for u, p in cl["pages"].items() if not u.startswith("/audit/")),
                        key=lambda kv: -(kv[1].get("sessions") or 0))[:8]
        rows = "".join(
            f"<tr><td class='path'>{E(u)}</td><td class='n'>{num(p.get('sessions'))}</td><td class='n'>{num(p.get('scroll_depth'))}%</td>"
            f"<td class='n'>{num(p.get('active_time'))}s</td><td class='n'>{num(p.get('DeadClickCount'))}</td><td class='n'>{num(p.get('RageClickCount'))}</td></tr>"
            for u, p in ranked)
        cl_html = (f'<section class="card wide"><h2>On the page</h2><div class="tw"><table><thead><tr><th>Page</th><th class="n">Sessions</th>'
                   f'<th class="n">Scroll</th><th class="n">Active</th><th class="n">Dead</th><th class="n">Rage</th></tr></thead><tbody>{rows}</tbody></table></div>'
                   f'<p class="src">Microsoft Clarity, last {cl.get("days", 3)} days, bot sessions excluded. Dead clicks on plain text are usually text selection.</p></section>')

    # pipeline
    pipe_html = ""
    pl = gh.get("pipeline")
    if pl:
        stages = "".join(f'<li><span class="pill">{E(st)}</span> {n}</li>' for st, n in pl["by_stage"].items())
        status = pl.get("by_status") or {}
        won = len(pl.get("won") or [])
        won_txt = ("Not measured: every opportunity is still open." if set(status) <= {"open"} else f"{won} won")
        if set(status) <= {"open"}:
            not_measured.append("Clients won: every opportunity in the pipeline is still open")
        pipe_html = (f'<section class="card"><h2>Pipeline</h2><p class="kv"><span>{E(pl["name"])}</span> <b>{pl["total"]} opportunities</b></p>'
                     f'<ul class="pills">{stages}</ul><p class="kv"><span>Won</span> <b>{E(won_txt)}</b></p>'
                     f'<p class="src">GoHighLevel, current state.</p></section>')
    leads_html = f'<section class="card"><h2>Leads</h2>{bookings_block(gh)}</section>' if gh.get("bookings") else ""

    for item in gbp.get("not_measured") or []:
        not_measured.append(f"Business Profile: {item}")
    if not gbp:
        not_measured.append("Business Profile: not read this run")
    nm_html = "".join(f"<li>{E(x)}</li>" for x in not_measured) or "<li>Everything in this profile was measured.</li>"
    since_html = ("".join(f"<li>{E(x)}</li>" for x in since) if since
                  else "<li>No KPI changed.</li>" if last_snap else "<li>First snapshot: the comparison starts next run.</li>")
    rt = ga.get("realtime")
    rt_html = (f'<span class="live"><span class="dot" aria-hidden="true"></span>{rt["active_users"]} on the site at {E(rt.get("read_at", "")[11:16])}</span>' if rt else "")

    page = TEMPLATE.format(
        title=E(biz.get("name", "Business")) + " Pulse",
        name=E(biz.get("name", "Business")),
        domain=E(", ".join(biz.get("domains") or [])),
        date=E(date), n=len(snaps), live=rt_html,
        windows="".join(f"<li>{E(w)}</li>" for w in win),
        since=since_html, hero=hero, tiles="".join(tiles),
        clicks=clicks_chart, impr=impr_chart,
        leads=leads_html, funnel=funnel_html, channels=ch_html, pipeline=pipe_html,
        pages=pages_html, queries=q_html, ix=ix_html, clarity=cl_html,
        nm=nm_html, generated=dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
    out = Path(a.out) if a.out else pdir / (prof.get("dashboard") or {}).get("file", "dashboard.html")
    out.write_text(page)
    print(f"wrote {out} ({len(page) // 1024} KB) from {len(snaps)} snapshot(s), latest {date}")


TEMPLATE = """<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: instrument panel. Summary strip, one hero number, a tile rack, then detail cards in a two-column grid that stacks on phones. */
:root {{
  --bg: #f4f6f8; --surface: #fdfdfc; --fg: #141820; --muted: #59606d; --line: #e1e5ea;
  --accent: #2a78d6; --accent-wash: rgba(42,120,214,.10);
  --good: #0ca30c; --good-bg: rgba(12,163,12,.10); --bad: #d03b3b; --bad-bg: rgba(208,59,59,.09);
  --warn: #b97800; --warn-bg: rgba(250,178,25,.18);
  --sans: "Public Sans", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #111418; --surface: #191d22; --fg: #edf0f4; --muted: #a2a9b5; --line: #2b3038;
  --accent: #3987e5; --accent-wash: rgba(57,135,229,.16);
  --good-bg: rgba(12,163,12,.18); --bad-bg: rgba(208,59,59,.2); --warn: #fab219; --warn-bg: rgba(250,178,25,.16);
  color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #111418; --surface: #191d22; --fg: #edf0f4; --muted: #a2a9b5; --line: #2b3038;
  --accent: #3987e5; --accent-wash: rgba(57,135,229,.16);
  --good-bg: rgba(12,163,12,.18); --bad-bg: rgba(208,59,59,.2); --warn: #fab219; --warn-bg: rgba(250,178,25,.16);
  color-scheme: dark; }}
body {{ background: var(--bg); color: var(--fg); font: 15px/1.5 var(--sans); }}
.wrap {{ max-width: 1120px; margin: 0 auto; padding-inline: 16px; padding-block: 24px 48px; display: grid; gap: 20px; }}
header {{ display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 8px 24px; }}
h1 {{ font-size: 1.6rem; font-weight: 700; letter-spacing: -.01em; margin: 0; text-wrap: balance; }}
h1 small {{ font-weight: 500; color: var(--muted); font-size: .95rem; margin-left: 8px; }}
.meta {{ font: 500 .8rem var(--mono); color: var(--muted); display: flex; flex-wrap: wrap; gap: 6px 16px; align-items: center; }}
.live {{ display: inline-flex; align-items: center; gap: 6px; color: var(--fg); }}
.live .dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--good); box-shadow: 0 0 0 3px var(--good-bg); }}
.strip {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px 28px; padding: 14px 0; border-block: 1px solid var(--line); }}
.strip h3 {{ font: 600 .72rem var(--sans); text-transform: uppercase; letter-spacing: .08em; color: var(--muted); margin: 0 0 6px; }}
.strip ul {{ margin: 0; padding-left: 18px; font-size: .88rem; }}
.top {{ display: grid; grid-template-columns: minmax(0, 300px) minmax(0, 1fr); gap: 16px; }}
@media (max-width: 760px) {{ .top {{ grid-template-columns: minmax(0, 1fr); }} }}
.hero {{ align-self: start; background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 20px; display: grid; gap: 8px; align-content: start; border-top: 3px solid var(--accent); }}
.h-lab, .t-lab {{ font-weight: 600; font-size: .85rem; color: var(--muted); }}
.h-row {{ display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }}
.h-val {{ font-size: 3.6rem; font-weight: 700; line-height: 1; letter-spacing: -.02em; }}
.h-sub {{ font-size: .85rem; margin-top: 6px; }}
.tiles {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }}
.tile {{ background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; display: grid; gap: 4px; align-content: start; min-width: 0; }}
.t-row {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
.t-val {{ font-size: 1.9rem; font-weight: 700; letter-spacing: -.01em; line-height: 1.1; }}
.t-val small {{ font-size: 1rem; color: var(--muted); font-weight: 500; }}
.t-sub {{ font-size: .82rem; }}
.src {{ font: .72rem/1.45 var(--mono); color: var(--muted); }}
.chip {{ display: inline-flex; align-items: center; gap: 4px; font: 500 .78rem var(--mono); padding: 2px 8px; border-radius: 999px; color: var(--fg); white-space: nowrap; }}
.chip.good {{ background: var(--good-bg); }} .chip.good .ar {{ color: var(--good); }}
.chip.bad {{ background: var(--bad-bg); }} .chip.bad .ar {{ color: var(--bad); }}
.chip.flat {{ background: var(--line); }}
.chip .was {{ color: var(--muted); }}
.spark {{ width: 120px; height: 34px; flex: none; }}
.sp-line {{ fill: none; stroke: var(--accent); stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }}
.sp-area {{ fill: var(--accent-wash); stroke: none; }}
.sp-dot {{ fill: var(--accent); stroke: var(--surface); stroke-width: 2; }}
.meter {{ display: block; height: 8px; border-radius: 4px; background: var(--accent-wash); overflow: hidden; margin-top: 4px; }}
.meter span {{ display: block; height: 100%; background: var(--accent); border-radius: 4px; }}
.grid2 {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
@media (max-width: 760px) {{ .grid2 {{ grid-template-columns: minmax(0, 1fr); }} }}
.card {{ background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 18px; display: grid; gap: 10px; align-content: start; min-width: 0; }}
.card.wide {{ grid-column: 1 / -1; }}
h2 {{ font-size: 1.02rem; font-weight: 700; margin: 0; text-wrap: balance; }}
.chart {{ width: 100%; height: auto; display: block; }}
.grid {{ stroke: var(--line); stroke-width: 1; }} .axis {{ stroke: var(--muted); stroke-width: 1; }}
.tick {{ fill: var(--muted); font: 11px var(--mono); }} .val {{ fill: var(--fg); font: 600 12px var(--mono); }}
.bar {{ fill: var(--accent); opacity: .55; }} .bar.last {{ opacity: 1; }}
.hit {{ fill: transparent; cursor: default; }} .hit:hover, .hit:focus {{ fill: var(--accent-wash); outline: none; }}
.as-table summary {{ cursor: pointer; font-size: .8rem; color: var(--muted); }}
.tw {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: .86rem; }}
th {{ text-align: left; font-weight: 600; color: var(--muted); font-size: .75rem; padding: 6px 8px; border-bottom: 1px solid var(--line); }}
td {{ padding: 7px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }}
.n {{ text-align: right; font-variant-numeric: tabular-nums; font-family: var(--mono); white-space: nowrap; }}
.path {{ font: .78rem var(--mono); color: var(--muted); word-break: break-all; }}
td.path {{ color: var(--fg); }}
.pill {{ display: inline-block; font: 500 .75rem var(--mono); padding: 1px 8px; border-radius: 999px; background: var(--accent-wash); color: var(--fg); }}
.pill.warn {{ background: var(--warn-bg); }}
.pills, .list {{ list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: .86rem; }}
.list {{ display: grid; gap: 6px; }}
.kv {{ margin: 0; display: flex; justify-content: space-between; gap: 12px; font-size: .88rem; flex-wrap: wrap; }}
.kv span {{ color: var(--muted); }}
.hb {{ display: grid; gap: 8px; }}
.hb-row {{ display: grid; grid-template-columns: minmax(0, 170px) minmax(0, 1fr) auto; gap: 10px; align-items: center; font-size: .84rem; }}
.hb-lab {{ font-family: var(--mono); font-size: .78rem; overflow-wrap: anywhere; }}
.hb-track {{ height: 14px; }}
.hb-fill {{ display: block; height: 100%; background: var(--accent); border-radius: 0 4px 4px 0; }}
.hb-val {{ font-family: var(--mono); font-variant-numeric: tabular-nums; white-space: nowrap; }}
.hb-val .was {{ color: var(--muted); font-size: .75rem; margin-left: 6px; }}
.nm {{ color: var(--muted); font-size: .88rem; margin: 0; }}
footer {{ font: .72rem var(--mono); color: var(--muted); }}
#tip {{ position: fixed; pointer-events: none; background: var(--fg); color: var(--bg); font: 500 .78rem var(--mono); padding: 5px 9px; border-radius: 6px; max-width: 280px; z-index: 9; }}
[tabindex]:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
@media (prefers-reduced-motion: no-preference) {{ .hb-fill, .meter span {{ transition: width .4s ease; }} }}
</style>
<div class="wrap">
<header>
  <h1>{name} <small>{domain}</small></h1>
  <div class="meta"><span>Snapshot {date}</span><span>{n} on file</span>{live}</div>
</header>
<div class="strip">
  <div><h3>Since the last snapshot</h3><ul>{since}</ul></div>
  <div><h3>Windows</h3><ul>{windows}</ul></div>
</div>
<div class="top">{hero}<div class="tiles">{tiles}</div></div>
<div class="grid2">
  <section class="card"><h2>Search clicks per week</h2>{clicks}<p class="src">Search Console, all countries, latest week emphasized.</p></section>
  <section class="card"><h2>Search impressions per week</h2>{impr}<p class="src">Search Console, all countries.</p></section>
  {leads}{funnel}{channels}{pipeline}{pages}{queries}{ix}{clarity}
  <section class="card wide"><h2>Not measured</h2><ul class="list">{nm}</ul></section>
</div>
<footer>Built {generated} by how-are-we-doing from {n} snapshot(s). Counts only; no names leave the profile folder.</footer>
</div>
<div id="tip" hidden></div>
<script>
(function () {{
  var tip = document.getElementById('tip');
  function show(el, x, y) {{ tip.textContent = el.getAttribute('data-tip'); tip.hidden = false;
    var w = tip.offsetWidth; tip.style.left = Math.max(8, Math.min(x + 12, innerWidth - w - 8)) + 'px'; tip.style.top = (y + 14) + 'px'; }}
  document.querySelectorAll('[data-tip]').forEach(function (el) {{
    el.addEventListener('pointermove', function (e) {{ show(el, e.clientX, e.clientY); }});
    el.addEventListener('pointerleave', function () {{ tip.hidden = true; }});
    el.addEventListener('focus', function () {{ var r = el.getBoundingClientRect(); show(el, r.left, r.bottom); }});
    el.addEventListener('blur', function () {{ tip.hidden = true; }});
  }});
}})();
</script>
"""

if __name__ == "__main__":
    main()
