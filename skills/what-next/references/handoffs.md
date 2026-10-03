# Hand-offs: who does the work

what-next doesn't do the work itself. Once the owner approves an action, it starts the skill or tool that does it, or writes manual steps when nothing fits.

## Resolve against what's installed, at run time

Read the available-skills list in this session (the system reminder that lists skills with their descriptions) and connected MCP tools. Match each approved action to a skill by **what its description says it does**, never by a name you remember. A skill named here may not exist on this machine. If nothing fits, write the steps out by hand: a numbered list the owner or Claude can follow, with the exact page, file or setting.

Typical matches, as shapes to look for rather than names to assume:

| Action | Look for a skill or tool that... | Fallback |
|---|---|---|
| Refresh or rewrite a blog post, a title/meta, a new section | plans, drafts or refreshes blog/web content in the business's voice with claim checks | Edit the page source directly, following the project's editorial rules |
| Fix a page that leaks visitors | audits conversion or UX on a specific page | Look at the heatmap, then edit the page |
| Check a page for broken or odd UI | scans a page for UI oddities or runs a usability pass | Open the page and inspect the element |
| Referral asks, review asks, follow-up messages | drafts email (a Gmail/email MCP that creates **drafts**) | Write the message text in chat for the owner to send |
| Request indexing, recrawl | Search Console tooling with inspection rights | Owner clicks Request indexing in the GSC UI |
| Deploy a change | the project's own deploy script or skill (read CLAUDE.md) | Leave undeployed and say so |
| Confirm a lead | none: owner knowledge | AskUserQuestion, then record in `profile.json` `people` |

## Rules for starting a hand-off

- **Approval first, per action.** Use one AskUserQuestion with `multiSelect: true` listing the ranked actions. Start only what the owner picks.
- **One at a time.** Start one hand-off, let it finish, then the next. Pass it the evidence row and the goal, not a pre-written solution.
- **Outward-facing steps keep their own confirmation.** Sending email, publishing a page, deploying, and posting all get confirmed again at the moment of action, inside the hand-off. An approved plan isn't permission to send.
- **Park the read when the action starts**, not when it's proposed: add the watchlist entry (date, baseline, exact read) as soon as the owner approves, so the next how-are-we-doing run picks it up.
