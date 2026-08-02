#!/usr/bin/env python3
"""Validate the cross-platform skill manifest and platform overlays."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

VALID_TARGETS = {"chatgpt", "claude"}
VALID_STATUSES = {"native", "adapted", "unsupported"}
HARD_CHATGPT_MARKERS = ("show_widget", "~/.claude/skills")


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"{path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return data


def platform_config(manifest: dict[str, Any], skill: str, target: str) -> dict[str, Any]:
    defaults = manifest.get("defaults", {}).get(target, {}) or {}
    override = manifest.get("skills", {}).get(skill, {}).get(target, {}) or {}
    if isinstance(defaults, str):
        defaults = {"status": defaults}
    if isinstance(override, str):
        override = {"status": override}
    return {**defaults, **override}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    manifest_path = root / "platforms" / "compatibility.yaml"
    errors: list[str] = []
    warnings: list[str] = []

    try:
        manifest = load_yaml(manifest_path)
    except ValueError as exc:
        print(f"ERROR {exc}")
        return 1

    if manifest.get("version") != 1:
        errors.append(f"{manifest_path}: version must be 1")

    skills_dir = root / "skills"
    skills = sorted(path.name for path in skills_dir.iterdir() if path.is_dir() and (path / "SKILL.md").exists())
    configured = set(manifest.get("skills", {}))
    unknown = configured - set(skills)
    for name in sorted(unknown):
        errors.append(f"manifest references missing skill {name!r}")

    for target in VALID_TARGETS:
        default = manifest.get("defaults", {}).get(target, {})
        if isinstance(default, str):
            default_status = default
        else:
            default_status = (default or {}).get("status", "native")
        if default_status not in VALID_STATUSES:
            errors.append(f"defaults/{target}: invalid status {default_status!r}")

    for skill in skills:
        skill_dir = skills_dir / skill
        body = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        for target in VALID_TARGETS:
            config = platform_config(manifest, skill, target)
            status = config.get("status", "native")
            if status not in VALID_STATUSES:
                errors.append(f"{skill}/{target}: invalid status {status!r}")
                continue
            if status == "unsupported" and not config.get("reason"):
                errors.append(f"{skill}/{target}: unsupported entries require a reason")
            overlay = config.get("overlay")
            if overlay and not (skill_dir / overlay).is_file():
                errors.append(f"{skill}/{target}: overlay {overlay!r} does not exist")
            if config.get("body_mode", "append") not in {"append", "replace"}:
                errors.append(f"{skill}/{target}: body_mode must be append or replace")

        chatgpt = platform_config(manifest, skill, "chatgpt")
        status = chatgpt.get("status", "native")
        mode = chatgpt.get("body_mode", "append")
        for marker in HARD_CHATGPT_MARKERS:
            if marker in body and status == "native":
                errors.append(f"{skill}/chatgpt: native skill contains hard platform marker {marker!r}")
            elif marker in body and status == "adapted" and mode != "replace":
                errors.append(
                    f"{skill}/chatgpt: adapted skill contains {marker!r}; use body_mode: replace or mark unsupported"
                )
        if status == "adapted" and not chatgpt.get("overlay") and not (skill_dir / "platforms" / "chatgpt.md").exists():
            warnings.append(f"{skill}/chatgpt: adapted without a ChatGPT overlay")

    for warning in warnings:
        print(f"WARN  {warning}")
    for error in errors:
        print(f"ERROR {error}")
    print(f"\n{len(skills)} skills checked -- {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
