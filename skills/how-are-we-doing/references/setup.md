# Setup: making a business profile

Goal: a profile that can run unattended next time. Discover first, then ask only what discovery couldn't answer. A question whose answer is already on disk wastes the user's time.

## 1. Discover (no questions yet)

```bash
python3 <skill dir>/scripts/discover.py --root . --domain <domain>
```

If you don't know the domain yet, ask for it first. It's the one question that has to come before discovery. The script prints JSON:

- `env_keys`: key **names** in `.env*` files grouped by source (GHL, Clarity, Ahrefs, ...). Values are never read.
- `service_accounts`: each Google service-account key found, its `client_email`, and which **Search Console** and **GA4** properties it can read. An empty list means no access. An `error` gives the exact reason.
- `mcp_servers`: configured MCP servers whose names suggest analytics, CRM or browser tools. Configured isn't the same as connected, so check your own tool list for the ones that loaded this session.
- `site`: GA4 measurement ids, GTM containers, Clarity project id, Ahrefs analytics tag, and sitemap URLs from robots.txt.

Also check this session's tools for a GA4 MCP (a `run_report`-style tool) and a browser tool (Claude in Chrome, Playwright, and so on).

Match what you found to sources:

| Source | Ready when | Else |
|---|---|---|
| Search Console | a service account lists the domain's property | Owner adds the SA email as a **Full** user in GSC → Settings → Users and permissions. Restricted can read Performance, but Google's permission table limits its URL Inspection to "Fetch only", so the indexing check needs Full. |
| Indexing | GSC is ready and a sitemap was found | same |
| GA4 | a service account lists the property (method `service_account`), or a GA4 MCP can read it (method `mcp`) | Owner adds the SA email in GA4 Admin → Property access management as **Viewer** (Google: "Can see settings and data ... via the user interface or the APIs") |
| Clarity metrics | a Clarity **export token** key name exists (a project id alone isn't enough) | Owner (a project admin) makes one: Clarity → Settings → Data Export → Generate new API token |
| Clarity heatmaps | someone can log into clarity.microsoft.com in a browser Claude can drive | skip |
| Google Business Profile | someone can log into the profile's Google account in a browser Claude can drive | skip |
| GoHighLevel | a private integration token key name exists + the location id | skip, or owner creates a PIT (Settings → Private Integrations) with contacts, calendars/events and opportunities read scopes |
| Domain Rating | an Ahrefs API key name exists | skip |

Probe each "ready" source once with a real read before trusting it. Discovery says a key *exists*; only a call proves it *works*.

## 2. The questionnaire

Use **AskUserQuestion** (up to 4 questions per call; the user can always type "Other"). Put what discovery found in the options so the user confirms instead of typing. Skip any question discovery already answered.

**Round 1: the business**
1. *Which business is this for, and what does it sell?* Offer the site's title and main service pages as the draft. This feeds the buyer test for opportunities.
2. *Who are the buyers, and where?* E.g. "Houston homeowners", "US SMBs". Sets `market.gsc_country` (GSC uses ISO-3166 alpha-3, lowercase: `usa`, `can`, `gbr`) and tells the reader which clicks matter.
3. *What counts as a lead?* Offer what exists: CRM calendar bookings, form fills (with the CRM tag), calls, GA4 key events discovery saw. Name the **one** that matters most.
4. *Which of these can Claude log into with the browser?* (multiSelect) Clarity dashboard, Google Business Profile, GA4 UI, other.

**Round 2: access gaps** (only for sources the user wants that aren't ready)
- Offer the exact fix from the table above: "add `<sa email>` to GSC as Restricted", "generate a Clarity export token and put it in `.env.local` as `CLARITY_EXPORT_TOKEN`". Never ask for a secret's value in chat. Ask the user to put it in an env file, and store only the file + key name.

**Round 3: what would mislead** (short, optional, skippable)
- *Anything in the numbers we should ignore?* E.g. staff test bookings, internal email domains, bot-heavy channels, a page that ranks for the wrong audience, or a known ranking oddity. These go in `people` / `noise` and in `notes.md`.
- *Anything we're waiting to see the result of?* E.g. a refreshed page or a title test. Each answer becomes a watchlist item with a date and a baseline.

## 3. Write the profile

Create `<root>/.claude/how-are-we-doing/<slug>/` from `templates/`:

- `profile.json`: start from `templates/profile.example.json`. Delete sources that aren't set up rather than leaving placeholders. Credential fields are **pointers only**: `{"env_file": ".env.local", "env_key": "NAME"}`, `{"env": "NAME"}` for a shell variable, or `"key_file": "<path to SA json>"`. Relative paths resolve against `root` (default `"../../.."`, the project root for this folder layout).
- `notes.md`: this business's reading context, in the owner's words where possible.
- `watchlist.md`: dated items from Round 3, plus the standing checks that apply.
- Gitignore check, as described in SKILL.md.

## 4. First pull

Run the pull. Show the summary, and before reporting anything, check with the user:
- Are the people classified correctly? (Every `unconfirmed` person gets a question.)
- Do the top pages and queries look like this business? A wrong GSC property looks plausible and misleads for months.

The first run has no "since last snapshot" line. Say so; the derivative starts on the next run.
