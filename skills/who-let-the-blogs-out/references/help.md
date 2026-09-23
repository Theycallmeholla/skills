# Help

Loaded when someone types `help` or asks what the commands do. This file explains the system in plain language — no jargon, no schema. Print it adapted to what actually exists in `.blog/`, so the examples name real clients and real posts when there are any.

Do not run anything from here. Help explains; it never acts.

## What to say

Lead with the shape, not the list. Someone asking for help usually doesn't know the order things happen in, and a bare alphabetical menu doesn't tell them.

### The one-paragraph version

This turns "write a blog post" into a line of steps that hand work to each other, plus a filing cabinet that remembers things between sessions. The filing cabinet is why it's a system and not four separate tools: what you say in an interview today shapes what gets drafted next month, and what you published in February stops you accidentally competing with it in August.

### The normal path

For a brand-new post, in order:

```
interview   →   brief   →   write   →   review   →   revise   →   publish
```

- **interview** — asks what you actually think about the topic. Your opinions, your war stories, your real numbers, and what you refuse to say. Two or three questions at a time, and only ones it can't answer from what you've already told it.
- **brief** — reads the pages already ranking for the topic, picks the angle, and commits to the list of questions the article must answer. This is the cheap thing to reject before an expensive draft exists.
- **write** — drafts the article from the brief and that research. It can only claim experience you actually gave it. **Scores itself automatically when it's done** — you get the draft and the findings together.
- **review** — scores the draft two ways and lists what's wrong. It never edits.
- **revise** — fixes what review found, then re-scores automatically.
- **publish** — records that it went live, and sets expiry dates on every fact in it.

You never have to remember to run `review`. Anything that produces a draft runs it — a draft never reaches you unscored.

### The other five commands

- **brand** — run once per client. Records who they are, how they talk, and what they'll never say. Everything else reads it.
- **plan** — run when you don't know what to write next. Proposes topics and checks them against what you've already published.
- **verify** — checks claims against sources and files the durable ones for reuse.
- **images** — turns "we need pictures" into a specific list of what each image must show.
- **refresh** — finds published posts whose facts have gone stale and updates them without rewriting what still works.

### Two things that take a while but pay for themselves

**`interview <client>` with no topic** runs the long one — an hour, once, covering their whole field instead of one article. Every interview after it is short, because the bank is already full. Worth it for a client you'll write for repeatedly; not worth it for a single post.

**`brand learn <client> <posts>`** reads 5–10 things they've already published and works out how *they* write, so the AI-tells check stops flagging their actual style as a tell. It will refuse if their existing posts look AI-written — which is worth knowing on its own.

### Two that only look and never touch anything

**`brand show <client>`** prints everything the system knows about a client — their positions, their verified numbers and when those expire, every post and its state — and flags anything malformed. It writes nothing and has no repair mode.

**Typing `wltbo` with nothing after it** gives a short menu built from what's actually sitting there: which post has findings open, which published posts have facts going stale. That's the "what should I do now" answer.

### What it remembers

Three things per client, and they build up over time:

1. **Your brand profile** — how this client talks, what they sell, what they never say.
2. **Your opinion bank** — your positions, stories, and turns of phrase. Interviews stop re-asking things you already answered.
3. **Your fact vault** — verified numbers with expiry dates, so old posts can be caught when a stat goes bad.

Plus an index of every post published, which is what makes "you already wrote this one" possible.

### What it does not do

- It does not push to WordPress or any CMS. It produces the file; a human ships it.
- It does not invent experience. If you didn't say it, it won't claim it.
- It does not change what your post argues. You say what the article is about; research can qualify a claim inside it, but it can't quietly turn your post into a different one.
- It does not save an opinion as yours unless you actually said it, picked it, or agreed to it. Something you pasted in for it to read is a source, not your opinion.
- It does not make you decide things an editor should decide. If a call is ordinary, it makes it and tells you.
- It does not write social posts, emails, or case studies. Those are other skills.

### If it's talking like a robot

Say so. "Talk to me like I'm an idiot," "I don't understand," or just "what?" makes it shorter and plainer for the rest of the session — that's a rule, not a courtesy. It should also never be reading you ID numbers and scores unless you asked for them.

## Shorthand

`wltbo` works in place of the full name. `wltbo write` is the same as `who-let-the-blogs-out write`.

## Answering "which one do I use?"

If they describe a situation rather than naming a command, map it and say why:

| They say | Point them at |
|---|---|
| "I need a post about X" | `interview` if no packet exists, else `brief` |
| "what should we even write about" | `plan` |
| "does this read AI-written" | `review` |
| "it doesn't sound like us" | `brand` first, then `review` |
| "fix what you found" | `revise` |
| "is this old post still accurate" | `refresh` |
| "it went live" | `publish` |
| "we need pictures" | `images` |
| "is that number still true" | `verify` |
| "what do we even know about this client" | `brand show` |
| "review keeps flagging how I write" | `brand learn` |
| "we'll be writing for them a lot" | `interview <client>` — the long one |

## Keep it short

Someone asking for help is already a bit lost. Give the flow, the five extras, and one line on what to type first — then stop. If they want the full contract for a single command, they can ask for that command by name.

If `.blog/` doesn't exist yet, end with the one thing to type: `who-let-the-blogs-out brand` — nothing else can run until a client exists.
