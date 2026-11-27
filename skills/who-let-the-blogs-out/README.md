<p align="center">
  <img src="../../docs/media/who-let-the-blogs-out/front.svg" alt="Who Let The Blogs Out card front: plan, interview, write, publish" width="48%">
  <img src="../../docs/media/who-let-the-blogs-out/back.svg" alt="Who Let The Blogs Out card back: a blog system with per-client memory that plans, interviews the author, verifies claims, writes, scores, revises and exports into your site" width="48%">
</p>

<!-- skill-family:start -->
**The family:** these skills are parts of this one, each also installable on its own.

<p><a href="../../skills/blog-topic-interview/"><img src="../../docs/media/blog-topic-interview/thumb.svg" width="140" align="top" alt="Blog Topic Interview"></a><a href="../../skills/seo-blog-writer/"><img src="../../docs/media/seo-blog-writer/thumb.svg" width="140" align="top" alt="SEO Blog Writer"></a><a href="../../skills/ai-writing-detector/"><img src="../../docs/media/ai-writing-detector/thumb.svg" width="140" align="top" alt="AI Writing Detector"></a></p>
<!-- skill-family:end -->

> **TL;DR:** A blog system that remembers each client. It interviews the real author, keeps every claim inside the evidence, scores every draft before you see it, and writes the finished post into your site's files. It never deploys or publishes on its own.

## Say this

`wltbo` · `wltbo write` · `write a blog post` · `refresh this post` · `it doesn't sound like us` · `it reads AI-written` · `the facts are made up` · `it's too thin`

A bare `wltbo` shows a menu built from what already exists for the client. It never auto-runs anything.

## The command map

<p align="center">
  <img src="../../docs/media/who-let-the-blogs-out/commands.svg" alt="14 commands in five groups: Setup (brand, intake, plan), Capture (interview, verify), Draft (brief, write, images), Ship (review, revise, export, publish, refresh) and Run (autopilot)" width="100%">
</p>

## How a post moves

```mermaid
flowchart LR
    BR["brand<br/><i>once per client</i>"] --> IN["intake<br/>one questionnaire"]
    IN --> IV["interview<br/>the author's real take"]
    IV --> VE["verify<br/>claims + expiry dates"]
    VE --> BF["brief<br/>angle + reader questions"]
    BF --> WR["write"]
    WR --> RV["review<br/>scored, never edits"]
    RV -->|open findings| RS["revise"]
    RS --> RV
    RV -->|clean| EX["export<br/>into the site's files"]
    EX --> PB["publish<br/>record URL + re-verify dates"]
    PB -.aging post.-> RF["refresh"]
    RF --> RV

    classDef step fill:#F3EEE6,stroke:#1D1A16,color:#1D1A16
    classDef hot fill:#F25A05,stroke:#1D1A16,color:#F6EFE3
    classDef out fill:#1C1B1A,stroke:#1D1A16,color:#F6EFE3
    class BR,IN,IV,VE,BF,RS,RF step
    class WR,RV hot
    class EX,PB out
```

Steps whose output already exists get skipped: pick a topic yourself and you're not sent back through `plan`. `autopilot` runs intake replies through to an export-ready draft with no input, stopping only at five hard stops.

## The rules it lives by

| | Rule |
|---|---|
| **1** | Your thesis is sticky. Research can support or qualify it, not replace it |
| **2** | Corrections win immediately, no defending the old reading |
| **3** | Evidence has three bands (explicit, implied, uncertain) and the article says which |
| **4** | Original value never means manufactured disagreement |
| **5** | No author stance is written from AI inference |
| **6** | Ordinary editorial calls get made without asking |
| **7** | Effort matches consequence |
| **8** | Confusion shortens the answer |
| **9** | The machinery stays internal: no IDs, scores or counts read aloud |
| **10** | The workflow adapts to what already exists |
| **11** | Research before asking; client questions go out once |

<details>
<summary><b>What it remembers, per client and per post</b></summary>

```text
.blog/
├── registry.json            what exists, two counts per post
├── clients/<client>/
│   ├── brand.md             voice and brand profile
│   ├── opinion-bank.md      the author's real positions, with provenance
│   └── facts.json           verified facts, each with an expiry date
└── posts/<slug>/
    ├── packet.md            the interview: stories and stances
    ├── brief.md             angle, intent, committed reader questions
    ├── claims.json          every claim and its evidence
    ├── media.json           image plan
    ├── draft-v1.md …        append-only: a new version, never an edit
    └── review-v1.json …
```

State lives in the project, never in the skill folder.

</details>

## Stat sheet

| | |
|---|---|
| **Input** | A client, a topic or command, and for `interview`, the author's real answers |
| **Output** | Scored drafts, then the post written into your site in the format its existing posts use |
| **Quality bar** | Something specific to this author or business, or it isn't done |
| **Truth rule** | Nothing is presented as first-hand experience unless it's in the interview or the fact vault |
| **Never** | Deploys, publishes on autopilot, or invents a disagreement to sound original |
| **Ships with** | One reference file per command, the governing rules, `scripts/check_wiring.py`, `scripts/tells_metrics.py`, acceptance tests |

## Plays well with

- **[blog-topic-interview](../blog-topic-interview/)** and **[seo-blog-writer](../seo-blog-writer/)**: the interview and writing steps as standalone skills, writing the same `.blog/` state
- **[ai-writing-detector](../ai-writing-detector/)**: the AI-tells scorer on its own, for any text
- **[case-study-builder](../case-study-builder/)**: for case studies, which this skill doesn't write

## Not for

Social posts, emails, case studies, site audits ([website-audit](../website-audit/)), or content calendars.

---

<sub><a href="../../README.md#skill-index">← All skills</a> · <a href="SKILL.md">Read the SKILL.md</a></sub>
