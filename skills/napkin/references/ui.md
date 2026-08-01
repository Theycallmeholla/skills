# UI Napkin

Generate **several radically different UI variants** on a single route, switchable from a floating bottom bar. The user flips between them in the browser, picks one (or steals bits from each), and the rest gets thrown away. If the question is about logic or state rather than appearance/behavior on screen, wrong branch — use [logic.md](logic.md).

## Host the variants in the real app — strongly preferred

A variant is much easier to judge **butting up against the rest of the app** — real header, real data, real density. A standalone route is a vacuum where every variant looks fine.

- **Preferred: existing page.** Render variants on the page's existing route, gated by `?variant=`. Existing data fetching, params, and auth all stay; only the rendered subtree swaps. A new section/card/step that would naturally live *inside* an existing page also counts — mount the variants in the host page.
- **Last resort: new throwaway route.** Only when the thing genuinely has no home (an entirely new top-level surface). Follow the project's existing routing convention, put `napkin` or `prototype` in the path, same `?variant=` pattern. Before choosing this, sanity-check that there's really no page to embed in — an empty route hides problems a populated one exposes.

## Process

### 1. Pick N and write the plan

Default **3 variants**; cap at 5 (past that it's noise, not exploration). One line, in a top-of-file comment next to the QUESTION:

> Three variants of the settings page, switchable via `?variant=`, on the existing `/settings` route.

### 2. Generate radically different variants

Each variant honors: the page's purpose and available data; the project's component/styling system; a clear exported name (`VariantA`, `VariantB`, ...).

Variants must be **structurally different** — different layout, information hierarchy, primary affordance. Three tweaked card grids isn't a napkin, it's wallpaper. If two drafts converge, redo one with an explicit exclusion ("no card grid").

### 3. Wire the switcher

One switcher on the route (pseudo-code — adapt to the framework):

```tsx
const variant = searchParams.get('variant') ?? 'A';
return (
  <>
    {variant === 'A' && <VariantA {...data} />}
    {variant === 'B' && <VariantB {...data} />}
    {variant === 'C' && <VariantC {...data} />}
    <PrototypeSwitcher variants={['A','B','C']} current={variant} />
  </>
);
```

Existing page: all data fetching stays above the switcher. Variants are **read-only** — if one needs a mutation, stub it; the question is what it should look like, not whether the backend works.

### 4. The floating switcher bar

Fixed at bottom-center: left arrow / `B — Sidebar layout` label / right arrow, wrapping both ways.

- Arrows update the URL param via the framework's router, so variants are shareable and reload-stable.
- `←`/`→` keys also cycle — but not when an input, textarea, or contenteditable is focused.
- Visually alien to the page (high-contrast pill, shadow) so nobody evaluates it as part of the design.
- **Hidden in production builds** — gate on the environment, so a stray merge can't ship it.
- One shared component, located wherever shared UI lives, so every future napkin reuses it.

### 5. Hand over, capture, clean up

Surface the URL and variant keys. The best feedback is usually composite — "header from B, sidebar from C" — that composite IS the answer. Capture QUESTION/ANSWER/EVIDENCE per the SKILL, fold the winner into the real page (rewritten properly — it was built under napkin rules), and remove losing variants and the switcher from the main branch. If the team wants the full variant set kept as a reference, park it on a throwaway branch — variant code left in main rots fast and confuses the next reader.

## Anti-patterns

- **Variants differing only in color or copy.** Real variants disagree about structure.
- **Sharing layout between variants.** A shared `<Header>` is fine; a shared `<Layout>` defeats the point.
- **Promoting variant code to production as-is.** Prototype constraints (no tests, minimal error handling) don't ship.
