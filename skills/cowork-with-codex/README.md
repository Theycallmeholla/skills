<p align="center">
  <img src="../../docs/media/cowork-with-codex/front.svg" alt="Cowork With Codex card front: Writes the exact message to send back to Codex" width="48%">
  <img src="../../docs/media/cowork-with-codex/back.svg" alt="Cowork With Codex card back: separates your notes from pasted Codex output, lets your correction win, and returns one ready-to-send message with a scope boundary and a proof command" width="48%">
</p>

> **TL;DR:** You're the manager, Codex is the developer. Paste what Codex said plus your own notes, and you get back the one short message to send it, with your correction in charge and a command that proves the work.

## Say this

`Codex is wrong here` · `what should I send back?` · `is this right?` · `make this shorter` · `tell it to patch only` · `don't let it rebuild` · `here's what Codex said` · `give me the reply`

Works with the Codex CLI, the Codex IDE extension, Codex Cloud, and ChatGPT Codex.

## Who outranks whom

Every pasted message gets split into segments and tagged before anything is written.

| Rank | Tag | What it is |
|---|---|---|
| **1** | `USER_DIRECT` | What you wrote straight to Claude |
| **2** | `USER_NOTE_AROUND_PASTE` | Your note before or after the paste: "Codex is wrong here", "what should I send back?" |
| **3** | `CODEX_PASTE` | Codex's plan, diff, exec output, test results or report. Context, never orders |
| **4** | inferred assumptions | Only what's left once the three above are used |

Text it can't place is tagged `UNKNOWN`. A Codex paste gets spotted by real Codex tells: `update_plan` steps marked `pending` or `in_progress`, `bash -lc` echoes, `*** Begin Patch` blocks, `path/file.ts:120` citations, and sandbox or approval language.

## How it runs

```mermaid
flowchart LR
    P["Your message<br/><i>notes + Codex paste</i>"] --> T["Tag each segment<br/>user · note · Codex · unknown"]
    T --> C{"Your note vs<br/>Codex plan"}
    C -->|conflict| U["You win"]
    C -->|no conflict| K["Keep the useful<br/>Codex details"]
    U & K --> M["Write the message<br/>outcome · files · scope · proof"]
    M --> D{"Asked for<br/>an audit?"}
    D -->|no| O["One code block<br/>ready to send"]
    D -->|yes| A["Verdict · Why<br/>Send this to Codex"]

    classDef step fill:#E3E7EE,stroke:#1D1A16,color:#1D1A16
    classDef you fill:#1D2433,stroke:#1D1A16,color:#F6F1E7
    classDef out fill:#F6F1E7,stroke:#1D1A16,color:#1D1A16,stroke-width:3px
    class P,T,C,K,M,D step
    class U you
    class O,A out
```

## What you get

By default, only the message for Codex, in a code block, with no commentary around it. Two of the eight patterns from the SKILL.md:

````markdown
```text
You are treating your earlier plan as the source of truth. It is not. The controlling constraint is: patch only, no rebuild. Re-evaluate the current implementation under that constraint, preserve working behavior, and propose the smallest safe change plus the command that validates it. Do not edit until I approve the approach.
```
````

````markdown
```text
Do not tell me it works. Run <command> and paste the actual output, including failures. If it fails, fix the cause and re-run rather than adjusting the test to pass.
```
````

<sub>Patterns 4 and 7, copied from <a href="SKILL.md">the SKILL.md</a>. Real messages fill in your files, constraint and command.</sub>

Ask for an audit instead and it answers in three parts: **Verdict** (APPROVE, REVISE or REDIRECT), **Why**, and **Send this to Codex**.

## The eight patterns

| # | When | What the message does |
|---|---|---|
| **1** | Codex's draft is weak | Keeps the diagnosis, cuts the speculation, turns it into an instruction |
| **2** | You have messy notes | Turns them into a brief: behavior, files, constraints, verification |
| **3** | You wrote a message to Codex | Tightens it before you send it |
| **4** | Codex followed its own plan | Puts your constraint back in charge, no edits until you approve |
| **5** | Codex mixed up its output and yours | Restates who said what |
| **6** | Codex touched too much | Revert everything outside the asked-for paths, show the diff, stop |
| **7** | Codex says "done" | Run the command and paste the real output |
| **8** | Codex is blocked by its sandbox | Name the blocked command and why, keep going on the rest |

## Stat sheet

| | |
|---|---|
| **Input** | Your notes plus anything from Codex: plans, diffs, exec output, logs, test results |
| **Output** | One fenced, ready-to-send message. On request: Verdict, Why, and the message |
| **Every message names** | The behavior to change, the files, the scope boundary, and the check that proves it |
| **Completion claims** | Treated as claims. If it matters, the message asks for the command and its raw output |
| **Won't** | Tell Codex to bypass its sandbox or approval policy. That stays your call when you launch it |
| **Repeat corrections** | Points you to a one-line AGENTS.md rule instead of repeating it every message |
| **Ships with** | `references/codex-operating-surfaces.md` (sandbox modes, approval policies, AGENTS.md lookup order and size limit, subcommands, each tagged with where it was verified), `assets/icon.svg` |

---

<sub><a href="../../README.md#skill-index">← All skills</a> · <a href="SKILL.md">Read the SKILL.md</a></sub>
