#!/usr/bin/env python3
"""Build platform-specific skill packages from one shared skills/ source tree."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import yaml

MAX_ZIP_BYTES = 25 * 1024 * 1024
VALID_TARGETS = {"chatgpt", "claude"}
VALID_STATUSES = {"native", "adapted", "unsupported"}
EXCLUDED_NAMES = {".DS_Store"}
EXCLUDED_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "tests", "evals", "platforms"}
CHATGPT_HARD_LEAKS = {
    "show_widget": "requires a host-provided custom widget tool",
    "~/.claude/skills": "references Claude's local installation directory",
}
CHATGPT_SOFT_LEAKS = {
    "Claude Code": "mentions a Claude-specific runtime",
    "Cowork": "mentions a Claude-specific runtime",
    "Bash(": "contains Claude allowed-tools syntax",
    "Task(": "contains Claude subagent syntax",
}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)


class BuildError(RuntimeError):
    pass


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise BuildError(f"{path} must contain a YAML mapping")
    return data


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = read_yaml(path)
    if manifest.get("version") != 1:
        raise BuildError(f"{path} must declare version: 1")
    return manifest


def parse_skill_md(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise BuildError(f"{path}: missing valid YAML frontmatter")
    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise BuildError(f"{path}: frontmatter must be a mapping")
    return metadata, text[match.end():]


def render_skill_md(metadata: dict[str, Any], body: str) -> str:
    frontmatter = yaml.safe_dump(
        metadata,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ).strip()
    return f"---\n{frontmatter}\n---\n\n{body.lstrip()}"


def humanize(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def merge_platform_config(manifest: dict[str, Any], skill: str, target: str) -> dict[str, Any]:
    defaults = manifest.get("defaults", {}).get(target, {}) or {}
    override = manifest.get("skills", {}).get(skill, {}).get(target, {}) or {}
    if isinstance(defaults, str):
        defaults = {"status": defaults}
    if isinstance(override, str):
        override = {"status": override}
    if not isinstance(defaults, dict) or not isinstance(override, dict):
        raise BuildError(f"invalid manifest configuration for {skill}/{target}")
    config = {**defaults, **override}
    config.setdefault("status", "native")
    if config["status"] not in VALID_STATUSES:
        raise BuildError(f"{skill}/{target}: invalid status {config['status']!r}")
    return config


def ignored_path(path: Path) -> bool:
    return path.name in EXCLUDED_NAMES or any(part in EXCLUDED_DIRS for part in path.parts)


def copy_payload(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for item in source.rglob("*"):
        relative = item.relative_to(source)
        if ignored_path(relative):
            continue
        target = destination / relative
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif item.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def apply_overlay(source: Path, target: str, config: dict[str, Any], body: str) -> str:
    overlay_value = config.get("overlay")
    overlay_path = source / overlay_value if overlay_value else source / "platforms" / f"{target}.md"
    if not overlay_path.exists():
        return body
    overlay = overlay_path.read_text(encoding="utf-8").strip()
    mode = config.get("body_mode", "append")
    if mode == "replace":
        return overlay + "\n"
    if mode != "append":
        raise BuildError(f"{source.name}/{target}: body_mode must be append or replace")
    return body.rstrip() + f"\n\n{overlay}\n"


def ensure_openai_metadata(skill_dir: Path, display_name: str) -> None:
    metadata_path = skill_dir / "agents" / "openai.yaml"
    if metadata_path.exists():
        data = read_yaml(metadata_path)
        interface = data.get("interface")
        if not isinstance(interface, dict) or not interface.get("display_name"):
            raise BuildError(f"{metadata_path}: interface.display_name is required")
        return
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        yaml.safe_dump(
            {"interface": {"display_name": display_name}},
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def inspect_chatgpt_body(body: str, status: str, body_mode: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for token, explanation in CHATGPT_HARD_LEAKS.items():
        if token in body:
            message = f"contains {token!r}: {explanation}"
            if status == "native" or body_mode != "replace":
                errors.append(message)
            else:
                warnings.append(message)
    for token, explanation in CHATGPT_SOFT_LEAKS.items():
        if token in body:
            warnings.append(f"contains {token!r}: {explanation}")
    return errors, warnings


def validate_built_skill(skill_dir: Path, target: str, status: str, body_mode: str) -> list[str]:
    metadata, body = parse_skill_md(skill_dir / "SKILL.md")
    name = skill_dir.name
    errors: list[str] = []
    warnings: list[str] = []
    if metadata.get("name") != name:
        errors.append(f"name {metadata.get('name')!r} does not match folder {name!r}")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("description is missing or empty")
    elif len(description) > 1024:
        errors.append("description exceeds 1024 characters")
    if target == "chatgpt":
        extras = set(metadata) - {"name", "description"}
        if extras:
            errors.append(f"ChatGPT frontmatter contains unsupported keys: {', '.join(sorted(extras))}")
        openai_yaml = skill_dir / "agents" / "openai.yaml"
        if not openai_yaml.exists():
            errors.append("agents/openai.yaml is missing")
        else:
            try:
                data = read_yaml(openai_yaml)
                if not isinstance(data.get("interface"), dict) or not data["interface"].get("display_name"):
                    errors.append("agents/openai.yaml lacks interface.display_name")
            except BuildError as exc:
                errors.append(str(exc))
        leak_errors, leak_warnings = inspect_chatgpt_body(body, status, body_mode)
        errors.extend(leak_errors)
        warnings.extend(leak_warnings)
    if errors:
        raise BuildError(f"{name}/{target}: " + "; ".join(errors))
    return warnings


def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / "skill.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(skill_dir.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(skill_dir.parent))
    size = zip_path.stat().st_size
    if size > MAX_ZIP_BYTES:
        zip_path.unlink(missing_ok=True)
        raise BuildError(f"{skill_dir.name}: package is {size:,} bytes, over the 25 MiB limit")
    return zip_path


def build_one(
    repo_root: Path,
    source: Path,
    target: str,
    manifest: dict[str, Any],
    output_root: Path,
    include_unsupported: bool,
) -> dict[str, Any]:
    name = source.name
    config = merge_platform_config(manifest, name, target)
    status = config["status"]
    if status == "unsupported" and not include_unsupported:
        return {
            "skill": name,
            "target": target,
            "status": "skipped",
            "support": status,
            "reason": config.get("reason", "declared unsupported"),
            "warnings": [],
        }

    source_md = source / "SKILL.md"
    if not source_md.exists():
        raise BuildError(f"{source}: SKILL.md is missing")
    metadata, body = parse_skill_md(source_md)
    if metadata.get("name") != name:
        raise BuildError(f"{source_md}: name does not match folder")

    with tempfile.TemporaryDirectory(prefix=f"skill-{target}-{name}-") as temp_dir:
        staging_parent = Path(temp_dir)
        staging_skill = staging_parent / name
        copy_payload(source, staging_skill)
        body = apply_overlay(source, target, config, body)

        if target == "chatgpt":
            metadata = {
                "name": metadata.get("name"),
                "description": metadata.get("description"),
            }
            ensure_openai_metadata(staging_skill, config.get("display_name", humanize(name)))

        (staging_skill / "SKILL.md").write_text(render_skill_md(metadata, body), encoding="utf-8")
        warnings = validate_built_skill(
            staging_skill,
            target,
            status,
            config.get("body_mode", "append"),
        )
        zip_path = package_skill(staging_skill, output_root / target / name)

    return {
        "skill": name,
        "target": target,
        "status": "built",
        "support": status,
        "path": str(zip_path.relative_to(repo_root)) if zip_path.is_relative_to(repo_root) else str(zip_path),
        "warnings": warnings,
    }


def discover_skills(repo_root: Path) -> list[Path]:
    skills_dir = repo_root / "skills"
    if not skills_dir.is_dir():
        raise BuildError(f"{skills_dir} does not exist")
    return sorted(path for path in skills_dir.iterdir() if path.is_dir() and (path / "SKILL.md").exists())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=sorted(VALID_TARGETS), required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--skill", action="append", dest="skills")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest", default="platforms/compatibility.yaml")
    parser.add_argument("--output-dir", default="dist")
    parser.add_argument("--include-unsupported", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    manifest_path = repo_root / args.manifest
    output_root = (repo_root / args.output_dir).resolve()
    try:
        manifest = load_manifest(manifest_path)
        discovered = {path.name: path for path in discover_skills(repo_root)}
        selected_names = sorted(discovered) if args.all else args.skills
        missing = [name for name in selected_names if name not in discovered]
        if missing:
            raise BuildError("unknown skill(s): " + ", ".join(missing))
        results = [
            build_one(
                repo_root,
                discovered[name],
                args.target,
                manifest,
                output_root,
                args.include_unsupported,
            )
            for name in selected_names
        ]
        report_path = output_root / f"{args.target}-report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        built = sum(item["status"] == "built" for item in results)
        skipped = sum(item["status"] == "skipped" for item in results)
        warnings = sum(len(item.get("warnings", [])) for item in results)
        print(f"{args.target}: {built} built, {skipped} skipped, {warnings} warning(s)")
        for item in results:
            if item["status"] == "skipped":
                print(f"SKIP {item['skill']}: {item['reason']}")
            for warning in item.get("warnings", []):
                print(f"WARN {item['skill']}: {warning}")
        print(f"report: {report_path}")
        return 0
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
