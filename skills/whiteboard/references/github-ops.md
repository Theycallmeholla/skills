# GitHub operations for whiteboard

All operations use the `gh` CLI. Infer the repo from `git remote -v` — `gh` does this automatically inside a clone. Use heredocs for multi-line bodies.

## Labels (create once per repo, idempotent)

```bash
for l in "whiteboard:map" "whiteboard:research" "whiteboard:napkin" "whiteboard:hot-seat" "whiteboard:task"; do
  gh label create "$l" --force 2>/dev/null || true
done
```

## The board

```bash
gh issue create --title "<board name>" --label "whiteboard:map" --body-file <(cat <<'EOF'
<board body per templates.md>
EOF
)
```

Update the board body (Decisions so far, parking lot, out of scope): `gh issue edit <board> --body-file <file>`. Fetch current body first (`gh issue view <board> --json body --jq .body`), edit, write back — never reconstruct from memory, another session may have appended since you loaded it.

**Verify the edit landed before writing it back.** A section-anchored insert into a body whose headings have drifted — hand-edited board, a body that never got the template, a renamed section — matches nothing and returns success. `sed`/`perl` exit 0 on zero substitutions. The decision line vanishes with no error, and the board is an index: a lost line is a lost decision.

So diff before and after in the same step, and treat no-change as a failure:

```bash
gh issue view <board> --json body --jq .body > /tmp/board.md
before=$(grep -c '^- \[' /tmp/board.md)
# ...insert the decision line...
after=$(grep -c '^- \[' /tmp/board.md)
[ "$after" -gt "$before" ] || { echo "board write failed: anchor missing"; exit 1; }
gh issue edit <board> --body-file /tmp/board.md
```

Anchor genuinely missing? Stop and tell the human the board body has drifted from the template — don't rebuild the board from memory to make the write fit.

Note for board creation: `gh issue create` has **no `--json` flag**. It prints the new issue's URL; take the number off the end (`| sed 's|.*/||'`). Piping it into `--json number --jq .number` fails, and a `||` fallback behind it will quietly create the board with the wrong body.

## Child tickets (sub-issues)

Create the ticket, then attach it to the board as a native sub-issue:

```bash
gh issue create --title "<question as a title>" --label "whiteboard:<type>" --body "..."
# attach as sub-issue (needs the child's database id, not its #number):
CHILD_DB_ID=$(gh api repos/{owner}/{repo}/issues/<child-number> --jq .id)
gh api --method POST repos/{owner}/{repo}/issues/<board-number>/sub_issues -F sub_issue_id=$CHILD_DB_ID
```

If sub-issues aren't enabled on the repo: fall back to a task-list line in the board body (`- [ ] #<child>`) plus `Part of #<board>` at the top of the child body.

## Blocking (native dependencies)

Native dependencies render the up-next visually in GitHub's UI — that's why they're canonical, not a body convention. Wire edges in a second pass after all tickets exist:

```bash
BLOCKER_DB_ID=$(gh api repos/{owner}/{repo}/issues/<blocker-number> --jq .id)
gh api --method POST repos/{owner}/{repo}/issues/<blocked-number>/dependencies/blocked_by -F issue_id=$BLOCKER_DB_ID
```

Note the id types: the dependencies endpoint takes the **database id** (`.id`), never the `#number` or `node_id`. A ticket is unblocked when `issue_dependencies_summary.blocked_by` is 0 (GitHub counts open blockers only — closed blockers drop off automatically).

Fallback where dependencies aren't available: a `Blocked by: #n, #n` line at the top of the ticket body; unblocked = every listed issue closed.

## Up-next query

Open children of the board, minus blocked, minus claimed, in board order. Pull `labels` too — that's what decides whether a session can take the ticket alone, and fetching it here saves a call per ticket:

```bash
gh api repos/{owner}/{repo}/issues/<board-number>/sub_issues --jq '
  [ .[] | select(.state == "open")
        | select((.assignees | length) == 0)
        | select((.issue_dependencies_summary.blocked_by // 0) == 0)
        | {number, title, type: (.labels | map(.name) | map(select(startswith("whiteboard:"))) | first)} ]'
```

(Task-list fallback: `gh issue list --state open` filtered to numbers in the board's task list, then apply the same assignee/blocked filters.)

For a `whiteboard:task` ticket, eligibility also needs the `Runs:` line from its body — the label can't carry it:

```bash
gh issue view <n> --json body --jq '.body | capture("(?i)^Runs:\\s*(?<who>agent|human)"; "m").who // "human"'
```

No match → `human`. See [run-loop.md](run-loop.md) for what the loop does with these.

## Claim / resolve / close

- **Claim** (first write of a Work session): `gh issue edit <n> --add-assignee @me`
- **Stale-claim check**: `gh issue view <n> --json assignees,updatedAt` — assigned + no update in 3+ days → ask the human before unclaiming (`--remove-assignee`).
- **Resolve**: `gh issue comment <n> --body "<the answer>"` then `gh issue close <n>`, then append the gist + link to the board's Decisions so far (read-modify-write per above).
- **Rule out of scope**: `gh issue close <n> --comment "Out of scope: <why> — see board"` plus the board's Out of scope line.
- **Close the board** (Snapshot mode only): `gh issue close <board> --comment "Board snapshotted. Artifact: <link>"`

## Concurrency etiquette

Between loading the board and writing to it, other sessions may have moved it. Cheap protections: re-fetch the board body immediately before editing it; re-check a ticket's assignee immediately before claiming; if a claim collides (assignee appeared between check and claim), pick the next up-next ticket instead of contesting.
