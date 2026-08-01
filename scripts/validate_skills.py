#!/usr/bin/env python3
"""Validate every skill in skills/ against the Agent Skills spec.

Exits 1 on any error. Warnings never fail the build.
Usage: python3 scripts/validate_skills.py [repo_root]
"""
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("pyyaml required: pip install pyyaml")

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ALLOWED_KEYS = {"name", "description", "license", "compatibility",
                "metadata", "allowed-tools"}
RESERVED = ("anthropic", "claude")
PATH_RE = re.compile(r"`((?:scripts|references|assets)/[A-Za-z0-9_./-]+)`")
BULLET_RE = re.compile(r"^- \*\*([a-z0-9-]+)\*\*", re.M)

MAX_DESC = 1024
WARN_DESC = 950
MAX_BODY = 500
WARN_BODY = 400

errors, warnings = [], []


def err(skill, msg):
    errors.append(f"{skill}: {msg}")


def warn(skill, msg):
    warnings.append(f"{skill}: {msg}")


def check_skill(root, name):
    path = os.path.join(root, "skills", name, "SKILL.md")
    rel = f"skills/{name}/SKILL.md"

    if not os.path.isfile(path):
        return err(name, "missing SKILL.md")

    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return err(name, f"{rel}: no frontmatter block")

    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return err(name, f"{rel}: frontmatter is not valid YAML — {e}")
    if not isinstance(fm, dict):
        return err(name, f"{rel}: frontmatter did not parse to a mapping")

    extra = set(fm) - ALLOWED_KEYS
    if extra:
        err(name, f"{rel}: unexpected frontmatter keys: {', '.join(sorted(extra))}")

    # --- name ---
    fmname = str(fm.get("name", ""))
    if not fmname:
        err(name, f"{rel}: missing name")
    else:
        if fmname != name:
            err(name, f"{rel}: name '{fmname}' does not match folder '{name}'")
        if len(fmname) > 64:
            err(name, f"{rel}: name is {len(fmname)} chars (max 64)")
        if not NAME_RE.match(fmname):
            err(name, f"{rel}: name must be lowercase alphanumeric with single hyphens")
        for word in RESERVED:
            if word in fmname:
                err(name, f"{rel}: name contains reserved word '{word}'")

    # --- description ---
    desc = (fm.get("description") or "").strip()
    if not desc:
        err(name, f"{rel}: missing or empty description")
    else:
        n = len(desc)
        if n > MAX_DESC:
            err(name, f"{rel}: description is {n} chars (max {MAX_DESC}) — skill will not load")
        elif n > WARN_DESC:
            warn(name, f"{rel}: description is {n} chars, close to the {MAX_DESC} limit")
    if re.search(r"<[a-zA-Z/][^>]*>", str(fm.get("description", ""))):
        err(name, f"{rel}: description contains an XML-style tag")

    # --- body size ---
    body = text[m.end():]
    lines = len(body.splitlines())
    if lines > MAX_BODY:
        err(name, f"{rel}: body is {lines} lines (max {MAX_BODY})")
    elif lines > WARN_BODY:
        warn(name, f"{rel}: body is {lines} lines, approaching the {MAX_BODY} limit")

    # --- referenced bundle files exist ---
    base = os.path.join(root, "skills", name)
    for ref in sorted(set(PATH_RE.findall(body))):
        if not os.path.exists(os.path.join(base, ref)):
            err(name, f"{rel}: references `{ref}` which does not exist")


def check_denylist(root, skills):
    """Hard block: named skills must never appear in this repo."""
    path = os.path.join(root, ".publish-denylist")
    if not os.path.isfile(path):
        return
    banned = set()
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if line:
            banned.add(line)
    for name in sorted(skills & banned):
        err(name, "is on .publish-denylist and must NEVER be published to this repo")


def check_readme(root, skills):
    path = os.path.join(root, "README.md")
    if not os.path.isfile(path):
        return err("README.md", "missing")
    listed = set(BULLET_RE.findall(open(path, encoding="utf-8").read()))
    for missing in sorted(skills - listed):
        err("README.md", f"skill '{missing}' has no entry")
    for stale in sorted(listed - skills):
        err("README.md", f"entry '{stale}' has no matching skill folder")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    skills_dir = os.path.join(root, "skills")
    if not os.path.isdir(skills_dir):
        sys.exit(f"no skills/ directory under {root}")

    names = sorted(d for d in os.listdir(skills_dir)
                   if os.path.isdir(os.path.join(skills_dir, d)))
    for name in names:
        check_skill(root, name)
    check_denylist(root, set(names))
    check_readme(root, set(names))

    for w in warnings:
        print(f"::warning::{w}" if os.environ.get("GITHUB_ACTIONS") else f"WARN  {w}")
    for e in errors:
        print(f"::error::{e}" if os.environ.get("GITHUB_ACTIONS") else f"ERROR {e}")

    print(f"\n{len(names)} skills checked — {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
