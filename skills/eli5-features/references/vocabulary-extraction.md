# Vocabulary Extraction

How to learn the product's UI terminology by reading its code, so the doc uses the same words the user sees on screen.

## Why this matters

A help doc that says "submit your closeout" when the button actually says "Send for Review" is broken. The user reads the doc, looks for the word, doesn't find it, gives up.

The fix is to **match the doc's vocabulary exactly to what's in the UI**. The skill should do this automatically by reading the code, not by guessing.

## Where UI strings live in different stacks

### React / Next.js / Vue / Svelte

- **JSX/TSX/template files** — string literals between tags, in attributes like `aria-label`, `title`, `placeholder`
- **Translation files** (if i18n) — `locales/en.json`, `messages/en.ts`, etc. These are the ground truth.
- **Constants** — files named `labels.ts`, `copy.ts`, `strings.ts` often centralize button text
- **Route titles** — `<title>` tags, Next.js `metadata.title`, page headings (`<h1>`, `<h2>`)
- **Form schemas** — Zod/Yup schemas often have field labels alongside validation

Quick extraction patterns:

```bash
# Button labels in JSX
grep -rE '<Button[^>]*>[^<]+</Button>' app/ components/
grep -rE '<button[^>]*>[^<]+</button>' app/ components/

# aria-labels and titles (often more accurate than visual text)
grep -rE 'aria-label="[^"]+"' app/ components/
grep -rE '\btitle="[^"]+"' app/ components/

# Page headings
grep -rE '<h[1-3][^>]*>[^<]+</h[1-3]>' app/ pages/

# Placeholders (form fields)
grep -rE 'placeholder="[^"]+"' app/ components/
```

### Plain HTML / templates

- `<button>` text directly
- `<label>` content for form fields
- `<title>` for page names
- Any framework-specific template tag (Handlebars `{{#each}}`, Liquid, ERB, Twig)

### Mobile (React Native / SwiftUI / Compose)

- `<Text>` content
- String resource files (`Localizable.strings`, `strings.xml`)

### Server-rendered (Rails / Django / Laravel)

- Views/templates (ERB, Jinja2, Blade) — same patterns as plain HTML
- Locale files (`config/locales/en.yml`, `locale/en/LC_MESSAGES/django.po`)
- Helper methods that wrap labels (`t('users.invite_button')` → look up the key)

## What to extract

For each feature you're documenting, you want a small list:

- **Button labels** — exact text on clickable elements involved in the flow
- **Field labels** — what each input is called in the UI
- **Page titles** — names of the pages the user visits
- **Status names** — if the feature involves statuses (e.g., "In Progress", "Resolved Review")
- **Section headings** — H1/H2 text on the relevant pages
- **Error messages** — what the user sees when things fail
- **Success messages** — confirmation text

You don't need every string in the app, just the ones the user encounters during this feature's flow.

## How to use what you extract

After extracting, when drafting the doc:

- **Refer to buttons by their exact label, in bold:** "Click **Send for Review**." Not "Click the submit button."
- **Refer to fields by their exact label, in bold:** "In **What changed**, write..." Not "In the description field..."
- **Refer to pages by their exact title:** "Go to **My Tickets**." Not "Go to your tickets page."
- **Refer to statuses by their exact name, in quotes:** The ticket moves to "Resolved Review." Not "the ticket moves to the review status."

## Tricky cases

### Capitalization

If the UI uses "Close Out" (capitalized as a label), the doc uses "Close Out" — both words, capitalized, when referring to the button. When using the same words as a verb in prose, you can lowercase: "to close out a ticket".

### Internal vs. external naming

Sometimes the code uses a different word than the UI. For example, the code may call it `actor.role.dev_admin` but the UI label says "Developer Admin" or just "Admin." Always use the UI string for the doc. The code identifier is for engineers; the doc reader never sees it.

### Conditional labels

A button that says "Submit" for one role and "Approve" for another is two different actions in the doc. Don't collapse them into one. Mention each context: "If you're the developer, you'll see **Send for Review**. If you're an admin reviewing, you'll see **Approve** instead."

### i18n / translation files

If the codebase has translation files (e.g., `locales/en.json`), those are the ground truth — they show the exact strings the user sees, with context keys. Read those preferentially over JSX scraping.

Example: a key like `"closeout.submit_button": "Send for Review"` tells you exactly what the button says and where it lives.

### Dynamic / templated strings

Strings like `"Welcome back, ${user.name}"` — the doc should describe the pattern, not invent a fake name. Write "the page greets you by name at the top" or use a placeholder: "the welcome line shows your name."

## When the vocabulary is messy

Real codebases are often inconsistent. The same concept might appear as "Closeout," "Close-out," "Close out," and "CloseOut" in different files. When this happens:

1. Look at what the *user* sees most — page headings, button labels in the most-used UI flow
2. Pick that one and use it consistently in the doc
3. Note the inconsistency to the user as an observation, not a complaint: "The UI uses 'Close Out' in most places and 'Closeout' in a few — I went with 'Close Out' in the doc since that's what's on the button."

The doc is a chance to be more consistent than the UI; just don't *invent* a new word.

## When you can't find a label

If you're documenting a feature and you can't find the user-facing name for some part of it:

1. Look harder — maybe it's in a sub-component
2. Look at older docs, if any exist
3. Ask the user: "What does this section get called in the UI? I see the code calls it `notificationPreferencesPanel` but I want to use the actual label."

Don't invent a name. The doc reader can't search for an invented term.

## Common UI vocabulary patterns to recognize

Some terms appear across many apps. Match the convention if the codebase uses it:

- "Save" vs "Submit" vs "Send" — apps usually pick one for similar actions
- "Settings" vs "Preferences" vs "Account" — usually distinct in a well-designed app
- "Sign in" vs "Log in" — pick whichever the UI uses, stick with it
- "Sign up" vs "Register" vs "Create account" — same
- "Profile" vs "Account" vs "My Info" — same
- "Notifications" vs "Alerts" vs "Updates" — same

If the codebase isn't consistent, again: pick what the user sees most and use that.
