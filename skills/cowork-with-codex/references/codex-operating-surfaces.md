# Codex operating surfaces

Everything below was verified, not recalled. Two provenances:

* **LOCAL** — read from `codex --help` / `codex exec --help` and a real session rollout on this machine, `codex-cli 0.147.0`, 2026-08-22.
* **DOCS** — OpenAI's published docs at `learn.chatgpt.com/docs/prompting` and `learn.chatgpt.com/docs/agent-configuration/agents-md`, read 2026-08-22.

Flags and defaults move between versions. Re-check with `codex --help` before asserting any of this to a user.

## Sandbox modes (LOCAL)

`-s, --sandbox <SANDBOX_MODE>` — "Select the sandbox policy to use when executing model-generated shell commands"

| value | meaning |
|---|---|
| `read-only` | model-generated commands cannot write |
| `workspace-write` | writes confined to the workspace |
| `danger-full-access` | no sandbox |

Related: `--add-dir <DIR>` adds writable directories alongside the primary workspace; `-C, --cd <DIR>` sets the working root.

## Approval policies (LOCAL)

`-a, --ask-for-approval <APPROVAL_POLICY>` — "Configure when the model requires human approval before executing a command"

| value | meaning (verbatim from `--help`) |
|---|---|
| `untrusted` | "Only run 'trusted' commands (e.g. ls, cat, sed) without asking for user approval. Will escalate to the user if the model proposes a command that is not in the 'trusted' set" |
| `on-request` | "The model decides when to ask the user for approval" |
| `never` | "Never ask for user approval. Execution failures are immediately returned to the model" |

Also present: `--approve-for-me` ("Route approval requests through automatic review using the workspace-write sandbox") and `--dangerously-bypass-approvals-and-sandbox` ("EXTREMELY DANGEROUS. Intended solely for running in environments that are externally sandboxed").

**Never write a message telling Codex to bypass these.** Sandbox and approval are the operator's launch-time decision. A message that needs wider access should say which command needs it and why, and stop.

## Subcommands that matter when correcting a run (LOCAL)

| command | what it does (verbatim) |
|---|---|
| `codex exec` | "Run Codex non-interactively" — prompt as arg or stdin |
| `codex review` | "Run a code review non-interactively" |
| `codex apply` | "Apply the latest diff produced by Codex agent as a `git apply` to your local working tree" |
| `codex resume [--last]` | "Resume a previous interactive session" |
| `codex fork [--last]` | "Fork a previous interactive session" — branch off instead of contaminating the current thread |
| `codex doctor` | "Diagnose local Codex installation, config, auth, and runtime health" |
| `codex sandbox` | "Run commands within a Codex-provided sandbox" |

`codex fork --last` is the right suggestion when a run has gone down a bad path and the user wants to retry from an earlier point rather than argue the agent out of it.

Config lives at `~/.codex/config.toml`; `-c key=value` overrides any dotted path for one run, `-p/--profile` layers `$CODEX_HOME/<name>.config.toml`.

## AGENTS.md (DOCS)

Codex reads AGENTS.md files before starting work. Lookup order:

1. **Global** — Codex home (`~/.codex` by default): `AGENTS.override.md` first, then `AGENTS.md`.
2. **Project** — from the Git root down to the current directory; at each level `AGENTS.override.md`, then `AGENTS.md`, then fallback filenames.
3. **Merge** — files concatenate from root down; closer files override earlier guidance.

Limits:

* Combined instruction budget defaults to **32 KiB**, controlled by `project_doc_max_bytes`. Codex stops once the limit is reached — an oversized chain silently loses its tail.
* At most **one file per directory**.
* The chain is rebuilt every run; there is no cache to clear.
* `AGENTS.override.md` is the temporary-override mechanism; delete it to restore shared guidance.

Practical consequence for this skill: a correction the user keeps repeating belongs in the nearest AGENTS.md as one line, not in every message. A correction that is specific to one task does not.

## OpenAI's stated prompting rules (DOCS)

* "Describe the result you need, not a detailed list of steps."
* "A useful Codex prompt names the behavior you want, points to the relevant code or reproduction steps, preserves important constraints, and says how to verify the change."
* For bugs, the repro steps and constraints "matter more than a high-level description."
* Ask for verification explicitly — "Codex should re-run the repro steps after the fix."
* Use `@` paths for file references; attach images for UI work; iterate with focused follow-ups.
* Use `/plan` for multi-step tasks so Codex proposes an approach first.
* "Codex runs local commands inside a sandbox that limits file and network access. If a task needs to cross that boundary, Codex follows your approval policy before continuing."
* Don't: assume unspoken context, skip verification, give vague repro steps.

## What Codex output actually looks like (LOCAL)

From a real rollout at `~/.codex/sessions/2026/08/14/rollout-*.jsonl`:

* Plans are a tool call, not prose: `tools.update_plan({plan:[{step:"…",status:"in_progress"}, {step:"…",status:"pending"}, …]})`. Statuses seen: `pending`, `in_progress`. The TUI renders this as a checklist, which is what gets pasted.
* Nearly all work arrives as `custom_tool_call` entries named `exec` — shell commands and their captured output.
* Assistant messages are terse and report-shaped: a one-line result, then bullets, then file/commit citations. Real examples:
  * A one-line result ("Pushed the isolated commit successfully.") followed by `Branch:` / `Commit:` / `Remote:` / `Push:` bullets and a fenced `git status` block.
  * A direct answer to the question asked ("Yes — the original concerns are implemented, tested, and pushed in commit `<sha>`.") followed by a "Covered:" bullet list and a closing paragraph naming the one remaining limitation.

That last shape is the one to be careful with: a confident completion report is a **claim**. When it matters, the outgoing message should demand the command and its raw output rather than the assertion.
