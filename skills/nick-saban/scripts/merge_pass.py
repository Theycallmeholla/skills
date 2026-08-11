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
    validate_verification(rf, index)


def validate_verification(rf, index):
    """Every finding must declare HOW its resolution will be verified.

    The requirement is not "every finding needs a mechanical check" — most
    findings in this system are judgment calls by design, and forcing a pattern
    match onto one produces a check that rubber-stamps whatever string happens to
    match. The requirement is that the choice is explicit. A missing verification
    block used to mean "resolves whenever a later pass forgets to mention it,"
    which is silent absence rather than a decision.
    """
    v = rf.get("verification")

    if v is None and isinstance(rf.get("mechanicalCheck"), dict):
        # Legacy raw finding — accept and upgrade in place rather than rejecting.
        v = {"mode": "mechanical", "check": rf["mechanicalCheck"], "legacy": True}
        rf["verification"] = v

    if not isinstance(v, dict) or v.get("mode") not in ("mechanical", "judgment"):
        raise ValueError(
            f"raw finding #{index} ({rf['signal']}) must declare "
            f"verification.mode as 'mechanical' or 'judgment'. "
            f"Mechanical needs a 'check'; judgment needs a 'reason' saying what "
            f"human judgment closing it depends on."
        )
    if v["mode"] == "mechanical" and not isinstance(v.get("check"), dict):
        raise ValueError(
            f"raw finding #{index} ({rf['signal']}) declares verification.mode "
            f"'mechanical' but carries no 'check' object"
        )
    if v["mode"] == "judgment" and not (v.get("reason") or "").strip():
        raise ValueError(
            f"raw finding #{index} ({rf['signal']}) declares verification.mode "
            f"'judgment' but gives no 'reason' — name what the judgment actually is"
        )


def next_id(prior_findings, prefix="HN-"):
    max_n = 0
    for f in prior_findings:
        m = re.match(rf"^{re.escape(prefix)}(\d+)$", f.get("id", ""))
        if m:
            max_n = max(max_n, int(m.group(1)))
    return max_n + 1


def normalize_verification(finding):
    """Upgrade a stored finding's verification block. Mirrors verify_resolution.py.

    A legacy finding with no recorded check normalizes to judgment mode, NOT to
    "freely resolvable." Otherwise introducing this schema would quietly weaken
    every finding written before it — a migration that disarms the protection it
    was meant to strengthen.
    """
    v = finding.get("verification")
    if isinstance(v, dict) and v.get("mode") in ("mechanical", "judgment"):
        return v
    if isinstance(finding.get("mechanicalCheck"), dict):
        return {"mode": "mechanical", "check": finding["mechanicalCheck"], "legacy": True}
    return {"mode": "judgment",
            "reason": "Legacy finding with no recorded verification method.",
            "legacy": True}


def merge(prior_record, raw_findings, waived, categories_scanned, this_pass,
          resolutions=None, warnings=None):
    prior_findings = (prior_record or {}).get("findings", [])
    prior_by_signal = {f["signal"]: f for f in prior_findings}
    seen_signals = set()
    resolutions = resolutions or {}
    warnings = warnings if warnings is not None else []

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
            "verification": rf.get("verification"),
            # Set by verify_resolution.py when it re-checked this finding:
            # condition_present | unverifiable. Absent means this pass detected
            # the finding directly rather than reinstating it.
            "verificationStatus": rf.get("verificationStatus"),
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

        verification = normalize_verification(f)

        # Mechanical findings: verify_resolution.py already re-ran the check and
        # would have pushed this signal back into raw_findings if the condition
        # were still present or unevaluable. Reaching here means the check said
        # the condition is genuinely gone.
        if verification["mode"] == "mechanical":
            merged.append({
                **f,
                "status": "resolved",
                "resolvedIn": this_pass,
                "resolvedBy": "mechanical check confirms the condition is gone",
            })
            continue

        # Judgment findings: nothing re-ran, so silence is not evidence. Closing
        # one requires this pass to say so explicitly, with a basis and evidence.
        # Without that, "the agent forgot to re-raise it" and "the agent verified
        # it was fixed" are indistinguishable — which is the original bug.
        claim = resolutions.get(f["signal"])
        if claim:
            merged.append({
                **f,
                "status": "resolved",
                "resolvedIn": this_pass,
                "resolvedBy": f"judgment: {claim['basis']}",
                "resolutionEvidence": claim["evidence"],
            })
            continue

        warnings.append(
            f"{f['id']} ({f['signal']}) is judgment-verified, its category WAS scanned, "
            f"but this pass neither re-raised it nor submitted a resolution claim. "
            f"Kept OPEN — closing it by silent omission is the failure mode this gate exists for."
        )
        merged.append({**f, "omittedWithoutClaim": this_pass})

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
    ap.add_argument("--resolutions", default=None,
                    help="Path to a JSON array of {signal, basis, evidence} objects: explicit "
                         "claims that a judgment-verified finding is fixed. Required to close "
                         "any judgment-mode finding — those never close by silent omission.")
    ap.add_argument("--skip-verify-gate", action="store_true",
                    help="Proceed without verify_resolution.py having run. Only for a first pass "
                         "or a genuinely script-less environment; it disables the false-resolution "
                         "guard, so say so in the summary if you use it.")
    ap.add_argument("--pass-type", choices=["detection", "scaffold"], default="detection",
                    help="'scaffold' is kickoff's baseline record: structure only, no detection ran. "
                         "It scores null/UNASSESSED rather than 100, because an empty findings list "
                         "means nothing was looked for, not that nothing is wrong.")
    args = ap.parse_args()

    project_dir = args.project_dir
    raw_findings = load_json(args.raw_findings, default=[])
    for i, rf in enumerate(raw_findings):
        try:
            validate_raw_finding(rf, i)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)

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

    # The verify_resolution gate is only a guarantee if it actually ran. Skipping
    # it silently would let every mechanically-checkable finding resolve on the
    # agent's say-so — the exact assumption that gate exists to stop trusting.
    marker = Path(args.raw_findings).with_suffix(".verified.json")
    if prior_record and args.pass_type == "detection" and not marker.exists() and not args.skip_verify_gate:
        print(f"error: verify_resolution.py has not run against {args.raw_findings} "
              f"(no {marker.name}). Run it first, or pass --skip-verify-gate and say "
              f"plainly in your summary that the false-resolution guard was bypassed.",
              file=sys.stderr)
        sys.exit(1)

    resolutions_list = load_json(args.resolutions, default=[]) if args.resolutions else []
    resolutions = {}
    for i, r in enumerate(resolutions_list):
        for k in ("signal", "basis", "evidence"):
            if not (r.get(k) or "").strip():
                print(f"error: resolution claim #{i} missing '{k}'. A claim needs the signal, "
                      f"the basis for closing it, and evidence someone can check in ten seconds.",
                      file=sys.stderr)
                sys.exit(1)
        resolutions[r["signal"]] = r

    warnings = []
    findings = merge(prior_record, raw_findings, waived, categories_scanned, this_pass,
                     resolutions=resolutions, warnings=warnings)

    if args.pass_type == "scaffold":
        # A scaffold pass looked for nothing, so it scores nothing. Emitting 100
        # here would mean "perfect" and "unexamined" share a number, and every
        # consumer downstream — registry, scouting-report delta, the user — would
        # have to be told that 100 actually means its opposite.
        computed_score = None
        status = "unassessed"
    else:
        computed_score = score(findings)
        status = "assessed"

    record = {
        "schema": 1,
        "pass": this_pass,
        "passType": args.pass_type,
        "status": status,
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

    if warnings:
        print(f"\n⚠ {len(warnings)} finding(s) stayed open for lack of an explicit resolution claim:")
        for w in warnings:
            print(f"  {w}")
        print("Either re-raise them in your raw findings, or submit a claim via --resolutions "
              "with the basis and evidence for closing each one.\n")

    mech = sum(1 for f in findings
               if normalize_verification(f)["mode"] == "mechanical" and f["status"] == "open")
    judg = sum(1 for f in findings
               if normalize_verification(f)["mode"] == "judgment" and f["status"] == "open")
    if mech or judg:
        print(f"verification coverage of open findings: {mech} mechanical, {judg} judgment")

    if computed_score is None:
        print("overall score: UNASSESSED (scaffold pass — no detection has run yet)")
    else:
        print(f"overall score: {computed_score['overall']}  |  open high-severity: {open_high}")


if __name__ == "__main__":
    main()
