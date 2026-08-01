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

Open children of the board, minus blocked, minus claimed, in board order:

```bash
gh api repos/{owner}/{repo}/issues/<board-number>/sub_issues --jq '
  [ .[] | select(.state == "open")
        | select((.assignees | length) == 0)
        | select((.issue_dependencies_summary.blocked_by // 0) == 0)
        | {number, title} ]'
```

(Task-list fallback: `gh issue list --state open` filtered to numbers in the board's task list, then apply the same assignee/blocked filters.)

## Claim / resolve / close

- **Claim** (first write of a Work session): `gh issue edit <n> --add-assignee @me`
- **Stale-claim check**: `gh issue view <n> --json assignees,updatedAt` — assigned + no update in 3+ days → ask the human before unclaiming (`--remove-assignee`).
- **Resolve**: `gh issue comment <n> --body "<the answer>"` then `gh issue close <n>`, then append the gist + link to the board's Decisions so far (read-modify-write per above).
- **Rule out of scope**: `gh issue close <n> --comment "Out of scope: <why> — see board"` plus the board's Out of scope line.
- **Close the board** (Snapshot mode only): `gh issue close <board> --comment "Board snapshotted. Artifact: <link>"`

## Concurrency etiquette

Between loading the board and writing to it, other sessions may have moved it. Cheap protections: re-fetch the board body immediately before editing it; re-check a ticket's assignee immediately before claiming; if a claim collides (assignee appeared between check and claim), pick the next up-next ticket instead of contesting.
