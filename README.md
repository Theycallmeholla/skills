# Claude Skills

A collection of custom skills for Claude (Claude Code / Cowork). Each skill is a self-contained folder under `skills/` with a `SKILL.md` (frontmatter + instructions) plus any `references/`, `assets/`, and `scripts/` it needs.

## Skills

### Code Quality & Testing

- **code-audit** — structured codebase audit: security, quality, performance, dependencies, architecture, testing hygiene, with a prioritized findings report
- **test-assessment** — assess a test suite: where tests are missing, where they're weak, which gaps matter
- **test-suggest** — propose specific, actionable test cases for a target module (without writing the code)

### UX & Product Testing

- **fresh-eyes** — approach an app or product as a genuine first-time user and surface what would confuse a newcomer
- **cover-story** — write the spoiler-free context brief a first-time tester gets (fresh-eyes companion)
- **ux-audit** — reconstruct a product flow and audit its usability with a severity-weighted findings report
- **ui-oddity-scan** — scan a page for duplicated copy, stray text, placeholder content, and other UI oddities

### Documentation

- **teach** — generate developer-facing "how X works" docs from a codebase
- **eli5-features** — generate plain-language end-user help docs from a codebase
- **walkthrough-gif** — generate browser walkthrough recordings (GIF/MP4) via Stagehand + Playwright

### Content

- **seo-blog-writer** — research-driven SEO articles built on search intent, verified claims, and original value

### Prompting & Workflow

- **genie-proof-prompts** — rewrite any prompt so a maliciously literal genie couldn't misinterpret it
- **handoff** — compact a working session into a handoff doc a fresh agent can pick up cold

## Using a skill

Copy the skill folder into your skills directory (`~/.claude/skills/` for Claude Code) or upload the folder as a skill in the Claude app.

## License

MIT
