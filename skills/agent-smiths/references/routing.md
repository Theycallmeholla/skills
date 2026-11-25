# Routing: the no-argument menu

Loaded only when agent-smiths is invoked with nothing to act on (bare `/agent-smiths`, or "use agent-smiths" with no plan and no lane file in view). Show the menu, wait for a choice. Don't run anything.

## 1. Look before showing the menu

Check quietly, if you have file access:

- Does `.agent-smiths/` exist in the current project?
- If yes, which lane files have lanes still `open`? Note the newest one's slug and how many lanes are open.
- Is there a plan in view? (earlier in this conversation, or an obvious plan file like `PLAN.md`, `docs/plan*.md`, a handoff doc)

## 2. Show the menu

Lead with the option that fits what you found.

**No `.agent-smiths/` folder, or no open lanes:**

```
agent-smiths: split a plan across parallel agents without them colliding.

1. split: give me a plan (paste it, or point at a file, board or handoff doc). I'll find which tasks can run at the same time, or tell you to run it in one go.
2. land: after the agents run, I check each one stayed in its lane.

Which one? (Most people start with split.)
```

If a plan is in view, name it in option 1: "split *the auth refactor plan from above*".

**Open lanes exist:**

```
agent-smiths: <slug> has <N> lanes still open.

1. land: check what the <slug> agents changed and whether they stayed in their lanes.
2. split: start a new plan.

Which one?
```

## 3. After the choice

Read the chosen command's reference (`split.md` or `land.md`) and follow it from Phase 1.
