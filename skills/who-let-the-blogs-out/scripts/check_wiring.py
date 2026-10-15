#!/usr/bin/env python3
"""Static wiring check for who-let-the-blogs-out. Run from the skill root:
    python3 scripts/check_wiring.py
Fails (exit 1) if a command is listed but not wired everywhere it must be,
if the rule count drifts, or if a reference file is orphaned."""
import re, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
skill = (root / "SKILL.md").read_text()
refs = {p.stem for p in (root / "references").glob("*.md")}
errors = []

# 0. frontmatter limits enforced by the skill loader
import yaml
fm = yaml.safe_load(skill.split("---\n")[1])
if len(fm.get("description", "")) > 1024:
    errors.append(f"description is {len(fm['description'])} chars; the limit is 1024")

# 1. command list line vs command table vs reference files
listed = re.search(r"^`([a-z ·]+)`$", skill, re.M).group(1).split(" · ")
table = re.findall(r"^\| `([a-z]+)` \|", skill, re.M)
for cmd in listed:
    if cmd == "help":
        if "help" not in refs: errors.append("help listed but references/help.md missing")
        continue
    if cmd not in table: errors.append(f"`{cmd}` in command list but not in command table")
    if cmd not in refs: errors.append(f"`{cmd}` has no references/{cmd}.md")
for cmd in table:
    if cmd not in listed: errors.append(f"`{cmd}` in table but not in command list line")

# 2. rule count consistency
n_rules = len(re.findall(r"^## Rule \d+ ", (root/"references/governing-rules.md").read_text(), re.M))
headlines = len(re.findall(r"^\d+\. \*\*", skill.split("## The ")[1].split("## ")[0] if "## The " in skill else "", re.M))
words = {10:"ten",11:"eleven",12:"twelve",13:"thirteen"}
word = words.get(n_rules, str(n_rules))
if f"## The {word} rules" not in skill: errors.append(f"SKILL.md heading should say '{word} rules' ({n_rules} in governing-rules.md)")
if headlines != n_rules: errors.append(f"SKILL.md lists {headlines} rule headlines, governing-rules.md has {n_rules}")
for p in (root/"references").glob("*.md"):
    for w in words.values():
        if w != word and re.search(rf"\b{w} rules\b", p.read_text()):
            errors.append(f"{p.name} still says '{w} rules'")

# 3. user-facing commands appear in routing menu and help
routing = (root/"references/routing.md").read_text()
helptxt = (root/"references/help.md").read_text()
for cmd in listed:
    if cmd in ("help","review","verify"):  # review is chained; verify appears inside Capture line
        pass
    if cmd not in ("help",) and cmd not in routing and cmd != "review":
        errors.append(f"`{cmd}` missing from routing.md menu")
    if cmd != "help" and cmd not in helptxt:
        errors.append(f"`{cmd}` missing from help.md")

# 4. orphaned reference files (not commands, not loaded anywhere)
alltext = skill + "".join((root/"references"/f"{r}.md").read_text() for r in refs)
for r in refs - set(listed):
    if f"{r}.md" not in alltext: errors.append(f"references/{r}.md is never referenced")

# 5. acceptance-test rule references point at real rules
for m in re.findall(r"\*\*Rule:\*\* ([^.]*)\.", (root/"references/acceptance-tests.md").read_text()):
    for n in re.findall(r"\b(\d+)\b", m):
        if int(n) > n_rules and "priority" not in m: errors.append(f"acceptance test cites Rule {n}, only {n_rules} exist")

if errors:
    print("FAIL"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK — {len(listed)} commands wired, {n_rules} rules consistent, no orphaned references")
