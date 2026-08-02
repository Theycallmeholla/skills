#!/usr/bin/env python3
"""
build_registry.py — derive .claude/nick-saban/registry.json from the files
actually on disk (audits/, orders/, waived.json). Never hand-edit registry.json.

Usage:
    python3 build_registry.py --project-dir /path/to/project
"""

import argparse
import json
from pathlib import Path


def state_dir(project_dir):
    return Path(project_dir) / ".claude" / "nick-saban"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-dir", required=True)
    args = ap.parse_args()

    sdir = state_dir(args.project_dir)
    audits_dir = sdir / "audits"
    orders_dir = sdir / "orders"

    audit_files = sorted(audits_dir.glob("[0-9][0-9][0-9].json")) if audits_dir.exists() else []

    if audit_files:
        with open(audit_files[-1]) as f:
            latest = json.load(f)
        current_audit = latest["pass"]
        last_audit_at = latest["created"]
        score = latest["score"]["overall"]
        open_high = sum(
            1 for finding in latest["findings"]
            if finding["status"] == "open" and finding["severity"] == "high"
        )
    else:
        current_audit = 0
        last_audit_at = None
        score = None
        open_high = 0

    orders = []
    if orders_dir.exists():
        for md_file in sorted(orders_dir.glob("*.md")):
            slug = md_file.stem
            frontmatter = _read_frontmatter(md_file)
            if frontmatter is None:
                continue
            criteria = frontmatter.get("criteria", [])
            unmet = sum(1 for c in criteria if c.get("status") != "met")
            orders.append({
                "slug": frontmatter.get("slug", slug),
                "title": frontmatter.get("title", slug),
                "created": frontmatter.get("created"),
                "lastAttest": frontmatter.get("lastAttest"),
                "criteriaUnmet": unmet,
            })

    registry = {
        "schema": 1,
        "currentAudit": current_audit,
        "lastAuditAt": last_audit_at,
        "score": score,
        "openHigh": open_high,
        "orders": orders,
    }

    out_path = sdir / "registry.json"
    sdir.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(registry, f, indent=2)
        f.write("\n")

    print(f"wrote {out_path}")
    print(f"currentAudit={current_audit} score={score} openHigh={open_high} orders={len(orders)}")


def _read_frontmatter(md_path):
    """Minimal YAML frontmatter reader — avoids requiring PyYAML as a dependency.
    Falls back to None (skip this file) if it can't parse cleanly; a command
    that needs richer YAML should read the file directly instead of depending
    on this best-effort parser."""
    text = md_path.read_text()
    if not text.startswith("---"):
        return None
    try:
        import yaml  # optional; most environments running this skill will have it
        end = text.index("\n---", 3)
        return yaml.safe_load(text[3:end])
    except ImportError:
        return _naive_frontmatter_parse(text)
    except ValueError:
        return None


def _naive_frontmatter_parse(text):
    """Extremely small fallback: top-level scalar keys only (slug, title,
    created, lastAttest). Doesn't parse the criteria list — criteriaUnmet
    will read as 0 in this fallback path. Good enough for the registry
    summary; commands needing the full order should read the .md directly."""
    end = text.index("\n---", 3)
    block = text[3:end]
    result = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            key, _, value = line.partition(":")
            value = value.strip().strip('"').strip("'")
            if value and value != "null":
                result[key.strip()] = value
    result.setdefault("criteria", [])
    return result


if __name__ == "__main__":
    main()
