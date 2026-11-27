<p align="center">
  <img src="../../docs/media/code-audit/card.svg" alt="Code Audit card: sweeps an entire repo in nine phases, pins every finding to a file and line, ranks them Critical to Info, and hands you a 30/60/90-day fix plan." width="100%">
</p>

> **TL;DR:** Point it at a repo. You get a report that ranks every problem by how much it can hurt you, with the file and line for each one and a plan for what to fix first.

## Say this

`audit this codebase` · `review this repo` · `security review` · `what's wrong with this codebase` · `due diligence on this project` · `can you eyeball my repo?`

## How it runs

Phase 1 is a gate: nothing gets judged until the inventory exists. On repos over about 100k lines, phases 2, 3 and 5 run as parallel subagents.

```mermaid
flowchart LR
    A["1 · Inventory<br/><i>gate</i>"] --> B["2 · Security"]
    A --> C["3 · Quality"]
    A --> D["4 · Performance"]
    A --> E["5 · Dependencies"]
    A --> F["6 · Architecture"]
    A --> G["7 · Tests & CI"]
    A --> H["8 · Docs & ops"]
    B & C & D & E & F & G & H --> R["9 · Report<br/>ranked findings + plan"]

    classDef gate fill:#0F7C8C,stroke:#1D1A16,color:#F6F1E7
    classDef pass fill:#DCEFF1,stroke:#1D1A16,color:#1D1A16
    classDef out fill:#F6F1E7,stroke:#1D1A16,color:#1D1A16,stroke-width:3px
    class A gate
    class B,C,D,E,F,G,H pass
    class R out
```

## What you get

<p align="center">
  <img src="../../docs/media/code-audit/report.svg" alt="Example report for a fictional project: 1 critical, 2 high, 2 medium, 1 low, 1 info finding, a findings table with file locations, and a 7/30/90-day plan" width="100%">
</p>
<sub>Illustrative example. The project is fictional; the layout follows <a href="assets/report-template.md"><code>assets/report-template.md</code></a>.</sub>

<details>
<summary><b>What one expanded finding looks like</b></summary>

```markdown
### F-01 — Hardcoded production database credentials in source

**Severity:** Critical
**Category:** Security
**Location:** `config/db.js:14`

**Why it matters**
Anyone with read access to the repo has the production database password,
and git history keeps it even after the line is deleted.

**Recommendation**
1. Rotate the credential immediately.
2. Read it from an environment variable; fail at boot if unset.
3. Add a pre-commit secret scanner.
4. Scan git history, not just HEAD.

**Effort to fix:** S
```

</details>

## Stat sheet

| | |
|---|---|
| **Input** | A repo path, a URL to clone, or an uploaded file tree |
| **Output** | Executive summary, findings table, expanded findings with evidence and a fix, a "what's good" section, and a 30/60/90-day plan |
| **Severity scale** | Critical · High · Medium · Low · Info. Inflation is called out as a failure: a lint issue is never Critical |
| **Rule it lives by** | Every finding cites `file:line` and gets verified first. No speculative alarms |
| **Big repos** | Over ~100k lines or 2,000 files it samples (entry points, auth code, the 10 most-changed files) and says what it skipped |
| **Without a shell** | Still works by reading files; the scripted checks become manual |
| **Ships with** | `scripts/inventory.sh`, `scan_secrets.sh`, `find_smells.sh`, `deps_check.sh`, six reference checklists, the report template |

## Plays well with

- **[test-assessment](../test-assessment/)**: when the audit says "tests are thin", this finds exactly where
- **[test-suggest](../test-suggest/)**: turns a gap into specific test cases

## Not for

Reviewing a diff or pull request (use the built-in `code-review` or `security-review`), or a single function.

---

<sub><a href="../../README.md#skill-index">← All 41 skills</a> · <a href="SKILL.md">Read the SKILL.md</a></sub>
