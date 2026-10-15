# Autopilot

Runs a post from the client's answers to a reviewed, export-ready draft with **no user input in between**. Returns one report at the end: what shipped, what was cut for lack of evidence, what still needs the client, and the next step.

**Invocation:**

| Invocation | What happens |
|---|---|
| `autopilot <client> <topic>` | Runs `intake`, sends the questionnaire, and **waits once** for the replies. Everything after the replies runs on its own. |
| `autopilot <slug>` | Picks up wherever the post is. If intake replies or a packet already exist, it starts running immediately. |
| `intake … --auto` | Same as the first row. |

**Reads / Writes:** whatever each chained command declares. Autopilot has no files of its own. Each step writes only its own declared paths, exactly as when run by hand.
**Stops at:** Never publishes and never deploys. Never accepts a finding on the author's behalf. Never invents an answer to a question it would normally have asked.

Load `references/governing-rules.md` first. **Every rule still applies.** Autopilot removes the *pauses*, not the *rules*. Where a command would have asked the user, autopilot takes the default in the table below. That default is always the one that stays inside the evidence.

---

## The run

```
intake → [wait for replies] → file replies → brief → verify → write → review
       → revise → review → (revise → review, at most once more) → images → export
```

1. **intake** — normal. The questionnaire is the only pause in the whole run.
2. **File the replies** — `intake` Phase 5. Pasted or tool-sounding answers get filed as research, not as the client's words, and get listed in the final report.
3. **interview** — skipped unless the replies left a gap that *changes the thesis*. If one does, that's a hard stop (below). Any other gap is written from cited research in a neutral voice, per `evidence-rules.md`.
4. **brief → verify → write → review** — normal, with the defaults below.
5. **revise ↔ review** — up to **two** revise passes. Stop early when no `high` or `medium` finding is open. Low findings left open are listed, not chased.
6. **images** — writes the plan only. Nothing is generated. Assets the client hasn't supplied stay `needed`.
7. **export** — only if the site repo or files are reachable, or a paste-ready fragment can be built (see `export.md`). Never deploys.

## Where a command would ask, autopilot does this instead

| Command | Normally asks | Autopilot default |
|---|---|---|
| `brief` | A required connector is down | Proceed on what's available, record it as `degraded`, and name the limitation in the report. |
| `brief` | Format fit is wrong | **Hard stop.** A well-made piece of the wrong format isn't worth producing. |
| `brief` | Cannibalization says merge or refresh | **Hard stop.** The user decides whether to kill or update their own work. |
| `brief` | Information gain came up empty | **Hard stop.** The article would add nothing. |
| `verify` | A claim only the client can settle | Mark it `awaiting-client`. The draft leaves it out, or uses a narrower claim the evidence does support. |
| `write` | The one up-front gap question | Write that section from cited research in a neutral voice, and list the gap in the publish checklist. |
| `revise` | Which findings to accept | Accept none. A finding that can't be fixed from the evidence stays `open` and goes in the report. |
| `revise` | A `fabrication` finding needing client material | **Cut the claim.** This is the first of `revise`'s three legitimate moves, and the only one autopilot may use without the author. |
| `images` | Who has which asset | Mark it `needed`, with the ask written into the report. |
| `export` | Proceed despite `needed` assets or `awaiting-client` claims | Proceed, with placeholders and a TODO per gap. Open `boundary` or `fabrication` findings still block. |

## Hard stops

Autopilot halts, says why in two plain sentences, gives its recommendation, and keeps everything written so far. These are the only five:

1. **The research disproves the user's thesis** (Rule 1). It reports the conflict and does not reinterpret the thesis.
2. **Format fit is wrong.**
3. **Cannibalization says merge or refresh.**
4. **Information gain is empty.**
5. **A `boundary` or `fabrication` finding survives two revise passes.** In practice this shouldn't happen, because cutting the claim always closes a fabrication finding.

A step that fails to run (a tool error, a missing file) is a stop too. Report it the same way. Never skip it silently.

## What autopilot may not do

- Ask the user anything after the questionnaire, except at a hard stop.
- Mark any finding `accepted`.
- Fill an answer the client didn't give, including with a "reasonable" guess.
- Rewrite the thesis, the title set after `brief`, or an earlier draft version.
- Write a file outside the running command's declared paths.
- Run `publish`, which needs a live URL a human confirms.

## The final report

One message, plain language, under Rule 9. No IDs, scores or version counts.

```
## new-24x80-surface-grinder — autopilot done

Ready to export: ~750 words, argues <thesis in the user's framing>.

Left out for lack of evidence (2):
- "40+ years" — no founding year anywhere public; client didn't answer.
- Gate valve sizes — the answer read like pasted research, not the owner's words.

Still needs the client:
- Part-on-chuck photo, fit diagram.

Stopped early? No.

Files: .blog/posts/<slug>/draft-vN.md · <export path or paste-ready fragment>
Next: deploy, then `wltbo publish <slug>` with the live URL.
```

If autopilot hit a hard stop, lead with it instead: what stopped it, the recommendation, and the single command that resumes the run once the user decides (`autopilot <slug>`).

## Confirm and stop

One wait for the client's answers, then run every step on its own, staying inside the evidence. Take the cautious default wherever a step would have asked, stop only at the five hard stops, never publish, and end with one plain report.
