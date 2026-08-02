# Writing a Finding

Loaded by `kickoff`, `check-playbook`, and `watch-film` — the three commands that write findings into a record. Read `references/state.md` first for the field schema; this file is about how to write a *good* one, not what shape it takes.

## The one test that matters: can you write the consequence?

Every finding needs a `claim` (what's true) and a `consequence` (why it costs the user something). If you can write the claim but not the consequence, you don't have a finding yet — you have an opinion about style. Keep digging until you can finish this sentence concretely, or don't raise it:

> "Because of this, [specific bad thing] happens when [specific situation]."

Weak: "The `CLAUDE.md` doesn't mention testing conventions." (So what?)
Strong: "No command runs `npm test` automatically, and nothing tells the agent to run it before claiming a task done — so completion claims in this repo currently mean nothing more than 'I stopped working,' and that's been true for at least two passes." (Concrete, and it names the actual cost.)

## Evidence: point at the thing, don't summarize it

`evidence` should let someone verify the finding in ten seconds without re-doing your work: a file and line number, a `grep` result, the absence of a specific file. "The permissions look loose" is not evidence. "`settings.json` has no `deny` block and `Bash(*)` is present under `allow`" is.

## mechanicalCheck: attach one whenever the finding is objectively checkable

This is the one field on a finding that isn't for the user — it's for the skill's own integrity. An adversarial test of this system found the real gap: `merge_pass.py` guarantees no ID reuse, no direct status writes, and formula-driven scoring, but none of that stops a finding from resolving just because a future pass's raw-findings list quietly leaves it out, even though the actual problem is untouched. `scripts/verify_resolution.py` closes that gap, but only for findings that carry a `mechanicalCheck` — so attach one whenever you can.

Three types, matched to what's actually checkable without judgment:

```json
{"type": "command_exit_zero", "command": "npm test"}
{"type": "claude_md_contains", "pattern": "Always run Prettier after editing"}
{"type": "settings_contains", "pattern": "Bash(*)"}
```

- `command_exit_zero` — for `verification`-category findings tied to a specific command from `verificationSurface`. This was the exact failure mode the adversarial test proved: a broken test command, silently dropped from a later pass's raw findings while still broken.
- `claude_md_contains` / `settings_contains` — for anything whose whole claim is "this specific text is still sitting in this specific file." Most `context`, `mechanism`, and `enforcement` findings qualify, since they're fundamentally about a passage of text existing where it shouldn't (or an instruction existing with nothing backing it).

**When to skip it:** genuinely judgment-based findings — is this MCP server actually "unvetted," is this rung actually the wrong one, is this content actually inferable rather than genuinely useful. Forcing a mechanical check onto something that needs a read and a judgment call just produces a check that rubber-stamps whatever pattern happens to match, which is worse than no check at all. Leave `mechanicalCheck` off entirely rather than write a fake one.

**Be honest about the limit even when you do attach one.** A pattern match isn't understanding — someone could reword a bad sentence just enough to dodge the exact string while leaving the real problem intact, and the check would wrongly call it fixed. That's a known, acceptable gap (catching *that* would require re-running full judgment every pass, which defeats the point of a cheap spot-check) — but don't present the mechanical check as a stronger guarantee than it is.

## Remedy: sketch it, don't build it

Findings written by `check-playbook` and `kickoff` don't fix anything — that's `adjust` and `drill`'s job, and only after showing a diff and getting approval (for `drill`, always; for `adjust`, when the change is non-trivial). `remedy` is a one- or two-sentence sketch precise enough that a different session could implement it without re-investigating: name the mechanism, name what gets deleted or superseded.

## Findings from a diff are a different animal (`watch-film` only)

Everything above applies, but the `kind` enum is different (`scope-creep` / `weakened-test` / `fixture-hardcode` / `unrelated-change` / `unverified-claim` / `criterion-unmet`) and the evidence is a `git diff` reference rather than a location in the standing config. The same discipline applies: name the specific line that changed and the specific criterion or expectation it undermines. "Tests were weakened" is not a finding; "the assertion on line 88 of `imports.spec.ts` changed from checking exact duplicate-count to `.toBeTruthy()`, which means AC-2's idempotency guarantee is no longer actually checked" is.

## What good findings are not

- Not a style preference dressed as a defect. If waiving it would cost nothing, it's `low` severity at most, and it's fair to ask yourself whether it's worth writing down at all.
- Not vague enough to apply to half the repo. A finding should point at one location, or a short enumerable list of locations, not "several files have this issue" with no list.
- Not a duplicate of something already open. Check the prior pass's open findings before writing a new one that's really the same thing worded differently — that's what the signal-matching system in `state.md` exists to prevent, but it only works if you're consistent about which detector produced the finding.
