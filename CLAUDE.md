# Working in this repo

Several Claude sessions run against this checkout at the same time. Some of them are not
even working on skills — they just happen to have been launched from this directory. That
makes branch state shared, and a branch switch in one session silently moves every other
session with it.

## Use a worktree

Do your work in a worktree, not in the root checkout:

```bash
git worktree add .claude/worktrees/<short-name> -b <branch>   # new branch
git worktree add .claude/worktrees/<short-name> <branch>      # existing branch
cd .claude/worktrees/<short-name>
```

`.claude/worktrees/` is gitignored, and the path is what the `EnterWorktree` tool expects,
so either route lands in the same place.

**Leave the root checkout on `main`.** It is the directory unrelated sessions inherit, so
whatever branch it sits on is the branch they will commit to by accident. Switch it only
to pull or to cut a new branch, then switch it back.

## Never `git add -A` at the repo root

Scope every add to the paths you actually changed:

```bash
git add -A skills/<skill-name>        # good
git add scripts/foo.py README.md      # good
git add -A                            # sweeps up other sessions' work
```

Skill scans drop packet files (`gap_packet.json`, `wwbd_packet.json`) at the repo root.
They are gitignored, but an unscoped add in an older checkout will still catch them.

## Before you commit

```bash
python3 scripts/validate_skills.py .
python3 scripts/validate_cross_platform.py .
```

Both must report 0 errors. Warnings do not fail CI, but a description over 1024 chars is
an error for a reason: the skill silently stops loading.

Adding a skill also means a README entry — CI fails without one. See the authoring section
in `README.md` for the full checklist.
