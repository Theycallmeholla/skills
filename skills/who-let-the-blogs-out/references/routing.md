# Routing — the no-argument menu

Loaded when blog is invoked with no command. The job is to answer "what should I do?" with something specific, drawn from actual state — not to print a static list and make the user figure it out.

**Never auto-run a command from here.** A bare invocation is a question. Answering it by doing something is how a system loses trust in its first week.

**A bare invocation is not the same as an invocation with intent attached** (`references/governing-rules.md`, Rule 10). `wltbo` alone is a question. `wltbo lets get started on the first one` is an instruction, and it routes to the work — not to this menu. Under Rule 10, an argument that names a choice the user already made is a choice already made. Read the state, find what they mean, and do the next useful thing.

## Procedure

1. Read `.blog/registry.json`. If it's missing, that's case A below — don't read anything else.
2. Identify the working client: the only one, the one named in the request, or the most recently updated.
3. Pick the case that matches and lead with its two or three recommendations, each with the exact string to type and a one-line reason drawn from real state.
4. Show the full command table underneath. The recommendation is the lede; the table is the fallback.

## The cases

**A — No `.blog/` yet.**

Lead with `who-let-the-blogs-out brand`. One line on why: nothing else can run until a client exists, because every other command reads the brand profile or writes into a client directory. Still show the full table so the shape of the system is visible.

**B — A client exists but `brandProfile` is `missing` or `partial`.**

Lead with `who-let-the-blogs-out brand <client>`, naming which sections are empty. A thin brand profile is the quiet cause of "it doesn't sound like us" — worth fixing before drafting anything, and it takes one conversation.

**C — A post has open findings.**

Lead with `who-let-the-blogs-out revise <slug>`, naming the count and the highest severity present. If any finding is `boundary` or `fabrication`, say so explicitly and lead with that instead — those two can't be accepted and block `publish`.

**D — A post is `drafted` but never reviewed.**

Lead with `who-let-the-blogs-out review <slug>`. A draft nobody scored is a draft nobody knows about.

This case should now be rare: `write`, `revise`, and `refresh` all chain into `review`, so a `drafted` post with no matching `review-vN.json` usually means the chain was interrupted. Say that when you recommend it — an unexplained gap in the pipeline is worth a sentence, not a silent re-run.

**E — Published posts have `staleClaims > 0`.**

Lead with `who-let-the-blogs-out refresh`, naming how many posts and roughly how old the oldest stale claim is. This is the case most likely to be genuinely news to the user, since nothing else surfaces it.

**F — A post is `idea` or `interviewed` with no brief.**

Lead with `who-let-the-blogs-out interview <slug>` if the packet is missing, `who-let-the-blogs-out brief <slug>` if it exists. Say which, and why that's the next gate.

**G — Nothing pressing.**

Lead with `who-let-the-blogs-out plan <client>` — it reads the published index and proposes what to write next, which is the useful default when nothing is mid-flight. Then show the table grouped by category.

When several cases apply, order by cost of ignoring: `boundary`/`fabrication` findings first, then stale claims on published posts, then unreviewed drafts, then everything else. A published article making a false claim outranks an unfinished draft every time.

## Shape of the response

Two or three picks, then the table. Something like:

```
2 posts need attention:

  blog revise local-seo-location-pages    3 open findings, 1 high (original-value)
  blog refresh                            4 published posts have claims that expired in June

Everything else:

Setup    brand · brand learn · brand show · plan
Capture  interview · interview <client> (foundational) · verify
Draft    brief · write · images
Ship     review · revise · publish · refresh
```

`review` isn't something the user runs after a draft — `write`, `revise`, and `refresh` each chain into it. Don't recommend it as a next step after one of those; recommend `revise` when findings are open.

Keep it short. This file is loaded on every bare invocation, which is the most frequent kind, so it should cost almost nothing to run.

## Reporting drift

If the registry disagrees with the records — a post listed as `published` with no URL, a `currentVersion` pointing at a draft that doesn't exist, a client directory with no registry entry — note it and continue presenting the menu.

**Surface it to the user only when it changes what they should do next.** A `currentVersion` pointing at a missing draft changes the menu, so say it in plain words. A stale timestamp does not, so keep it internal. Rule 9.

Do not repair it. Rule 5 of the state contract applies here as much as anywhere: someone asking "what should I do?" has not asked for six files to be rewritten.


## export

Reviewed draft, site-file time → `export <slug>`. Writes `lib/posts/<slug>.ts` + the `lib/blog.ts` entry; never deploys, never records — `publish` still does the recording once the post is live.
