# Watch-Film

Checks a finished diff against its work order: every acceptance criterion needs a named command and its actual exit result, and the diff itself gets inspected for the specific failure modes an agent under pressure to appear "done" tends to produce.

**Reads:** `orders/<slug>.md`, `git diff <range>`, the live output of running the order's verify commands
**Writes:** `orders/<slug>.md` frontmatter (`criteria[].status`, `criteria[].evidence`, `lastAttest`), `orders/<slug>.attest-N.json`, `registry.json`
**Stops at:** Fixes nothing it finds — that's a separate task, done knowingly, not folded into this check. Never writes to `audits/` and never moves the standing playbook score; a bad diff on one feature shouldn't swing the harness score for the whole repo. Never runs a command it hasn't shown the user first — a verify command comes from a file that was possibly written days ago and deserves the same scrutiny as any other command about to execute. Never marks a criterion `met` without naming the exact command and its exit result.

## Why this is a different record type than check-playbook's

`check-playbook` findings are about the standing harness and persist, resolving only when the underlying problem goes away for good. This command's findings are about one specific diff and don't persist the same way — a `watch-film` result from attempt 1 doesn't need to "resolve" on attempt 2, it's simply superseded by a fresh attestation. Keeping these separate is what stops one bad diff from corrupting the harness score, and what stops the append-only rule for `audits/` from having to account for a record type it was never designed to.

## Phase 1: Load the order

Read `orders/<slug>.md`. If it doesn't exist, stop — there's no contract to check against, and inventing one after the fact defeats the entire purpose of `gameplan` existing.

## Phase 2: Show and run each verify command

For every criterion, show the user the exact command from the order before running it. Then run it and capture the actual exit result — not a summary, the actual pass/fail and relevant output. A criterion whose command doesn't exist anymore or errors out for reasons unrelated to the feature gets `status: unverifiable`, with the reason stated plainly — that's different from `unmet`, and collapsing the two hides a `verification`-category problem worth a separate `check-playbook` finding.

## Phase 3: Scan the diff itself

Beyond running the commands, read the actual `git diff` for the range in question and look for:

- **scope-creep** — changes outside what `outOfScope` named, or well beyond what the goal required
- **weakened-test** — an existing assertion loosened, an exact check replaced with something like `.toBeTruthy()`, a test skipped or its scope narrowed
- **fixture-hardcode** — a solution that only works for the specific test data rather than the general case the criterion describes
- **unrelated-change** — files touched that have nothing to do with the order
- **unverified-claim** — anywhere the diff's own commit message or comments assert something is done or fixed with no corresponding verify command backing it up
- **criterion-unmet** — a criterion whose verify command actually failed, or whose behavior plainly isn't present in the diff

Each finding needs the same discipline as any other finding in this system: a specific location, a specific consequence. "Scope creep" alone isn't a finding; "the diff touches `src/auth/session.ts`, which `outOfScope` explicitly named, and changes token expiry behavior nobody asked for" is.

## Phase 4: Write the attestation record

```json
{
  "schema": 1,
  "attempt": <next number for this slug>,
  "order": "<slug>",
  "range": "<git range checked>",
  "created": "<ISO timestamp>",
  "verdict": "pass | fail | partial",
  "findings": [
    { "id": "AT-<n>", "kind": "<one of the six kinds above>",
      "location": "<file:line or path>", "claim": "...",
      "consequence": "...", "evidence": "git diff reference or command output" }
  ]
}
```

Save as `orders/<slug>.attest-N.json`, N incrementing per slug. Update the order's frontmatter — `criteria[].status`, `criteria[].evidence` (the command and its result), and `lastAttest` — in place, since that's the one deliberate exception to append-only for this command. Then run `scripts/build_registry.py`.

## Output

```
## Watch-Film: <slug>, attempt <N>

**Verdict: <pass/fail/partial>**

| Criterion | Status | Evidence |
|---|---|---|
[one row per criterion]

**Diff findings:**
[list, or "none — the diff matches the contract"]
```

## Confirm and stop

Fixes nothing. Never touches `audits/` or the playbook score. Never runs an unshown command. Never marks a criterion met without a named command and its actual result.
