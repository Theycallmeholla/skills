# Export

Writes the reviewed draft into the site's own files, in whatever format that site already uses for its posts. This command writes; it never deploys, and it never records — `publish` does the recording after the post is actually live.

**Reads:** `posts/<slug>/post.json` · `draft-v(currentVersion).md` · `media.json` · `claims.json` · `brief.md` · `review-v(currentVersion).json` · `clients/<c>/brand.md` (its `export` frontmatter block, when recorded) · two existing posts in the site's repo, plus whatever registers them, as the shape reference
**Writes:** the new post's file(s) where the site keeps posts, and the site's post index or registration file if it has one — **site files only** — plus, the first time a site's shape is learned and confirmed, the `export` block in `brand.md`'s frontmatter (that key and nothing else). Never other `.blog/` state, never `registry.json`, never the draft.
**Stops at:** Never deploys or pushes. Never records a publish. Never edits the draft or review state. Never guesses a site's format. Same hard gate as publish: open `boundary` or `fabrication` findings stop this command cold.

## Phase 1 — Gate

Read the review file for `currentVersion`. Open `boundary`/`fabrication` findings block — the site file is one deploy away from public, so the gate is publish's gate. Assets still `needed` and claims still `awaiting-client` warn; list them and ask one consolidated proceed question.

## Phase 2 — Learn the site's shape

Every site stores posts its own way. Export copies the site's existing pattern exactly; it never invents one.

**1. Recorded shape first.** If `brand.md` has an `export` block, use it. Open the post named in its `reference` and confirm it still matches the recorded format. If the site has changed since, say so in one line and re-learn from step 2. With no block, a sentence in `brand.md` or the site's own content docs (a content README, a contributing note) saying where posts go is the place to start.

**2. Otherwise, find how this site stores posts.** Start from what is already known, in this order: a file for this very post (search the repo for its slug, its title, or its opening sentence); the site's own content docs; then this client's other posts in the registry, by slug or URL. The file a post lives in is the pattern. Common shapes — examples, not a whitelist:

- markdown or MDX files with frontmatter in a content folder (Astro, Next.js MDX, Hugo, Jekyll, Eleventy)
- TypeScript or JavaScript objects in a posts folder, imported by an index file
- JSON or YAML data files read by a template
- no post files at all, because posts live in a CMS (WordPress, Webflow, Ghost, a headless CMS)

**3. Read two existing posts end to end** — preferably ones this system wrote (their slugs are in the registry), newest by the site's own date field rather than file modification time — plus whatever makes a post appear on the site (an index that imports posts, a collection config, a route file, a sitemap generator, an ordering rule) and every rule the site keeps about its content: a content README, a schema or type, validation gates, lint rules. Write down:

- where one post's file goes, and how its folder and file name are built — from the slug, or from other fields such as city, category, or kind
- the format: which frontmatter or object fields exist, which are required, and how the body is represented
- how a post becomes visible: an index entry, its position, any sort order
- how images, internal links, dates, and the author are written
- any type definition or schema the files must satisfy
- every transform the site's rules require: placeholders or tokens instead of literal numbers, banned elements, required fields the draft has no counterpart for

**4. Confirm once.** Show the shape in two or three plain lines — "Posts are MDX files in `src/content/blog/`, frontmatter has title, description, pubDate, heroImage; nothing else registers them" — and ask once. On a yes, write it to `brand.md`:

```yaml
export:
  postsDir: src/content/blog          # where one post's file goes
  filePattern: "<slug>.mdx"           # may use any field the posts carry, e.g. "<city>/<category>.md"
  byKind: null                        # when the folder depends on the post's kind: {intro: content/intros, post: content/blog}
  format: mdx                         # markdown · mdx · ts-object · js-object · json · yaml · other
  index: null                         # file that lists or imports posts, or null
  reference: src/content/blog/a-real-existing-post.mdx
  notes: "frontmatter: title, description, pubDate (YYYY-MM-DD), heroImage"
  learnedOn: 2026-10-07
```

**5. Check whether this post is already in the site.** Look for a file at the target path, or one carrying this post's slug or title. If there is one, compare it with the current draft before writing anything:

- **It matches the draft.** There is nothing to export. Say so.
- **The site's copy changed after it was written** — later commits, hand edits, another tool. Stop and show what changed. Never overwrite it silently: that reverts someone's work. If the user wants the newer draft in, write it with the site-side changes carried over unless they say otherwise.
- **The draft is newer and the site's copy is untouched.** Overwrite it, and say it's a re-export.

**Stop, and say so in one line, when:**

- **The site keeps posts in a CMS.** There are no files to write. The draft's CMS paste block from `write` is the deliverable; point at it.
- **The repo has no posts yet.** Ask where the first post should go and which existing page to copy the pattern from. Don't pick a format.
- **Two existing posts disagree with each other** (the site is mid-migration). Ask which one is current.

## Phase 3 — Convert

Map the draft onto the site's fields: the brief's title set onto the site's title, description, and SEO fields; the hero asset onto its image field; the one permitted byline onto its author field. Respect the site's length rules where a type or schema states them.

- **Apply every transform the site's rules require** (step 3's list). A site that writes counts as tokens gets tokens, not the draft's literal numbers.
- **Match the existing pattern on optional fields.** If the site's posts leave a field out, leave it out, even when the draft has a value for it.
- **Fields the draft doesn't carry** (a model name, an internal ID): on a re-export, copy them from this post's existing file. Otherwise ask once. Never invent one.
- **Dates**, in the site's own format: a first export uses the go-live date. A re-export keeps the original publish date and sets any updated date to today.

Convert the body into the site's body format. Wherever that format can't carry something the draft has — inline links, captions, a table — downgrade it to the nearest thing the format supports, and **record every downgrade in the report**. Internal links that become plain mentions still need adding on the other pages, so `publish`'s checklist depends on that list.

`[IMAGE: M-xxx]` markers become whatever the site uses for images, with `media.json`'s src, alt, and caption. Decorative images get empty alt text.

Where the format allows comments (TypeScript, JavaScript, MDX), keep a receipts comment at the top: the claim ledger's sources with URLs, and the NOT-claimed list. Where it doesn't, list the sources in the report instead.

## Phase 4 — Wire and check

Register the post the way the existing ones are registered — same file, same position rule (newest first, alphabetical, by date). If posts register themselves (a content collection, a folder the site globs), there is nothing to wire; say so.

Run the cheapest check the site has: a type check, a lint, a content-schema validation, or a build of that one page. Say plainly if the file shipped unchecked.

## Worked example — new-cursive-site

A front-end-only Next.js site. Posts are `Article` objects in `lib/posts/<slug>.ts`, imported and listed newest-first in `lib/blog.ts`.

- **Fields:** `title` = h1 · `desc` = dek · `seoTitle` = searchTitle **minus the brand suffix**, ≤ 60 chars (the type doc is the law) · `seoDesc` = metaDescription (120–158) · `image` = the hero asset's `/blog/...` path · `category`/`categoryLabel` by cluster · `readTime` = body words ÷ 225, "N min read" · `date` = "Mon D, YYYY" for the day it goes live, bumped at deploy if that slips · `author` = the only permitted byline.
- **Body:** markdown becomes `ArticleBlock[]`: paragraphs → `p`, `##`/`###` → `h2`/`h3`, image markers → `image` blocks, blockquotes → `quote`, lists → `list`, the closing conversion move → one `cta` block (its defaults are the on-page calendar).
- **No inline links** in this body format, so internal links become plain mentions, each recorded as a downgrade. External sources go in the file's top comment, copied from `claims.json`, alongside the house receipts block: cluster and query family, gap check, information gain, claim ledger, NOT-claimed list.
- **Wiring:** import at the top of the import block, entry first in `articles`; the newest-first comment in `lib/blog.ts` is the law. `tsc --noEmit` is the cheap check.

## Output

Files written, the link downgrades, anything the site's format couldn't carry (a hero caption, say), whether the check ran, then the two remaining steps: deploy, then `publish <slug>` with the live URL. Status stays untouched — a post isn't published until publish records a URL that resolves.
