# Write-set analysis (shared procedure, not a command)

Loaded by **split** every time (to predict write-sets) and by **land** when it has to decide whether a file outside a lane's write-set is a real violation or a predictable miss.

A write-set is the list of files and resources a lane is allowed to change. Two lanes can run at the same time only if their write-sets cannot overlap. Reads never matter: any lane may read anything.

---

## 1. Predict a task's write-set

Work from most concrete to least. Stop at the first level that gives a real answer.

1. **Paths the plan names.** Take them literally, then check each one exists (`git ls-files`, `ls`, a search). A path that doesn't exist is either a new file (fine, record the exact intended path) or a typo (fix it from the repo, and say so).
2. **Paths the codebase implies.** The plan says "add a password-reset endpoint"; the repo has `src/api/auth/login.ts` and `src/api/auth/index.ts`. The write-set is the new file `src/api/auth/reset.ts` plus `src/api/auth/index.ts` if that's where routes get registered. Search for the pattern the task would follow (how was the last similar thing added?) and copy its footprint.
3. **A narrow glob**, only when the task is truly vague ("clean up the auth module"). Use the smallest directory that contains the work: `src/api/auth/**`, never `src/**` and never `**`.

Name files, not vibes. "The backend" is not a write-set.

### Hidden writes: check every task against this list

Agents touch files the plan never mentions. These are the usual culprits, and the usual cause of two "independent" lanes colliding:

| Category | Typical files | Trigger in the task |
|---|---|---|
| Dependency manifests | `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `requirements.txt`, `poetry.lock`, `go.mod`/`go.sum`, `Cargo.toml`/`Cargo.lock`, `composer.json`/`.lock` | adds or upgrades a library |
| Schema and migrations | `prisma/schema.prisma`, `migrations/**`, `*.sql`, ORM model files | new field, new table, new relation |
| Generated code | Prisma client, GraphQL/OpenAPI types, `*.generated.*`, `types/` | anything that changes a schema or API contract |
| Registries and barrels | `index.ts` re-exports, route tables, nav/menu configs, DI containers, plugin lists, `urls.py` | adds a new route, page, component, or service |
| Strings and content | i18n files (`locales/*.json`), copy files, CMS seed data | adds user-facing text |
| Config | `.env.example`, `config/*`, feature flags, `next.config.*`, `vite.config.*`, `tsconfig.json` | new env var, new build behavior |
| Global styles | theme tokens, `globals.css`, Tailwind config | new color, spacing, or global class |
| Tests and fixtures | the task's own tests (include these), shared fixtures, snapshot files, test helpers | any change with tests |
| Docs | `README.md`, `CHANGELOG.md`, `docs/**` | user-facing change, release notes |
| CI and tooling | `.github/workflows/**`, lint configs, scripts | new check, new build step |

Add a task's own tests to its write-set. Shared fixtures, snapshot files and test helpers are hotspots: treat them like shared files.

### Resources that aren't files

Write them into the write-set as tokens so overlap checks catch them:

- `db:<name>` — a shared dev database a task migrates or seeds
- `port:<n>` — a dev server or service port the task needs bound
- `service:<name>` — an external system the task writes to (a Stripe test account, a shared Supabase project, a CMS)
- `global:<thing>` — global installs, shared caches, machine-level config

Git itself (branch, index, working tree) is a shared resource too, but split solves that with one worktree per lane, so it doesn't go in write-sets.

---

## 2. Confidence

Give every lane's write-set one confidence level, the lowest of its tasks:

- **high** — every path is named or verified in the repo
- **medium** — inferred from codebase conventions (step 2 above)
- **low** — a guess: no repo access, or the task is too vague to place

**Low confidence counts as unknown** for partitioning.

## 3. Unknown write-sets

An unknown write-set conflicts with everything. Before accepting that, escalate in this order:

1. **Read the code.** Most unknowns die after one search. Cheap; always try it.
2. **Ask the user**, all remaining unknowns batched into one question, each with your best guess attached. Skip this when the user said they're walking away.
3. **Isolate it.** The task becomes its own lane that runs alone: either before every other lane (if others build on it) or after all of them (if it touches broad territory). It never runs alongside anything. This keeps the rest of the plan parallel instead of collapsing the whole thing to sequential.

---

## 4. Overlap test

Two write-set entries overlap when any of these hold:

- same path
- a glob matches the other's path (`src/api/auth/**` and `src/api/auth/index.ts`)
- two globs could match the same path (one directory contains the other, or patterns intersect)
- same resource token (`db:dev` and `db:dev`)
- either one is unknown

Overlap is symmetric. When in doubt, call it an overlap: a false "these conflict" costs a little wall time, a false "these are safe" costs a merge mess.

---

## 5. Near-miss rubric (used by land)

For each file a lane actually changed that is **not** in its declared write-set, classify it:

| Class | Test | Severity |
|---|---|---|
| **collision** | The same file was changed by two or more lanes that ran at the same time (not ordered by `depends_on`) | Highest. Always. Merge will conflict or silently clobber. |
| **violation** | The file is in another lane's write-set, or is a shared file owned by another lane | High. The partition broke even if no collision happened yet. |
| **predictable-miss** | Nobody declared it, and it's a hidden-write category (section 1 table) tied to this lane's own work, e.g. a lockfile after this lane added a dependency | Medium. Not a collision on its own, but split should have caught it. Note it so the next split does. |
| **stray** | Nobody declared it and it has no link to the lane's tasks (a reformatting sweep, a drive-by fix, an accidental edit) | Medium. Needs a human look before merge. |

Ignore as noise, never classify:

- `.agent-smiths/**` (this skill's own state)
- the lane worktree folders themselves (`.claude/worktrees/**`, or wherever split put them)
- files the repo's `.gitignore` excludes (build output, caches)
- OS junk (`.DS_Store`, `Thumbs.db`)

A rename counts as a change to both the old path and the new path.
