You are a fresh Claude Code session. The user typed this command in the repository at /private/tmp/claude-501/-Users-ryan--claude-spares-spare-63SXoD/e01a2c93-f207-4c1f-9092-0c98579bcf0a/scratchpad/driver/work/tmpeg6vvbxm/tmp135j9tch/tasks:

/litestack Add an optional due date to tasks. `python3 -m tasks add <title> --due YYYY-MM-DD` stores the date with the task. `list` prints it after the title and tags as ` due YYYY-MM-DD`, as in `[ ] 1 Buy milk #home due 2026-11-01`. Tasks without a due date print as before. `list --overdue` lists only the open tasks whose due date is earlier than today, and prints `No tasks.` when there are none. An invalid date, such as `2026-02-30`, makes `add` exit with status 2 and print an error that names the value to stderr, and nothing is stored. Task files written before this change must still load.

Run it. Read `/private/tmp/claude-501/-Users-ryan--claude-spares-spare-63SXoD/e01a2c93-f207-4c1f-9092-0c98579bcf0a/scratchpad/driver/work/tmpeg6vvbxm/tmp135j9tch/tasks/.claude/skills/litestack/SKILL.md` in full and follow it exactly, as if the user had invoked the skill. Its other files are next to it in `/private/tmp/claude-501/-Users-ryan--claude-spares-spare-63SXoD/e01a2c93-f207-4c1f-9092-0c98579bcf0a/scratchpad/driver/work/tmpeg6vvbxm/tmp135j9tch/tasks/.claude/skills/litestack/`.

Rules for this environment:
- Work only inside /private/tmp/claude-501/-Users-ryan--claude-spares-spare-63SXoD/e01a2c93-f207-4c1f-9092-0c98579bcf0a/scratchpad/driver/work/tmpeg6vvbxm/tmp135j9tch/tasks. Run every command from there. Never read or search outside it.
- The litestack-designer and litestack-reviewer agent types in this session may be an older install. For each, use `subagent_type: "general-purpose"` and open its brief with "Read `/private/tmp/claude-501/-Users-ryan--claude-spares-spare-63SXoD/e01a2c93-f207-4c1f-9092-0c98579bcf0a/scratchpad/driver/work/tmpeg6vvbxm/tmp135j9tch/tasks/.claude/agents/<type>.md` in full and follow it. Edit nothing." Keep the skill's other subagent rules.
- Nobody will answer questions. Decide as the skill says, and Stop where it says to Stop.
- Your final message is the skill's reply to the user.
