# litestack

A fast, verified workflow for small features, bug fixes, refactors, and chores. Each task runs through a playbook and a fixed set of engineering principles in one session. There are no delegates, swarms, or multi-model review panels. What stays is the part that catches mistakes. Every change gets a pin before the first edit, verification on the real surface, and one independent review before it ships.

## Install

From a clone:

```bash
./install.sh
```

From GitHub:

```bash
curl -fsSL https://raw.githubusercontent.com/RayenTellissy/litestack/main/install.sh | sh
```

The script copies the `litestack` skill into `~/.claude/skills/` and the `litestack-reviewer` agent into `~/.claude/agents/`. Run it again to update. Start a new session after you install so the agent loads.

## Use

```
/litestack <task>
```

Litestack reads its principles, matches the task to a playbook, and copies the playbook's steps into a task list.

| Playbook | For | The pin |
|----------|-----|---------|
| Feature | A new option, field, command, endpoint, screen element, or validation rule | An acceptance check that fails today, covering every entry point |
| Bug fix | A defect to reproduce and root-cause | The repro, failing, on the surface where the bug shows |
| Refactor | A rename, extract, inline, dedupe, or move | Tests or recorded outputs that capture today's behavior |
| Chore | Docs, config, copy, dependency bumps, build fixes, tests | The build, render, or load that consumes the change |

A mixed task splits into parts, each with its own playbook and commit.

Every playbook ends the same way.

1. **Verify.** Rerun the pin, the type check, lint, and the touched tests. UI and CLI changes are driven on the real surface, through the project's `verify-*` skill when it has one. Output is pasted verbatim.
2. **Review.** One read-only `litestack-reviewer` on a different model from the session's. It reruns the fast checks, opens the evidence, and reviews the diff against the principles and the usual small-change traps. The session triages each finding, fixes what is real, and verifies again.
3. **Ship.** Small ordered commits in Conventional Commits form, and a ready PR with Why, What changed, Scope, Risk, and Verification sections.
4. **Reply.** What changed for the user, the pasted proof, the review outcome, the principles that shaped decisions, and the PR link.

## Gate

Litestack takes a change in one feature area, at most about 6 files and 300 lines. Public API, schema, and format changes must be additive and backward compatible. It refuses concurrency, auth, permissions, security, payments, and data deletion. A bug qualifies when its mechanism turns up within about three passes. A design fork qualifies when a quick sketch settles it.

When the task fails the gate or outgrows it midway, litestack stops and reports instead of pushing on. The report names the reason and hands over the pin and what it learned.

## Files

- `skills/litestack/SKILL.md` holds the router, gate, rules, review, and writing standards.
- `skills/litestack/principles.md` holds the principles that the session and the reviewer both apply.
- `skills/litestack/playbooks/` holds the Feature, Bug fix, Refactor, Chore, and Ship playbooks.
- `agents/litestack-reviewer.md` is the read-only reviewer.
- `install.sh` installs the skill and the agent.

## License

[MIT](LICENSE)
