# Permission Baseline

The standing default policy for `drill permissions`. These are decisions already made — they apply to every repo unless the owner explicitly opts out, and opting out of one is a `decline` with a written reason, not a silent omission.

Do not re-derive these per repo, and do not ask the owner whether they'd like secrets protected. What the repo supplies is the *specifics*: which paths, which services, which tools, which exceptions.

## Default policy

| # | Policy | Default | Strongest layer that usually holds it |
|---|---|---|---|
| 1 | **Secrets are not readable or writable by the agent** — `.env*`, credential files, keychains, production config | Deny | Tool deny rule (`Read`/`Edit`/`Bash` deny on the paths) |
| 2 | **Paid operations require explicit approval** — billable API calls, anything metered | Gate | Tool approval rule; hook on the specific CLI families |
| 3 | **Destructive git is restricted** — history rewrite, force-push, `reset --hard`, `clean -xfd`, `stash clear`, `reflog expire` | Deny, override available | Hook over enumerated git subcommands |
| 4 | **Broad staging is prevented** — `git add -A`, `git add .` | Deny, explicit paths instead | Hook on the `git add` family |
| 5 | **Data destruction is protected** — delete/move/truncate/overwrite of designated data paths and database files | Deny, override available | Filesystem isolation where possible; hook over enumerated command families otherwise |
| 6 | **Untrusted alternate tool surfaces are denied** — MCP shells, MCP filesystem servers, browser terminals not explicitly trusted in this repo | Deny | Tool deny rule (the only layer that works here) |

Policy 6 is what makes the other five mean anything. A hook registered on `Bash` does not see an MCP shell tool, so an unlisted MCP server with shell access voids policies 2 through 5 at once. Decide it in the same package, never as a follow-up.

## What the repo has to supply

The defaults above are policy. These are the facts that turn them into mechanisms — gather them in Phase 2c:

- **Paths** holding live, client, or sensitive data (policy 5)
- **Services** that cost money per call, and how they're invoked (policy 2)
- **Tools** deliberately trusted here, and which are denied (policy 6)
- **Override** mechanism, if the owner wants one for policies 3 and 5
- **Exceptions** the owner already knows they want

## What this baseline is not

It is not a set of files to copy in. Installing rules the repo has no evidence of needing is the over-scaffolding failure `ladder.md` warns about, and it's worse than useless here — a permission file full of rules for resources that don't exist reads as coverage and trains the owner to skim.

The baseline decides *what classes get protected*. The repo decides *what exists to protect*. A repo with no database gets no database rule, and that is the baseline working correctly, not being skipped.

## On claiming coverage

Every mechanism written from this baseline carries the same honesty requirement as everything else in `drill`: name the layer and the supported command families, never the resource. "Blocks `rm`/`mv`/`find` deletion of `data/` from Bash; interpreters and MCP filesystem tools are not covered" is true. "Protects `data/`" is not.
