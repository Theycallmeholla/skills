# Browser Mode: Auditing a Live App

You have a running app and a browser automation tool (Playwright, Claude in Chrome, Puppeteer, or similar). This is the truest mode — you experience the flow as a user does, with real latency, real feedback, real layout. The discipline is to behave like a first-time user, not an operator who already knows the answers.

## Tool selection

This machine typically exposes multiple browser MCP servers. Prefer **playwright-mcp** for clean-profile audits with file-based screenshot evidence (`browser_take_screenshot` saves named files). Use **claude-in-chrome** when the flow needs the user's real authenticated session — note that its screenshots land in context, not on disk, so adapt the evidence convention to descriptive notes. Load all the MCP tools you'll need in ONE batched ToolSearch call before starting.

## Prerequisites

- A reachable URL for the flow's entry point.
- A browser tool available in the environment. If none is connected, fall back to spec mode (work from a description/screenshots) or code mode, and note the limitation.
- Test credentials or test data if the flow requires login or payment. Ask the user for these rather than inventing them, and never enter real payment details — use the provider's documented test values, or stop at the payment step and audit it visually.

## Step 1: Walk the happy path first

Navigate the flow start to finish as a new user would, at each step capturing:

- A **screenshot** (your primary evidence — name them `step-01-landing.png`, `step-02-email.png`, …; if the tool cannot save screenshot files, record the step's evidence as inline observations instead).
- The **URL** and a one-line note of what the screen asks and what you did.
- Anything that made you hesitate, re-read, or guess. Those hesitations *are* the findings — record them in the moment, before you "learn" the flow and stop noticing.

This pass produces the Phase 1 flow map.

## Step 2: Time and feel the transitions

- Note **latency** between actions and whether the UI gives feedback during it (spinner, skeleton, disabled button) or appears frozen.
- Note **confirmation** after meaningful actions — is it clear something happened?
- Note **progress** — on a multi-step flow, do you always know how far you are?

## Step 3: Probe the unhappy paths

A happy-path-only audit misses where flows actually break. Deliberately trigger:

- **Validation errors** — submit empty, submit a malformed email, mismatched passwords. Read the error: does it say what's wrong and how to fix it? Where does it appear?
- **Back/forward** — use the browser back button mid-flow. Is progress preserved or lost? Does the app break?
- **Refresh** — reload mid-flow. Does state survive, or does the user restart?
- **Edit-earlier** — try to change a value entered two steps ago without restarting.
- **Empty / no-results** states where applicable.
- **Interruption** — abandon and return; is there resume?

Capture a screenshot of each.

## Step 4: Resize and re-walk on mobile

Set the viewport to a phone size (e.g., 390×844) and walk the primary path again. Watch for:

- Tap targets too small or crowded; primary action out of thumb reach.
- On-screen keyboard covering the active field or submit button.
- Horizontal scroll, overlap, text too small, sticky bars eating the viewport.

Capture mobile screenshots alongside the desktop ones.

## Step 5: Quick accessibility probe

- **Keyboard-only** — Tab through the flow. Can you complete it without the mouse? Is the focus ring visible? Does focus move sensibly on step change / modal open?
- **Names** — do icon-only buttons have accessible names? (Inspect the accessibility tree if the tool exposes it.)
- **Contrast** — flag obviously low-contrast text or color-only state signals.

## Evidence format for browser mode

Reference findings by **step + screenshot filename** ("Step 4 (`step-04-payment.png`): …"). Embed or attach the screenshots with the report if the environment supports it. (When the tool cannot save screenshot files, reference findings by step number plus a descriptive inline observation instead.) A screenshot of the confusing moment is the most persuasive evidence a UX audit can carry.

## Cautions

- **Don't bypass human-verification (CAPTCHA) or bot-detection** — respect it and note it as a step the audit couldn't automate past.
- **Don't submit real personal or payment data.** Use test values; stop and audit visually where you can't.
- **Don't perform destructive or irreversible actions** (delete account, place a real order) without explicit user confirmation — audit up to that point.
- Behave like a user, not an exploit: you're evaluating the experience, not stress-testing security.
