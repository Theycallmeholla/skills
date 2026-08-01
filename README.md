# Skills

A collection of custom skills for Claude (Claude Code / Cowork). Each skill is a self-contained folder under `skills/` with a `SKILL.md` (frontmatter + instructions) plus any `references/`, `assets/`, and `scripts/` it needs.

## Skills

### Code Quality & Testing

- **code-audit** — structured codebase audit: security, quality, performance, dependencies, architecture, testing hygiene, with a prioritized findings report
- **test-assessment** — assess a test suite: where tests are missing, where they're weak, which gaps matter
- **test-suggest** — propose specific, actionable test cases for a target module (without writing the code)

### Requirements & Discovery

- **swipe-deck** — Tinder-style swipe interview that pulls requirements out of someone's head, with a live saturation meter that decides when to stop
- **hot-seat** — one question at a time until a plan, decision, or idea actually holds up
- **opinion-interview** — capture the author's real opinions and stances before any content is written on their behalf
- **blog-topic-interview** — pre-writing interview for blog topics; produces an Opinion Packet for seo-blog-writer

### UX & Product Testing

- **fresh-eyes** — approach an app or product as a genuine first-time user and surface what would confuse a newcomer
- **cover-story** — write the spoiler-free context brief a first-time tester gets (fresh-eyes companion)
- **ux-audit** — reconstruct a product flow and audit its usability with a severity-weighted findings report
- **ui-oddity-scan** — scan a page for duplicated copy, stray text, placeholder content, and other UI oddities
- **conversion-audit** — audit a landing page through one lens: the ONE action it wants visitors to take, with cold-read persona agents
- **website-audit** — end-to-end site audit (technical, SEO, links, mobile, design, copy, conversion) in prospect and QA modes

### Documentation

- **teach** — generate developer-facing "how X works" docs from a codebase
- **eli5-features** — generate plain-language end-user help docs from a codebase
- **walkthrough-gif** — generate browser walkthrough recordings (GIF/MP4) via Stagehand + Playwright

### Content

- **seo-blog-writer** — research-driven SEO articles built on search intent, verified claims, and original value
- **ai-writing-detector** — score writing for AI-generation tells with a weighted 0–100 scorecard and ranked fixes
- **case-study-builder** — build client case studies through a low-overwhelm multiple-choice interview, with web-ready copy and a media plan
- **who-let-the-blogs-out** — end-to-end blog system with per-client memory: interview, brief, draft, score, revise, publish, refresh

### Prompting & Workflow

- **genie-proof-prompts** — rewrite any prompt so a maliciously literal genie couldn't misinterpret it
- **handoff** — compact a working session into a handoff doc a fresh agent can pick up cold
- **elihadhd** — restructure any response for an ADHD brain: TL;DR first, punchy steps, one clear next action
- **skills-repo-sync** — check for custom skills missing from this repo, add them in the expected format, and push
- **skills-repo-push** — the reverse direction: push repo skills back out to your local `~/.claude/skills`, with a dry run first and local-only skills left alone
- **skill-system-architect** — design the architecture for a multi-command skill system before any skill files get written
- **whiteboard** — plan work too big for one session as a map of investigation tickets on GitHub Issues
- **whiteboard-help** — quick-reference guide for the whiteboard planning system
- **napkin** — throwaway prototypes that answer exactly one design question
- **connotation-cop** — police project vocabulary, keep the glossary sharp, lock in decisions as ADRs

## Using a skill

Copy the skill folder into your skills directory (`~/.claude/skills/` for Claude Code) or upload the folder as a skill in the Claude app.

## License

MIT
