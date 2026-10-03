#!/usr/bin/env python3
"""Merge what Claude read outside pull.py (GA4 via an MCP, browser reads such as
Google Business Profile) into a history snapshot, so the dashboard and the
what-next skill can use it.

    python3 record.py --profile <dir> --ga4 ga4.json
    python3 record.py --profile <dir> --gbp gbp.json
    python3 record.py --profile <dir> --ga4 ga4.json --gbp gbp.json --date 2026-10-02

Writes into history/<date>.json (default: the newest snapshot), then
recomputes the GA4/GBP KPI lines. Run it AFTER pull.py: a second pull.py on
the same day rewrites that day's snapshot and drops what was recorded.

ga4.json: the raw MCP report outputs, keyed by call name, plus the windows.
  {
    "window": {"cur": ["2026-09-04", "2026-10-01"], "prev": ["2026-08-07", "2026-09-03"]},
    "channels-cur": {<raw report>}, "channels-prev": {<raw report>},
    "events-cur": {<raw report>},   "events-prev": {<raw report>},
    "landing": {<raw report>},      "cities": {<raw report>},       (optional)
    "realtime": {"active_users": 3, "read_at": "2026-10-02T14:05"}    (optional)
  }
  A raw report is what ga4_run_report returns: {dimensionHeaders, metricHeaders, rows}.
  landing and cities may be trimmed to their top rows; say so in "trimmed": true.

gbp.json: numbers exactly as the Performance panel shows them, labels unchanged.
  {
    "read_at": "2026-10-02",
    "range": "Sep 2026–Sep 2026",
    "metrics": [{"label": "Business Profile interactions", "value": 120,
                 "comparison": "+12% (vs Sep 2025)"}],
    "reviews": {"rating": 4.8, "count": 31},
    "not_measured": ["Website clicks tab rendered blank"]
  }
"""
import argparse
import json
from pathlib import Path


def rows(report, metric_types=None):
    """Raw GA4 report -> list of dicts keyed by header name, numbers parsed."""
    if not report:
        return []
    dims = report.get("dimensionHeaders") or []
    mets = report.get("metricHeaders") or []
    out = []
    for r in report.get("rows") or []:
        d = dict(zip(dims, r.get("dimensions") or []))
        for name, v in zip(mets, r.get("metrics") or []):
            try:
                f = float(v)
                d[name] = int(f) if f.is_integer() else round(f, 4)
            except (TypeError, ValueError):
                d[name] = v
        out.append(d)
    return out


def ga4_section(raw, profile):
    sec = {"method": "mcp", "window": raw.get("window")}
    for key in ("channels-cur", "channels-prev", "events-cur", "events-prev", "landing", "cities"):
        if key in raw:
            sec[key.replace("-", "_")] = rows(raw[key])
    if raw.get("trimmed"):
        sec["trimmed"] = True
    if raw.get("realtime"):
        sec["realtime"] = raw["realtime"]
    return sec


def ga4_kpis(sec, profile):
    k = {}
    ch = {r.get("sessionDefaultChannelGroup"): r for r in sec.get("channels_cur") or []}
    org = ch.get("Organic Search")
    if org:
        k["organic_sessions"] = org.get("sessions")
        if isinstance(org.get("engagementRate"), (int, float)):
            k["organic_engaged_pct"] = round(org["engagementRate"] * 100)
    bots = (profile.get("noise") or {}).get("bot_channels") or []
    if bots:
        k["bot_channel_sessions"] = sum((ch.get(b) or {}).get("sessions") or 0 for b in bots)
    return k


def gbp_kpis(sec):
    k = {}
    rv = sec.get("reviews") or {}
    if isinstance(rv.get("count"), (int, float)):
        k["gbp_reviews"] = rv["count"]
    if isinstance(rv.get("rating"), (int, float)):
        k["gbp_rating"] = rv["rating"]
    return k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--ga4")
    ap.add_argument("--gbp")
    ap.add_argument("--date", help="snapshot date (YYYY-MM-DD); default = newest")
    a = ap.parse_args()
    if not (a.ga4 or a.gbp):
        raise SystemExit("nothing to record: pass --ga4 and/or --gbp")

    pdir = Path(a.profile).expanduser().resolve()
    profile = json.loads((pdir / "profile.json").read_text())
    hist = pdir / "history"
    snaps = sorted(hist.glob("*.json"))
    if not snaps:
        raise SystemExit(f"no snapshots in {hist}; run pull.py first")
    path = hist / f"{a.date}.json" if a.date else snaps[-1]
    if not path.exists():
        raise SystemExit(f"{path} does not exist")
    snap = json.loads(path.read_text())
    snap.setdefault("kpis", {})

    if a.ga4:
        sec = ga4_section(json.loads(Path(a.ga4).read_text()), profile)
        snap["ga4"] = sec
        snap["kpis"].update(ga4_kpis(sec, profile))
    if a.gbp:
        sec = json.loads(Path(a.gbp).read_text())
        snap["gbp"] = sec
        snap["kpis"].update(gbp_kpis(sec))

    path.write_text(json.dumps(snap, indent=1, default=str))
    added = [s for s in ("ga4", "gbp") if getattr(a, s)]
    print(f"recorded {', '.join(added)} into {path.name}; kpis now: "
          + ", ".join(f"{k}={v}" for k, v in snap["kpis"].items()))


if __name__ == "__main__":
    main()
