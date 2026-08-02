#!/usr/bin/env python3
"""
merge_pass.py — assemble a new audits/NNN.json from raw findings.

Implements the one part of this skill too risky to leave to a hand-authored
JSON file on every pass: signal-based ID inheritance, resolved-detection, and
score computation. See references/state.md for the full explanation of why.

Usage:
    python3 merge_pass.py \\
        --project-dir /path/to/project \\
        --raw-findings /path/to/raw_findings.json \\
        --categories-scanned context,mechanism,enforcement,verification,permissions,bounds \\
        --verification-surface /path/to/verification_surface.json \\
        [--pass-number N]   # auto-detected from audits/ if omitted

raw_findings.json is a JSON array of objects, each with:
    signal, detector, category, rung, severity, location, claim,
    consequence, evidence, remedy
(no id / status / firstSeen / resolvedIn / resolvedBy — those are computed)

verification_surface.json is the verificationSurface object (see state.md),
or omit --verification-surface to write an empty {}.

Writes .claude/nick-saban/audits/<NNN>.json (zero-padded to 3 digits) and
prints the path. Does NOT touch registry.json — run build_registry.py after.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SEVERITY_WEIGHT = {"high": 15, "medium": 6, "low": 2}
CATEGORIES = ["context", "mechanism", "enforcement", "verification", "permissions", "bounds"]
VALID_RUNGS = {"prose", "scoped-rule", "skill", "hook", "permission", "ci", "test"}
VALID_SEVERITIES = set(SEVERITY_WEIGHT)


def load_json(path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    with open(p) as f:
        return json.load(f)


def state_dir(project_dir):
    return Path(project_dir) / ".claude" / "nick-saban"


def audits_dir(project_dir):
    d = state_dir(project_dir) / "audits"
    d.mkdir(parents=True, exist_ok=True)
    return d


def latest_audit(project_dir):
    """Return (pass_number, record_dict) for the highest-numbered audit, or (0, None)."""
    d = audits_dir(project_dir)
    files = sorted(d.glob("[0-9][0-9][0-9].json"))
    if not files:
        return 0, None
    latest = files[-1]
    with open(latest) as f:
        record = json.load(f)
    return int(latest.stem), record


def validate_raw_finding(rf, index):
    required = ["signal", "detector", "category", "rung", "severity", "location",
                "claim", "consequence", "evidence", "remedy"]
    missing = [k for k in required if k not in rf or rf[k] in (None, "")]
    if missing:
        raise ValueError(f"raw finding #{index} missing required field(s): {missing}")
    if rf["category"] not in CATEGORIES:
        raise ValueError(f"raw finding #{index} has unknown category '{rf['category']}' (must be one of {CATEGORIES})")
    if rf["rung"] not in VALID_RUNGS:
        raise ValueError(f"raw finding #{index} has unknown rung '{rf['rung']}' (must be one of {sorted(VALID_RUNGS)})")
    if rf["severity"] not in VALID_SEVERITIES:
        raise ValueError(f"raw finding #{index} has unknown severity '{rf['severity']}' (must be one of {sorted(VALID_SEVERITIES)})")
    if not re.match(r"^[a-z0-9-]+:[a-z0-9-]+$", rf["signal"]):
        raise ValueError(
            f"raw finding #{index} signal '{rf['signal']}' doesn't match "
            f"'<detector-id>:<subject-slug>' (lowercase, hyphens only)"
        )


def next_id(prior_findings, prefix="HN-"):
    max_n = 0
    for f in prior_findings:
        m = re.match(rf"^{re.escape(prefix)}(\d+)$", f.get("id", ""))
        if m:
            max_n = max(max_n, int(m.group(1)))
    return max_n + 1


def merge(prior_record, raw_findings, waived, categories_scanned, this_pass):
    prior_findings = (prior_record or {}).get("findings", [])
    prior_by_signal = {f["signal"]: f for f in prior_findings}
    seen_signals = set()

    merged = []
    next_available_id = next_id(prior_findings)

    # 1-2: new pass findings inherit id/firstSeen if signal matches, else get a fresh id
    for rf in raw_findings:
        sig = rf["signal"]
        seen_signals.add(sig)
        prior = prior_by_signal.get(sig)

        if prior and prior["signal"] not in waived:
            finding_id = prior["id"]
            first_seen = prior["firstSeen"]
        elif prior and prior["signal"] in waived:
            # was previously seen (even if waived) — keep continuity of id/firstSeen
            finding_id = prior["id"]
            first_seen = prior["firstSeen"]
        else:
            finding_id = f"HN-{next_available_id:03d}"
            next_available_id += 1
            first_seen = this_pass

        status = "waived" if sig in waived else "open"

        merged.append({
            "id": finding_id,
            "signal": sig,
            "detector": rf["detector"],
            "category": rf["category"],
            "rung": rf["rung"],
            "severity": rf["severity"],
            "location": rf["location"],
            "claim": rf["claim"],
            "consequence": rf["consequence"],
            "evidence": rf["evidence"],
            "remedy": rf["remedy"],
            "mechanicalCheck": rf.get("mechanicalCheck"),
            "status": status,
            "firstSeen": first_seen,
            "resolvedIn": None,
            "resolvedBy": None,
        })

    # 3: prior OPEN findings whose signal didn't fire this pass, in a category we
    #    actually scanned, and that aren't already carried forward above -> resolved
    for f in prior_findings:
        if f["signal"] in seen_signals:
            continue
        if f["status"] != "open":
            # already resolved/waived previously; carry forward unchanged unless waived list changed
            if f["signal"] in waived and f["status"] != "waived":
                f = {**f, "status": "waived"}
            elif f["signal"] not in waived and f["status"] == "waived":
                # a decline was revoked — reopen it so it gets re-detected next pass,
                # but since it didn't fire THIS pass either, treat as resolved is wrong;
                # safest is to reopen as open with a note, since we can't re-run detection here.
                f = {**f, "status": "open"}
            merged.append(f)
            continue
        if f["category"] not in categories_scanned:
            # not scanned this pass -- leave completely untouched, still open
            merged.append(f)
            continue
        # genuinely resolved
        merged.append({
            **f,
            "status": "resolved",
            "resolvedIn": this_pass,
            "resolvedBy": "signal no longer detected as of this pass",
        })

    return merged


def score(findings):
    per_category = {}
    for cat in CATEGORIES:
        penalty = sum(
            SEVERITY_WEIGHT[f["severity"]]
            for f in findings
            if f["category"] == cat and f["status"] == "open"
        )
        per_category[cat] = max(0, 100 - penalty)
    overall = round(sum(per_category.values()) / len(CATEGORIES))
    return {**per_category, "overall": overall}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project-dir", required=True)
    ap.add_argument("--raw-findings", required=True, help="Path to a JSON array of raw finding objects")
    ap.add_argument("--categories-scanned", required=True, help="Comma-separated list, e.g. context,mechanism,enforcement")
    ap.add_argument("--verification-surface", default=None, help="Path to a verificationSurface JSON object")
    ap.add_argument("--pass-number", type=int, default=None, help="Override auto-detected pass number")
    args = ap.parse_args()

    project_dir = args.project_dir
    raw_findings = load_json(args.raw_findings, default=[])
    for i, rf in enumerate(raw_findings):
        validate_raw_finding(rf, i)

    categories_scanned = [c.strip() for c in args.categories_scanned.split(",") if c.strip()]
    for c in categories_scanned:
        if c not in CATEGORIES:
            print(f"error: unknown category '{c}' in --categories-scanned", file=sys.stderr)
            sys.exit(1)

    waived_data = load_json(state_dir(project_dir) / "waived.json", default={"signals": {}})
    waived = set(waived_data.get("signals", {}).keys())

    prior_pass, prior_record = latest_audit(project_dir)
    this_pass = args.pass_number if args.pass_number is not None else prior_pass + 1

    verification_surface = load_json(args.verification_surface, default={}) if args.verification_surface else {}

    findings = merge(prior_record, raw_findings, waived, categories_scanned, this_pass)
    computed_score = score(findings)

    record = {
        "schema": 1,
        "pass": this_pass,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "categoriesScanned": categories_scanned,
        "verificationSurface": verification_surface,
        "score": computed_score,
        "findings": findings,
    }

    out_dir = audits_dir(project_dir)
    out_path = out_dir / f"{this_pass:03d}.json"
    if out_path.exists():
        print(f"error: {out_path} already exists — refusing to overwrite an audit record. "
              f"Pass a different --pass-number if this is intentional.", file=sys.stderr)
        sys.exit(1)

    with open(out_path, "w") as f:
        json.dump(record, f, indent=2)
        f.write("\n")

    open_high = sum(1 for f in findings if f["status"] == "open" and f["severity"] == "high")
    print(f"wrote {out_path}")
    print(f"overall score: {computed_score['overall']}  |  open high-severity: {open_high}")


if __name__ == "__main__":
    main()
