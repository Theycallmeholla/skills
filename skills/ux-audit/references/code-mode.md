# Code Mode: Auditing a Flow from Frontend Source

You have the source. The advantage over a manual walkthrough is total: you can see *every* branch, validation rule, error state, and copy string — including the unhappy paths a click-through would never trigger. The challenge is reconstructing the lived experience from static code.

## Step 1: Orient

1. **Identify the framework and router.** Next.js (`app/` or `pages/`), React Router, Remix, SvelteKit, plain React, etc. The router tells you the screens and their order.
2. **Run `scripts/ui_inventory.sh <path>`** (if you have a shell) to list route/page files, components, form elements, and copy strings. Otherwise walk the directory tree by reading folders.
3. **Find the flow's entry point.** Where does the user land first — a marketing page, a `/signup` route, a funnel step? Start there.

## Step 2: Reconstruct the journey

Trace control flow the way a user moves through it:

- **Routes / pages** are your steps. For Next.js `app/`, each `page.tsx` is a screen; route groups and layouts shape the frame. For multi-step flows inside one route, the "steps" are component states.
- **Step machines** — look for the state that drives multi-step flows: a `step`/`currentStep` state variable, a wizard/stepper component, a state machine (XState), or an array of step components. This is the spine of the flow; map every state and the transitions between them.
- **Conditional rendering** — `{isLoggedIn ? ... : ...}`, `{error && ...}`, `{loading ? <Spinner/> : ...}`, `switch(step)`. Each branch is a state a user can land in. Enumerate them; the rare ones (error, empty, expired) are where flows break.
- **Navigation calls** — `router.push`, `<Link>`, `redirect()`, form `action`/`onSubmit` handlers. These are the edges between steps. Follow each to confirm where it lands and whether it loses state.
- **Guards & redirects** — middleware, `useEffect` redirects, auth checks. These are *gates*; note any that block access before value (Phase 3).

Write the explicit step map (Phase 1 of the audit) from this trace.

## Step 3: Read what the user reads

- **Copy strings** — labels, button text, headings, helper text, error messages, empty-state text, toasts. Pull them straight from JSX/strings/i18n files. This is the raw material for the Phase 4 clarity pass. Watch for placeholder-as-label (`placeholder="Email"` with no `<label>`).
- **Form definitions** — find the form library (React Hook Form, Formik, plain controlled inputs) and read the field list, the validation schema (Zod/Yup/custom), and the error-message strings. The schema tells you exactly what's required, what formats are accepted, and when validation fires (`mode: 'onSubmit'` vs `'onBlur'` vs `'onChange'`).
- **Input types & attributes** — `type`, `inputMode`, `autoComplete`, `required`, `aria-*`. Missing/incorrect ones are Phase 8/10 findings you can assert with certainty from code.

## Step 4: Verify the dynamic behavior you can't see

Some things are only visible at runtime. From code you can still infer most:

- **Loading/feedback** — is there a loading state between submit and result, or does the UI freeze? Look for pending state on mutations and disabled-button handling.
- **Latency-sensitive steps** — network calls in the flow (fetch, server actions). Flag any with no loading UI or no timeout/error handling.
- **Focus management** — on step change or modal open, is focus moved (`ref.focus()`, `autoFocus`)? Its absence is a real keyboard/screen-reader finding.

When a behavior truly can't be confirmed statically, note it as "verify against running app" rather than asserting.

## Evidence format for code mode

Cite `path/to/file.tsx:line` for every finding. Quote the minimal relevant snippet (a label string, a validation rule, a branch condition) — short, just enough to prove the point. Never paste large blocks.

## Code smells that become UX smells

These code-level patterns are reliable predictors of user-facing problems. Spotting one isn't proof of a bad experience (see the operating principle on code vs. user complexity) — it's a lead to chase from the user's side:

- **Near-duplicate components** rendering different versions of the same concept (`SignupForm`, `SignupFormV2`, `NewSignup`) — usually means the user meets inconsistent versions of one thing.
- **Button labels naming the implementation** ("Trigger sync," "Run job") instead of the user value.
- **Configuration asked before the outcome is explained** — setup steps that front-load decisions with no stated payoff.
- **Required fields with no user-facing justification** in the schema.
- **A screen rendering several primary actions** at equal weight.
- **Repeated save / continue / publish / review actions** whose differences aren't explained.
- **Internal state names** (`draft`, `pending`, `generated`, `enhanced`, `verified`) rendered directly with no translation.
- **Edge-case branches that silently reroute** the user without telling them why.
- **One step mixing unrelated concerns** — business identity + preferences + content + billing + publishing crammed into a single form.
- **Success states that don't say what happened or what's next** — a redirect with no confirmation.

## Common code-mode quick hits

- Required fields that aren't truly needed (cross-reference the schema against the stated goal).
- Validation `mode: 'onSubmit'` only → user discovers all errors at once, late.
- `placeholder` used as the only label.
- Generic error strings ("Something went wrong", "Invalid") with no recovery guidance.
- A multi-step `step` state with no progress indicator component anywhere.
- A branch (`error`, empty list, `!data`) that renders nothing or a bare message with no action.
- `router.push` after submit with no success confirmation in between.
- Missing `type="email"`/`inputMode` on obviously-typed fields.
- Auth guard redirecting to login before the user has seen any value.
