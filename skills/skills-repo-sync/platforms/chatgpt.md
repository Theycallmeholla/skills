# Skills Repo Sync for ChatGPT

Keep `Theycallmeholla/skills` current using ChatGPT's connected GitHub repository as the source and destination. ChatGPT cannot enumerate an account-level local skills directory, so this version synchronizes only skills explicitly supplied in the conversation, available as files, or already present in a connected repository or branch.

## Intake sources

Accept a candidate skill from one of these sources:

1. an uploaded skill folder or ZIP
2. a GitHub branch, pull request, or repository path
3. a skill created in the current conversation
4. a mounted file tree available to the execution environment

Do not claim to discover private ChatGPT account skills automatically.

## Procedure

1. Inspect the candidate and locate exactly one `SKILL.md` entrypoint per skill folder.
2. Establish authorship and publication intent. Never publish a skill unless the user explicitly asked to add that skill to the public repository.
3. Check `.publish-denylist` and reject matches without offering to publish them.
4. Compare the candidate against `skills/<name>/` on the target branch.
5. Preserve the complete folder structure: `SKILL.md`, `agents/`, `references/`, `assets/`, and `scripts/` when present.
6. Validate the shared skill and cross-platform declaration:

```bash
python3 scripts/validate_skills.py .
python3 scripts/validate_cross_platform.py .
```

7. Build both targets:

```bash
python3 scripts/build_skills.py --target chatgpt --skill <name>
python3 scripts/build_skills.py --target claude --skill <name>
```

8. Scan added or changed files for credentials, personal data, client identifiers, internal URLs, and non-placeholder contact details.
9. Update the README index and compatibility manifest when required.
10. Commit the changes on a feature branch and open a pull request. Do not push directly to `main` unless the user explicitly requests direct changes and repository policy permits it.

## Existing skills

Never silently overwrite an existing skill. Show the material differences, preserve unrelated files, and update only the approved skill.

## ChatGPT metadata

The shared source may omit `agents/openai.yaml` because the builder can generate it. Add explicit metadata only when a custom display name, icon, or interface description is needed.

## Verification report

Report:

- skills added or updated
- validation and build results
- files changed
- security or privacy findings
- branch and pull request

Never claim account-level installation or synchronization. This skill manages the GitHub source repository and distributable packages only.