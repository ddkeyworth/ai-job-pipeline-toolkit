# Open issues

Known gaps to revisit.

## Score visibility for non-interview-stage applications

Score rationale currently only surfaces in full via the Briefing Pack, which is only generated once an application reaches `interviewing` or later. Most applications never get that far, so their score rationale lives only in the application file's own prose, with no dashboard-level way to browse or compare it. Worth deciding whether the dashboard should surface a condensed score rationale for every application, not just ones with a full Briefing Pack.

## Verify "Currently unknown" placeholder behavior in a fresh session

`SKILL.md` asks a session to attempt real synthesis for Briefing Pack sections and only fall back to a placeholder when genuinely no material exists. This hasn't been explicitly tested end-to-end in an independent session with thin source material. Worth a dedicated test to confirm it doesn't default to placeholders too readily, or over-fill with generic, unevidenced content.

## Recommended file-organisation guidance for new users

The README doesn't currently suggest a folder structure for a new user's own source documents (CVs, job descriptions, cover letters) before they start using the skill. Worth adding a short "before you start" section with a recommended layout, so ambiguity (which CV is current, etc.) is avoided rather than resolved reactively.

## Duplicate/reposted-role detection

The skill has no check for whether a company+role combination has already been scored or applied to before creating a new application file. Worth adding a lightweight pre-check that flags a likely duplicate or repost rather than silently creating a second record.
