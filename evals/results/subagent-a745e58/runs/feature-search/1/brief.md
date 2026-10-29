You are a fresh Claude Code session. The user typed this command in the repository at /private/tmp/claude-501/-Users-ryan--claude-spares-spare-u1NzCf/69e29eb5-525f-441b-a171-2f2eff666512/scratchpad/evalwork/litestack-eval-subagent-a745e58-7588z0he/feature-search-1/repo:

/litestack Add a `search` command to the tasks CLI. `python3 -m tasks search <text>` lists the open tasks whose title contains <text>, ignoring case, in the same format as `list`. `--all` also includes done tasks, as it does for `list`. When nothing matches, it prints `No matching tasks.` and exits with status 1.

Run it. Read `/private/tmp/claude-501/-Users-ryan--claude-spares-spare-u1NzCf/69e29eb5-525f-441b-a171-2f2eff666512/scratchpad/evalwork/litestack-eval-subagent-a745e58-7588z0he/feature-search-1/repo/.claude/skills/litestack/SKILL.md` in full and follow it exactly, as if the user had invoked the skill. Its other files are next to it in `/private/tmp/claude-501/-Users-ryan--claude-spares-spare-u1NzCf/69e29eb5-525f-441b-a171-2f2eff666512/scratchpad/evalwork/litestack-eval-subagent-a745e58-7588z0he/feature-search-1/repo/.claude/skills/litestack/`.

Rules for this environment:
- Work only inside /private/tmp/claude-501/-Users-ryan--claude-spares-spare-u1NzCf/69e29eb5-525f-441b-a171-2f2eff666512/scratchpad/evalwork/litestack-eval-subagent-a745e58-7588z0he/feature-search-1/repo. Run every command from there. Never read or search outside it.
- The litestack-designer and litestack-reviewer agent types in this session may be an older install. For each, use `subagent_type: "general-purpose"` and open its brief with "Read `/private/tmp/claude-501/-Users-ryan--claude-spares-spare-u1NzCf/69e29eb5-525f-441b-a171-2f2eff666512/scratchpad/evalwork/litestack-eval-subagent-a745e58-7588z0he/feature-search-1/repo/.claude/agents/<type>.md` in full and follow it. Edit nothing." Keep the skill's other subagent rules.
- Nobody will answer questions. Decide as the skill says, and Stop where it says to Stop.
- Your final message is the skill's reply to the user.
