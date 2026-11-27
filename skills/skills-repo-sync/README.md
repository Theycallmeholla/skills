<p align="center">
  <img src="../../docs/media/skills-repo-sync/front.svg" alt="Skills Repo Sync card front: Adds your missing skills to the repo, one yes each" width="48%">
  <img src="../../docs/media/skills-repo-sync/back.svg" alt="Skills Repo Sync card back: finds custom skills the repo is missing, asks about each one with no as the default, scans for secrets, commits, and asks again before pushing" width="48%">
</p>

> **TL;DR:** It looks for skills you wrote that aren't in your public skills repo yet and asks you about each one, one at a time. The ones you say yes to get copied in, checked for secrets, listed in the README and committed, and nothing gets pushed until you say yes again.

## Say this

`sync my skills repo` · `check for new skills` · `update the skills repo` · `push my skills to github` · `backup my skills` · `are any skills missing from my repo?`

Also right after a new custom skill has been created.

## How it runs

```mermaid
flowchart LR
    E["Enumerate<br/><i>account skills + Claude Code skills</i>"] --> X["Drop exclusions<br/>installed, stock, plugin, denylist"]
    X --> D["Diff against<br/>the repo"]
    D --> A{"Publish this one?<br/><i>one skill at a time</i>"}
    A -->|no or unclear| N["Skipped"]
    A -->|clear yes| C["Copy folder<br/>dereference symlinks"]
    C --> R["Add README bullet"]
    R --> S["Secret and<br/>sensitive-data scan"]
    S --> G["Commit locally"]
    G --> P{"Push now?<br/><i>asked in the moment</i>"}
    P -->|yes| U["git push"]
    P -->|not approved| L["Commit stays local<br/>push command reported"]

    classDef step fill:#E3E7EE,stroke:#1D1A16,color:#1D1A16
    classDef you fill:#1D2433,stroke:#1D1A16,color:#F6F1E7
    classDef out fill:#F6F1E7,stroke:#1D1A16,color:#1D1A16,stroke-width:3px
    class E,X,D,C,R,S,G,N step
    class A,P you
    class U,L out
```

A skill that trips the scan is left out of the sync and reported. Never push first and ask later.

## What you get

| Artifact | Format |
|---|---|
| **Skill folder** | `skills/<skill-name>/` with `SKILL.md` and any `references/`, `assets/`, `scripts/`, copied verbatim |
| **README index line** | `- **skill-name** — lowercase one-line summary`, under an existing `###` category |
| **Commit** | `Sync skills: add <names>` |
| **Push gate** | It stops, shows the skill names, file count and anything notable, and asks for an explicit yes |
| **Changed skills** | Listed in the report, not overwritten, unless you approve |

<sub>Formats quoted from <a href="SKILL.md">the SKILL.md</a>.</sub>

## What never gets synced

The only test for inclusion is whether you wrote it. Installed isn't authored.

| Excluded | How it's spotted |
|---|---|
| **Installed third-party skills** | Located in or symlinked into `~/.agents/skills/`, or frontmatter crediting another author, homepage, licence or package |
| **Anthropic stock skills** | A fixed list in the SKILL.md (`docx`, `pdf`, `pptx`, `xlsx`, `skill-creator` and others) |
| **Plugin skills** | Names with a colon, like `small-business:*` |
| **Private skills** | Anything matching a glob in the repo's `.publish-denylist`. Never offered at all; CI fails the build if one lands in `skills/` |
| **Unclear provenance** | It asks. It never defaults to syncing |

## Stat sheet

| | |
|---|---|
| **Input** | Your local skill folders (account skills cache and Claude Code skills), a clone of the repo, and you, to answer each prompt |
| **Output** | New skill folders, one README bullet each, a local commit, and a push only after a fresh yes |
| **Default answer** | No. A skill that doesn't get a clear yes stays out, however safe it looks |
| **Secret scan** | API keys, tokens, JWTs, private keys and assignment-style secrets, plus client names, Sheet or Doc IDs, internal URLs and real emails or phone numbers |
| **Push approval** | Must come in the moment. "Sync my repo" up front doesn't count |
| **Verifies** | Every new `SKILL.md` frontmatter parses, no symlinks left, README bullet count matches folder count |
| **Ships with** | `SKILL.md`, `platforms/chatgpt.md` (a ChatGPT version that syncs supplied skills through a feature branch and pull request) |

## Plays well with

- **[skills-repo-push](../skills-repo-push/)**: the other direction, repo to your local skills folder

---

<sub><a href="../../README.md#skill-index">← All skills</a> · <a href="SKILL.md">Read the SKILL.md</a></sub>
