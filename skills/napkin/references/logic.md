# Logic Napkin

A tiny interactive terminal app that lets the user drive a state model by hand. Right when the question is about **business logic, state transitions, or data shape** — things that look reasonable on paper and only feel wrong once pushed through real cases. If the question is "what should this look like", wrong branch — use [ui.md](ui.md).

## Process

### 1. Isolate the logic in a portable module

The bit that answers the question goes behind a small, pure interface that could be lifted into the real codebase later. The terminal shell around it is throwaway; the logic module is not. Pick the shape that fits the question:

- **Pure reducer** — `(state, action) => state`. Discrete events, single state value.
- **State machine** — explicit states + transitions. Right when "which actions are even legal now" IS the question.
- **Set of pure functions** over a plain data type. Right when there's no current state, just transformations.
- **Class/module with a clear method surface** — when the logic genuinely owns ongoing internal state.

Keep it pure: no I/O, no terminal code, no console output for control flow. The shell imports the module; nothing flows the other way. This purity is what lets the validated logic survive the napkin's deletion.

### 2. Language and tooling

Whatever the host project uses. No new package managers or runtimes for a throwaway. Docs repo with no runtime? Ask.

### 3. Build the smallest shell that exposes the state

A lightweight TUI: on every action, clear the screen and re-render one full frame — a stable view, not growing scrollback. Each frame, top to bottom:

1. **Current state**, pretty-printed and diff-friendly — one field per line or formatted JSON. Bold field names, dim secondary info (IDs, timestamps, derived values). Raw ANSI codes are fine (`\x1b[1m` bold, `\x1b[2m` dim, `\x1b[0m` reset); no styling library unless the project already has one.
2. **Keyboard shortcuts** at the bottom: `[a] add item  [x] cancel  [t] tick clock  [q] quit`.

Loop: init state → render → read one keystroke → dispatch to the logic module → re-render. The whole frame fits on one screen.

Seed the initial state with data that makes the hard cases reachable in a few keys — an empty state that takes 15 keystrokes to reach the interesting transition wastes the user's patience.

### 4. Hand it over

Give the run command. The user drives it; the payoff moments are "wait, that shouldn't be possible" and "huh, I assumed X" — bugs in the *idea*, which is what the napkin exists to find. If they ask for new actions, add them; napkins evolve.

### 5. Capture and clean up

Per the SKILL: QUESTION/ANSWER/EVIDENCE captured somewhere durable, then the validated reducer/machine/functions get absorbed (rewritten properly) and the shell gets deleted.

## Anti-patterns

- **Tests.** A napkin that needs tests is no longer a napkin.
- **The real database.** In-memory unless persistence IS the question.
- **Generalizing.** No "what if we later support X." One question.
- **Blurring logic and shell.** A reducer that calls console output or reads keys is no longer portable — and portability is the one thing worth keeping.
