#!/usr/bin/env python3
"""
verify_resolution.py — independent spot-check gate, run BEFORE merge_pass.py.

Why this exists: an adversarial test of this skill proved that merge_pass.py's
guarantees (no ID reuse, no direct status writes, formula-driven scoring) all
rest on one unverified assumption — that the agent's raw-findings list for
this pass is honest. Nothing stopped a finding from silently "resolving"
just because the agent forgot to re-raise it, even though the underlying
problem was untouched. That's the exact failure mode this skill exists to
catch, relocated one level up, into the tool itself.

This script closes that gap for the subset of findings that are objectively
checkable without human judgment — a specific command's exit code, a specific
string still present in CLAUDE.md or settings.json. It cannot and does not try
to replace judgment-based detection (bloat, misplaced instructions, whether an
MCP server is "unvetted") — those still depend on the agent actually looking,
honestly, same as always. What this adds is a trip-wire for the narrower,
provable case: "the finding's own recorded mechanical check says the bad
condition is still true, but this pass's raw findings list doesn't mention it."

Usage:
    python3 verify_resolution.py \\
        --project-dir /path/to/project \\
        --raw-findings /path/to/raw_findings.json

Reads the latest audits/NNN.json for prior OPEN findings that carry a
mechanicalCheck. For each one whose signal is absent from raw_findings.json,
re-runs the check live against the actual repo. If the check says the
condition still holds, the finding is appended back into raw_findings.json
(same file, in place) and a warning is printed. This means merge_pass.py can
never resolve a checkable finding whose real-world condition didn't change,
regardless of what the agent's draft said.

Prints a summary line at the end: "0 reinstated" is what a well-behaved pass
looks like. Any number above zero means this gate just caught a pass that
would otherwise have produced a false resolution — treat that as a serious
signal about the detection pass that just ran, not a routine event.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

MECHANICAL_CHECK_TYPES = {"command_exit_zero", "claude_md_contains", "settings_contains"}


def load_json(path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    with open(p) as f:
        return json.load(f)


def latest_audit(project_dir):
    d = Path(project_dir) / ".claude" / "nick-saban" / "audits"
    if not d.exists():
        return None
    files = sorted(d.glob("[0-9][0-9][0-9].json"))
    if not files:
        return None
    with open(files[-1]) as f:
        return json.load(f)


def evaluate_check(check, project_dir):
    """Return (still_broken: bool, detail: str)."""
    ctype = check.get("type")
    project_dir = Path(project_dir)

    if ctype == "command_exit_zero":
        command = check["command"]
        try:
            result = subprocess.run(
                command, shell=True, cwd=project_dir,
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                return False, f"'{command}' now exits 0"
            return True, f"'{command}' still exits {result.returncode}"
        except Exception as e:
            return True, f"'{command}' still fails to run cleanly ({e})"

    if ctype == "claude_md_contains":
        pattern = check["pattern"]
        target = project_dir / "CLAUDE.md"
        text = target.read_text() if target.exists() else ""
        if pattern in text:
            return True, f"CLAUDE.md still contains: {pattern!r}"
        return False, f"CLAUDE.md no longer contains: {pattern!r}"

    if ctype == "settings_contains":
        pattern = check["pattern"]
        target = project_dir / ".claude" / "settings.json"
        text = target.read_text() if target.exists() else ""
        if pattern in text:
            return True, f"settings.json still contains: {pattern!r}"
        return False, f"settings.json no longer contains: {pattern!r}"

    # Unknown check type: don't block the pass on something this script
    # can't evaluate, but say so loudly rather than silently passing.
    return None, f"unknown mechanicalCheck type '{ctype}' — could not verify, not blocking"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project-dir", required=True)
    ap.add_argument("--raw-findings", required=True)
    args = ap.parse_args()

    prior = latest_audit(args.project_dir)
    if not prior:
        print("no prior audit record — nothing to spot-check on a first pass.")
        return

    raw_findings = load_json(args.raw_findings, default=[])
    raw_signals = {rf["signal"] for rf in raw_findings}

    reinstated = []
    unverifiable = []

    for f in prior.get("findings", []):
        if f.get("status") != "open":
            continue
        check = f.get("mechanicalCheck")
        if not check:
            continue
        if f["signal"] in raw_signals:
            continue  # agent already re-raised it this pass, nothing to gate

        still_broken, detail = evaluate_check(check, args.project_dir)

        if still_broken is None:
            unverifiable.append((f["id"], detail))
            continue

        if still_broken:
            reinstated.append((f["id"], detail))
            raw_findings.append({
                "signal": f["signal"],
                "detector": f["detector"],
                "category": f["category"],
                "rung": f["rung"],
                "severity": f["severity"],
                "location": f["location"],
                "claim": f["claim"],
                "consequence": f["consequence"],
                "evidence": f"{f['evidence']} · REINSTATED by verify_resolution.py: {detail}",
                "remedy": f["remedy"],
                "mechanicalCheck": check,
            })

    with open(args.raw_findings, "w") as fh:
        json.dump(raw_findings, fh, indent=2)

    if reinstated:
        print(f"⚠ {len(reinstated)} finding(s) reinstated — the agent's raw findings for this pass "
              f"omitted them, but their mechanical check says the underlying condition is still true:")
        for fid, detail in reinstated:
            print(f"  {fid}: {detail}")
    if unverifiable:
        print(f"({len(unverifiable)} finding(s) had a mechanicalCheck this script doesn't know how to run — not blocked, not verified)")
        for fid, detail in unverifiable:
            print(f"  {fid}: {detail}")

    print(f"\n{len(reinstated)} reinstated, {len(prior.get('findings', []))} prior findings checked.")


if __name__ == "__main__":
    main()
