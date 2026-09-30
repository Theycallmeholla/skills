# Sources: what each one measures, how it's read, known gotchas

Every endpoint here was verified against vendor docs or a live call. The date is when. Anything not listed gets checked against the vendor's docs before use, never recalled.

## Search Console (script: `gsc`), verified 2026-09-30

- Auth: service-account JSON key, scope `webmasters.readonly`. POST `https://www.googleapis.com/webmasters/v3/sites/{urlencoded siteUrl}/searchAnalytics/query`.
- Domain properties are `sc-domain:example.com`; URL-prefix properties are `https://example.com/`. Use exactly what `discover.py` lists.
- Data lags 2–3 days. The script finds the latest date with data and ends the window there.
- Country filter: `{"dimension":"country","operator":"equals","expression":"usa"}` (alpha-3, lowercase).
- Query rows are privacy-truncated, so query totals come to less than the date totals. Totals come from the `date` dimension.
- Average position is impression-weighted and moves when *new* low-ranking impressions arrive. A position "drop" alongside an impressions gain is usually reach, not a lost ranking. Check the page's clicks and its top query before calling it a loss.

## Indexing (script: `indexing`), verified 2026-09-30

- POST `https://searchconsole.googleapis.com/v1/urlInspection/index:inspect` with `{inspectionUrl, siteUrl}`, same key and scope as GSC. Quota: 2,000 inspections/day per property.
- Sitemap `<loc>` values are XML-escaped (`&amp;`). The script unescapes them. Without that, Google reports those URLs as "unknown", a false alarm that has happened once already.
- Indexed (PASS) results from a snapshot under 7 days old are reused, so a full pass (~2.5 min per 180 URLs) only runs weekly.
- Meaning: "Discovered – currently not indexed" = Google knows the URL and hasn't crawled it. "Crawled – currently not indexed" = crawled and chose not to index (a quality or duplication signal). "URL is unknown to Google" = never seen: check internal links and the sitemap.

## GA4 (script with `method: service_account`, or Claude via MCP)

- **MCP method** (verified 2026-09-30 with the `ga4-gtm` MCP's `ga4_run_report`): make these calls in parallel. Current window = N days ending **yesterday**, prior = the N days before. Pass exact `YYYY-MM-DD` dates. The MCP takes no filters, so filter rows yourself.

  | Call | dimensions | metrics | window | limit |
  |---|---|---|---|---|
  | channels-cur / channels-prev | `sessionDefaultChannelGroup` | `sessions, totalUsers, engagementRate, averageSessionDuration` | cur / prev | 20 |
  | landing | `sessionDefaultChannelGroup, landingPage` | `sessions, engagedSessions, averageSessionDuration` | cur | 250 |
  | events-cur / events-prev | `eventName` | `eventCount, totalUsers` | cur / prev | 100 |
  | cities | `sessionDefaultChannelGroup, city` | `sessions, engagementRate` | cur | 100 |

- **Service-account method:** POST `https://analyticsdata.googleapis.com/v1beta/properties/{id}:runReport`, scope `analytics.readonly`. A 403 "User does not have sufficient permissions" means the SA isn't a user on the property. The success path is written to the Data API contract but **hasn't yet been confirmed against a live property**. On the first profile that uses it, compare one number with the GA4 UI and record the result here.
- Realtime: if the MCP has a realtime report tool, active users over the last 30 minutes is the only real-time number available.

## Microsoft Clarity metrics (script: `clarity`), verified 2026-09-30

- GET `https://www.clarity.ms/export-data/api/v1/project-live-insights?numOfDays=1|2|3&dimension1=URL`, header `Authorization: Bearer <export token>`.
- **Limits:** 10 requests per project per day; the last 1–3 days only (UTC); up to 3 dimensions; 1,000 rows; no pagination. The script spends 2 calls per run (URL, Channel) and keeps a ledger (`clarity-calls.json`, default budget 8/day).
- Dimensions: Browser, Device, Country/Region, OS, Source, Medium, Campaign, Channel, URL.
- Response: a list of `{metricName, information:[...]}`. Observed metricNames and fields: `Traffic` (totalSessionCount, totalBotSessionCount, distinctUserCount, pagesPerSessionPercentage), `ScrollDepth` (averageScrollDepth), `EngagementTime` (totalTime, activeTime, in seconds), and `DeadClickCount` / `RageClickCount` / `QuickbackClick` / `ExcessiveScroll` / `ScriptErrorCount` / `ErrorClickCount` (sessionsCount, sessionsWithMetricPercentage, subTotal). Each row carries the dimension, e.g. `Url`.
- Because each window is only 3 days, the trend comes from **history snapshots over time**, not from one call.
- Bots leak past Clarity's own filter: 1–3 s sessions with zero clicks from datacenter countries. Treat tiny-session spikes as noise until checked.

## Clarity heatmaps (browser)

- There's no API for heatmaps. Only read them when the profile lists a Clarity login under `browser`.
- Open the project from `https://clarity.microsoft.com/projects/view/<projectId>/dashboard`, then Heatmaps from the project's own navigation. Don't guess deeper URLs.
- Pick pages from the pull: high traffic with low scroll depth, dead/rage clicks, or a page an opportunity is about. Read the click map and the scroll map, and report what's clicked, what's ignored, and where attention stops. Dead clicks on plain text are usually people selecting text, not broken UI: check what the element is before calling it a bug.

## Google Business Profile (browser)

- The GBP Performance API needs OAuth plus approved API access. It isn't wired here. Only read GBP when the profile lists a login.
- Read whatever the profile's Performance view shows (searches, views, calls, website clicks, direction requests, and so on). Record each metric **with its on-screen label, date range and comparison exactly as shown**. Don't rename or reinterpret them.
- Reviews: count, average and newest dates, from the profile or Maps listing.

## GoHighLevel (script: `ghl`), verified 2026-09-30

- Private integration token; send a browser-like User-Agent (Cloudflare returns 1010 otherwise).
- `GET /calendars/events?locationId&calendarId&startTime&endTime` (ms epoch, header `Version: 2021-04-15`). The range filters on appointment **start** time, so the script queries wide and buckets by `dateAdded` (when it was booked).
- `POST /contacts/search` (Version 2021-07-28) with `{"locationId","page","pageLimit":100,"filters":[{"field":"tags","operator":"contains","value":"<tag>"}]}`.
- `GET /contacts/{id}`, `GET /opportunities/pipelines?locationId=`, `GET /opportunities/search?location_id=&pipeline_id=&limit=100` (follow `meta.nextPageUrl`).
- If every opportunity is `open`, won/lost isn't recorded. Report "not measured", never "0 won".

## Ahrefs Domain Rating (script: `ahrefs_dr`), verified 2026-09-30

- `GET https://api.ahrefs.com/v3/public/domain-rating-free?target=<domain>`, header `Authorization: Bearer <key>`. Works on a free/public-tier key. Other v3 endpoints return 401 on that tier.
- DR moves slowly and in steps. Report the value and the last snapshot's value, not a trend line.

## Custom commands (script: `commands`)

- `profile.sources.commands.list[] = {name, run, description, timeout}`. It runs with the profile folder as cwd. The **last stdout line** must be a JSON array of rows. `at_ms` (epoch ms) puts a row in or out of the window, and `contactId` gets classified through GHL. Use this for anything a single business has (its own server logs, tool records, a local database).
