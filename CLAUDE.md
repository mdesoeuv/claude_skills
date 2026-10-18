# Claude Code skills repository

- One skill per directory under `skills/<name>/SKILL.md`. Keep the layout flat; the tier (`core` or `recommended`) lives in frontmatter `metadata.tier`, not in folder nesting.
- Every SKILL.md needs `name` and `description`; the description is the trigger, so it states both what the skill does and when to use it.
- Keep each SKILL.md under ~150 lines. Put long reference material in `skills/<name>/references/` and link to it.
- Explain the why behind each rule; avoid shouting MUST/NEVER without a reason.
- Validate with `claude plugin validate .` before committing. Install locally with `./install.py --all` to try changes.
