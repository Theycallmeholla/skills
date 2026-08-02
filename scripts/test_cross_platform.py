#!/usr/bin/env python3
"""Regression tests for cross-platform skill packaging."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
BUILDER = SCRIPT_DIR / "build_skills.py"
VALIDATOR = SCRIPT_DIR / "validate_cross_platform.py"


def write_skill(root: Path, name: str, extra_frontmatter: str = "", body: str = "# Test\n") -> None:
    skill = root / "skills" / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test skill for packaging.\n{extra_frontmatter}---\n\n{body}",
        encoding="utf-8",
    )


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="cross-platform-tests-") as temp:
        root = Path(temp)
        (root / "platforms").mkdir()
        (root / "scripts").mkdir()
        write_skill(root, "portable", "allowed-tools:\n  - Bash(echo *)\n")
        write_skill(root, "widget-only", body="# Widget\nCall show_widget now.\n")
        manifest = {
            "version": 1,
            "defaults": {
                "claude": {"status": "native"},
                "chatgpt": {"status": "native"},
            },
            "skills": {
                "widget-only": {
                    "chatgpt": {
                        "status": "unsupported",
                        "reason": "custom widget runtime",
                    }
                }
            },
        }
        (root / "platforms" / "compatibility.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False),
            encoding="utf-8",
        )

        validation = run(str(VALIDATOR), ".", cwd=root)
        assert validation.returncode == 0, validation.stdout + validation.stderr

        chatgpt = run(
            str(BUILDER),
            "--target", "chatgpt",
            "--all",
            "--repo-root", ".",
            cwd=root,
        )
        assert chatgpt.returncode == 0, chatgpt.stdout + chatgpt.stderr
        assert "1 built, 1 skipped" in chatgpt.stdout

        zip_path = root / "dist" / "chatgpt" / "portable" / "skill.zip"
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path) as archive:
            names = set(archive.namelist())
            assert "portable/SKILL.md" in names
            assert "portable/agents/openai.yaml" in names
            skill_text = archive.read("portable/SKILL.md").decode()
            header = skill_text.split("---", 2)[1]
            metadata = yaml.safe_load(header)
            assert set(metadata) == {"name", "description"}
            assert "allowed-tools" not in metadata

        claude = run(
            str(BUILDER),
            "--target", "claude",
            "--skill", "portable",
            "--repo-root", ".",
            cwd=root,
        )
        assert claude.returncode == 0, claude.stdout + claude.stderr
        claude_zip = root / "dist" / "claude" / "portable" / "skill.zip"
        with zipfile.ZipFile(claude_zip) as archive:
            skill_text = archive.read("portable/SKILL.md").decode()
            metadata = yaml.safe_load(skill_text.split("---", 2)[1])
            assert "allowed-tools" in metadata

    print("cross-platform tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
