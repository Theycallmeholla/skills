# Performance & Scalability Checklist

Don't speculate. Look for the patterns that bite under real load. The list below is ordered roughly by impact-per-incidence: database issues are usually #1, frontend issues #2, everything else farther down.

## 1. Database access patterns

### N+1 queries

The most common production performance bug. Pattern:

```js
// Fetch list of orders, then loop through and fetch each customer
const orders = await db.query('SELECT * FROM orders');
for (const order of orders) {
  order.customer = await db.query('SELECT * FROM customers WHERE id = ?', [order.customer_id]);
}
```

What looks like 1 query is actually `1 + N`. With 1,000 orders, you get 1,001 queries — and the query log shows it instantly.

How to find:
- Loops with `await` on a database call inside
- ORM `.map`/`.forEach` accessing a relation that wasn't eager-loaded
- ORM N+1 typical signatures: Sequelize without `include`, ActiveRecord without `includes`/`preload`, Django without `select_related`/`prefetch_related`, Prisma without `include`

Fix: batch fetch with `WHERE id IN (...)` or use the ORM's eager-loading.

### Missing indexes

Look at WHERE/JOIN/ORDER BY columns and check the schema. Common missing indexes:

- Foreign key columns (most engines don't auto-index FKs)
- Columns used in `WHERE` filters in hot endpoints
- Columns used in `ORDER BY` for paginated queries
- Composite indexes for queries with multiple filter columns (column order matters)

Verify on a running system with `EXPLAIN` / `EXPLAIN ANALYZE`. If you can't run it, flag suspicious queries for the owner to verify.

### `SELECT *` on wide tables

A users table with a `bio` TEXT column or a `preferences` JSONB column means `SELECT *` ships kilobytes of irrelevant data per row. List queries especially should select only what's rendered.

### Pagination

- Offset pagination (`LIMIT 50 OFFSET 100000`) gets pathologically slow on large offsets — the DB still has to count past the skipped rows
- Cursor / keyset pagination (`WHERE id > last_id LIMIT 50`) scales properly
- Hard limit on page size — `?limit=1000000` should be capped server-side

### Transaction scope

- Transactions that span network calls (HTTP, queue publish) hold DB locks while waiting for I/O — unacceptable
- Transactions held open across slow user input (form processing) — same problem
- "Long-running read transactions" in PostgreSQL block VACUUM and cause table bloat

### Connection pools

- Pool sized appropriately (not 5 connections for 200 req/sec, not 500 for a small app)
- Connection leak detection: connections checked out and never returned
- Pool exhaustion handling — what happens when no connection is available? Block forever, or fail fast with a useful error?

## 2. Caching

### Where it should exist but doesn't

- Hot-path computations that are deterministic and recomputed every request
- External API calls in the request hot path with no caching
- Database lookups for slowly-changing data (config, feature flags, lookup tables) hit on every request
- Rendered output for anonymous traffic (HTTP cache, CDN)

### Where it exists but is wrong

- **Cache key collisions**: two different inputs producing the same key. Audit the key derivation.
- **Cache stampede**: cache expiry causes a thundering herd of regeneration. Defenses: probabilistic early refresh, single-flight locking.
- **Stale data with no invalidation**: cache writes data, source updates, cache returns stale. Either short TTL or write-through invalidation.
- **In-memory caches in horizontally-scaled apps**: each instance has its own cache, hit rates collapse, "cached" data isn't consistent across instances. Use Redis/Memcached.
- **Caching authenticated responses with no per-user key**: user A sees user B's data. Critical security finding, listed here because it's caching-shaped.

## 3. Synchronous I/O on hot paths

Anywhere a request handler does blocking work serially when concurrent or async would do:

- File reads with `readFileSync` in request handlers (Node)
- HTTP calls without timeouts — one slow upstream blocks the request, then the worker, then the pool
- Cryptographic operations (`bcrypt.hashSync` in a route handler) blocking the event loop
- Loading large datasets fully into memory before returning (use streaming)

Verify timeouts on every external call:
```bash
grep -rEn 'fetch\s*\(|axios\.|requests\.|httpClient\.' --include='*.{js,ts,py}' . | head
```
Check each result has explicit timeout configured.

## 4. Memory

### Leaks

- Event listeners added without removal (especially in long-lived processes)
- Closures capturing large objects unnecessarily
- Module-level caches with no eviction (they grow forever)
- Timers/intervals never cleared

### Excessive allocation

- Loading entire files / datasets when only a portion is needed (use streams)
- Re-allocating in tight loops (string concatenation in JVM, list comprehension that could be generator in Python)
- Large objects copied where references would do

## 5. Algorithmic complexity

- O(n²) where O(n) is available — most commonly nested loops over the same collection where a hash map would do
- Repeated sorting of the same collection
- Linear scans of large lists where a `Set` or `Map` is appropriate
- Recursive solutions without memoization on overlapping subproblems

## 6. Concurrency / parallelism missed

- Sequential `await` of independent operations that could run in parallel:
  ```js
  const a = await fetchA();
  const b = await fetchB();   // Could be Promise.all([fetchA(), fetchB()])
  ```
- Sequential database queries that could be batched into a single round trip
- Single-threaded processing of work that's embarrassingly parallel

## 7. Serialization

- JSON parsing/stringifying huge payloads in request hot paths
- Repeatedly serializing the same data (cache the serialized form)
- Inefficient serialization formats where binary/columnar would be appropriate (transferring 100MB of CSV on every request)

## 8. Frontend specifics

If the codebase has a frontend:

### Bundle size

- Bundle analyzer output should exist or be runnable. If a single bundle is >1MB gzipped, that's a finding for typical web apps.
- Importing entire libraries when tree-shaking would suffice (`import _ from 'lodash'` vs `import debounce from 'lodash/debounce'`)
- Polyfills shipped to modern browsers
- Source maps shipped to production end-users (security concern + size)

### React/Vue rendering

- Components that render unnecessarily — children re-rendering when the parent updates an unrelated piece of state
- `useEffect` with missing dependencies (silent staleness) or unnecessary dependencies (excess re-runs)
- Inline object/function props in render breaking memoization
- Large lists rendered without virtualization (1000+ items)

### Network

- Waterfall: each request waits for the previous to finish. Check if requests can be batched or parallelized.
- Missing request deduplication — same data fetched 5x because 5 components needed it
- No HTTP caching headers on static assets, or cache-busting URLs missing for assets that change

### Images and media

- Images served at native resolution into small UI elements (1080p photo in a 64×64 avatar)
- No `loading="lazy"` on below-fold images
- No modern formats (WebP, AVIF) where browser supports them
- Large inline SVGs that could be optimized with SVGO

### Render-blocking

- Synchronous third-party scripts in `<head>`
- Critical CSS not inlined for above-fold content
- Missing `<link rel="preload">` for critical resources

## 9. External dependencies (network calls)

- Sequential calls to external APIs that could be parallel
- No timeouts (covered above) — every external call must have a timeout
- No retries on transient failures, OR aggressive retries with no backoff (cascading failure)
- No circuit breakers on dependencies that go down — every request paying the timeout cost
- No rate limiting on outbound calls — burst traffic gets your IP throttled by the provider

## 10. Background jobs / queues

- Long-running tasks done synchronously in the request path (sending email, generating PDF, calling slow API). Move to background workers.
- Queue with no dead-letter handling: failures retry forever or get silently dropped
- No idempotency on jobs that might be retried — duplicate side effects

## 11. Build / startup performance

- Production deploys taking 20+ minutes because of inefficient pipelines (full rebuild instead of incremental, no caching of node_modules, no parallel jobs)
- Cold-start time on serverless runtimes — large bundles, heavy init code, sync requires of optional dependencies
- Long boot time blocking horizontal scaling responsiveness

---

## How to talk about performance findings

Performance findings often look bad on paper but don't matter at the project's actual traffic. Calibrate:

- "An N+1 on an admin page hit twice a day" → Low or Info
- "An N+1 on the home page that everyone hits" → High or Critical
- "Bundle is 1.5MB" → context-dependent: matters more for a public landing page than an internal dashboard

When in doubt, ask the owner about traffic patterns before assigning severity.

## Verification

Wherever possible, verify findings rather than assert them:

```bash
# Find database calls inside loops (Node)
grep -rEn 'for.*\{[^}]*\b(await|\.then)\s*[^.]*\.(query|find|select)' --include='*.{js,ts}' .

# Look for missing await (returns Promise)
grep -rEn 'function.*\{[^}]*\.then\s*\(' --include='*.{js,ts}' .

# Synchronous file ops in Node
grep -rEn '\b(readFileSync|writeFileSync|existsSync|statSync)\b' --include='*.{js,ts}' .

# Sequential awaits that could parallelize
grep -B1 -rEn '^\s*const \w+ = await ' --include='*.{js,ts}' . | grep -B1 'const \w+ = await' | head
```

Real performance issues should be measurable. If you can't measure, mark the finding "needs verification under load" and move on.
