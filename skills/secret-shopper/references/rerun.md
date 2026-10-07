# Re-run mode

For when the user wants to know what changed since a previous secret-shopper run: "run it again after the fixes", "did they fix it?", "check again". The answer they need is a scorecard against last time, not a fresh report they have to compare by hand.

## Find the last report

Look for `secret-shopper-<site>-*.md` in the working folder, or use the one the user points at. Take the newest. If there isn't one, say so in one line and do a normal first run.

## Run first, compare after

**Read only the old report's header before the run:** the shopper card, device, browser, mode, entry point, and the task list. Do not read its moments, tasks results, or builder notes yet.

The old moments say exactly where everything is and what goes wrong. A shopper who has read them knows where the price list lives, which is the one thing the test depends on them not knowing. So the run happens blind, and the comparison happens after.

Reuse from the header, unchanged:

- the same shopper card, including patience
- the same device size and browser
- the same tasks, in the same words
- the same entry point

Then run the whole thing as SKILL.md describes: first look, tasks, wander, moments log, leak check. Nothing about the run changes.

If a task's goal no longer exists on the site (the booking form was removed on purpose), note it, skip it, and mark it ❓ in the comparison. Don't invent a replacement task.

## Then match old against new

Open the old report only after the leak check. Match by **where it happened and what the shopper hit**, not by tag or wording.

For every old moment:

- **✅ Fixed** — the thing it pointed at is gone or now works. Say what you saw instead.
- **➖ Still there** — same place, same reaction.
- **🔀 Changed** — the original problem is gone, but something else trips the shopper in the same spot.
- **❓ Couldn't check** — this run never reached that spot (different path, hard stop, task skipped). Not reaching a page is never evidence it was fixed.

Every moment in this run with no match in the old report is **🆕 New**. A new moment on a screen the fixes touched is probably a regression from the fix. Say that plainly.

For every task, compare the old and new result, steps, and dead ends.

## Report additions

Save a new file with today's date. Never overwrite the old report; the pair is the record.

Add this section right after the TL;DR:

```
## Since last run ([old date])
**Fixed:** N · **Still there:** N · **Changed:** N · **New:** N · **Couldn't check:** N

| Last time | Moment | Now | What I saw this time |
|---|---|---|---|
| #3 | WHERE'S…? · Blocker — no prices anywhere | ✅ Fixed | "Prices" in the menu, one tap |
| #5 | TWICE? · Papercut — two phone numbers | ➖ Still there | same red bar, same second number |
| — | WAIT, WHAT? · Slowdown — new popup on load | 🆕 New | appeared before the first scroll |
```

The Tasks table gets a **Last time** column next to **Result**. The TL;DR verdict compares the two runs in the shopper's voice: "Last time I gave up finding prices. This time it took one tap."

Builder notes cover what is still there and what is new. Anything fixed stays out of them.
