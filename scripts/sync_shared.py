#!/usr/bin/env python3
"""Copy shared files from their owning skill into every skill that carries a copy.

The list lives in shared-files.yaml at the repo root. Edit the owner's file,
then run this. validate_skills.py fails CI when a copy has drifted.

Usage: python3 scripts/sync_shared.py [repo_root] [--check]
  --check   report drifted copies and exit 1 instead of writing
"""
import filecmp
import os
import shutil
import sys

try:
    import yaml
except ImportError:
    sys.exit("pyyaml required: pip install pyyaml")


def load_pairs(root):
    """Yield (source, copy) path pairs from shared-files.yaml."""
    path = os.path.join(root, "shared-files.yaml")
    if not os.path.isfile(path):
        return
    data = yaml.safe_load(open(path, encoding="utf-8")) or {}
    for group in data.get("groups") or []:
        owner = group["owner"]
        for rel in group.get("files") or []:
            source = os.path.join(root, "skills", owner, rel)
            for skill in group.get("copies_in") or []:
                yield source, os.path.join(root, "skills", skill, rel)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv[1:]
    root = args[0] if args else "."

    stale = 0
    for source, copy in load_pairs(root):
        if not os.path.isfile(source):
            sys.exit(f"missing owner file: {os.path.relpath(source, root)}")
        if os.path.isfile(copy) and filecmp.cmp(source, copy, shallow=False):
            continue
        stale += 1
        rel = os.path.relpath(copy, root)
        if check:
            print(f"STALE {rel}")
        else:
            os.makedirs(os.path.dirname(copy), exist_ok=True)
            shutil.copy2(source, copy)
            print(f"synced {rel}")

    if check and stale:
        print(f"\n{stale} copy/copies out of date — run python3 scripts/sync_shared.py")
        return 1
    if not stale:
        print("all shared copies up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
