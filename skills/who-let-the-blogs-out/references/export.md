# Export

Writes the reviewed draft into the site's code as the post file. This command writes; it never deploys, and it never records — `publish` does the recording after the post is actually live.

**Reads:** `posts/<slug>/post.json` · `draft-v(currentVersion).md` · `media.json` · `claims.json` · `brief.md` · `review-v(currentVersion).json` · the site's `lib/blog.ts` and one existing `lib/posts/*.ts` as the shape reference
**Writes:** `lib/posts/<slug>.ts` · `lib/blog.ts` (import + newest-first array entry) — **site files only.** Never `.blog/` state, never `registry.json`, never the draft.
**Stops at:** Never deploys or pushes. Never records a publish. Never edits the draft or review state. Same hard gate as publish: open `boundary` or `fabrication` findings stop this command cold.

## Phase 1 — Gate

Read the review file for `currentVersion`. Open `boundary`/`fabrication` findings block — the site file is one deploy away from public, so the gate is publish's gate. Assets still `needed` and claims still `awaiting-client` warn; list them and ask one consolidated proceed question.

## Phase 2 — Shape map (this repo)

The site is front-end-only: posts are `Article` objects in `lib/posts/<slug>.ts`, assembled newest-first in `lib/blog.ts`. Map the title set:

- `title` = h1 · `desc` = dek · `seoTitle` = searchTitle **minus the brand suffix**, ≤ 60 chars (the type doc is the law) · `seoDesc` = metaDescription (120–158)
- `image` = the hero asset's `/blog/...` path · `category`/`categoryLabel` by cluster · `readTime` = body words ÷ 225, "N min read" · `date` = "Mon D, YYYY" for the day it goes live — bump it at deploy if that slips · `author` = the only permitted byline

## Phase 3 — Block conversion

Markdown → `ArticleBlock[]`: paragraphs → `p`, `##`/`###` → `h2`/`h3`, `[IMAGE: M-xxx]` markers → `image` blocks with `media.json`'s src/alt/caption (decorative = empty alt), blockquotes → `quote`, lists → `list`, the closing conversion move → one `cta` block (its defaults are the on-page calendar).

**This body format has no inline links.** Internal links become plain-prose mentions — record every downgrade in the report so publish's add-links-to-this-post checklist still happens on the other pages. External sources move to the file's top comment, copied from `claims.json` with URLs. Reproduce the house comment block: cluster + query family, gap check, information gain, claim ledger, NOT-claimed list. That comment is where this site keeps its receipts.

## Phase 4 — Wire and check

Import at the top of the import block, entry first in `articles` — the newest-first comment in `lib/blog.ts` is the law. Run `tsc --noEmit` if it's cheap; say plainly if the file shipped unchecked.

## Output

Files written, the link downgrades, anything the template can't render (a hero caption, say), then the two remaining steps: deploy, then `publish <slug>` with the live URL. Status stays untouched — a post isn't published until publish records a URL that resolves.
