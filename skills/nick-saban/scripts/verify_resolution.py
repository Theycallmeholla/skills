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
re-runs the check live against the actual repo. The result is tri-state:

  condition_present  -> the problem is still there; reinstated as open
  condition_absent   -> the problem is genuinely gone; allowed to resolve
  unverifiable       -> the check could not be evaluated; kept open, unresolved

The third state is the one that matters most and the one this script originally
got wrong. It used to return "could not verify, not blocking" and let the
finding fall through to resolution — fail-open, in the one script whose job is
to stop false resolutions. A check we could not run is not evidence of a fix.
Fail closed means the FINDING cannot close; it does not mean the audit cannot
finish, so unrelated new findings are still recorded normally.

Prints a summary line at the end: "0 reinstated, 0 unverifiable" is what a
well-behaved pass looks like. Reinstatements mean the detection pass just missed
something real. Unverifiable counts mean the gate is blind in that spot — that
finding now needs a human judgment call or a migrated check, not another pass.
"""

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

MECHANICAL_CHECK_TYPES = {
    "command_exit_zero",
    "file_contains",
    "instruction_surfaces_contain",
    "registered_hook_missing",
}

# Every place an agent picks up standing instructions in a repo. Used by
# instruction_surfaces_contain when a finding doesn't name its own paths.
DEFAULT_INSTRUCTION_SURFACES = [
    "CLAUDE.md",
    ".claude/*.md",
    ".claude/rules/**/*.md",
    ".claude/skills/**/SKILL.md",
    ".claude/agents/*.md",
]

PRESENT = "condition_present"
ABSENT = "condition_absent"
UNVERIFIABLE = "unverifiable"

# Characters that mean a legacy command string wants a shell. We refuse to
# reconstruct those into an argv — the meaning would change — and mark the
# check unverifiable so a human migrates it deliberately.
SHELL_META = set("|&;<>()$`\n*?[]{}~!#\\\"'")


def resolve_argv(check):
    """Return (argv, note). argv is None when the check can't be run safely.

    New records carry `argv` as a list and run with shell=False. Records written
    before that change carry `command` as a string; those are adapted here for
    simple commands only. This adapter is migration scaffolding, not the schema —
    writers should emit `argv`.
    """
    argv = check.get("argv")
    if isinstance(argv, list) and argv and all(isinstance(a, str) for a in argv):
        return argv, None
    if argv is not None:
        return None, "malformed 'argv' — expected a non-empty list of strings"

    legacy = check.get("command")
    if not isinstance(legacy, str) or not legacy.strip():
        return None, "check has neither 'argv' nor a usable legacy 'command'"
    if any(ch in legacy for ch in SHELL_META):
        return None, (f"legacy command {legacy!r} uses shell syntax — "
                      f"cannot be converted to argv safely, migrate it by hand")
    try:
        parts = shlex.split(legacy)
    except ValueError as e:
        return None, f"legacy command {legacy!r} could not be parsed ({e})"
    if not parts:
        return None, f"legacy command {legacy!r} parsed to nothing"
    return parts, "adapted from legacy 'command' field"


def normalize_check(check):
    """Map legacy check shapes onto the current path-aware ones.

    `claude_md_contains` and `settings_contains` hard-coded their target file in
    the type name. They are exactly `file_contains` with a fixed path, so they
    translate losslessly — and translating them here rather than deleting them is
    what keeps audit records written before this change readable. Records must be
    backward-readable before writers emit the new shape; the alternative is that
    every pre-existing check silently becomes 'unknown type' and stops gating.
    """
    if not isinstance(check, dict):
        return None
    ctype = check.get("type")
    if ctype == "claude_md_contains":
        return {"type": "file_contains", "path": "CLAUDE.md", "pattern": check.get("pattern")}
    if ctype == "settings_contains":
        return {"type": "file_contains", "path": ".claude/settings.json", "pattern": check.get("pattern")}
    return check


def normalize_verification(finding):
    """Return the finding's verification block, upgrading legacy records.

    Three shapes exist in the wild:
      1. {"verification": {"mode": "mechanical", "check": {...}}}   — current
      2. {"mechanicalCheck": {...}}                                  — legacy
      3. neither                                                     — legacy

    Shape 3 is the dangerous one. It must NOT become "resolves freely" just
    because no check was recorded — that would let this schema change quietly
    weaken every finding that predates it. It normalizes to judgment mode, which
    requires an explicit resolution claim to close.
    """
    v = finding.get("verification")
    if isinstance(v, dict) and v.get("mode") in ("mechanical", "judgment"):
        if v.get("mode") == "mechanical":
            return {**v, "check": normalize_check(v.get("check"))}
        return v

    legacy = finding.get("mechanicalCheck")
    if isinstance(legacy, dict):
        return {"mode": "mechanical", "check": normalize_check(legacy), "legacy": True}

    return {
        "mode": "judgment",
        "reason": "Legacy finding with no recorded verification method.",
        "legacy": True,
    }


def reinstate_payload(finding, check, outcome, detail):
    """Rebuild a prior finding as a raw finding so merge_pass carries it forward."""
    marker = "REINSTATED" if outcome == PRESENT else "KEPT OPEN, UNVERIFIED"
    return {
        "signal": finding["signal"],
        "detector": finding["detector"],
        "category": finding["category"],
        "rung": finding["rung"],
        "severity": finding["severity"],
        "location": finding["location"],
        "claim": finding["claim"],
        "consequence": finding["consequence"],
        "evidence": f"{finding['evidence']} · {marker} by verify_resolution.py: {detail}",
        "remedy": finding["remedy"],
        "verification": {"mode": "mechanical", "check": check},
        "verificationStatus": outcome,
    }


def write_marker(path, prior_pass, checked):
    """Record that this gate actually ran, for merge_pass to require.

    Without this, the whole gate is optional in practice: skip the script and
    every mechanically-checkable finding resolves on the agent's say-so, which is
    the exact hole the script was written to close.
    """
    with open(path, "w") as fh:
        json.dump({"gate": "verify_resolution", "priorPass": prior_pass, "checked": checked}, fh)


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
    """Return (outcome, detail).

    outcome is one of:
      PRESENT      — the bad condition is still true; the finding must stay open
      ABSENT       — the bad condition is gone; the finding may resolve
      UNVERIFIABLE — this script could not evaluate the check at all

    UNVERIFIABLE is deliberately NOT the same as PRESENT: "we don't know" is not
    "still broken." It is also deliberately not ABSENT — a check we couldn't run
    is not evidence of a fix, and letting it fall through to resolution is the
    exact fail-open hole this script exists to close. Unverifiable keeps the
    finding open and says so; it never silently closes it, and it never aborts
    the pass, since unrelated new findings still deserve to be recorded.
    """
    ctype = check.get("type")
    project_dir = Path(project_dir)

    if ctype == "command_exit_zero":
        argv, note = resolve_argv(check)
        if argv is None:
            return UNVERIFIABLE, note
        printable = " ".join(argv)
        suffix = f" ({note})" if note else ""
        try:
            result = subprocess.run(
                argv, shell=False, cwd=project_dir,
                capture_output=True, text=True,
                timeout=check.get("timeoutSeconds", 120),
            )
        except FileNotFoundError as e:
            return UNVERIFIABLE, f"'{printable}' could not be executed ({e}){suffix}"
        except subprocess.TimeoutExpired:
            return PRESENT, f"'{printable}' still does not complete within the timeout{suffix}"
        if result.returncode == 0:
            return ABSENT, f"'{printable}' now exits 0{suffix}"
        return PRESENT, f"'{printable}' still exits {result.returncode}{suffix}"

    # file_contains — "this specific text is still sitting in THIS specific file."
    # The path matters: for a finding whose remedy is relocation (move a rule out
    # of CLAUDE.md into .claude/rules/), the text existing elsewhere afterwards is
    # the fix working, not the problem persisting.
    if ctype == "file_contains":
        rel = check.get("path")
        pattern = check.get("pattern")
        if not rel or pattern is None:
            return UNVERIFIABLE, "file_contains requires both 'path' and 'pattern'"
        target = project_dir / rel
        text = target.read_text() if target.is_file() else ""
        if pattern in text:
            return PRESENT, f"{rel} still contains: {pattern!r}"
        return ABSENT, f"{rel} no longer contains: {pattern!r}"

    # instruction_surfaces_contain — "this instruction still exists ANYWHERE the
    # agent reads, with nothing executing it." Use for enforcement findings, where
    # moving the sentence between instruction files changes nothing about the fact
    # that no mechanism backs it.
    if ctype == "instruction_surfaces_contain":
        pattern = check.get("pattern")
        globs = check.get("paths") or DEFAULT_INSTRUCTION_SURFACES
        if pattern is None:
            return UNVERIFIABLE, "instruction_surfaces_contain requires 'pattern'"
        hits = []
        for g in globs:
            for path in sorted(project_dir.glob(g)):
                if path.is_file() and pattern in path.read_text():
                    hits.append(str(path.relative_to(project_dir)))
        if hits:
            return PRESENT, f"{pattern!r} still present in: {', '.join(hits)}"
        return ABSENT, f"{pattern!r} no longer present in any instruction surface ({', '.join(globs)})"

    # registered_hook_missing — proves a mechanism is CONNECTED, not that it is
    # correct. A hook file on disk is not a hook that runs: it has to be registered,
    # on the right event, against the right tool matcher. Whether the registered
    # hook actually covers every way the prohibited thing can happen is a different
    # question, and no string match answers it — that's the drill coverage matrix.
    if ctype == "registered_hook_missing":
        settings_rel = check.get("settingsPath", ".claude/settings.json")
        event = check.get("event")
        matcher = check.get("toolMatcher")
        command = check.get("command")
        if not event or not command:
            return UNVERIFIABLE, "registered_hook_missing requires 'event' and 'command'"
        target = project_dir / settings_rel
        if not target.is_file():
            return PRESENT, f"{settings_rel} does not exist — no hook is registered"
        try:
            settings = json.loads(target.read_text())
        except json.JSONDecodeError as e:
            return UNVERIFIABLE, f"{settings_rel} is not valid JSON ({e}) — cannot confirm registration"
        for entry in (settings.get("hooks", {}) or {}).get(event, []) or []:
            if matcher is not None and entry.get("matcher") != matcher:
                continue
            for h in entry.get("hooks", []) or []:
                if command in (h.get("command") or ""):
                    where = f"{event}/{matcher}" if matcher else event
                    return ABSENT, f"{command} is registered on {where} in {settings_rel}"
        where = f"{event} matching {matcher!r}" if matcher else event
        return PRESENT, f"no {where} hook in {settings_rel} runs {command}"

    return UNVERIFIABLE, f"unknown check type {ctype!r} — cannot be evaluated by this script"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project-dir", required=True)
    ap.add_argument("--raw-findings", required=True)
    args = ap.parse_args()

    marker_path = Path(args.raw_findings).with_suffix(".verified.json")

    prior = latest_audit(args.project_dir)
    if not prior:
        print("no prior audit record — nothing to spot-check on a first pass.")
        write_marker(marker_path, prior_pass=None, checked=0)
        return

    raw_findings = load_json(args.raw_findings, default=[])
    raw_signals = {rf["signal"] for rf in raw_findings}

    reinstated = []
    unverifiable = []
    judgment_pending = []

    for f in prior.get("findings", []):
        if f.get("status") != "open":
            continue
        if f["signal"] in raw_signals:
            continue  # agent already re-raised it this pass, nothing to gate

        verification = normalize_verification(f)

        # Judgment-mode findings aren't checkable here by construction. They are
        # not free to resolve either — merge_pass requires an explicit resolution
        # claim for those. Listed here so the operator sees what's pending.
        if verification["mode"] == "judgment":
            judgment_pending.append((f["id"], f["signal"]))
            continue

        check = verification.get("check")
        if not check:
            unverifiable.append((f["id"], "mechanical mode with no usable check recorded"))
            raw_findings.append(reinstate_payload(f, check, UNVERIFIABLE,
                                                  "mechanical mode with no usable check recorded"))
            continue

        outcome, detail = evaluate_check(check, args.project_dir)

        if outcome == ABSENT:
            continue  # the condition is genuinely gone — let merge_pass resolve it

        # PRESENT and UNVERIFIABLE both keep the finding open. They are reported
        # separately because they mean different things: one is evidence the
        # problem persists, the other is absence of evidence either way.
        if outcome == PRESENT:
            reinstated.append((f["id"], detail))
        else:
            unverifiable.append((f["id"], detail))

        raw_findings.append(reinstate_payload(f, check, outcome, detail))

    with open(args.raw_findings, "w") as fh:
        json.dump(raw_findings, fh, indent=2)

    write_marker(marker_path, prior_pass=prior.get("pass"),
                 checked=len(prior.get("findings", [])))

    if reinstated:
        print(f"⚠ {len(reinstated)} finding(s) reinstated — the agent's raw findings for this pass "
              f"omitted them, but their mechanical check says the underlying condition is still true:")
        for fid, detail in reinstated:
            print(f"  {fid}: {detail}")
    if unverifiable:
        print(f"⚠ {len(unverifiable)} finding(s) kept open because their check could not be evaluated. "
              f"This is not evidence the problem persists — it is absence of evidence either way, "
              f"and a finding never closes on that:")
        for fid, detail in unverifiable:
            print(f"  {fid}: {detail}")

    if judgment_pending:
        print(f"{len(judgment_pending)} judgment-mode finding(s) are open and absent from this pass. "
              f"They cannot be checked mechanically and will NOT resolve without an explicit "
              f"resolution claim passed to merge_pass.py --resolutions:")
        for fid, sig in judgment_pending:
            print(f"  {fid}: {sig}")

    print(f"\n{len(reinstated)} reinstated, {len(unverifiable)} unverifiable, "
          f"{len(judgment_pending)} awaiting judgment claim, "
          f"{len(prior.get('findings', []))} prior findings checked.")

    if reinstated or unverifiable:
        print("\nReport these counts to the user in this pass's summary — a reinstatement means "
              "the detection pass missed something; an unverifiable check means the gate is blind "
              "there and the finding needs a judgment call or a migrated check.")


if __name__ == "__main__":
    main()
