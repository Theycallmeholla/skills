# Headline Contract

Loaded by `brief` (decides the fields), `write` (writes headings that honor them), `review` (checks they still agree), and `refresh` (re-checks after edits).

The problem this solves: most posts treat the title as one string pasted into six different slots, then have a heading structure improvised during drafting. Both are fixable by deciding once, early, and checking later.

## The six fields

One article, six coordinated fields, each doing a different job.

| Field | Job | Written for |
|---|---|---|
| `searchTitle` (`<title>`) | Browser tab and the primary signal for Google's title link | The searcher scanning results |
| `h1` | The visible article title | The reader who already clicked |
| `headline` (structured data) | Identifies the article headline to parsers | Machines. Usually the H1 or very close. |
| `dek` | One sentence under the H1 saying what this covers | The reader deciding whether to keep going |
| `metaDescription` | Why this result is worth clicking | The searcher, again — but a different pitch than the title |
| `slug` | Stable page identifier | Nobody. It just has to never change. |

**The rule is: same claim, different phrasing.**

Divergence between `searchTitle` and `h1` is permitted — they genuinely do different jobs, and forcing them to be byte-identical usually makes one of them worse. But divergence is a permitted side effect of optimizing two jobs, never a goal. Google's single most common reason for rewriting a displayed title is a `<title>` that doesn't match what's visibly on the page, so manufacturing difference for its own sake *increases* rewrite risk. If the two make different claims, one of them is wrong.

A working example:

```
searchTitle:  Local SEO Location Pages: A Scalable Framework | Cursive Media
h1:           How to Build Location Pages That Do Not Look Mass-Produced
dek:          A practical framework for creating useful city pages at scale.
meta:         Learn how to create useful, differentiated location pages without
              producing thin or repetitive local SEO content.
slug:         local-seo-location-pages
```

Same article, same promise, five different framings of it. The meta description does not restate the title — it adds the reason to click.

## Where each field is decided

`plan` reserves the **slug** at idea stage, because a slug is a stable page identifier and changing it after publish costs a redirect. Everything else is decided by `brief` and stays editable until `publish`.

`write` may not change the title set. If the draft outgrew its promise — the article ended up making a different argument than the brief committed to — that's a finding for `review`, not a quiet edit. A brief that the draft can silently overwrite has stopped being a gate.

## Heading craft

Applied when `brief` builds the outline and when `write` renders it.

**One obvious H1**, and it should be the most visually prominent text on the page. Multiple `<h1>` elements are not technically forbidden, but the cleaner approach is one — and the real failure mode isn't the tag count, it's several headings at *equal visual weight* competing to be the page's true title. When that happens, the page has no clear main title, which is one of the conditions that gets a title rewritten in search results.

**H2s are the reader's questions**, taken from the brief's coverage targets. Not keyword slots. If a heading exists primarily to hold a phrase, delete it — the article is not improved by a heading nobody wanted to read.

**The skim test.** Someone who reads only the headings should come away with the argument, not just the topic list. This is the fastest single check on whether an outline is actually reasoning about something or just enumerating subtopics.

**Section depth follows value, not symmetry.** Three sections of near-identical length is a strong tell that the outline was filled rather than thought through. This overlaps with `voice-and-tells.md`, which owns the rhythm rules in full — don't duplicate them here, load that file when drafting.

## Working targets — heuristics, not rules

State the status when you use these, because a target quoted without its status gets enforced as if it were a requirement, and then accuracy gets sacrificed to hit a character count. That trade is always wrong.

```
searchTitle       ~45-65 characters
h1                ~6-14 words
metaDescription   ~140-165 characters
slug              3-7 meaningful words, lowercase, hyphenated, no stop words
```

What's actually true: Google publishes **no character limit** for the `<title>` element — titles are truncated for display, typically to fit device width, which is a rendering behavior and not a rule. Google also no longer publishes a character limit for the Article `headline` property; the current guidance is only to consider a concise title because long ones may be truncated on some devices. The old 110-character `headline` rule is gone.

So: never remove an important word to hit 60 characters. A title that is accurate at 71 characters beats one that is vague at 58.

## What blog cannot enforce

Google's actual concern is **visual** prominence — whether the H1 stands out from everything else on the rendered page. Blog emits markdown. Whether the rendered H1 outranks every H2 is a template decision owned by the CMS, and no amount of markdown discipline controls it.

So `review` reports heading prominence as a recommendation with that caveat attached, not as a pass/fail. Once a post has a live URL, the rendered page can be fetched and checked for real — that's the only point at which the check becomes factual rather than advisory.

Saying this plainly is better than implying an enforcement the system can't deliver. A checklist item that silently means "we hope so" is worse than one marked "verify in the template."

## The checks `review` runs

These produce findings in existing categories — `structure` for craft, `technical-seo` for field coordination. No new category.

- H1 and `headline` describe the same article the body actually delivers
- `searchTitle` is neither the H1 pasted verbatim nor a different claim
- `metaDescription` gives a reason to click rather than restating the title
- No heading exists primarily to hold a keyword
- Heading levels are not skipped (H2 → H4), which breaks screen-reader navigation
- The dek is a paragraph, not a heading — this is the detail most templates get wrong
- Visible "Updated" date matches `dateModified`, and the date was bumped because something changed
- Slug is unchanged since `plan` reserved it, or a redirect is noted in the post's `notes.md`
