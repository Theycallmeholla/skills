# Skills Repo Push for ChatGPT

Distribute skills from `Theycallmeholla/skills` into ChatGPT-compatible packages. ChatGPT does not expose a writable local installed-skills directory, so replace Claude-local synchronization with repository packaging and downloadable or CI artifacts.

## Direction

**Repository source -- ChatGPT packages**

## Workflow

1. Read the repository's `platforms/compatibility.yaml`.
2. Build all compatible skills with:

```bash
python3 scripts/build_skills.py --target chatgpt --all
```

3. Read `dist/chatgpt-report.json` and report:
   - built skills
   - skipped skills and reasons
   - warnings
4. Verify every built package exists at `dist/chatgpt/<skill>/skill.zip`.
5. When running inside GitHub without a local checkout, inspect the latest validation workflow and provide the `chatgpt-skills` workflow artifact rather than claiming a local build.
6. For a single skill, run:

```bash
python3 scripts/build_skills.py --target chatgpt --skill <name>
```

## Safety

- Never modify the shared source skill while distributing it.
- Never mark an unsupported skill as compatible merely to force a ZIP.
- Never claim a package exists without build output or a workflow artifact.
- Preserve the one-folder-per-ZIP structure and exact filename `skill.zip`.
- Do not reference or write to `~/.claude/skills`.

## Output

Return a compact distribution report with package count, skipped count, warnings, and exact artifact locations. When files are available in the current environment, link the generated ZIPs. When only GitHub is available, identify the workflow run and artifact that contains them.