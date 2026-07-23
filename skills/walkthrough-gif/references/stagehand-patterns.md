# Stagehand Patterns Reference

> **This reference targets Stagehand v3** (verified against `@browserbasehq/stagehand@3.6.0`).
> Before scaffolding, run `npm view @browserbasehq/stagehand version` — if a new major has shipped,
> re-verify these patterns against https://docs.stagehand.dev before generating code.

## v3 API essentials (differences from older code you may have seen)

- `act()` / `extract()` / `observe()` live on the **stagehand instance**, not the page:
  `await stagehand.act("click the login button")`. The v2 form `page.act({ action: ... })` is gone.
- `stagehand.page` is deprecated — get pages via `stagehand.context.pages()[0]` or pass an explicit
  `{ page }` option to `act()`.
- `stagehand.init()` takes **no options**. Headless/viewport/launch args go in the constructor's
  `localBrowserLaunchOptions`.
- There is **no `recordVideo` option** in v3's `localBrowserLaunchOptions` (v3 uses its own CDP
  driver, not Playwright, under the hood). Video recording is done by connecting Playwright to
  Stagehand's browser over CDP — see the template below. This is the officially documented
  integration path (`docs.stagehand.dev/v3/integrations/playwright`).
- Models are provider-prefixed strings: `"anthropic/claude-sonnet-4-6"`, `"openai/gpt-5"`, etc.
  API keys auto-load from env (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, ...).

## Installation

```bash
npm install @browserbasehq/stagehand@^3.6.0 playwright@^1.61.1 dotenv@^17.4.2
npm install -D typescript@^6.0.3 tsx@^4.23.0 @types/node
npx playwright install chromium
```

> **API key prerequisite:** Stagehand calls an LLM for every `act()`/`observe()`/`extract()`.
> Set `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY` / `GOOGLE_GENERATIVE_AI_API_KEY`, matching the
> model provider you configure) in `.env` before running anything.

### package.json template

```json
{
  "name": "walkthrough-demo",
  "private": true,
  "version": "1.0.0",
  "scripts": {
    "walkthrough": "tsx src/walkthrough.ts",
    "convert": "bash scripts/convert.sh"
  },
  "dependencies": {
    "@browserbasehq/stagehand": "^3.6.0",
    "dotenv": "^17.4.2",
    "playwright": "^1.61.1"
  },
  "devDependencies": {
    "@types/node": "^24.0.0",
    "tsx": "^4.23.0",
    "typescript": "^6.0.3"
  }
}
```

Pin the Stagehand major to what `npm view @browserbasehq/stagehand version` reports at scaffold
time — do not leave the dependency unversioned.

### tsconfig.json template

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "outDir": "dist"
  },
  "include": ["src"]
}
```

(`resolveJsonModule` matters if the walkthrough imports a `cookies.json` — see Auth Patterns.)

---

## Basic Script Structure

```typescript
import { Stagehand } from "@browserbasehq/stagehand";
import { chromium, type Page } from "playwright";
import * as fs from "fs";
import * as path from "path";
import dotenv from "dotenv";
dotenv.config();

const OUTPUT_DIR = path.join(__dirname, "../output");
const VIEWPORT = { width: 1280, height: 800 };

async function runWalkthrough() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  const stagehand = new Stagehand({
    env: "LOCAL",
    model: "anthropic/claude-sonnet-4-6", // provider-prefixed; check docs.stagehand.dev for the newest supported Claude model
    // ANTHROPIC_API_KEY auto-loads from .env
    localBrowserLaunchOptions: {
      headless: false, // set true for CI; false is better for debugging
      viewport: VIEWPORT,
    },
    verbose: 1,
  });

  await stagehand.init(); // init() takes no options in v3

  // Connect Playwright to Stagehand's browser over CDP so we can record video.
  // (v3 has no recordVideo launch option — Playwright owns the recording context.)
  const browser = await chromium.connectOverCDP({
    wsEndpoint: stagehand.connectURL(),
  });
  const recordingContext = await browser.newContext({
    viewport: VIEWPORT,
    recordVideo: { dir: OUTPUT_DIR, size: VIEWPORT },
  });
  const page = await recordingContext.newPage();
  const video = page.video();

  try {
    // Inject click overlay (see below)
    await injectClickOverlay(page);

    // === WALKTHROUGH STEPS GO HERE ===
    // Every stagehand.act() targets the recording page via { page }.
    await page.goto("https://example.com", { waitUntil: "networkidle" });
    await page.waitForTimeout(1500);

    await stagehand.act("click the login button", { page });
    await page.waitForTimeout(1000);

    // Secrets/typed values go through `variables` (%name% placeholders are
    // substituted locally and NOT sent to the LLM). Never inline them in the
    // instruction string — that text IS sent to the LLM.
    await stagehand.act("type %email% into the email field", {
      variables: { email: process.env.DEMO_EMAIL! },
      page,
    });
    await stagehand.act("type %password% into the password field", {
      variables: { password: process.env.DEMO_PASSWORD! },
      page,
    });
    await stagehand.act("click the sign in button", { page });
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    // === END STEPS ===

    console.log("Walkthrough complete. Saving video...");
    await page.waitForTimeout(1000); // let the final frame settle
  } finally {
    // Closing the recording context flushes the video file to disk.
    await recordingContext.close();
    await stagehand.close();
  }

  // Playwright names the .webm with a random hash; save it to a stable name.
  if (video) {
    const dest = path.join(OUTPUT_DIR, "walkthrough.webm");
    await video.saveAs(dest);
    console.log(`Video saved: ${dest}`);
    console.log("Now run: bash scripts/convert.sh");
  } else {
    console.warn("No video handle — check that recordVideo was set on the context.");
  }
}

runWalkthrough().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

---

## `act()` Translation Patterns

Natural language → `stagehand.act()` calls. Be specific but not overly prescriptive about
selectors. All calls in the walkthrough should pass `{ page }` so they hit the recording page.

| User Description | `act()` Call |
|---|---|
| "click the submit button" | `stagehand.act("click the submit button", { page })` |
| "fill in the email field" | `stagehand.act("type %email% into the email input field", { variables: { email }, page })` |
| "select 'Monthly' from the billing dropdown" | `stagehand.act("select 'Monthly' from the billing frequency dropdown", { page })` |
| "open the settings menu" | `stagehand.act("click the settings or gear icon to open the settings menu", { page })` |
| "scroll down to the pricing section" | `stagehand.act("scroll down until the pricing section is visible", { page })` |
| "hover over the profile avatar" | `stagehand.act("hover over the user profile avatar or icon", { page })` |
| "drag the item to the done column" | `stagehand.act("drag the task card to the Done column", { page })` |

### Typed values: use `variables`, not inline text

There is no `value` parameter — typed input goes through `variables` with `%name%` placeholders
in the instruction:

```typescript
await stagehand.act("type %query% into the search bar", {
  variables: { query: "credit repair services" },
  page,
});
```

Per the Stagehand docs, variable *values* are substituted locally and are **not shared with the
LLM provider** — only the placeholder name appears in the prompt. This also keeps cache keys
stable across different values.

> **Warning — never pass secrets through the instruction string.** Everything in the instruction
> text is sent to the LLM. `stagehand.act(\`type ${password} into the password field\`)` leaks the
> secret. Use `variables` (as above) or deterministic keyboard input (see Auth Patterns).

### Pacing Between Steps

```typescript
// After navigation
await page.waitForLoadState("networkidle");
await page.waitForTimeout(1500);

// Between UI interactions (gives viewer time to follow)
await page.waitForTimeout(800);

// After modals / transitions
await page.waitForTimeout(1200);
```

---

## Click Overlay Injection

Adds a ripple animation at every click point. Inject this before the walkthrough starts.

Init scripts run at document start, when `document.head`/`document.body` may not exist yet —
the snippet defers style injection until the DOM is ready and guards every append.

```typescript
async function injectClickOverlay(page: Page) {
  await page.addInitScript(() => {
    const install = () => {
      const style = document.createElement("style");
      style.textContent = `
        .click-ripple {
          position: fixed;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: rgba(255, 100, 50, 0.6);
          pointer-events: none;
          transform: translate(-50%, -50%) scale(0);
          animation: ripple-anim 0.6s ease-out forwards;
          z-index: 999999;
        }
        @keyframes ripple-anim {
          0% { transform: translate(-50%, -50%) scale(0); opacity: 1; }
          100% { transform: translate(-50%, -50%) scale(2.5); opacity: 0; }
        }
      `;
      (document.head ?? document.documentElement).appendChild(style);

      document.addEventListener("click", (e) => {
        const ripple = document.createElement("div");
        ripple.className = "click-ripple";
        ripple.style.left = `${e.clientX}px`;
        ripple.style.top = `${e.clientY}px`;
        (document.body ?? document.documentElement).appendChild(ripple);
        setTimeout(() => ripple.remove(), 700);
      }, true);
    };

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", install, { once: true });
    } else {
      install();
    }
  });
}
```

---

## Auth Patterns

### Username/Password (from .env) — preferred: `variables`

```typescript
await stagehand.act("type %email% into the email field", {
  variables: { email: process.env.DEMO_EMAIL! },
  page,
});
await stagehand.act("type %password% into the password field", {
  variables: { password: process.env.DEMO_PASSWORD! },
  page,
});
await stagehand.act("click the sign in button", { page });
await page.waitForLoadState("networkidle");
```

### Fully deterministic alternative (no LLM sees the field interaction)

```typescript
await stagehand.act("click the email field", { page });
await page.keyboard.type(process.env.DEMO_EMAIL!);
await stagehand.act("click the password field", { page });
await page.keyboard.type(process.env.DEMO_PASSWORD!);
await stagehand.act("click the sign in button", { page });
await page.waitForLoadState("networkidle");
```

Both are safe for secrets. What is NOT safe is interpolating the secret into the `act()`
instruction string itself.

### Cookie-based Session (pre-authenticated)

If the app requires MFA or complex auth, export cookies from a logged-in browser and load them
into the context **before** navigating. Add them to the recording context (the one whose pages
you drive):

```typescript
import cookies from "../cookies.json"; // exported from browser DevTools
// requires "resolveJsonModule": true in tsconfig.json (included in the template above)

await recordingContext.addCookies(cookies);
const page = await recordingContext.newPage();
```

If instead you drive Stagehand's default context (no Playwright recording context), v3 exposes
the same API there:

```typescript
await stagehand.context.addCookies([
  {
    name: "session_id",
    value: "abc123",
    domain: ".example.com",
    path: "/",
    httpOnly: true,
    secure: true,
    sameSite: "Lax",
  },
]);
```

Each cookie needs either `url` or both `domain` and `path`. To export cookies from Chrome:
DevTools → Application → Cookies → right-click → "Copy all as JSON" (or use a cookie-export
extension). Treat the exported file as a secret — add `cookies.json` to `.gitignore`.

### Skip Auth Entirely (public demo)

If a public demo/sandbox environment is available, prefer it over recording a real login flow.

---

## Extracting Steps for .md Annotation

Keep a log array and write it after the walkthrough:

```typescript
const steps: { time: number; action: string }[] = [];
const startTime = Date.now();

function logStep(action: string) {
  steps.push({ time: Math.round((Date.now() - startTime) / 1000), action });
}

// In the walkthrough:
logStep("Navigate to the dashboard");
await page.goto("https://app.example.com/dashboard");

logStep("Click New Report button");
await stagehand.act("click the New Report button", { page });

// After walkthrough:
const mdContent = steps
  .map((s, i) => `${i + 1}. [${s.time}s] ${s.action}`)
  .join("\n");
fs.writeFileSync(path.join(OUTPUT_DIR, "walkthrough.md"), `# Walkthrough Steps\n\n${mdContent}\n`);
```

---

## Common Gotchas

- **`page.act(...)` / `act({ action, value })` are v2 APIs** — they do not exist in v3. If you see
  them in old examples, translate to `stagehand.act("instruction", { variables, page })`.
- **The video file won't exist until the recording context is closed** — always close
  `recordingContext` (and only then `saveAs`) in a `finally` block.
- **Playwright names the .webm with a random hash** — use `page.video()?.saveAs(...)` after the
  context closes to get a stable filename (the template above does this).
- **Stagehand can't see inside cross-origin iframes reliably** — if the target UI is in an iframe,
  use Playwright's `page.frameLocator()` and interact deterministically.
- **act() may fail on very fast transitions** — add `waitForTimeout(500)` before the act if the UI
  is mid-animation.
- **Headless recording looks different** — some CSS transitions/animations are disabled in
  headless; use `headless: false` during development.
- **No system Chrome found** — Stagehand's LOCAL env launches Chrome/Chromium; if it can't find
  one, point `localBrowserLaunchOptions.executablePath` at the Chromium installed by
  `npx playwright install chromium`.
