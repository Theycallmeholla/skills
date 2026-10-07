#!/usr/bin/env python3
"""
test_guard_matrix.py — test a whole permission PACKAGE against what is actually
installed, and report what that does and does not prove.

Why this exists, and why it tests wiring rather than files: a guard's author
testing their own examples proves only that the author was consistent. The
sharper failure is one level down —

    guard-data.sh passes 20/20
    settings.json never calls guard-data.sh
    package reported green

A hook file that is executable, correct, and unregistered enforces nothing. So
every hook mechanism here is verified as REGISTERED first (right event, right
matcher, command pointing at the expected file) and is then invoked EXACTLY as
settings.json invokes it. A passing hook the agent never calls fails the package.

A permission package is more than one hook: several hooks, settings.json deny
rules, MCP/alternate-tool restrictions, override configuration. This runs every
mechanism in a manifest and returns one package result. No single mechanism's
result is ever reported as the package's.

What a green package proves and what it does not:

    PROVES      the enumerated command families behave as specified, against the
                mechanisms as they are currently wired.
    DOES NOT    prove the protected resources are protected. A hook receives
    PROVE       command text; variables, symlinks, interpreters, custom scripts,
                command substitution and indirect execution are not resolvable
                from text, and tools that never reach the hook are not seen at
                all. Both halves are printed, always.

Manifest format:

    {
      "package": "permissions",
      "strict": true,
      "settings": ".claude/settings.json",
      "mechanisms": [
        {
          "id": "guard-data",
          "type": "hook",
          "enforcementLayer": "hook",
          "registration": {
            "event": "PreToolUse",
            "matcher": "Bash",
            "command": ".claude/hooks/guard-data.sh"
          },
          "supportedFamilies": ["rm", "mv", "find -delete"],
          "uncoveredSurfaces": ["python -c and any interpreter",
                                "mcp__filesystem__* (never reaches a Bash hook)"],
          "cases": [
            {"command": "rm -rf data", "expect": "block", "why": "direct"},
            {"command": "rm -rf ../data", "cwd": "sub", "expect": "block",
             "why": "relative escape from a subdirectory"},
            {"command": "sqlite3 data/x.db .tables", "expect": "allow", "why": "read-only"}
          ]
        },
        {
          "id": "deny-secrets",
          "type": "settings_rule",
          "enforcementLayer": "tool-deny",
          "mode": "deny",
          "rules": ["Read(./.env)", "Edit(./.env)"],
          "supportedFamilies": ["Read/Edit of .env"],
          "uncoveredSurfaces": ["a shell command that cats .env"]
        },
        {
          "id": "deny-mcp-shell",
          "type": "tool_denied",
          "enforcementLayer": "tool-deny",
          "tools": ["mcp__desktop-commander__execute_command"],
          "supportedFamilies": ["the named MCP tools"],
          "uncoveredSurfaces": ["any MCP server added later and not denied"]
        }
      ]
    }

Hook decision protocol (nothing else counts as a block):
    exit 2                                          -> block
    exit 0, empty stdout                            -> allow
    exit 0, JSON permissionDecision deny|ask        -> block
    exit 0, JSON permissionDecision allow           -> allow
    exit 0, JSON legacy {"decision": "block"}       -> block
    anything else (exit 1, non-JSON stdout, crash)  -> UNVERIFIABLE, fails

Keyword sniffing of stdout is deliberately NOT used: "No deny rule matched.
Command allowed." contains the word "deny" and would score as a block.

Usage:
    python3 test_guard_matrix.py --project-dir /path/to/repo --manifest package.json
    python3 test_guard_matrix.py --project-dir . --manifest package.json --json
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

BLOCK, ALLOW, UNVERIFIABLE = "block", "allow", "unverifiable"


# --------------------------------------------------------------------------
# registration
# --------------------------------------------------------------------------

def find_registration(settings, reg):
    """Locate the registered hook entry. Return (registered_command, detail).

    registered_command is None when the mechanism is not wired — which is a
    package failure regardless of how well the script itself behaves.
    """
    event = reg.get("event")
    matcher = reg.get("matcher")
    expected = reg.get("command")
    if not event or not expected:
        return None, "registration needs both 'event' and 'command'"

    entries = (settings.get("hooks", {}) or {}).get(event) or []
    if not entries:
        return None, f"no {event} hooks registered at all"

    matcher_seen = []
    for entry in entries:
        entry_matcher = entry.get("matcher")
        matcher_seen.append(repr(entry_matcher))
        if matcher is not None and entry_matcher != matcher:
            continue
        for h in entry.get("hooks", []) or []:
            cmd = h.get("command") or ""
            if expected in cmd:
                return cmd, f"registered on {event}/{entry_matcher}"

    return None, (f"no {event} hook with matcher {matcher!r} runs {expected} "
                  f"(matchers present: {', '.join(matcher_seen) or 'none'})")


# --------------------------------------------------------------------------
# execution
# --------------------------------------------------------------------------

def run_case(registered_command, project_dir, case, event, timeout=20):
    """Invoke the hook exactly as registered. Return (outcome, detail)."""
    cwd = project_dir / case.get("cwd", ".")
    if not cwd.is_dir():
        return UNVERIFIABLE, f"case cwd {case.get('cwd')!r} does not exist"

    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir), **(case.get("env") or {})}
    payload = json.dumps({
        "hook_event_name": event,
        "tool_name": case.get("tool", "Bash"),
        "tool_input": {"command": case["command"]},
        "cwd": str(cwd),
    })

    # shell=True is correct HERE and only here: the value comes from
    # settings.json's own hook registration, which Claude Code itself runs
    # through a shell. Splitting it into argv would test something other than
    # what actually executes, which is the entire point of this script.
    try:
        result = subprocess.run(
            registered_command, shell=True, cwd=cwd, env=env,
            input=payload, capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return UNVERIFIABLE, f"hook did not finish within {timeout}s"
    except OSError as e:
        return UNVERIFIABLE, f"hook could not be executed ({e})"

    return interpret_decision(result)


def interpret_decision(result):
    """Map a hook's exit code and stdout onto block/allow/unverifiable."""
    if result.returncode == 2:
        return BLOCK, "exit 2"
    if result.returncode not in (0, 2):
        # exit 1 is a non-blocking error in the hook protocol: the tool call
        # proceeds. A guard that errors out is not a guard that blocked, and
        # calling it "allow" would hide a broken hook, so it is neither.
        return UNVERIFIABLE, f"exit {result.returncode} (non-blocking error, not a decision)"

    out = (result.stdout or "").strip()
    if not out:
        return ALLOW, "exit 0, no decision emitted"

    try:
        decision = json.loads(out)
    except json.JSONDecodeError:
        return UNVERIFIABLE, "exit 0 with non-JSON stdout — no parseable decision"

    if not isinstance(decision, dict):
        return UNVERIFIABLE, "exit 0 with JSON that is not an object"

    specific = decision.get("hookSpecificOutput") or {}
    pd = specific.get("permissionDecision")
    if pd in ("deny", "ask"):
        return BLOCK, f"permissionDecision: {pd}"
    if pd == "allow":
        return ALLOW, "permissionDecision: allow"

    legacy = decision.get("decision")
    if legacy == "block":
        return BLOCK, "legacy decision: block"
    if legacy in ("approve", "allow"):
        return ALLOW, f"legacy decision: {legacy}"

    return UNVERIFIABLE, "exit 0 with JSON carrying no recognised decision field"


# --------------------------------------------------------------------------
# mechanism types
# --------------------------------------------------------------------------

def check_hook(mech, settings, project_dir):
    reg = mech.get("registration") or {}
    registered_command, detail = find_registration(settings, reg)

    if registered_command is None:
        return {"id": mech["id"], "type": "hook", "wired": False, "wiring": detail,
                "cases": [], "failed": len(mech.get("cases", [])) or 1,
                "total": len(mech.get("cases", [])) or 1}

    expected_file = project_dir / reg["command"]
    if not expected_file.exists():
        return {"id": mech["id"], "type": "hook", "wired": False,
                "wiring": f"registered, but {reg['command']} does not exist",
                "cases": [], "failed": 1, "total": 1}
    if not os.access(expected_file, os.X_OK):
        return {"id": mech["id"], "type": "hook", "wired": False,
                "wiring": f"registered, but {reg['command']} is not executable",
                "cases": [], "failed": 1, "total": 1}

    results, failed = [], 0
    for case in mech.get("cases", []):
        outcome, why = run_case(registered_command, project_dir, case, reg["event"])
        ok = outcome == case["expect"]
        if not ok:
            failed += 1
        results.append({**case, "actual": outcome, "ok": ok, "detail": why})

    return {"id": mech["id"], "type": "hook", "wired": True,
            "wiring": f"{detail} -> {registered_command}",
            "cases": results, "failed": failed, "total": len(results)}


def check_settings_rule(mech, settings, project_dir):
    mode = mech.get("mode", "deny")
    present = set((settings.get("permissions", {}) or {}).get(mode, []) or [])
    missing = [r for r in mech.get("rules", []) if r not in present]
    return {"id": mech["id"], "type": "settings_rule", "wired": not missing,
            "wiring": (f"all {len(mech.get('rules', []))} {mode} rule(s) present"
                       if not missing else f"missing from permissions.{mode}: {missing}"),
            "cases": [], "failed": len(missing), "total": max(1, len(mech.get("rules", [])))}


def check_tool_denied(mech, settings, project_dir):
    deny = set((settings.get("permissions", {}) or {}).get("deny", []) or [])
    missing = []
    for tool in mech.get("tools", []):
        if not any(tool in rule for rule in deny):
            missing.append(tool)
    return {"id": mech["id"], "type": "tool_denied", "wired": not missing,
            "wiring": ("all named tools denied" if not missing
                       else f"NOT denied, reachable: {missing}"),
            "cases": [], "failed": len(missing), "total": max(1, len(mech.get("tools", [])))}


CHECKERS = {"hook": check_hook, "settings_rule": check_settings_rule,
            "tool_denied": check_tool_denied}


# --------------------------------------------------------------------------
# strict validation
# --------------------------------------------------------------------------

def strict_violations(manifest):
    """Coverage claims are author-written. In strict mode they must at least exist.

    This does not make the claims true — nothing here can. It makes their ABSENCE
    impossible, so a package can't come back green while quietly declaring nothing
    about what it fails to cover.
    """
    problems = []
    for m in manifest.get("mechanisms", []):
        mid = m.get("id", "<unnamed>")
        if not m.get("enforcementLayer"):
            problems.append(f"{mid}: no enforcementLayer declared")
        if not m.get("supportedFamilies"):
            problems.append(f"{mid}: no supportedFamilies declared")
        if "uncoveredSurfaces" not in m:
            problems.append(f"{mid}: no uncoveredSurfaces key — declare the residuals, "
                            f"or declare 'none' with a justification")
        else:
            unc = m["uncoveredSurfaces"]
            if not unc:
                if not (m.get("uncoveredJustification") or "").strip():
                    problems.append(f"{mid}: uncoveredSurfaces is empty and no "
                                    f"uncoveredJustification explains why nothing is uncovered")
        if m.get("type") == "hook" and not m.get("cases"):
            problems.append(f"{mid}: hook mechanism with no test cases")
    return problems


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project-dir", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    project_dir = Path(args.project_dir).resolve()
    manifest = json.loads(Path(args.manifest).read_text())
    strict = manifest.get("strict", True)

    settings_path = project_dir / manifest.get("settings", ".claude/settings.json")
    if not settings_path.is_file():
        print(f"error: {settings_path} does not exist — a package cannot be verified "
              f"without the settings file that wires it", file=sys.stderr)
        sys.exit(2)
    try:
        settings = json.loads(settings_path.read_text())
    except json.JSONDecodeError as e:
        print(f"error: {settings_path} is not valid JSON ({e})", file=sys.stderr)
        sys.exit(2)

    violations = strict_violations(manifest) if strict else []

    mech_results = []
    for m in manifest.get("mechanisms", []):
        checker = CHECKERS.get(m.get("type"))
        if checker is None:
            mech_results.append({"id": m.get("id", "<unnamed>"), "type": m.get("type"),
                                 "wired": False, "wiring": f"unknown mechanism type {m.get('type')!r}",
                                 "cases": [], "failed": 1, "total": 1})
            continue
        mech_results.append(checker(m, settings, project_dir))

    total = sum(r["total"] for r in mech_results)
    failed = sum(r["failed"] for r in mech_results)
    unwired = [r for r in mech_results if not r["wired"]]
    package_ok = failed == 0 and not unwired and not violations

    if args.json:
        print(json.dumps({
            "package": manifest.get("package", "permissions"),
            "ok": package_ok, "total": total, "failed": failed,
            "unwired": [r["id"] for r in unwired],
            "strictViolations": violations,
            "mechanisms": mech_results,
            "supportedFamilies": [f for m in manifest.get("mechanisms", [])
                                  for f in m.get("supportedFamilies", [])],
            "uncoveredSurfaces": [u for m in manifest.get("mechanisms", [])
                                  for u in m.get("uncoveredSurfaces", [])],
        }, indent=2))
        sys.exit(0 if package_ok else 1)

    print(f"\nPackage: {manifest.get('package', 'permissions')}   "
          f"({len(mech_results)} mechanisms, settings: {manifest.get('settings', '.claude/settings.json')})")

    for r in mech_results:
        head = "ok " if r["wired"] and r["failed"] == 0 else "FAIL"
        print(f"\n[{head}] {r['id']}  ({r['type']})")
        print(f"       wiring: {r['wiring']}")
        if not r["wired"]:
            print("       NOT WIRED — this mechanism enforces nothing as installed, "
                  "however well the file itself behaves.")
        for c in r["cases"]:
            mark = "   " if c["ok"] else " ✗ "
            loc = f"  [cwd {c['cwd']}]" if c.get("cwd") and c["cwd"] != "." else ""
            note = "" if c["ok"] else f"   <- expected {c['expect']}, got {c['actual']} ({c['detail']})"
            print(f"    {mark}{c['command']}{loc}  expect {c['expect']}{note}")

    if violations:
        print(f"\nSTRICT VALIDATION FAILED ({len(violations)}):")
        for v in violations:
            print(f"  - {v}")

    print(f"\n{total - failed}/{total} checks passed"
          + (f"; {len(unwired)} mechanism(s) not wired" if unwired else ""))

    fams = [f for m in manifest.get("mechanisms", []) for f in m.get("supportedFamilies", [])]
    unc = [u for m in manifest.get("mechanisms", []) for u in m.get("uncoveredSurfaces", [])]
    print(f"\nSupported command families: {', '.join(fams) if fams else '(none declared)'}")
    print("NOT covered by this package:")
    for u in unc or ["(nothing declared)"]:
        print(f"  - {u}")

    print("\nA green package proves the families above behave as specified against the\n"
          "mechanisms as currently wired. It does not prove the resources are protected.\n"
          "Report both halves.")

    print(f"\nPACKAGE: {'PASS' if package_ok else 'FAIL'}")
    sys.exit(0 if package_ok else 1)


if __name__ == "__main__":
    main()
