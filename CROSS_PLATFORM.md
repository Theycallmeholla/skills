# Cross-platform skill builds

This repository keeps one shared skill source tree under `skills/` and compiles platform-specific packages for Claude and ChatGPT.

The shared `SKILL.md` remains the source of truth. Platform differences belong in the compatibility manifest or optional overlays, not in duplicated skill folders.

## Commands

Build every ChatGPT-compatible skill:

```bash
python3 scripts/build_skills.py --target chatgpt --all
```

Build one ChatGPT skill:

```bash
python3 scripts/build_skills.py --target chatgpt --skill handoff
```

Build Claude packages:

```bash
python3 scripts/build_skills.py --target claude --all
```

Validate platform declarations:

```bash
python3 scripts/validate_cross_platform.py .
```

Outputs are written to:

```text
dist/chatgpt/<skill>/skill.zip
dist/claude/<skill>/skill.zip
dist/chatgpt-report.json
dist/claude-report.json
```

Every ZIP is named `skill.zip` and contains exactly one top-level skill folder.

## Compatibility levels

- `native` -- the shared skill works without a platform-specific rewrite.
- `adapted` -- the core workflow works, but runtime substitutions or an overlay may be needed.
- `unsupported` -- a required host capability does not exist or the skill manages another platform directly.

Declarations live in `platforms/compatibility.yaml`.

## Optional overlays

A skill may include:

```text
skills/<name>/platforms/chatgpt.md
skills/<name>/platforms/claude.md
```

The default overlay mode appends the platform instructions to the shared body. For a full runtime rewrite, configure the skill with `body_mode: replace` and optionally an explicit `overlay` path:

```yaml
skills:
  example:
    chatgpt:
      status: adapted
      body_mode: replace
      overlay: platforms/chatgpt.md
```

Use replacement mode when the shared body contains an incompatible interaction model such as a custom widget tool.

## ChatGPT packaging behavior

The ChatGPT builder:

1. Keeps only `name` and `description` in `SKILL.md` frontmatter.
2. Generates `agents/openai.yaml` when the source skill does not provide it.
3. Excludes tests, evals, caches, and platform-source overlays from the distributable ZIP.
4. Rejects packages over 25 MiB.
5. Skips skills declared unsupported unless `--include-unsupported` is explicitly passed.
6. Writes a machine-readable report containing built, skipped, and warning results.

## Adding a new skill

1. Add the skill normally under `skills/<name>/`.
2. Keep the core instructions capability-based instead of naming a host tool when possible.
3. Add a manifest entry only when the skill is not natively portable.
4. Add an overlay when the outcome is portable but execution differs.
5. Run both validators and both builds before merging.

Do not call a skill cross-platform merely because its YAML parses. Cross-platform means its required tools, state model, interaction model, and packaging all work on the target host.
